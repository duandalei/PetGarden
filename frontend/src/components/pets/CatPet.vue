<script setup lang="ts">
import { computed } from 'vue'

import PetFace from './PetFace.vue'
import StageAccessories from './StageAccessories.vue'
import type { PetLevel, PetMood } from './types'

const props = defineProps<{
  level: PetLevel
  mood: PetMood
}>()

const earTilt = computed(() => (props.mood === 'sad' ? 6 : props.mood === 'happy' ? -2 : 0))
const headTilt = computed(() => (props.mood === 'sad' ? -2.5 : props.mood === 'happy' ? 0.5 : 0))
</script>

<template>
  <g class="pet-tail">
    <path d="M140 150 C168 146 178 120 160 103" fill="none" stroke="var(--pet-ink)" stroke-width="16" stroke-linecap="round" />
    <path d="M140 150 C168 146 178 120 160 103" fill="none" stroke="var(--pet-accent)" stroke-width="11" stroke-linecap="round" />
    <circle cx="160" cy="103" r="6" fill="var(--pet-accent)" stroke="var(--pet-ink)" stroke-width="2" />
  </g>

  <g class="pet-body">
    <ellipse cx="100" cy="145" rx="46" ry="36" fill="var(--pet-body)" stroke="var(--pet-ink)" stroke-width="2.5" />
    <ellipse cx="100" cy="151" rx="28" ry="24" fill="var(--pet-belly)" opacity="0.92" />
    <ellipse cx="78" cy="172" rx="15" ry="8" fill="var(--pet-body)" stroke="var(--pet-ink)" stroke-width="2" />
    <ellipse cx="122" cy="172" rx="15" ry="8" fill="var(--pet-body)" stroke="var(--pet-ink)" stroke-width="2" />
    <StageAccessories :level="level" layer="body" />
  </g>

  <g class="pet-head-wrap" :transform="`rotate(${headTilt} 100 132)`">
    <g class="pet-head">
      <g class="pet-ears">
        <g :transform="`rotate(${earTilt} 74 60)`">
          <g class="pet-ear pet-ear-l">
            <path d="M62 64 L54 26 L88 48 Z" fill="var(--pet-body)" stroke="var(--pet-ink)" stroke-width="2.5" stroke-linejoin="round" />
            <path d="M66 57 L62 37 L80 49 Z" fill="var(--pet-inner)" opacity="0.9" />
          </g>
        </g>
        <g :transform="`rotate(${-earTilt} 126 60)`">
          <g class="pet-ear pet-ear-r">
            <path d="M138 64 L146 26 L112 48 Z" fill="var(--pet-body)" stroke="var(--pet-ink)" stroke-width="2.5" stroke-linejoin="round" />
            <path d="M134 57 L138 37 L120 49 Z" fill="var(--pet-inner)" opacity="0.9" />
          </g>
        </g>
      </g>
      <circle cx="100" cy="92" r="44" fill="var(--pet-body)" stroke="var(--pet-ink)" stroke-width="2.5" />
      <PetFace :species="'cat'" :mood="mood" />
      <StageAccessories :level="level" layer="head" />
    </g>
  </g>
</template>