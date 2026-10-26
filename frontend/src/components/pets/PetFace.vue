<script setup lang="ts">
import { computed } from 'vue'

import type { PetMood, SpeciesId } from './types'

const props = defineProps<{
  species: SpeciesId
  mood: PetMood
}>()

const eyeStroke = computed(() => (props.species === 'panda' ? '#FFFFFF' : 'var(--pet-ink)'))

const cheekOpacity = computed(() =>
  props.mood === 'happy' ? 0.45 : props.mood === 'sad' ? 0.15 : 0.28,
)
</script>

<template>
  <!-- 眼斑（熊猫） -->
  <template v-if="species === 'panda'">
    <ellipse cx="82" cy="92" rx="14" ry="17" transform="rotate(-12 82 92)" fill="var(--pet-ink)" />
    <ellipse cx="118" cy="92" rx="14" ry="17" transform="rotate(12 118 92)" fill="var(--pet-ink)" />
  </template>

  <!-- 吻部 -->
  <ellipse
    v-if="species === 'dog'" cx="100" cy="109" rx="22" ry="15"
    fill="var(--pet-belly)" opacity="0.92"
  />
  <ellipse
    v-else-if="species === 'fox'" cx="100" cy="109" rx="20" ry="13"
    fill="var(--pet-belly)" opacity="0.95"
  />
  <ellipse
    v-else-if="species === 'dragon'" cx="100" cy="109" rx="18" ry="11"
    fill="var(--pet-belly)" opacity="0.92"
  />
  <ellipse
    v-else cx="100" cy="108" rx="13" ry="9"
    fill="var(--pet-belly)" opacity="0.85"
  />

  <!-- 眼睛 -->
  <g v-if="mood === 'happy'" class="pet-eyes">
    <path d="M75 95 Q82 87 89 95" fill="none" :stroke="eyeStroke" stroke-width="3.6" stroke-linecap="round" />
    <path d="M111 95 Q118 87 125 95" fill="none" :stroke="eyeStroke" stroke-width="3.6" stroke-linecap="round" />
  </g>
  <g v-else-if="mood === 'sad'" class="pet-eyes">
    <path d="M75 90 Q82 97 89 90" fill="none" :stroke="eyeStroke" stroke-width="3.4" stroke-linecap="round" />
    <path d="M111 90 Q118 97 125 90" fill="none" :stroke="eyeStroke" stroke-width="3.4" stroke-linecap="round" />
  </g>
  <g v-else-if="species === 'panda'" class="pet-eyes">
    <ellipse cx="82" cy="92" rx="6" ry="7" fill="#FFFFFF" />
    <ellipse cx="118" cy="92" rx="6" ry="7" fill="#FFFFFF" />
    <circle cx="82" cy="93" r="3.4" fill="var(--pet-ink)" />
    <circle cx="118" cy="93" r="3.4" fill="var(--pet-ink)" />
    <circle cx="80.8" cy="90.8" r="1.2" fill="#FFFFFF" />
    <circle cx="116.8" cy="90.8" r="1.2" fill="#FFFFFF" />
  </g>
  <g v-else class="pet-eyes">
    <ellipse cx="82" cy="92" rx="5.6" ry="7.2" fill="var(--pet-ink)" />
    <ellipse cx="118" cy="92" rx="5.6" ry="7.2" fill="var(--pet-ink)" />
    <circle cx="80.2" cy="89.2" r="1.8" fill="#FFFFFF" />
    <circle cx="116.2" cy="89.2" r="1.8" fill="#FFFFFF" />
  </g>

  <!-- 腮红 -->
  <ellipse cx="66" cy="105" rx="7.5" ry="4" fill="var(--pet-accent)" :opacity="cheekOpacity" />
  <ellipse cx="134" cy="105" rx="7.5" ry="4" fill="var(--pet-accent)" :opacity="cheekOpacity" />

  <!-- 鼻子 -->
  <path
    d="M96.5 104.5 Q100 101.5 103.5 104.5 Q102 108.5 100 108.5 Q98 108.5 96.5 104.5 Z"
    fill="var(--pet-ink)"
  />

  <!-- 嘴 -->
  <path
    v-if="mood === 'happy'" d="M92 113 Q100 121 108 113"
    fill="none" stroke="var(--pet-ink)" stroke-width="2.4" stroke-linecap="round"
  />
  <path
    v-else-if="mood === 'sad'" d="M94 118 Q100 112 106 118"
    fill="none" stroke="var(--pet-ink)" stroke-width="2.3" stroke-linecap="round"
  />
  <path
    v-else d="M96 114 Q100 117 104 114"
    fill="none" stroke="var(--pet-ink)" stroke-width="2.2" stroke-linecap="round"
  />

  <!-- 物种特征 -->
  <g
    v-if="species === 'cat'" stroke="var(--pet-ink)" stroke-width="1.4"
    stroke-linecap="round" opacity="0.55"
  >
    <path d="M65 105 L42 101" />
    <path d="M65 109 L42 113" />
    <path d="M135 105 L158 101" />
    <path d="M135 109 L158 113" />
  </g>
  <path
    v-else-if="species === 'dog' && mood === 'happy'"
    d="M96 116 Q100 126 104 116 Z"
    fill="#E98B8B" stroke="var(--pet-ink)" stroke-width="1.5" stroke-linejoin="round"
  />
  <g
    v-else-if="species === 'rabbit'" fill="#FFFFFF"
    stroke="var(--pet-ink)" stroke-width="1.2"
  >
    <rect x="96" y="116" width="3.4" height="6" rx="1.2" />
    <rect x="100.6" y="116" width="3.4" height="6" rx="1.2" />
  </g>
  <g
    v-else-if="species === 'fox'" stroke="var(--pet-ink)"
    stroke-width="1.3" stroke-linecap="round" opacity="0.4"
  >
    <path d="M66 107 L46 103" />
    <path d="M134 107 L154 103" />
  </g>
  <template v-else-if="species === 'dragon'">
    <g fill="none" stroke="var(--pet-accent)" stroke-width="1.8" stroke-linecap="round" opacity="0.8">
      <path d="M82 108 C62 104 52 96 44 84" />
      <path d="M118 108 C138 104 148 96 156 84" />
    </g>
    <circle cx="95" cy="105" r="1.2" fill="var(--pet-ink)" opacity="0.55" />
    <circle cx="105" cy="105" r="1.2" fill="var(--pet-ink)" opacity="0.55" />
  </template>
</template>