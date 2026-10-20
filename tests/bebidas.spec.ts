// Persona B: lista de bebidas, explicación de la IA y flujo con fetch mockeado
import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from '../src/App.vue'
import BebidasLista from '../src/components/BebidasLista.vue'
import ExplicacionPanel from '../src/components/ExplicacionPanel.vue'
import { bebidaPorDefecto } from '../src/data/catalogo'
import type { Bebida, CalculoResponse } from '../src/types/alcohol'

function montarLista(bebidas: Bebida[] = [bebidaPorDefecto()]) {
  const w = mount(BebidasLista, {
    props: {
      modelValue: bebidas,
      'onUpdate:modelValue': (v: Bebida[]) => w.setProps({ modelValue: v }),
    },
  })
  return w
}

describe('BebidasLista', () => {
  it('añade una bebida', async () => {
    const w = montarLista()
    await w.find('[data-test="anadir"]').trigger('click')
    expect(w.findAll('[data-test="bebida"]')).toHaveLength(2)
  })

  it('quita una bebida', async () => {
    const w = montarLista([bebidaPorDefecto('vino'), bebidaPorDefecto('licor')])
    await w.findAll('[data-test="quitar"]')[0]!.trigger('click')
    expect(w.props('modelValue')).toEqual([bebidaPorDefecto('licor')])
  })

  it('no deja quitar la última bebida', async () => {
    const w = montarLista()
    const quitar = w.find('[data-test="quitar"]')
    expect(quitar.attributes()).toHaveProperty('disabled')
    await quitar.trigger('click')
    expect(w.findAll('[data-test="bebida"]')).toHaveLength(1)
  })

  it('carga los valores por defecto al cambiar el tipo', async () => {
    const w = montarLista()
    await w.find('select').setValue('licor')
    expect(w.props('modelValue')[0]).toEqual({ tipo: 'licor', volumen_ml: 40, graduacion: 40, cantidad: 1 })
  })

  it('cambia la cantidad sin bajar de 1', async () => {
    const w = montarLista()
    await w.find('[aria-label="Una menos"]').trigger('click')
    expect(w.props('modelValue')[0]!.cantidad).toBe(1)
    await w.find('[aria-label="Una más"]').trigger('click')
    expect(w.find('[data-test="cantidad"]').text()).toBe('2')
  })
})

describe('ExplicacionPanel', () => {
  it('muestra el spinner mientras carga', () => {
    const w = mount(ExplicacionPanel, { props: { loading: true } })
    expect(w.find('.spinner').exists()).toBe(true)
    expect(w.find('[data-test="explicacion"]').exists()).toBe(false)
  })

  it('muestra explicación y consejos', () => {
    const w = mount(ExplicacionPanel, { props: { explicacion: 'Vas bien.', consejos: ['Agua', 'Taxi'] } })
    expect(w.find('[data-test="explicacion"]').text()).toBe('Vas bien.')
    expect(w.findAll('.consejos li')).toHaveLength(2)
    expect(w.find('.alerta').exists()).toBe(false)
  })

  it('muestra la alerta si el nivel es peligroso', () => {
    const w = mount(ExplicacionPanel, { props: { explicacion: 'x', consejos: [], peligro: true } })
    expect(w.find('.alerta').text()).toContain('112')
  })
})

const RESPUESTA: CalculoResponse = {
  tasa_gl: 0.45,
  nivel: 'alegre',
  horas_hasta_cero: 3,
  explicacion: 'Estás algo alegre.',
  consejos: ['Bebe agua.'],
  aviso_conduccion: 'No conduzcas.',
  origen: 'ia',
}

describe('App con fetch mockeado', () => {
  afterEach(() => vi.unstubAllGlobals())

  it('envía persona y bebidas y pinta el resultado', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => RESPUESTA })
    vi.stubGlobal('fetch', fetchMock)

    const w = mount(App)
    await w.find('form').trigger('submit')
    await flushPromises()

    const cuerpo = JSON.parse(fetchMock.mock.calls[0]![1].body)
    expect(cuerpo.bebidas).toHaveLength(1)
    expect(cuerpo.peso_kg).toBe(70)
    expect(w.find('.tasa').text()).toContain('0.45')
    expect(w.find('[data-test="explicacion"]').text()).toBe('Estás algo alegre.')
  })

  it.each([
    [422, 'no son válidos'],
    [500, 'problema'],
    [502, 'explicación no responde'],
  ])('muestra la tarjeta de error para %i', async (status, texto) => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status }))
    const w = mount(App)
    await w.find('form').trigger('submit')
    await flushPromises()
    expect(w.find('.error').text()).toContain(texto)
  })

  it('muestra error de red y reintenta', async () => {
    const fetchMock = vi
      .fn()
      .mockRejectedValueOnce(new TypeError('Failed to fetch'))
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => RESPUESTA })
    vi.stubGlobal('fetch', fetchMock)

    const w = mount(App)
    await w.find('form').trigger('submit')
    await flushPromises()
    expect(w.find('.error').text()).toContain('conexión')

    await w.find('.reintentar').trigger('click')
    await flushPromises()
    expect(fetchMock).toHaveBeenCalledTimes(2)
    expect(w.find('.error').exists()).toBe(false)
    expect(w.find('.tasa').exists()).toBe(true)
  })
})
