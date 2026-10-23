<script setup lang="ts">
import { ref } from 'vue'
import { Show, SignInButton, SignUpButton, UserButton } from '@clerk/vue'
import BebidasLista from './components/BebidasLista.vue'
import ErrorCard from './components/ErrorCard.vue'
import ExplicacionPanel from './components/ExplicacionPanel.vue'
import PersonaForm from './components/PersonaForm.vue'
import ResultadoPanel from './components/ResultadoPanel.vue'
import TabernaDecor from './components/TabernaDecor.vue'
import { bebidaPorDefecto } from './data/catalogo'
import { calcular } from './services/api'
import type { Bebida, CalculoResponse, DatosPersona } from './types/alcohol'


//parte de clerk y control de usuario
import {useAuth} from '@clerk/vue'

const {isLoaded, isSignedIn} = useAuth()
const {getToken} = useAuth()


const persona = ref<DatosPersona>({
  peso_kg: 70,
  sexo: 'hombre',
  tiempo_horas: 1,
  estomago: 'algo',
})
const bebidas = ref<Bebida[]>([bebidaPorDefecto()])

const loading = ref(false)
const error = ref<string | null>(null)
const resultado = ref<CalculoResponse | null>(null)

async function handleSubmit() {
  const token = await getToken.value()

  if (!token) {
    throw new Error('Debes iniciar sesion')
  }
  loading.value = true
  error.value = null
  try {
    resultado.value = await calcular({ ...persona.value, bebidas: bebidas.value },token)
  } catch (e) {
    resultado.value = null
    error.value = e instanceof Error ? e.message : 'No se pudo calcular el resultado.'
  } finally {
    loading.value = false
  }
}
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
              <div v-if="!isLoaded">
          Cargando aplicacion...
        </div>

        <div v-else-if="!isSignedIn">
          <nav class="auth-controls" aria-label="Autenticación">
              <Show when="signed-out">
                <SignInButton mode="modal">
                  <button class="auth-button auth-button-secondary" type="button">Entrar</button>
                </SignInButton>
                <SignUpButton mode="modal">
                  <button class="auth-button auth-button-primary" type="button">Crear cuenta</button>
                </SignUpButton>
              </Show>

            </nav>
        </div>
        <div v-else>
              <Show when="signed-in">
                <UserButton />
              </Show>
    <div class="escenario">
      <form class="formulario" @submit.prevent="handleSubmit">
        <PersonaForm v-model="persona" :disabled="loading" />

        <BebidasLista v-model="bebidas" :disabled="loading" />

        <button class="boton" type="submit" :disabled="loading">
          <span v-if="loading" class="spinner" aria-hidden="true"></span>
          {{ loading ? 'Sirviendo…' : 'Ponme la cuenta' }}
        </button>
      </form>

      <div class="columna-resultado">
        <ErrorCard v-if="error" :mensaje="error" @reintentar="handleSubmit" />

        <template v-if="resultado">
          <ResultadoPanel :resultado="resultado" />
          <ExplicacionPanel
            :explicacion="resultado.explicacion"
            :consejos="resultado.consejos"
            :loading="loading"
            :peligro="resultado.nivel === 'peligroso'"
          />
        </template>
        <section v-else class="pizarra pizarra-vacia">
          <h2 class="titulo-tiza">Especial de la casa</h2>
          <p class="jarra" aria-hidden="true">🍺</p>
          <p>Rellena tus datos y pide la cuenta para ver cómo vas.</p>
          <ul class="medidor medidor-fila" aria-hidden="true">
            <li>Sobrio</li>
            <li>Contento</li>
            <li>Borracho</li>
            <li>Peligroso</li>
          </ul>
          <p class="nota">Estimación orientativa. No sustituye a un alcoholímetro.</p>
        </section>
      </div>
    </div>
    </div>
  </main>
  
</template>
