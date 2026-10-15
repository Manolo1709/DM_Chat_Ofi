<script setup lang="ts">
defineProps<{
  explicacion?: string
  consejos?: string[]
  loading?: boolean
  peligro?: boolean
}>()
</script>

<template>
  <section class="pizarra explicacion" aria-live="polite" :aria-busy="loading">
    <h2 class="titulo-tiza">El camarero dice…</h2>

    <p v-if="loading" class="cargando">
      <span class="spinner" aria-hidden="true"></span>
      Pensando qué decirte…
    </p>

    <template v-else>
      <p v-if="peligro" class="alerta" role="alert">
        Tasa muy alta: deja de beber. Si hay vómitos, confusión o somnolencia intensa, llama al 112.
      </p>
      <p data-test="explicacion">{{ explicacion }}</p>
      <ul v-if="consejos?.length" class="consejos">
        <li v-for="consejo in consejos" :key="consejo">{{ consejo }}</li>
      </ul>
    </template>
  </section>
</template>
