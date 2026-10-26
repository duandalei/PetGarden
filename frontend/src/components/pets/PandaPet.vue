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
    <circle cx="146" cy="162" r="9" fill="var(--pet-ink)" />
    <circle cx="146" cy="160" r="3" fill="var(--pet-body)" opacity="0.35" />
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
        <g :transform="`rotate(${earTilt} 68 58)`">
          <g class="pet-ear pet-ear-l">
            <circle cx="68" cy="56" r="16" fill="var(--pet-ink)" />
          </g>
        </g>
        <g :transform="`rotate(${-earTilt} 132 58)`">
          <g class="pet-ear pet-ear-r">
            <circle cx="132" cy="56" r="16" fill="var(--pet-ink)" />
          </g>
        </g>
      </g>
      <circle cx="100" cy="92" r="44" fill="var(--pet-body)" stroke="var(--pet-ink)" stroke-width="2.5" />
      <PetFace :species="'panda'" :mood="mood" />
      <StageAccessories :level="level" layer="head" />
    </g>
  </g>
</template>