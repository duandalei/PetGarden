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
    <path d="M140 148 C166 142 174 120 166 102" fill="none" stroke="var(--pet-ink)" stroke-width="15" stroke-linecap="round" />
    <path d="M140 148 C166 142 174 120 166 102" fill="none" stroke="var(--pet-accent)" stroke-width="10" stroke-linecap="round" />
    <circle cx="166" cy="102" r="5.5" fill="var(--pet-accent)" stroke="var(--pet-ink)" stroke-width="2" />
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
        <g :transform="`rotate(${earTilt - 20} 58 80)`">
          <g class="pet-ear pet-ear-l">
            <ellipse cx="46" cy="88" rx="17" ry="32" fill="var(--pet-accent)" stroke="var(--pet-ink)" stroke-width="2.4" />
            <ellipse cx="46" cy="92" rx="9" ry="21" fill="var(--pet-inner)" opacity="0.75" />
          </g>
        </g>
        <g :transform="`rotate(${-earTilt + 20} 142 80)`">
          <g class="pet-ear pet-ear-r">
            <ellipse cx="154" cy="88" rx="17" ry="32" fill="var(--pet-accent)" stroke="var(--pet-ink)" stroke-width="2.4" />
            <ellipse cx="154" cy="92" rx="9" ry="21" fill="var(--pet-inner)" opacity="0.75" />
          </g>
        </g>
      </g>
      <circle cx="100" cy="92" r="44" fill="var(--pet-body)" stroke="var(--pet-ink)" stroke-width="2.5" />
      <PetFace :species="'dog'" :mood="mood" />
      <StageAccessories :level="level" layer="head" />
    </g>
  </g>
</template>