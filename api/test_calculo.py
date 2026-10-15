"""Persona A: pruebas del cálculo, de /api/health y de los 422 de la persona."""

import pytest
from fastapi.testclient import TestClient

from api.calculo import calcular_tasa, clasificar_nivel, gramos_alcohol, horas_hasta_cero
from api.index import app
from api.schemas import CalculoRequest, NivelEnum

client = TestClient(app)


def peticion(**cambios) -> dict:
    base = {
        "peso_kg": 80,
        "sexo": "hombre",
        "tiempo_horas": 0,
        "estomago": "vacio",
        "bebidas": [{"tipo": "cerveza", "volumen_ml": 500, "graduacion": 5, "cantidad": 2}],
    }
    return {**base, **cambios}


def req(**cambios) -> CalculoRequest:
    return CalculoRequest.model_validate(peticion(**cambios))


def test_gramos_alcohol():
    # 2 x 500 ml al 5 % -> 50 ml de alcohol -> 40 g
    assert gramos_alcohol(req().bebidas) == pytest.approx(40)


def test_widmark_resultado_conocido():
    # 40 g / (80 kg x 0,68) = 0,735 g/L
    assert calcular_tasa(req()) == pytest.approx(0.7353, abs=1e-3)


def test_eliminacion_por_tiempo():
    # 0,7353 - 0,15 x 2 h = 0,4353 g/L
    assert calcular_tasa(req(tiempo_horas=2)) == pytest.approx(0.4353, abs=1e-3)


def test_tasa_nunca_negativa():
    assert calcular_tasa(req(tiempo_horas=24)) == 0.0
    assert horas_hasta_cero(0.0) == 0.0


def test_mujer_tiene_tasa_mayor():
    assert calcular_tasa(req(sexo="mujer")) > calcular_tasa(req(sexo="hombre"))


def test_estomago_lleno_reduce_la_tasa():
    vacio = calcular_tasa(req(estomago="vacio"))
    algo = calcular_tasa(req(estomago="algo"))
    lleno = calcular_tasa(req(estomago="lleno"))
    assert vacio > algo > lleno


@pytest.mark.parametrize(
    "tasa, nivel",
    [
        (0.0, NivelEnum.sobrio),
        (0.19, NivelEnum.sobrio),
        (0.2, NivelEnum.alegre),
        (0.8, NivelEnum.borracho),
        (1.5, NivelEnum.peligroso),
        (3.0, NivelEnum.peligroso),
    ],
)
def test_clasificar_nivel(tasa, nivel):
    assert clasificar_nivel(tasa) == nivel


def test_horas_hasta_cero():
    assert horas_hasta_cero(0.75) == pytest.approx(5)


def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


@pytest.mark.parametrize(
    "cambios",
    [
        {"peso_kg": 10},
        {"peso_kg": 400},
        {"tiempo_horas": -1},
        {"sexo": "otro"},
        {"estomago": "medio"},
    ],
)
def test_422_datos_persona(cambios):
    assert client.post("/api/calcular", json=peticion(**cambios)).status_code == 422
