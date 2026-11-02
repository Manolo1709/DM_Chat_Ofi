"""Pruebas de autenticación de Clerk sin llamadas al servicio real."""

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

# Permite importar `api` cuando este archivo se ejecuta directamente desde el IDE.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api.index import app
from api.schemas import CalculoIA

client = TestClient(app)

PETICION = {
    "peso_kg": 70,
    "sexo": "mujer",
    "tiempo_horas": 1,
    "estomago": "algo",
    "bebidas": [{"tipo": "vino", "volumen_ml": 150, "graduacion": 13, "cantidad": 2}],
}


def configurar_clerk(monkeypatch):
    monkeypatch.setenv("CLERK_SECRET_KEY", "sk_test_pruebas")
    monkeypatch.setenv("FRONTEND_ORIGIN", "http://localhost:5173")
    monkeypatch.delenv("AWS_URL", raising=False)


def test_token_ausente_devuelve_401_sin_verificar_clerk(monkeypatch):
    configurar_clerk(monkeypatch)
    with (
        patch("api.index.authenticate_request") as authenticate,
        patch("api.index.ia.calcular_con_ia") as calcular_ia,
    ):
        respuesta = client.post("/api/calcular", json=PETICION)

    assert respuesta.status_code == 401
    assert respuesta.json()["detail"] == "Debes iniciar sesión"
    authenticate.assert_not_called()
    calcular_ia.assert_not_called()


def test_token_invalido_devuelve_401(monkeypatch):
    configurar_clerk(monkeypatch)
    estado = SimpleNamespace(is_signed_in=False, reason="token inválido")
    with (
        patch("api.index.authenticate_request", return_value=estado),
        patch("api.index.ia.calcular_con_ia") as calcular_ia,
    ):
        respuesta = client.post(
            "/api/calcular", json=PETICION,
            headers={"Authorization": "Bearer token-invalido"},
        )

    assert respuesta.status_code == 401
    assert respuesta.json()["detail"] == "token inválido"
    calcular_ia.assert_not_called()


def test_token_valido_permite_acceso_y_acepta_origen_aws(monkeypatch):
    configurar_clerk(monkeypatch)
    monkeypatch.setenv("AWS_URL", "https://app.example.com")
    estado = SimpleNamespace(is_signed_in=True, reason=None, payload={"sub": "user_123"})
    with (
        patch("api.index.authenticate_request", return_value=estado) as authenticate,
        patch("api.index.limitar_usuario"),
        patch("api.index.ia.calcular_con_ia") as calcular_ia,
    ):
        calcular_ia.return_value = CalculoIA(tasa_gl=0.42, explicacion="Vas algo alegre.", consejos=["Bebe agua."])
        respuesta = client.post(
            "/api/calcular", json=PETICION,
            headers={"Authorization": "Bearer token-valido"},
        )

    assert respuesta.status_code == 200
    opciones = authenticate.call_args.args[1]
    assert opciones.secret_key == "sk_test_pruebas"
    assert opciones.authorized_parties == ["http://localhost:5173", "https://app.example.com"]
    assert opciones.accepts_token == ["session_token"]


def test_undecima_peticion_en_un_minuto_devuelve_429(monkeypatch):
    configurar_clerk(monkeypatch)
    estado = SimpleNamespace(is_signed_in=True, reason=None, payload={"sub": "user_limite"})
    with (
        patch("api.index.authenticate_request", return_value=estado),
        patch("api.index.ia.calcular_con_ia") as calcular_ia,
    ):
        calcular_ia.return_value = CalculoIA(tasa_gl=0.42, explicacion="Vas algo alegre.", consejos=["Bebe agua."])
        codigos = [
            client.post(
                "/api/calcular", json=PETICION,
                headers={"Authorization": "Bearer token-valido"},
            ).status_code
            for _ in range(11)
        ]

    assert codigos[:10] == [200] * 10
    assert codigos[10] == 429
    assert calcular_ia.call_count == 10


@pytest.mark.parametrize("variable", ["CLERK_SECRET_KEY", "FRONTEND_ORIGIN"])
def test_configuracion_clerk_incompleta_devuelve_500(monkeypatch, variable):
    configurar_clerk(monkeypatch)
    monkeypatch.delenv(variable)
    with patch("api.index.authenticate_request") as authenticate:
        respuesta = client.post(
            "/api/calcular", json=PETICION,
            headers={"Authorization": "Bearer token-valido"},
        )

    assert respuesta.status_code == 500
    assert respuesta.json()["detail"] == "La autenticación no está configurada correctamente"
    authenticate.assert_not_called()
