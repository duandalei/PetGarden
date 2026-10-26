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
const wingScale = computed(() => (0.82 + props.level * 0.055).toFixed(2))
</script>

<template>
  <!-- 龙翼（L5 时最大，随等级展开） -->
  <g class="dragon-wings" :transform="`translate(100 130) scale(${wingScale}) translate(-100 -130)`">
    <path
      d="M72 122 C58 98 34 78 20 84 C30 98 30 110 26 122 C38 118 46 124 50 134 C58 128 66 132 74 138 Z"
      fill="var(--pet-inner)" stroke="var(--pet-ink)" stroke-width="2" stroke-linejoin="round"
    />
    <path
      d="M128 122 C142 98 166 78 180 84 C170 98 170 110 174 122 C162 118 154 124 150 134 C142 128 134 132 126 138 Z"
      fill="var(--pet-inner)" stroke="var(--pet-ink)" stroke-width="2" stroke-linejoin="round"
    />
    <path
      d="M70 120 L28 92 M70 122 L32 111 M130 120 L172 92 M130 122 L168 111"
      stroke="var(--pet-accent)" stroke-width="1.4" opacity="0.38" stroke-linecap="round"
    />
  </g>

  <g class="pet-tail">
    <path d="M138 156 C180 160 188 190 144 190 C122 190 116 176 132 170" fill="none" stroke="var(--pet-ink)" stroke-width="18" stroke-linecap="round" />
    <path d="M138 156 C180 160 188 190 144 190 C122 190 116 176 132 170" fill="none" stroke="var(--pet-accent)" stroke-width="13" stroke-linecap="round" />
    <path d="M132 170 L118 162 L124 178 Z" fill="var(--pet-accent)" stroke="var(--pet-ink)" stroke-width="1.5" stroke-linejoin="round" />
  </g>

  <g class="pet-body">
    <ellipse cx="100" cy="145" rx="46" ry="36" fill="var(--pet-body)" stroke="var(--pet-ink)" stroke-width="2.5" />
    <ellipse cx="100" cy="151" rx="28" ry="24" fill="var(--pet-belly)" opacity="0.92" />
    <path
      d="M82 154 Q100 162 118 154 M86 162 Q100 169 114 162"
      fill="none" stroke="var(--pet-accent)" stroke-width="1.5" opacity="0.35" stroke-linecap="round"
    />
    <ellipse cx="78" cy="172" rx="15" ry="8" fill="var(--pet-body)" stroke="var(--pet-ink)" stroke-width="2" />
    <ellipse cx="122" cy="172" rx="15" ry="8" fill="var(--pet-body)" stroke="var(--pet-ink)" stroke-width="2" />
    <StageAccessories :level="level" layer="body" />
  </g>

  <g class="pet-head-wrap" :transform="`rotate(${headTilt} 100 132)`">
    <g class="pet-head">
      <g class="pet-ears">
        <g :transform="`rotate(${earTilt} 100 60)`">
          <g class="pet-ear pet-ear-l">
            <path
              d="M80 62 C72 48 68 34 72 22 C78 34 86 44 92 51 Z"
              fill="var(--pet-belly)" stroke="var(--pet-ink)" stroke-width="2.2" stroke-linejoin="round"
            />
          </g>
        </g>
        <g :transform="`rotate(${-earTilt} 100 60)`">
          <g class="pet-ear pet-ear-r">
            <path
              d="M120 62 C128 48 132 34 128 22 C122 34 114 44 108 51 Z"
              fill="var(--pet-belly)" stroke="var(--pet-ink)" stroke-width="2.2" stroke-linejoin="round"
            />
          </g>
        </g>
        <path d="M62 92 L48 82 L60 74 Z" fill="var(--pet-inner)" stroke="var(--pet-ink)" stroke-width="2" stroke-linejoin="round" />
        <path d="M138 92 L152 82 L140 74 Z" fill="var(--pet-inner)" stroke="var(--pet-ink)" stroke-width="2" stroke-linejoin="round" />
      </g>
      <circle cx="100" cy="92" r="44" fill="var(--pet-body)" stroke="var(--pet-ink)" stroke-width="2.5" />
      <PetFace :species="'dragon'" :mood="mood" />
      <StageAccessories :level="level" layer="head" />
    </g>
  </g>
</template>