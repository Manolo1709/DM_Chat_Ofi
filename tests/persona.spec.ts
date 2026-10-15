// Persona A: formulario de la persona y panel del resultado
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import PersonaForm from '../src/components/PersonaForm.vue'
import ResultadoPanel from '../src/components/ResultadoPanel.vue'
import type { CalculoResponse, DatosPersona } from '../src/types/alcohol'

const persona: DatosPersona = { peso_kg: 70, sexo: 'hombre', tiempo_horas: 1, estomago: 'algo' }

function montarForm(disabled = false) {
  return mount(PersonaForm, {
    props: {
      modelValue: { ...persona },
      'onUpdate:modelValue': () => {},
      disabled,
    },
  })
}

describe('PersonaForm', () => {
  it('muestra los cuatro controles', () => {
    const w = montarForm()
    expect(w.find('#peso').exists()).toBe(true)
    expect(w.findAll('input[name="sexo"]')).toHaveLength(2)
    expect(w.find('#tiempo').exists()).toBe(true)
    expect(w.findAll('input[name="estomago"]')).toHaveLength(3)
  })

  it('actualiza el modelo al cambiar los datos', async () => {
    const w = montarForm()
    await w.find('#peso').setValue(85)
    await w.find('input[value="mujer"]').setValue()
    await w.find('input[value="lleno"]').setValue()
    const modelo = w.props('modelValue')
    expect(modelo.peso_kg).toBe(85)
    expect(modelo.sexo).toBe('mujer')
    expect(modelo.estomago).toBe('lleno')
  })

  it('formatea el tiempo en horas y minutos', async () => {
    const w = montarForm()
    await w.find('#tiempo').setValue(1.5)
    expect(w.text()).toContain('1 h 30 min')
  })

  it('se deshabilita mientras carga', () => {
    expect(montarForm(true).find('fieldset').attributes()).toHaveProperty('disabled')
  })
})

const resultado: CalculoResponse = {
  tasa_gl: 0.62,
  nivel: 'alegre',
  horas_hasta_cero: 4.1,
  explicacion: '',
  consejos: [],
  aviso_conduccion: 'No conduzcas si has bebido alcohol.',
}

describe('ResultadoPanel', () => {
  it('muestra tasa, nivel, tiempo hasta 0 y aviso', () => {
    const w = mount(ResultadoPanel, { props: { resultado } })
    expect(w.find('.tasa').text()).toContain('0.62')
    expect(w.find('.nivel').text()).toBe('Contento')
    expect(w.text()).toContain('4 h 6 min')
    expect(w.find('.aviso').text()).toBe(resultado.aviso_conduccion)
    expect(w.find('.resultado').classes()).toContain('nivel-alegre')
  })

  it('marca el nivel activo en el medidor', () => {
    const w = mount(ResultadoPanel, { props: { resultado: { ...resultado, nivel: 'peligroso' } } })
    expect(w.find('.medidor .activo').text()).toBe('Peligroso')
  })

  it('indica cuando ya se está a 0,0 g/L', () => {
    const w = mount(ResultadoPanel, {
      props: { resultado: { ...resultado, tasa_gl: 0, nivel: 'sobrio', horas_hasta_cero: 0 } },
    })
    expect(w.text()).toContain('Ya estás a 0,0 g/L')
  })
})
