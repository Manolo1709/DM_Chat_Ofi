"""API FastAPI: punto de entrada local (uvicorn) y función serverless de Vercel."""

import sys
from pathlib import Path

# Permite `from api.x import ...` tanto en local como en la función de Vercel
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv  # noqa: E402
from fastapi import FastAPI  # noqa: E402

from api import ia  # noqa: E402
from api.registro import logger  # noqa: E402
from api.calculo import calcular_tasa, clasificar_nivel, horas_hasta_cero  # noqa: E402
from api.schemas import CalculoRequest, CalculoResponse, OrigenEnum  # noqa: E402

load_dotenv()

# El frontend muestra siempre debajo "Estimación orientativa. No sustituye a un alcoholímetro."
AVISO_CONDUCCION = "No conduzcas si has bebido alcohol, aunque la estimación sea baja."

app = FastAPI(title="Calculadora de alcohol en sangre")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/calcular", response_model=CalculoResponse)
def calcular(datos: CalculoRequest) -> CalculoResponse:
    # La IA calcula la tasa; si falla, se usa la fórmula con una explicación genérica
    try:
        texto = ia.calcular_con_ia(datos)
        tasa = texto.tasa_gl
        nivel = clasificar_nivel(tasa)
        origen = OrigenEnum.ia
    except ia.IAError as e:
        # Solo se anota el motivo, nunca los datos del usuario ni la respuesta de la IA
        causa = type(e.__cause__).__name__ if e.__cause__ else "sin causa"
        logger.warning("IA no disponible, se usa la fórmula: %s [%s]", e, causa)
        tasa = calcular_tasa(datos)
        nivel = clasificar_nivel(tasa)
        texto = ia.explicacion_generica(nivel)
        origen = OrigenEnum.respaldo

    return CalculoResponse(
        tasa_gl=round(tasa, 2),
        nivel=nivel,
        horas_hasta_cero=round(horas_hasta_cero(tasa), 2),
        explicacion=texto.explicacion,
        consejos=texto.consejos,
        aviso_conduccion=AVISO_CONDUCCION,
        origen=origen,
    )
