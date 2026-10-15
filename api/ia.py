"""Cliente del modelo de lenguaje que redacta la explicación del resultado.

Usa la API de chat compatible con OpenAI (`POST {LLM_BASE_URL}/chat/completions`),
que ofrecen OpenRouter, OpenCode Zen, OpenAI, Groq, etc. Por defecto, OpenRouter.

La IA calcula la tasa con el método de Widmark que se le describe en el prompt:
recibe solo valores de enums y números (nunca texto libre del usuario) y devuelve
JSON con `tasa_gl`, `explicacion` y `consejos`. Si falla, el endpoint usa la
fórmula de `api.calculo`. La clave vive solo en el servidor.
"""

import json
import os
import re

import httpx
from pydantic import ValidationError

from api.schemas import CalculoIA, CalculoRequest, EstomagoEnum, ExplicacionIA, NivelEnum

TIMEOUT_S = 30.0
BASE_URL_POR_DEFECTO = "https://openrouter.ai/api/v1"
MODELO_POR_DEFECTO = "poolside/laguna-s-2.1:free"

PROMPT_SISTEMA = """\
Eres el camarero responsable de una taberna. Recibes los datos de una persona y lo que ha \
bebido, y calculas su tasa de alcohol en sangre (g/L) con la fórmula de Widmark:

1. Gramos de alcohol = suma de (volumen ml × graduación / 100 × 0,8 × cantidad).
2. Multiplica los gramos por el factor de estómago: vacío 1,0; algo de comida 0,9; lleno 0,75.
3. Pico = gramos / (peso kg × coeficiente), con coeficiente 0,68 para hombre y 0,55 para mujer.
4. Tasa = pico − 0,15 × horas bebiendo. Si sale negativa, la tasa es 0.

Niveles: menos de 0,2 sobrio; menos de 0,8 alegre; menos de 1,5 borracho; desde 1,5 peligroso.

Responde EXCLUSIVAMENTE con un objeto JSON válido, sin markdown ni texto alrededor, con esta forma:
{"tasa_gl": <número con 2 decimales>, "explicacion": "<2-4 frases en español, tono cercano>", \
"consejos": ["<consejo>", "..."]}

Reglas:
- "consejos" tiene entre 2 y 4 frases cortas.
- Recuerda siempre que no se debe conducir tras beber, sea cual sea la tasa.
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
    """Mensaje del usuario: solo enums y números ya validados por Pydantic."""
    return (
        f"Persona: {datos.sexo.value}, {datos.peso_kg} kg, "
        f"estómago {DESCRIPCION_ESTOMAGO[datos.estomago]}, {datos.tiempo_horas:g} h bebiendo.\n"
        f"Bebidas: {resumen_bebidas(datos)}."
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

    try:
        res = httpx.post(
            f"{base}/chat/completions",
            headers={
                "Authorization": f"Bearer {clave}",
                # Cabecera opcional de OpenRouter para identificar la app
                "X-Title": "La Taberna",
            },
            json={
                "model": modelo,
                "messages": [
                    {"role": "system", "content": PROMPT_SISTEMA},
                    {"role": "user", "content": construir_mensaje(datos)},
                ],
                "temperature": 0.4,
                "max_tokens": 600,
            },
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
