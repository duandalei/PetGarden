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
    <path
      d="M138 150 C172 146 186 118 168 94 C158 112 146 122 132 130 Z"
      fill="var(--pet-accent)" stroke="var(--pet-ink)" stroke-width="2.2" stroke-linejoin="round"
    />
    <ellipse cx="166" cy="97" rx="10" ry="8" transform="rotate(-30 166 97)" fill="var(--pet-belly)" opacity="0.95" />
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
            <path d="M60 66 L48 22 L92 50 Z" fill="var(--pet-body)" stroke="var(--pet-ink)" stroke-width="2.5" stroke-linejoin="round" />
            <path d="M66 58 L58 34 L82 51 Z" fill="var(--pet-accent)" opacity="0.55" />
          </g>
        </g>
        <g :transform="`rotate(${-earTilt} 126 60)`">
          <g class="pet-ear pet-ear-r">
            <path d="M140 66 L152 22 L108 50 Z" fill="var(--pet-body)" stroke="var(--pet-ink)" stroke-width="2.5" stroke-linejoin="round" />
            <path d="M134 58 L142 34 L118 51 Z" fill="var(--pet-accent)" opacity="0.55" />
          </g>
        </g>
      </g>
      <circle cx="100" cy="92" r="44" fill="var(--pet-body)" stroke="var(--pet-ink)" stroke-width="2.5" />
      <PetFace :species="'fox'" :mood="mood" />
      <StageAccessories :level="level" layer="head" />
    </g>
  </g>
</template>