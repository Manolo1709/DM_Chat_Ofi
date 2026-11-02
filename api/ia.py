"""Cliente del modelo de lenguaje que redacta la explicación del resultado.

Usa la API de chat compatible con OpenAI (`POST {LLM_BASE_URL}/chat/completions`),
que ofrecen OpenRouter, OpenCode Zen, OpenAI, Groq, etc. Por defecto, OpenRouter.

La tasa la calcula el servidor con la fórmula de Widmark de `api.calculo` y se le
pasa ya hecha a la IA, que solo la explica: recibe enums y números (nunca texto
libre del usuario) y devuelve JSON con `tasa_gl`, `explicacion` y `consejos`.
La clave vive solo en el servidor.
"""

import json
import os
import re

import httpx
from pydantic import ValidationError

from api.calculo import (
    ELIMINACION_GL_H,
    calcular_tasa,
    clasificar_nivel,
    horas_hasta_cero,
)
from api.schemas import CalculoIA, CalculoRequest, EstomagoEnum, ExplicacionIA, NivelEnum

TIMEOUT_S = 30.0
BASE_URL_POR_DEFECTO = "https://openrouter.ai/api/v1"
MODELO_POR_DEFECTO = "nvidia/nemotron-3.5-lightning:free"

PROMPT_SISTEMA = """\
Eres el camarero responsable de una taberna. Recibes los datos de una persona, lo que ha \
bebido y su tasa de alcohol en sangre (g/L), ya calculada por el servidor con la fórmula de \
Widmark. También recibes el nivel y las horas de espera.

NO recalcules nada: usa exactamente esos números. En "tasa_gl" copia la tasa recibida.

Niveles: menos de 0,2 sobrio; menos de 0,8 alegre; menos de 1,5 borracho; desde 1,5 peligroso. \
Límites legales para conducir en España: 0,5 g/L en general y 0,3 g/L para noveles \
(menos de 2 años de carné) y profesionales.

Responde EXCLUSIVAMENTE con un objeto JSON válido, sin markdown ni texto alrededor, con esta forma:
{"tasa_gl": <número con 2 decimales>, "explicacion": "<4-5 frases en español>", \
"consejos": ["<consejo>", "..."]}

Quien lee puede haber bebido y le cuesta concentrarse. Escribe para que se entienda a la primera:
- Frases cortas (máximo 15 palabras), una idea por frase, sin subordinadas largas.
- Palabras sencillas y sin tecnicismos (nada de UBE ni gramos). A "coctel" llámalo "cubata".
- Números redondeados: horas a la media hora más cercana ("unas 3 horas y media").
- Tono claro y respetuoso, en tú, sin coloquialismos, bromas, jerga ni exclamaciones.

La "explicacion" debe ser concreta para ESTA persona, con sus datos:
- Qué ha bebido, nombrando sus bebidas tal como las recibes (por ejemplo "4 cubatas y 2 vinos"). \
No conviertas a copas estándar ni a gramos: confunde.
- Cómo puede sentirse con esa tasa (reflejos, equilibrio, decisiones, sueño...).
- Cuántas horas faltan para llegar a 0, y si está por encima de 0,5 o 0,3 g/L, \
cuántas horas para bajar de cada límite.

Reglas:
- "consejos" tiene entre 3 y 4 frases cortas que empiezan por un verbo y dicen qué hacer \
ahora (beber agua, parar, cómo volver a casa, qué vigilar), adaptadas a su nivel.
- Recuerda siempre que no se debe conducir tras beber, sea cual sea la tasa: las horas hasta \
el límite legal son informativas, no un permiso para conducir.
- Deja claro que es una estimación orientativa y no sustituye a un alcoholímetro.
- Si el nivel es "borracho" o "peligroso", recomienda dejar de beber.
- Si el nivel es "peligroso", indica que llame al 112 si hay vómitos, confusión o somnolencia intensa.
- No des consejos médicos ni trucos para "bajar" la tasa más rápido (café, ducha...)."""

CONSEJOS_GENERICOS = {
    NivelEnum.sobrio: ["Si vas a seguir bebiendo, alterna con agua y come algo."],
    NivelEnum.alegre: [
        "Bebe agua entre copa y copa.",
        "Plantéate parar aquí y comer algo.",
    ],
    NivelEnum.borracho: [
        "Deja de beber por hoy.",
        "Bebe agua y no te quedes solo.",
        "Vuelve a casa en taxi o transporte público.",
    ],
    NivelEnum.peligroso: [
        "Deja de beber inmediatamente.",
        "Si hay vómitos, confusión o somnolencia intensa, llama al 112.",
        "No te quedes solo: avisa a alguien de confianza.",
    ],
}


class IAError(Exception):
    """Fallo al obtener o interpretar la respuesta del modelo."""


