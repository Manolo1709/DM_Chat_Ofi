"""Configuración de pytest: las pruebas no escriben en logs/errores.txt."""

import os
from types import SimpleNamespace

import pytest

os.environ["LOG_ARCHIVO"] = "false"


@pytest.fixture(autouse=True)
def simular_clerk(monkeypatch, request):
    """Las pruebas de API parten de una sesión válida, salvo que la prueben."""
    from api import index

    monkeypatch.setenv("CLERK_SECRET_KEY", "sk_test_pruebas")
    monkeypatch.setenv("FRONTEND_ORIGIN", "http://localhost:5173")
    monkeypatch.delenv("AWS_URL", raising=False)
    # Cada prueba empieza sin peticiones contadas, o el límite por usuario devuelve 429
    index.peticiones_minuto.clear()
    index.peticiones_dia.clear()
    monkeypatch.setattr(
        index,
        "authenticate_request",
        lambda *_args, **_kwargs: SimpleNamespace(
            is_signed_in=True,
            reason=None,
            payload={"sub": "user_test"},
        ),
    )
    # Las pruebas preexistentes del endpoint modelan una sesión autenticada.
    # test_auth.py controla explícitamente la presencia del header en cada caso.
    if request.path.name != "test_auth.py":
        client = getattr(request.module, "client", None)
        if client is not None:
            client.headers["Authorization"] = "Bearer token-de-prueba"
