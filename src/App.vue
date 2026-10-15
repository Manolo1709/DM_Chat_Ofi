<script setup lang="ts">
import { ref } from 'vue'
import BebidasLista from './components/BebidasLista.vue'
import PersonaForm from './components/PersonaForm.vue'
import TabernaDecor from './components/TabernaDecor.vue'
import { bebidaPorDefecto } from './data/catalogo'
import type { Bebida, DatosPersona } from './types/alcohol'

const persona = ref<DatosPersona>({
  peso_kg: 70,
  sexo: 'hombre',
  tiempo_horas: 1,
  estomago: 'algo',
})
const bebidas = ref<Bebida[]>([bebidaPorDefecto()])
</script>

<template>
  <TabernaDecor />

  <main class="contenedor">
    <header class="cabecera">
      <div class="rotulo">
        <span class="rotulo-mini" aria-hidden="true">Cerveza · Licores · Desde 1989</span>
        <h1 class="letrero">La Taberna</h1>
        <p class="lema">«Cuéntame qué has bebido y te digo cómo vas.»</p>
      </div>
      <p class="cartel">
        <span class="chincheta" aria-hidden="true"></span>
        Si bebes, no conduzcas. Pide un taxi.
      </p>
    </header>

    <div class="escenario">
      <form class="formulario" @submit.prevent>
        <PersonaForm v-model="persona" />

        <BebidasLista v-model="bebidas" />
      </form>
    </div>
  </main>
</template>
