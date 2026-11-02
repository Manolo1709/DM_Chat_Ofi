# Modelo de datos: La Taberna (App 2)

Ningún dato se guarda: todas las entidades existen solo durante una petición. Fuente de verdad: `api/schemas.py` (Pydantic) y `src/types/alcohol.ts` (TypeScript).

## Bebida

| Campo | Tipo | Reglas |
|---|---|---|
| `tipo` | enum | `cerveza`, `vino`, `licor`, `coctel`, `otro` |
| `volumen_ml` | entero | 1 a 2000 |
| `graduacion` | decimal | 0 a 100 |
| `cantidad` | entero | 1 a 50 |

## CalculoRequest

| Campo | Tipo | Reglas |
|---|---|---|
| `peso_kg` | entero | 30 a 250 |
| `sexo` | enum | `hombre`, `mujer` |
| `tiempo_horas` | decimal | 0 a 24 |
| `estomago` | enum | `vacio`, `algo`, `lleno` |
| `bebidas` | lista de Bebida | 1 a 50 elementos |

## CalculoResponse

| Campo | Tipo | Reglas |
|---|---|---|
| `tasa_gl` | decimal | ≥ 0, dos decimales |
| `nivel` | enum | `sobrio` (<0,2), `alegre` (<0,8), `borracho` (<1,5), `peligroso` (≥1,5) |
| `horas_hasta_cero` | decimal | ≥ 0, dos decimales |
| `explicacion` | texto | de la IA o genérica |
| `consejos` | lista de texto | 1 a 6 |
| `aviso_conduccion` | texto | siempre presente |
| `origen` | enum | `ia` o `respaldo` |

## Respuesta exigida a la IA (CalculoIA)

| Campo | Tipo | Reglas |
|---|---|---|
| `tasa_gl` | decimal | 0 a 6; si no, se descarta |
| `explicacion` | texto | 1 a 2000 caracteres |
| `consejos` | lista de texto | 1 a 6 |

## Sesión (no se almacena)

| Dato | Origen | Uso |
|---|---|---|
| Token de sesión | Clerk, en la cabecera `Authorization: Bearer` | Verificar que el usuario está autenticado y que el token se emitió para `FRONTEND_ORIGIN` |
| `sub` | Contenido del token | Identificar al usuario para el límite de peticiones en memoria |

## Reglas de cálculo

1. Gramos = volumen × graduación / 100 × 0,8 × cantidad.
2. Gramos efectivos = gramos × factor de estómago (1,0 / 0,9 / 0,75).
3. Pico = gramos efectivos / (peso × 0,68 si es hombre o 0,55 si es mujer).
4. Tasa = max(0, pico − 0,15 × horas).
5. Horas hasta cero = tasa / 0,15.
