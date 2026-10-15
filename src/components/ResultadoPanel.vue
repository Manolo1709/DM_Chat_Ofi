<script setup lang="ts">
import { computed } from 'vue'
import type { CalculoResponse, Nivel } from '../types/alcohol'

const props = defineProps<{ resultado: CalculoResponse }>()

const niveles: { valor: Nivel; nombre: string }[] = [
  { valor: 'sobrio', nombre: 'Sobrio' },
  { valor: 'alegre', nombre: 'Contento' },
  { valor: 'borracho', nombre: 'Borracho' },
  { valor: 'peligroso', nombre: 'Peligroso' },
]

const nombreNivel = computed(
  () => niveles.find((n) => n.valor === props.resultado.nivel)?.nombre ?? '',
)

// La barra llega al 100 % con 2,0 g/L
const porcentaje = computed(() => Math.min(100, (props.resultado.tasa_gl / 2) * 100))

const tiempoCero = computed(() => {
  const h = props.resultado.horas_hasta_cero
  if (h <= 0) return 'Ya estás a 0,0 g/L'
  const horas = Math.floor(h)
  const min = Math.round((h - horas) * 60)
  return `${horas} h ${min} min`
})
</script>

<template>
  <section class="tele resultado" :class="`nivel-${resultado.nivel}`" aria-live="polite">
    <div class="tele-carcasa">
      <div class="tele-pantalla lectura">
        <h2 class="tele-canal">La cuenta</h2>
        <p class="tasa">
          {{ resultado.tasa_gl.toFixed(2) }} <span>g/L</span>
        </p>
        <p class="nivel">{{ nombreNivel }}</p>

        <div
          class="barra"
          role="meter"
          aria-label="Tasa de alcohol en sangre"
          :aria-valuenow="resultado.tasa_gl"
          aria-valuemin="0"
          aria-valuemax="2"
        >
          <div class="barra-relleno" :style="{ width: porcentaje + '%' }"></div>
        </div>

        <p v-if="resultado.horas_hasta_cero > 0" class="dato">
          Tiempo hasta 0,0 g/L: <strong>{{ tiempoCero }}</strong>
        </p>
        <p v-else class="dato"><strong>{{ tiempoCero }}</strong></p>
      </div>

      <div class="tele-panel">
        <ul class="medidor" aria-label="Niveles de embriaguez">
          <li
            v-for="n in niveles"
            :key="n.valor"
            :class="{ activo: n.valor === resultado.nivel }"
            :aria-current="n.valor === resultado.nivel ? 'true' : undefined"
          >
            {{ n.nombre }}
          </li>
        </ul>
        <div class="tele-mandos" aria-hidden="true">
          <span class="perilla"></span>
          <span class="perilla"></span>
        </div>
        <span class="rejilla" aria-hidden="true"></span>
      </div>
    </div>

    <div class="tele-pegatinas">
      <p class="aviso">{{ resultado.aviso_conduccion }}</p>
      <p class="nota">Estimación orientativa. No sustituye a un alcoholímetro.</p>
    </div>
  </section>
</template>
