"""Persona B: pruebas del cliente de IA (sin llamadas reales) y de los 422 de bebidas."""

import json
from unittest.mock import MagicMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from api import ia
from api.index import app
from api.calculo import calcular_tasa
from api.schemas import CalculoRequest

client = TestClient(app)

PETICION = {
    "peso_kg": 70,
    "sexo": "mujer",
    "tiempo_horas": 1,
    "estomago": "algo",
    "bebidas": [{"tipo": "vino", "volumen_ml": 150, "graduacion": 13, "cantidad": 2}],
}
SALIDA_OK = {
    "tasa_gl": 0.42,
    "explicacion": "Vas algo alegre.",
    "consejos": ["Bebe agua.", "No conduzcas."],
}


@pytest.fixture(autouse=True)
def entorno(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "clave-de-prueba")
    monkeypatch.setenv("LLM_BASE_URL", "https://ia.test/v1")
    monkeypatch.setenv("LLM_MODEL", "modelo-de-prueba")


def respuesta_modelo(contenido) -> MagicMock:
    res = MagicMock()
    res.raise_for_status.return_value = None
    res.json.return_value = {"choices": [{"message": {"role": "assistant", "content": contenido}}]}
    return res


def obtener():
    return ia.calcular_con_ia(CalculoRequest.model_validate(PETICION))


# --- Cliente de IA -------------------------------------------------------------


def test_respuesta_valida_y_peticion_correcta():
    with patch("api.ia.httpx.post", return_value=respuesta_modelo(json.dumps(SALIDA_OK))) as post:
        resultado = obtener()

    assert resultado.tasa_gl == 0.42
    assert resultado.explicacion == "Vas algo alegre."
    assert resultado.consejos == ["Bebe agua.", "No conduzcas."]

    url = post.call_args.args[0]
    kwargs = post.call_args.kwargs
    assert url == "https://ia.test/v1/chat/completions"
    assert kwargs["headers"]["Authorization"] == "Bearer clave-de-prueba"
    assert kwargs["json"]["model"] == "modelo-de-prueba"
    sistema, usuario = kwargs["json"]["messages"]
    assert sistema["role"] == "system" and "JSON" in sistema["content"]
    assert "Widmark" in sistema["content"]
    assert "mujer, 70 kg, estómago con algo de comida, 1 h" in usuario["content"]
    assert "2 x vino 150 ml 13%" in usuario["content"]


def test_valores_por_defecto(monkeypatch):
    monkeypatch.delenv("LLM_BASE_URL")
    monkeypatch.delenv("LLM_MODEL")
    with patch("api.ia.httpx.post", return_value=respuesta_modelo(json.dumps(SALIDA_OK))) as post:
        obtener()
    assert post.call_args.args[0] == "https://openrouter.ai/api/v1/chat/completions"
    assert post.call_args.kwargs["json"]["model"] == ia.MODELO_POR_DEFECTO


def test_respuesta_con_markdown():
    texto = "Aquí tienes:\n```json\n" + json.dumps(SALIDA_OK) + "\n```"
    with patch("api.ia.httpx.post", return_value=respuesta_modelo(texto)):
        assert obtener().consejos == SALIDA_OK["consejos"]


@pytest.mark.parametrize(
    "contenido",
    [
        "No soy JSON",
        json.dumps({"explicacion": "Falta la lista de consejos"}),
        json.dumps({"explicacion": "", "consejos": ["x"]}),
        json.dumps({"explicacion": "Sin tasa", "consejos": ["x"]}),
        json.dumps({**SALIDA_OK, "tasa_gl": -0.3}),
        json.dumps({**SALIDA_OK, "tasa_gl": 12}),
        None,
    ],
)
def test_respuesta_invalida(contenido):
    with patch("api.ia.httpx.post", return_value=respuesta_modelo(contenido)):
        with pytest.raises(ia.IAError):
            obtener()


def test_respuesta_sin_choices():
    res = MagicMock()
    res.raise_for_status.return_value = None
    res.json.return_value = {"error": {"message": "Rate limit"}}
    with patch("api.ia.httpx.post", return_value=res):
        with pytest.raises(ia.IAError):
            obtener()


def test_timeout():
    with patch("api.ia.httpx.post", side_effect=httpx.ReadTimeout("lento")):
        with pytest.raises(ia.IAError, match="a tiempo"):
            obtener()


@pytest.mark.parametrize("codigo", [401, 429, 500])
def test_error_http(codigo):
    peticion = httpx.Request("POST", "https://ia.test/v1/chat/completions")
    error = httpx.HTTPStatusError(
        str(codigo), request=peticion, response=httpx.Response(codigo, request=peticion)
    )
    res = MagicMock()
    res.raise_for_status.side_effect = error
    with patch("api.ia.httpx.post", return_value=res):
        with pytest.raises(ia.IAError, match=str(codigo)):
            obtener()


def test_sin_clave(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY")
    with patch("api.ia.httpx.post") as post:
        with pytest.raises(ia.IAError):
            obtener()
    post.assert_not_called()


# --- Endpoint ------------------------------------------------------------------


def test_calcular_con_ia():
    with patch("api.ia.httpx.post", return_value=respuesta_modelo(json.dumps(SALIDA_OK))):
        res = client.post("/api/calcular", json=PETICION)

    assert res.status_code == 200
    cuerpo = res.json()
    assert cuerpo["explicacion"] == SALIDA_OK["explicacion"]
    # La tasa, el nivel y las horas salen de lo que calcula la IA
    assert cuerpo["tasa_gl"] == 0.42
    assert cuerpo["nivel"] == "alegre"
    assert cuerpo["horas_hasta_cero"] == 2.8
    assert "No conduzcas" in cuerpo["aviso_conduccion"]


def test_calcular_si_la_ia_falla_usa_fallback():
    with patch("api.ia.httpx.post", side_effect=httpx.ConnectError("caído")):
        res = client.post("/api/calcular", json=PETICION)

    assert res.status_code == 200
    cuerpo = res.json()
    # Sin IA, la tasa sale de la fórmula de Widmark
    assert cuerpo["tasa_gl"] == round(calcular_tasa(CalculoRequest.model_validate(PETICION)), 2)
    assert cuerpo["consejos"]
    assert "No se ha podido generar" in cuerpo["explicacion"]


@pytest.mark.parametrize(
    "bebidas",
    [
        [],
        [{"tipo": "vino", "volumen_ml": 150, "graduacion": 120, "cantidad": 1}],
        [{"tipo": "vino", "volumen_ml": 150, "graduacion": -1, "cantidad": 1}],
        [{"tipo": "vino", "volumen_ml": 0, "graduacion": 13, "cantidad": 1}],
        [{"tipo": "vino", "volumen_ml": 150, "graduacion": 13, "cantidad": 0}],
        [{"tipo": "absenta", "volumen_ml": 150, "graduacion": 13, "cantidad": 1}],
    ],
)
def test_422_bebidas(bebidas):
    with patch("api.ia.httpx.post") as post:
        res = client.post("/api/calcular", json={**PETICION, "bebidas": bebidas})
    assert res.status_code == 422
    post.assert_not_called()
