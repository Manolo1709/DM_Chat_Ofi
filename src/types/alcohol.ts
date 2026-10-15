// Contrato de datos compartido con api/schemas.py (Pydantic v2).

export type Sexo = 'hombre' | 'mujer'
export type Estomago = 'vacio' | 'algo' | 'lleno'
export type TipoBebida = 'cerveza' | 'vino' | 'licor' | 'coctel' | 'otro'
export type Nivel = 'sobrio' | 'alegre' | 'borracho' | 'peligroso'

export interface Bebida {
  tipo: TipoBebida
  volumen_ml: number
  graduacion: number
  cantidad: number
}

// Datos que rellena la persona A (formulario de la persona)
export interface DatosPersona {
  peso_kg: number
  sexo: Sexo
  tiempo_horas: number
  estomago: Estomago
}

export interface CalculoRequest extends DatosPersona {
  bebidas: Bebida[]
}

export interface CalculoResponse {
  tasa_gl: number
  nivel: Nivel
  horas_hasta_cero: number
  explicacion: string
  consejos: string[]
  aviso_conduccion: string
}

export const LIMITES = {
  peso_kg: { min: 30, max: 250 },
  tiempo_horas: { min: 0, max: 24, paso: 0.25 },
} as const

export const LIMITES_BEBIDA = {
  volumen_ml: { min: 1, max: 2000 },
  graduacion: { min: 0, max: 100 },
  cantidad: { min: 1, max: 50 },
} as const
