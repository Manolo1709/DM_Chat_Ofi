"""Cálculo de la tasa de alcohol en sangre con la fórmula de Widmark.

Funciones puras, sin IA: el valor numérico debe ser reproducible y testeable.
"""

from api.schemas import Bebida, CalculoRequest, EstomagoEnum, NivelEnum, SexoEnum

DENSIDAD_ALCOHOL = 0.8  # g/ml
ELIMINACION_GL_H = 0.15  # g/L por hora

COEFICIENTE_SEXO = {
    SexoEnum.hombre: 0.68,
    SexoEnum.mujer: 0.55,
}

# Fracción del pico que se alcanza según el estómago: con comida la absorción
# es más lenta y parte del alcohol se elimina antes de llegar a la sangre.
FACTOR_ESTOMAGO = {
    EstomagoEnum.vacio: 1.0,
    EstomagoEnum.algo: 0.9,
    EstomagoEnum.lleno: 0.75,
}

# Límite superior (exclusivo) de cada nivel en g/L. Fácil de ajustar.
UMBRALES_NIVEL = [
    (0.2, NivelEnum.sobrio),
    (0.8, NivelEnum.alegre),
    (1.5, NivelEnum.borracho),
]


def gramos_alcohol(bebidas: list[Bebida]) -> float:
    return sum(b.volumen_ml * b.graduacion / 100 * DENSIDAD_ALCOHOL * b.cantidad for b in bebidas)


def calcular_tasa(datos: CalculoRequest) -> float:
    gramos = gramos_alcohol(datos.bebidas) * FACTOR_ESTOMAGO[datos.estomago]
    pico = gramos / (datos.peso_kg * COEFICIENTE_SEXO[datos.sexo])
    return max(0.0, pico - ELIMINACION_GL_H * datos.tiempo_horas)


def clasificar_nivel(tasa_gl: float) -> NivelEnum:
    for limite, nivel in UMBRALES_NIVEL:
        if tasa_gl < limite:
            return nivel
    return NivelEnum.peligroso


def horas_hasta_cero(tasa_gl: float) -> float:
    return tasa_gl / ELIMINACION_GL_H
