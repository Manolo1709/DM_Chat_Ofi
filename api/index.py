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


# imports de clerk:
import os
import time
import threading

from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from clerk_backend_api import (
    authenticate_request,
    AuthenticateRequestOptions,
)




load_dotenv()

# El frontend muestra siempre debajo "Estimación orientativa. No sustituye a un alcoholímetro."
AVISO_CONDUCCION = "No conduzcas si has bebido alcohol, aunque la estimación sea baja."

app = FastAPI(title="Calculadora de alcohol en sangre")


def verificar_usuario(request: Request) -> str:
    # El frontend debe enviar Authorization: Bearer <token>
    if not request.headers.get("Authorization", "").startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Debes iniciar sesión",
        )

    try:
        estado = authenticate_request(
            request,
            AuthenticateRequestOptions(
                secret_key=os.environ["CLERK_SECRET_KEY"],
                publishable_key=os.environ["CLERK_PUBLISHABLE_KEY"],
                jwt_key=os.environ["CLERK_JWT_KEY"],
                authorized_parties=[
                    origen.strip()
                    for origen in os.environ["FRONTEND_ORIGIN"].split(",")
                ],
                accepts_token=["session_token"],
            ),
        )
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Sesión no válida",
        )

    if not estado.is_signed_in:
        raise HTTPException(
            status_code=401,
            detail="Sesión no válida o caducada",
        )

    usuario_id = (estado.payload or {}).get("sub")

    if not usuario_id:
        raise HTTPException(
            status_code=401,
            detail="No se ha podido identificar al usuario",
        )

    return usuario_id

MAX_POR_MINUTO = 10
MAX_POR_DIA = 50

peticiones_minuto = defaultdict(deque)
peticiones_dia = defaultdict(int)
bloqueo = threading.Lock()


def limitar_usuario(usuario_id: str) -> None:
    ahora = time.monotonic()
    hoy = datetime.now(timezone.utc).date().isoformat()

    with bloqueo:
        recientes = peticiones_minuto[usuario_id]

        while recientes and ahora - recientes[0] >= 60:
            recientes.popleft()

        clave_dia = (usuario_id, hoy)

        if peticiones_dia[clave_dia] >= MAX_POR_DIA:
            raise HTTPException(
                status_code=429,
                detail="Has alcanzado el límite diario",
            )

        if len(recientes) >= MAX_POR_MINUTO:
            raise HTTPException(
                status_code=429,
                detail="Demasiadas peticiones. Espera un minuto",
            )

        # Contamos la petición antes de llamar al modelo.
        recientes.append(ahora)
        peticiones_dia[clave_dia] += 1



@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/calcular", response_model=CalculoResponse)
def calcular(
    datos: CalculoRequest,
    usuario_id: Annotated[str, Depends(verificar_usuario)],) -> CalculoResponse:
    limitar_usuario(usuario_id)

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
