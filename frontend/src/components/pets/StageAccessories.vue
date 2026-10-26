<script setup lang="ts">
import { computed } from 'vue'

import type { PetLevel } from './types'

const props = defineProps<{
  level: PetLevel
  layer: 'back' | 'body' | 'head'
}>()

const particles = computed(() => {
  const pts: Array<[number, number]> = [
    [100, 18], [150, 50], [170, 104], [150, 160],
    [100, 184], [50, 160], [30, 104], [50, 50],
  ]
  return pts.map(([cx, cy], i) => ({ cx, cy, r: 1.8 + (i % 3), i }))
})
</script>

<template>
  <!-- L4+ 背后虚线光环（缓慢旋转） -->
  <g v-if="layer === 'back' && level >= 4" class="pet-aura">
    <circle
      cx="100" cy="108" r="72" fill="none" stroke="var(--pet-accent)"
      stroke-width="1.8" stroke-dasharray="7 11" opacity="0.36"
    />
    <circle
      cx="100" cy="108" r="64" fill="none" stroke="var(--pet-accent)"
      stroke-width="1" stroke-dasharray="2 13" opacity="0.24"
    />
  </g>

  <template v-if="layer === 'body'">
    <!-- L2+ 围巾 -->
    <g v-if="level >= 2">
      <path
        d="M64 132 Q100 150 136 132 L134 143 Q100 160 66 143 Z"
        fill="var(--pet-accent)" stroke="var(--pet-ink)" stroke-width="2.2" stroke-linejoin="round"
      />
      <circle cx="100" cy="146" r="5" fill="var(--pet-belly)" stroke="var(--pet-ink)" stroke-width="1.5" />
    </g>
    <!-- L3+ 胸前徽章 -->
    <g v-if="level >= 3">
      <circle cx="100" cy="156" r="7.5" fill="#E6B04A" stroke="var(--pet-ink)" stroke-width="1.8" />
      <path
        d="M100 151.5 L101.6 155 L105.3 155.2 L102.4 157.6 L103.4 161.2 L100 159.2 L96.6 161.2 L97.6 157.6 L94.7 155.2 L98.4 155 Z"
        fill="#FFFDF7" opacity="0.9"
      />
    </g>
    <!-- L5 粒子环 -->
    <g v-if="level >= 5" class="pet-particles">
      <circle
        v-for="p in particles" :key="p.i"
        class="pet-particle" :cx="p.cx" :cy="p.cy" :r="p.r"
        fill="var(--pet-accent)" opacity="0" :style="{ '--i': p.i }"
      />
    </g>
  </template>

  <template v-if="layer === 'head'">
    <!-- L4+ 额头纹样 -->
    <path
      v-if="level >= 4"
      d="M100 66 L106 73 L100 80 L94 73 Z"
      fill="var(--pet-accent)" opacity="0.55"
    />
    <!-- L5 皇冠 -->
    <g v-if="level >= 5">
      <path
        d="M78 46 L84 27 L92 39 L100 23 L108 39 L116 27 L122 46 Z"
        fill="#E6B04A" stroke="var(--pet-ink)" stroke-width="2" stroke-linejoin="round"
      />
      <circle cx="84" cy="42" r="2.2" fill="#B85C3E" />
      <circle cx="100" cy="38" r="2.4" fill="#B85C3E" />
      <circle cx="116" cy="42" r="2.2" fill="#B85C3E" />
    </g>
  </template>
</template>