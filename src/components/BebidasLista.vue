<script setup lang="ts">
import { nextTick, useTemplateRef } from 'vue'
import { CATALOGO, TIPOS, bebidaPorDefecto } from '../data/catalogo'
import { LIMITES_BEBIDA } from '../types/alcohol'
import type { Bebida, TipoBebida } from '../types/alcohol'

const bebidas = defineModel<Bebida[]>({ required: true })
defineProps<{ disabled?: boolean }>()

const lista = useTemplateRef<HTMLUListElement>('lista')

// Si la lista tiene scroll propio, se baja hasta la bebida nueva
async function anadir() {
  bebidas.value = [...bebidas.value, bebidaPorDefecto()]
  await nextTick()
  lista.value?.lastElementChild?.scrollIntoView?.({ block: 'nearest', behavior: 'smooth' })
}

// Siempre debe quedar al menos una bebida
function quitar(indice: number) {
  if (bebidas.value.length <= 1) return
  bebidas.value = bebidas.value.filter((_, i) => i !== indice)
}

// Al cambiar el tipo se cargan su volumen y graduación por defecto
function cambiarTipo(indice: number, tipo: TipoBebida) {
  bebidas.value = bebidas.value.map((b, i) =>
    i === indice ? { ...bebidaPorDefecto(tipo), cantidad: b.cantidad } : b,
  )
}

function cambiarCantidad(indice: number, delta: number) {
  const { min, max } = LIMITES_BEBIDA.cantidad
  bebidas.value = bebidas.value.map((b, i) =>
    i === indice ? { ...b, cantidad: Math.min(max, Math.max(min, b.cantidad + delta)) } : b,
  )
}
</script>

<template>
  <fieldset class="tarjeta madera bebidas" :disabled="disabled">
    <legend class="titulo">¿Qué has tomado?</legend>

    <ul ref="lista" class="lista-bebidas">
      <li v-for="(bebida, i) in bebidas" :key="i" class="bebida" data-test="bebida">
        <div class="campo campo-tipo">
          <label :for="`tipo-${i}`">Bebida</label>
          <select
            :id="`tipo-${i}`"
            :value="bebida.tipo"
            @change="cambiarTipo(i, ($event.target as HTMLSelectElement).value as TipoBebida)"
          >
            <option v-for="t in TIPOS" :key="t" :value="t">
              {{ CATALOGO[t].nombre }} ({{ CATALOGO[t].unidad }})
            </option>
          </select>
        </div>

        <div class="campo">
          <label :for="`volumen-${i}`">Volumen</label>
          <div class="entrada-unidad">
            <input
              :id="`volumen-${i}`"
              v-model.number="bebida.volumen_ml"
              type="number"
              inputmode="numeric"
              :min="LIMITES_BEBIDA.volumen_ml.min"
              :max="LIMITES_BEBIDA.volumen_ml.max"
              required
            />
            <span>ml</span>
          </div>
        </div>

        <div class="campo">
          <label :for="`graduacion-${i}`">Graduación</label>
          <div class="entrada-unidad">
            <input
              :id="`graduacion-${i}`"
              v-model.number="bebida.graduacion"
              type="number"
              inputmode="decimal"
              step="0.5"
              :min="LIMITES_BEBIDA.graduacion.min"
              :max="LIMITES_BEBIDA.graduacion.max"
              required
            />
            <span>%</span>
          </div>
        </div>

        <div class="campo">
          <span class="etiqueta" :id="`cantidad-${i}`">Cantidad</span>
          <div class="contador" role="group" :aria-labelledby="`cantidad-${i}`">
            <button
              type="button"
              aria-label="Una menos"
              :disabled="bebida.cantidad <= LIMITES_BEBIDA.cantidad.min"
              @click="cambiarCantidad(i, -1)"
            >
              −
            </button>
            <output data-test="cantidad">{{ bebida.cantidad }}</output>
            <button
              type="button"
              aria-label="Una más"
              :disabled="bebida.cantidad >= LIMITES_BEBIDA.cantidad.max"
              @click="cambiarCantidad(i, 1)"
            >
              +
            </button>
          </div>
        </div>

        <button
          type="button"
          class="quitar"
          data-test="quitar"
          :aria-label="`Quitar ${CATALOGO[bebida.tipo].nombre.toLowerCase()}`"
          :disabled="bebidas.length <= 1"
          @click="quitar(i)"
        >
          ✕
        </button>
      </li>
    </ul>

    <button type="button" class="anadir" data-test="anadir" @click="anadir">+ Otra ronda</button>
  </fieldset>
</template>
