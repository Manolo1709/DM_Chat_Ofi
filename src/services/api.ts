import type { CalculoRequest, CalculoResponse } from '../types/alcohol'

// Con VITE_USE_MOCK=true se devuelve una respuesta de ejemplo para diseñar
// la interfaz sin backend.
const USAR_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

const MOCK: CalculoResponse = {
  tasa_gl: 0.62,
  nivel: 'alegre',
  horas_hasta_cero: 4.1,
  explicacion: 'Respuesta de ejemplo para diseñar la interfaz.',
  consejos: ['Bebe agua entre copa y copa.', 'Evita seguir bebiendo.'],
  aviso_conduccion: 'No conduzcas si has bebido alcohol.',
}

// Error con el código HTTP (0 si ni siquiera hubo respuesta)
export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

const MENSAJES: Record<number, string> = {
  422: 'Hay datos que no son válidos. Revisa el formulario.',
  500: 'El servidor ha tenido un problema. Inténtalo de nuevo.',
  502: 'El servicio de explicación no responde. Inténtalo de nuevo.',
}

export async function calcular(datos: CalculoRequest): Promise<CalculoResponse> {
  if (USAR_MOCK) {
    await new Promise((r) => setTimeout(r, 600))
    return MOCK
  }

  let res: Response
  try {
    res = await fetch('/api/calcular', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos),
    })
  } catch {
    throw new ApiError(0, 'No hay conexión con el servidor. Comprueba tu red.')
  }

  if (!res.ok) {
    throw new ApiError(
      res.status,
      MENSAJES[res.status] ?? `El servidor respondió con un error (${res.status}).`,
    )
  }
  return res.json()
}
