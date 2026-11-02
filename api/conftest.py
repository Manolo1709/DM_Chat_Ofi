"""Configuración de pytest: las pruebas no escriben en logs/errores.txt."""

import os

import pytest

os.environ["LOG_ARCHIVO"] = "false"


@pytest.fixture(autouse=True)
def simular_clerk(monkeypatch, request):
    """Las pruebas de API parten de una sesión válida, salvo las de test_auth.py,
    que prueban la verificación real de Clerk."""
    from api import index

    monkeypatch.setenv("CLERK_SECRET_KEY", "sk_test_pruebas")
    monkeypatch.setenv("FRONTEND_ORIGIN", "http://localhost:5173")
    monkeypatch.delenv("AWS_URL", raising=False)
    # Cada prueba empieza sin peticiones contadas, o el límite por usuario devuelve 429
    index.peticiones_minuto.clear()
    index.peticiones_dia.clear()

    if request.path.name != "test_auth.py":
        index.app.dependency_overrides[index.verificar_usuario] = lambda: "user_test"
    yield
    index.app.dependency_overrides.clear()
