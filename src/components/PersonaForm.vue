<script setup lang="ts">
import { computed } from 'vue'
import { LIMITES } from '../types/alcohol'
import type { DatosPersona, Estomago, Sexo } from '../types/alcohol'

const persona = defineModel<DatosPersona>({ required: true })
defineProps<{ disabled?: boolean }>()

const sexos: { valor: Sexo; etiqueta: string }[] = [
  { valor: 'hombre', etiqueta: 'Hombre' },
  { valor: 'mujer', etiqueta: 'Mujer' },
]

const estomagos: { valor: Estomago; etiqueta: string; detalle: string }[] = [
  { valor: 'vacio', etiqueta: 'Vacío', detalle: 'Sin comer' },
  { valor: 'algo', etiqueta: 'Algo', detalle: 'Picoteo' },
  { valor: 'lleno', etiqueta: 'Lleno', detalle: 'Comida' },
]

const horas = computed(() => {
  const h = Math.floor(persona.value.tiempo_horas)
  const m = Math.round((persona.value.tiempo_horas - h) * 60)
  return m === 0 ? `${h} h` : `${h} h ${m} min`
})
</script>

<template>
  <fieldset class="tarjeta madera" :disabled="disabled">
    <legend class="titulo">Cuéntale a la barra</legend>

    <div class="campos">
    <div class="campo">
      <label for="peso">Peso corporal</label>
      <div class="entrada-unidad">
        <input
          id="peso"
          v-model.number="persona.peso_kg"
          type="number"
          inputmode="numeric"
          :min="LIMITES.peso_kg.min"
          :max="LIMITES.peso_kg.max"
          required
        />
        <span>kg</span>
      </div>
    </div>

    <div class="campo">
      <span class="etiqueta" id="sexo-label">Sexo biológico</span>
      <div class="segmentos" role="radiogroup" aria-labelledby="sexo-label">
        <label v-for="s in sexos" :key="s.valor" class="segmento">
          <input v-model="persona.sexo" type="radio" name="sexo" :value="s.valor" />
          <span>{{ s.etiqueta }}</span>
        </label>
      </div>
    </div>

    <div class="campo">
      <div class="fila-etiqueta">
        <label for="tiempo">Tiempo bebiendo</label>
        <strong>{{ horas }}</strong>
      </div>
      <input
        id="tiempo"
        v-model.number="persona.tiempo_horas"
        type="range"
        :min="LIMITES.tiempo_horas.min"
        :max="LIMITES.tiempo_horas.max"
        :step="LIMITES.tiempo_horas.paso"
      />
    </div>

    <div class="campo">
      <span class="etiqueta" id="estomago-label">Estómago</span>
      <div class="segmentos tres" role="radiogroup" aria-labelledby="estomago-label">
        <label v-for="e in estomagos" :key="e.valor" class="segmento">
          <input v-model="persona.estomago" type="radio" name="estomago" :value="e.valor" />
          <span>
            {{ e.etiqueta }}
            <small>{{ e.detalle }}</small>
          </span>
        </label>
      </div>
    </div>
    </div>
  </fieldset>
</template>
