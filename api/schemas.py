"""Contrato de datos compartido con src/types/alcohol.ts (Pydantic v2)."""

from enum import Enum

from pydantic import BaseModel, Field


class SexoEnum(str, Enum):
    hombre = "hombre"
    mujer = "mujer"


class EstomagoEnum(str, Enum):
    vacio = "vacio"
    algo = "algo"
    lleno = "lleno"


class TipoBebidaEnum(str, Enum):
    cerveza = "cerveza"
    vino = "vino"
    licor = "licor"
    coctel = "coctel"
    otro = "otro"


class NivelEnum(str, Enum):
    sobrio = "sobrio"
    alegre = "alegre"
    borracho = "borracho"
    peligroso = "peligroso"


# Mismos límites que LIMITES en src/types/alcohol.ts
PESO_MIN, PESO_MAX = 30, 250
TIEMPO_MAX = 24


class Bebida(BaseModel):
    tipo: TipoBebidaEnum
    volumen_ml: int = Field(gt=0, le=2000)
    graduacion: float = Field(ge=0, le=100)
    cantidad: int = Field(ge=1, le=50)


class CalculoRequest(BaseModel):
    peso_kg: int = Field(ge=PESO_MIN, le=PESO_MAX)
    sexo: SexoEnum
    tiempo_horas: float = Field(ge=0, le=TIEMPO_MAX)
    estomago: EstomagoEnum
    bebidas: list[Bebida] = Field(min_length=1, max_length=50)


class CalculoResponse(BaseModel):
    tasa_gl: float = Field(ge=0)
    nivel: NivelEnum
    horas_hasta_cero: float = Field(ge=0)
    explicacion: str
    consejos: list[str]
    aviso_conduccion: str


class ExplicacionIA(BaseModel):
    """Explicación y consejos (también la salida genérica si la IA falla)."""

    explicacion: str = Field(min_length=1, max_length=2000)
    consejos: list[str] = Field(min_length=1, max_length=6)


# Tasa máxima que se acepta del modelo; por encima se considera un error de cálculo
TASA_IA_MAX = 6.0


class CalculoIA(ExplicacionIA):
    """Salida que se exige al modelo de lenguaje: la tasa calculada y su explicación."""

    tasa_gl: float = Field(ge=0, le=TASA_IA_MAX)
