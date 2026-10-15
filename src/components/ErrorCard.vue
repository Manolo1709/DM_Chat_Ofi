<script setup lang="ts">
defineProps<{ mensaje: string }>()
defineEmits<{ reintentar: [] }>()
</script>

<template>
  <div class="error" role="alert">
    <p>{{ mensaje }}</p>
    <button type="button" class="reintentar" @click="$emit('reintentar')">Reintentar</button>
  </div>
</template>
