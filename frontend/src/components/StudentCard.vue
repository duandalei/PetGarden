<script setup lang="ts">
import { computed } from 'vue'

import type { Student } from '../api/types'
import { SPECIES_VISUALS } from './pets/visuals'
import PetSprite from './pets/PetSprite.vue'
import ScoreButtons from './ScoreButtons.vue'
import type { PetReaction } from './pets/types'

const props = defineProps<{
  student: Student
  reaction?: PetReaction | null
  disabled?: boolean
}>()

const emit = defineEmits<{
  score: [delta: number]
  reason: [delta: number]
  open: []
}>()

const accent = computed(() => SPECIES_VISUALS[props.student.species].accent)
const levelLabel = computed(() => `L${props.student.level}`)
</script>

<template>
  <article
    class="student-card card"
    :style="{ '--species-accent': accent }"
    tabindex="0"
    :aria-label="`${student.name}，${student.score} 分，等级 ${levelLabel} ${student.stage}`"
    @click="emit('open')"
    @keydown.enter="emit('open')"
  >
    <div class="pet-area">
      <PetSprite
        :species="student.species"
        :level="student.level as 1 | 2 | 3 | 4 | 5"
        :mood="student.mood"
        :reaction="reaction"
        :seed="student.id"
        :size="112"
        decorative
      />
    </div>
    <div class="student-name">{{ student.name }}</div>
    <div class="student-meta">
      <span v-if="student.student_no">学号 {{ student.student_no }}</span>
      <span v-if="student.seat_no">座位 {{ student.seat_no }}</span>
    </div>
    <div class="score-line">
      <span class="score-num num-display">{{ student.score }}</span>
      <span class="score-unit">/100</span>
    </div>
    <div class="badge-row">
      <span class="badge">{{ levelLabel }} · {{ student.stage }}</span>
    </div>
    <div class="progress-track" aria-hidden="true">
      <span class="progress-fill" :style="{ width: `${student.score_percent}%` }" />
    </div>
    <div @click.stop>
      <ScoreButtons
        :disabled="disabled ?? false"
        :name="student.name"
        @minus="emit('score', -1)"
        @plus="emit('score', 1)"
        @long-minus="emit('reason', -1)"
        @long-plus="emit('reason', 1)"
      />
    </div>
  </article>
</template>

<style scoped>
.student-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px 14px 14px;
  border-top: 3px solid var(--species-accent);
  cursor: pointer;
  transition:
    transform 0.16s ease,
    box-shadow 0.16s ease,
    border-color 0.16s ease;
}

.student-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-pop);
}

.pet-area {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  height: 118px;
  margin: -2px -4px 0;
  border-radius: var(--radius-md);
  background: var(--surface-sunken);
}

.student-name {
  overflow: hidden;
  font-size: 17px;
  font-weight: 700;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.student-meta {
  display: flex;
  gap: 8px;
  color: var(--ink-faint);
  font-size: 12px;
}

.score-line {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.score-num {
  font-size: 32px;
  font-weight: 700;
  line-height: 1;
}

.score-unit {
  color: var(--ink-faint);
  font-size: 12px;
}

.badge-row {
  display: flex;
  gap: 6px;
}
</style>