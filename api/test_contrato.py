"""Pruebas del contrato de POST /api/calcular: escenarios válidos, límites y fallos externos.

Todas usan un mock de la IA: nunca se llama al proveedor real ni se consumen créditos.
"""

import json
from unittest.mock import MagicMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from api.index import app

client = TestClient(app)

CLAVE = "clave-de-prueba"
CAMPOS_RESPUESTA = {
    "tasa_gl",
    "nivel",
    "horas_hasta_cero",
    "explicacion",
    "consejos",
    "aviso_conduccion",
    "origen",
}
BEBIDA = {"tipo": "cerveza", "volumen_ml": 200, "graduacion": 5, "cantidad": 1}
PETICION = {
    "peso_kg": 70,
    "sexo": "hombre",
    "tiempo_horas": 1,
    "estomago": "algo",
    "bebidas": [BEBIDA],
}
SALIDA_IA = {"tasa_gl": 0.3, "explicacion": "Vas tranquilo.", "consejos": ["Bebe agua."]}


@pytest.fixture(autouse=True)
def entorno(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", CLAVE)
    monkeypatch.setenv("LLM_BASE_URL", "https://ia.test/v1")
    monkeypatch.setenv("LLM_MODEL", "modelo-de-prueba")


def respuesta_ia(contenido) -> MagicMock:
    res = MagicMock()
    res.raise_for_status.return_value = None
    res.json.return_value = {"choices": [{"message": {"content": contenido}}]}
    return res


def con_bebida(**cambios) -> dict:
    return {**BEBIDA, **cambios}


def con_persona(**cambios) -> dict:
    return {**PETICION, **cambios}


def enviar(peticion, **mock):
    """Envía la petición con la IA simulada y devuelve (respuesta, mock de httpx.post)."""
    mock.setdefault("return_value", respuesta_ia(json.dumps(SALIDA_IA)))
    with patch("api.ia.httpx.post", **mock) as post:
        return client.post("/api/calcular", json=peticion), post


# --- Entrada válida ---------------------------------------------------------------


def test_entrada_valida_hace_una_sola_llamada_a_la_ia():
    res, post = enviar(PETICION)

    assert res.status_code == 200
    post.assert_called_once()
    cuerpo = res.json()
    assert set(cuerpo) == CAMPOS_RESPUESTA
    assert cuerpo["origen"] == "ia"


def test_repetir_el_envio_no_acumula_nada():
    primero, _ = enviar(PETICION)
    segundo, post = enviar(PETICION)

    assert primero.json() == segundo.json()
    post.assert_called_once()


# --- Límites: dentro se acepta; fuera, 422 y sin llamar a la IA --------------------


@pytest.mark.parametrize(
    "peticion",
    [
        con_persona(peso_kg=30),
        con_persona(peso_kg=250),
        con_persona(tiempo_horas=0),
        con_persona(tiempo_horas=24),
        con_persona(bebidas=[con_bebida(volumen_ml=1)]),
        con_persona(bebidas=[con_bebida(volumen_ml=2000)]),
        con_persona(bebidas=[con_bebida(graduacion=0)]),
        con_persona(bebidas=[con_bebida(graduacion=100)]),
        con_persona(bebidas=[con_bebida(cantidad=1)]),
        con_persona(bebidas=[con_bebida(cantidad=50)]),
        con_persona(bebidas=[BEBIDA] * 50),
    ],
    ids=lambda p: f"{p['peso_kg']}kg-{p['tiempo_horas']}h-{len(p['bebidas'])}bebidas-{p['bebidas'][0]}",
)
def test_en_el_limite_se_acepta(peticion):
    res, post = enviar(peticion)

    assert res.status_code == 200
    post.assert_called_once()


@pytest.mark.parametrize(
    "peticion",
    [
        con_persona(peso_kg=29),
        con_persona(peso_kg=251),
        con_persona(tiempo_horas=-0.25),
        con_persona(tiempo_horas=24.25),
        con_persona(bebidas=[]),
        con_persona(bebidas=[BEBIDA] * 51),
        con_persona(bebidas=[con_bebida(volumen_ml=0)]),
        con_persona(bebidas=[con_bebida(volumen_ml=2001)]),
        con_persona(bebidas=[con_bebida(graduacion=-1)]),
        con_persona(bebidas=[con_bebida(graduacion=100.5)]),
        con_persona(bebidas=[con_bebida(cantidad=0)]),
        con_persona(bebidas=[con_bebida(cantidad=51)]),
    ],
    ids=lambda p: f"{p['peso_kg']}kg-{p['tiempo_horas']}h-{len(p['bebidas'])}bebidas",
)
def test_fuera_del_limite_da_422_sin_llamar_a_la_ia(peticion):
    res, post = enviar(peticion)

    assert res.status_code == 422
    post.assert_not_called()


# --- Entradas vacías o mal formadas --------------------------------------------------


@pytest.mark.parametrize("campo", ["peso_kg", "sexo", "tiempo_horas", "estomago", "bebidas"])
def test_campo_ausente_da_422(campo):
    peticion = {k: v for k, v in PETICION.items() if k != campo}
    res, post = enviar(peticion)

    assert res.status_code == 422
    post.assert_not_called()


@pytest.mark.parametrize("valor", ["", " ", "   "])
def test_texto_vacio_o_solo_espacios_da_422(valor):
    for peticion in (con_persona(sexo=valor), con_persona(estomago=valor)):
        res, post = enviar(peticion)
        assert res.status_code == 422
        post.assert_not_called()


def test_cuerpo_vacio_o_no_json_da_422():
    with patch("api.ia.httpx.post") as post:
        assert client.post("/api/calcular", json={}).status_code == 422
        assert client.post("/api/calcular", content="esto no es json").status_code == 422
    post.assert_not_called()


# --- Fallos externos y timeout: se controlan y no se rompe nada -----------------------


def fallo_http(codigo: int) -> MagicMock:
    peticion = httpx.Request("POST", "https://ia.test/v1/chat/completions")
    res = MagicMock()
    res.raise_for_status.side_effect = httpx.HTTPStatusError(
        str(codigo), request=peticion, response=httpx.Response(codigo, request=peticion)
    )
    return res


@pytest.mark.parametrize(
    "mock",
    [
        {"side_effect": httpx.ReadTimeout("lento")},
        {"side_effect": httpx.ConnectError("caído")},
        {"return_value": fallo_http(401)},
        {"return_value": fallo_http(429)},
        {"return_value": fallo_http(500)},
        {"return_value": respuesta_ia("esto no es JSON")},
        {"return_value": respuesta_ia(json.dumps({**SALIDA_IA, "tasa_gl": 12}))},
        {"return_value": respuesta_ia(None)},
    ],
    ids=["timeout", "sin-conexion", "401", "429", "500", "no-json", "tasa-absurda", "sin-contenido"],
)
def test_fallo_de_la_ia_usa_el_respaldo(mock):
    res, post = enviar(PETICION, **mock)

    assert res.status_code == 200
    post.assert_called_once()
    cuerpo = res.json()
    assert set(cuerpo) == CAMPOS_RESPUESTA
    assert cuerpo["origen"] == "respaldo"
    assert cuerpo["consejos"]


def test_sin_clave_no_se_llama_a_la_ia(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY")
    res, post = enviar(PETICION)

    assert res.status_code == 200
    assert res.json()["origen"] == "respaldo"
    post.assert_not_called()


def test_la_respuesta_no_expone_clave_ni_errores_internos():
    res, _ = enviar(PETICION, side_effect=httpx.ReadTimeout("lento"))

    assert CLAVE not in res.text
    assert "Traceback" not in res.text
    assert "ReadTimeout" not in res.text
