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
    <circle cx="148" cy="162" r="11" fill="var(--pet-belly)" stroke="var(--pet-ink)" stroke-width="2.2" />
    <circle cx="148" cy="162" r="5" fill="var(--pet-inner)" opacity="0.7" />
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
        <g :transform="`rotate(${earTilt} 84 78)`">
          <g class="pet-ear pet-ear-l">
            <ellipse cx="84" cy="42" rx="12" ry="38" fill="var(--pet-body)" stroke="var(--pet-ink)" stroke-width="2.4" />
            <ellipse cx="84" cy="44" rx="6" ry="27" fill="var(--pet-inner)" opacity="0.9" />
          </g>
        </g>
        <g :transform="`rotate(${-earTilt} 116 78)`">
          <g class="pet-ear pet-ear-r">
            <ellipse cx="116" cy="42" rx="12" ry="38" fill="var(--pet-body)" stroke="var(--pet-ink)" stroke-width="2.4" />
            <ellipse cx="116" cy="44" rx="6" ry="27" fill="var(--pet-inner)" opacity="0.9" />
          </g>
        </g>
      </g>
      <circle cx="100" cy="92" r="44" fill="var(--pet-body)" stroke="var(--pet-ink)" stroke-width="2.5" />
      <PetFace :species="'rabbit'" :mood="mood" />
      <StageAccessories :level="level" layer="head" />
    </g>
  </g>
</template>