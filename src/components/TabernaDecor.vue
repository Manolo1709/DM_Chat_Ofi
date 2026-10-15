<script setup lang="ts">
// Decoración fija de la taberna (ilustración original en SVG): lámparas colgantes,
// rótulos de neón, diana, estante con botellas y tarro de huevos. La barra con
// taburetes va aparte, como pie de página. Los laterales solo se ven en pantallas anchas.
const colores = ['#4f7a3a', '#8a3b2a', '#b8862b', '#3a5f7a', '#6b2f4a']
const botellas = [40, 50, 36, 46, 42].map((alto, i) => ({
  x: 12 + i * 30,
  alto,
  color: colores[i] as string,
}))
const taburetes = [8, 22, 36, 64, 78, 92]
const lamparas = [18, 50, 82]
</script>

<template>
  <div class="decor" aria-hidden="true">
    <!-- Lámparas colgantes con su cono de luz -->
    <div v-for="x in lamparas" :key="x" class="lampara-techo" :style="{ left: x + '%' }">
      <span class="cable"></span>
      <span class="tulipa"></span>
      <span class="luz"></span>
    </div>

    <!-- Pared izquierda: neón de cerveza y diana -->
    <div class="lateral izq">
      <svg class="neon-cartel" viewBox="0 0 180 110">
        <rect x="6" y="6" width="168" height="98" rx="49" fill="none" stroke="#5dff9a" stroke-width="4" class="tubo verde" />
        <text x="90" y="52" text-anchor="middle" class="tubo rojo texto-neon">Cerveza</text>
        <text x="90" y="82" text-anchor="middle" class="tubo ambar texto-neon pequeno">bien fría</text>
      </svg>

      <svg class="diana" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r="56" fill="#1a1a1a" />
        <g v-for="(r, i) in [48, 38, 28, 18]" :key="r">
          <circle cx="60" cy="60" :r="r" :fill="i % 2 ? '#e9dcb6' : '#1f5c3a'" />
        </g>
        <circle cx="60" cy="60" r="8" fill="#b3241f" />
        <circle cx="60" cy="60" r="3" fill="#1f5c3a" />
        <g stroke="#c9a243" stroke-width="1" opacity="0.7">
          <line x1="60" y1="8" x2="60" y2="112" />
          <line x1="8" y1="60" x2="112" y2="60" />
          <line x1="23" y1="23" x2="97" y2="97" />
          <line x1="97" y1="23" x2="23" y2="97" />
        </g>
        <!-- Dardo clavado -->
        <line x1="70" y1="48" x2="98" y2="20" stroke="#d8d8d8" stroke-width="3" />
        <path d="M94 16 l10 -6 l-2 12 z" fill="#b3241f" />
      </svg>
    </div>

    <!-- Pared derecha: neón de abierto y estante con botellas y tarro de huevos -->
    <div class="lateral der">
      <svg class="neon-cartel parpadeo" viewBox="0 0 180 70">
        <rect x="6" y="6" width="168" height="58" rx="10" fill="none" stroke="#ff4f6d" stroke-width="4" class="tubo rojo" />
        <text x="90" y="46" text-anchor="middle" class="tubo ambar texto-neon">Abierto</text>
      </svg>

      <svg class="estante" viewBox="0 0 170 150">
        <g v-for="(b, i) in botellas" :key="i">
          <rect :x="b.x" :y="70 - b.alto" width="16" :height="b.alto" rx="3" :fill="b.color" />
          <rect :x="b.x + 5" :y="60 - b.alto" width="6" height="11" :fill="b.color" />
          <rect :x="b.x + 2" :y="78 - b.alto + 14" width="12" height="10" fill="#e9dcb6" opacity="0.8" />
        </g>
        <rect x="2" y="70" width="166" height="8" fill="#5a3418" />
        <!-- Tarro de huevos en vinagre -->
        <rect x="52" y="92" width="66" height="10" rx="3" fill="#7a7a7a" />
        <rect x="48" y="100" width="74" height="44" rx="10" fill="#c9d98a" opacity="0.55" stroke="#e9f0c8" stroke-width="2" />
        <g fill="#f6f1df" stroke="#d9cfa8">
          <ellipse cx="66" cy="126" rx="9" ry="11" />
          <ellipse cx="85" cy="130" rx="9" ry="11" />
          <ellipse cx="104" cy="125" rx="9" ry="11" />
          <ellipse cx="76" cy="112" rx="9" ry="11" />
          <ellipse cx="95" cy="112" rx="9" ry="11" />
        </g>
        <rect x="2" y="144" width="166" height="6" fill="#5a3418" />
      </svg>
    </div>

  </div>

  <!-- Barra y taburetes: pie de página en el flujo normal, nunca tapa contenido -->
  <div class="pie-barra" aria-hidden="true">
    <div class="mostrador"></div>
    <svg
      v-for="x in taburetes"
      :key="x"
      class="taburete"
      :style="{ left: x + '%' }"
      viewBox="0 0 60 90"
    >
      <ellipse cx="30" cy="12" rx="26" ry="9" fill="#a11d1d" />
      <ellipse cx="30" cy="9" rx="26" ry="8" fill="#d23a2e" />
      <rect x="27" y="18" width="6" height="64" fill="#9aa0a6" />
      <ellipse cx="30" cy="58" rx="16" ry="4" fill="none" stroke="#9aa0a6" stroke-width="3" />
      <ellipse cx="30" cy="86" rx="20" ry="4" fill="#6c7176" />
    </svg>
  </div>
</template>
