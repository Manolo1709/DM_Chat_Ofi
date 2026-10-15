import type { Bebida, TipoBebida } from '../types/alcohol'

// Valores por defecto de cada tipo de bebida (una unidad típica)
export const CATALOGO: Record<TipoBebida, { nombre: string; unidad: string; volumen_ml: number; graduacion: number }> = {
  cerveza: { nombre: 'Cerveza', unidad: 'caña', volumen_ml: 200, graduacion: 5 },
  vino: { nombre: 'Vino', unidad: 'copa', volumen_ml: 150, graduacion: 13 },
  licor: { nombre: 'Licor', unidad: 'chupito', volumen_ml: 40, graduacion: 40 },
  coctel: { nombre: 'Cóctel', unidad: 'cubata', volumen_ml: 250, graduacion: 12 },
  otro: { nombre: 'Otra', unidad: 'vaso', volumen_ml: 100, graduacion: 10 },
}

export const TIPOS = Object.keys(CATALOGO) as TipoBebida[]

export function bebidaPorDefecto(tipo: TipoBebida = 'cerveza'): Bebida {
  const { volumen_ml, graduacion } = CATALOGO[tipo]
  return { tipo, volumen_ml, graduacion, cantidad: 1 }
}
