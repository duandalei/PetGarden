<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import CatPet from './CatPet.vue'
import DogPet from './DogPet.vue'
import DragonPet from './DragonPet.vue'
import FoxPet from './FoxPet.vue'
import PandaPet from './PandaPet.vue'
import RabbitPet from './RabbitPet.vue'
import StageAccessories from './StageAccessories.vue'
import './pet.css'
import type { PetLevel, PetMood, PetReaction, SpeciesId } from './types'
import { LEVEL_SCALES, MOOD_WORDS, SPECIES_VISUALS } from './visuals'
import { usePetMotionStyle } from './usePetMotion'

const props = withDefaults(
  defineProps<{
    species: SpeciesId
    level: PetLevel
    mood: PetMood
    reaction?: PetReaction | null
    seed: number | string
    size?: number
    label?: string
    decorative?: boolean
  }>(),
  { reaction: null, size: 120, label: undefined, decorative: false },
)

const SPECIES_COMPONENTS = {
  cat: CatPet,
  dog: DogPet,
  rabbit: RabbitPet,
  panda: PandaPet,
  fox: FoxPet,
  dragon: DragonPet,
} as const

const speciesComponent = computed(() => SPECIES_COMPONENTS[props.species])
const scale = computed(() => LEVEL_SCALES[props.level - 1])
const motionStyle = computed(() => usePetMotionStyle(props.seed, props.species, props.mood))

const ariaLabel = computed(() => {
  if (props.label) return props.label
  const name = SPECIES_VISUALS[props.species].name
  return `${name}，等级 ${props.level}，心情${MOOD_WORDS[props.mood]}`
})

const reactionClass = ref('')
let timer: number | undefined

watch(
  () => props.reaction?.nonce,
  () => {
    if (!props.reaction) return
    window.clearTimeout(timer)
    reactionClass.value = `reaction-${props.reaction.type}`
    const duration =
      props.reaction.type === 'evolve' ? 1100 : props.reaction.type === 'cheer' ? 900 : 700
    timer = window.setTimeout(() => {
      reactionClass.value = ''
    }, duration)
  },
)
</script>

<template>
  <svg
    class="pet-svg"
    viewBox="0 0 200 200"
    :width="size"
    :height="size"
    v-bind="decorative ? { 'aria-hidden': 'true' } : { role: 'img', 'aria-label': ariaLabel }"
  >
    <g
      class="pet-scale"
      :transform="`translate(100 180) scale(${scale}) translate(-100 -180)`"
    >
      <g class="pet-root pet-reaction" :class="reactionClass" :style="motionStyle">
        <ellipse class="pet-shadow" cx="100" cy="178" rx="52" ry="8" />
        <StageAccessories :level="level" layer="back" />
        <component :is="speciesComponent" :level="level" :mood="mood" />
        <circle
          class="evolve-burst" cx="100" cy="108" r="44"
          fill="none" stroke="var(--pet-accent)" stroke-width="3"
        />
      </g>
    </g>
  </svg>
</template>