def explicacion_generica(nivel: NivelEnum) -> ExplicacionIA:
    return ExplicacionIA(
        explicacion=(
            "No se ha podido generar la explicación detallada. La tasa mostrada es una "
            "estimación con la fórmula de Widmark y puede variar de una persona a otra."
        ),
        consejos=CONSEJOS_GENERICOS[nivel],
    )


def resumen_bebidas(datos: CalculoRequest) -> str:
    return ", ".join(
        f"{b.cantidad} x {b.tipo.value} {b.volumen_ml} ml {b.graduacion:g}%" for b in datos.bebidas
    )


DESCRIPCION_ESTOMAGO = {
    EstomagoEnum.vacio: "vacío",
    EstomagoEnum.algo: "con algo de comida",
    EstomagoEnum.lleno: "lleno",
}


def construir_mensaje(datos: CalculoRequest) -> str:
    """Mensaje del usuario: solo enums y números ya validados por Pydantic,
    más la tasa calculada por el servidor para que la IA no haga cuentas."""
    tasa = round(calcular_tasa(datos), 2)

    def horas_hasta(limite: float) -> float:
        return round(max(0.0, (tasa - limite) / ELIMINACION_GL_H), 1)

    return (
        f"Persona: {datos.sexo.value}, {datos.peso_kg} kg, "
        f"estómago {DESCRIPCION_ESTOMAGO[datos.estomago]}, {datos.tiempo_horas:g} h bebiendo.\n"
        f"Bebidas: {resumen_bebidas(datos)}.\n"
        f"Tasa calculada: {tasa:.2f} g/L. Nivel: {clasificar_nivel(tasa).value}.\n"
        f"Horas hasta 0 g/L: {round(horas_hasta_cero(tasa), 1)}. "
        f"Horas hasta bajar de 0,5 g/L: {horas_hasta(0.5)}. "
        f"Horas hasta bajar de 0,3 g/L: {horas_hasta(0.3)}."
    )


def limpiar_json(texto: str) -> dict:
    """Quita vallas de markdown y extrae el primer objeto JSON del texto."""
    texto = re.sub(r"```(?:json)?", "", texto).strip()
    inicio, fin = texto.find("{"), texto.rfind("}")
    if inicio == -1 or fin == -1:
        raise IAError("La respuesta del modelo no contiene JSON")
    try:
        return json.loads(texto[inicio : fin + 1])
    except json.JSONDecodeError as e:
        raise IAError("JSON inválido en la respuesta del modelo") from e


def parsear_respuesta(cuerpo: dict) -> CalculoIA:
    try:
        contenido = cuerpo["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        raise IAError("Respuesta del modelo sin contenido") from e
    if not isinstance(contenido, str):
        raise IAError("Respuesta del modelo sin contenido")

    try:
        return CalculoIA.model_validate(limpiar_json(contenido))
    except ValidationError as e:
        raise IAError("La salida del modelo no cumple el esquema") from e


def calcular_con_ia(datos: CalculoRequest) -> CalculoIA:
    clave = os.getenv("LLM_API_KEY")
    base = os.getenv("LLM_BASE_URL", BASE_URL_POR_DEFECTO).rstrip("/")
    modelo = os.getenv("LLM_MODEL", MODELO_POR_DEFECTO)
    if not clave:
        raise IAError("Falta LLM_API_KEY")

    cuerpo_peticion = {
        "model": modelo,
        "messages": [
            {"role": "system", "content": PROMPT_SISTEMA},
            {"role": "user", "content": construir_mensaje(datos)},
        ],
        "temperature": 0.4,
        "max_tokens": 1000,
    }
    # Modelos con razonamiento (p. ej. Gemini 2.5): "none" evita que el
    # razonamiento gaste los tokens y deje el JSON cortado
    razonamiento = os.getenv("LLM_REASONING_EFFORT")
    if razonamiento:
        cuerpo_peticion["reasoning_effort"] = razonamiento

    try:
        res = httpx.post(
            f"{base}/chat/completions",
            headers={
                "Authorization": f"Bearer {clave}",
                # Cabecera opcional de OpenRouter para identificar la app
                "X-Title": "La Taberna",
            },
            json=cuerpo_peticion,
            timeout=TIMEOUT_S,
        )
        res.raise_for_status()
        cuerpo = res.json()
    except httpx.TimeoutException as e:
        raise IAError("El modelo no respondió a tiempo") from e
    except httpx.HTTPStatusError as e:
        raise IAError(f"El proveedor de IA respondió con {e.response.status_code}") from e
    except (httpx.HTTPError, ValueError) as e:
        raise IAError("No se pudo contactar con el proveedor de IA") from e

    return parsear_respuesta(cuerpo)
