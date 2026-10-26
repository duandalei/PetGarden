<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { api } from '../api/client'
import type { DisplayData, Student } from '../api/types'
import PetSprite from '../components/pets/PetSprite.vue'
import type { PetLevel, PetReaction } from '../components/pets/types'
import { usePolling } from '../composables/usePolling'
import { useReducedMotion } from '../composables/useReducedMotion'

const route = useRoute()
const router = useRouter()
const { applyPreference } = useReducedMotion()

const classId = computed(() => Number(route.params.id))
const data = ref<DisplayData | null>(null)
const sortMode = ref<'seat' | 'score'>('seat')
const reactions = ref<Record<number, PetReaction>>({})
const topbarVisible = ref(true)

let nonce = 0
let hideTimer: number | undefined
const prevLevels = new Map<number, number>()

const students = computed(() => {
  const list = data.value?.students ?? []
  if (sortMode.value === 'score') {
    return [...list].sort((a, b) => b.score - a.score || a.id - b.id)
  }
  return list
})

const petSize = computed(() => {
  const n = students.value.length
  if (n > 40) return 96
  if (n > 24) return 120
  return 150
})

async function fetchDisplay() {
  const res = await api.get<DisplayData>(`/api/classes/${classId.value}/display`)
  // 检测升级并触发 evolve
  for (const s of res.students) {
    const prev = prevLevels.get(s.id)
    if (prev !== undefined && s.level > prev) {
      nonce += 1
      reactions.value[s.id] = { type: 'evolve', nonce }
    }
    prevLevels.set(s.id, s.level)
  }
  data.value = res
}

const { failed } = usePolling(fetchDisplay, 3000)

function onMouseMove() {
  topbarVisible.value = true
  window.clearTimeout(hideTimer)
  hideTimer = window.setTimeout(() => {
    topbarVisible.value = false
  }, 3000)
}

onMounted(() => {
  window.addEventListener('mousemove', onMouseMove)
  onMouseMove()
  // 大屏继承应用内减少动效设置
  void api
    .get<{ motion_pref: 'system' | 'reduced' }>('/api/settings')
    .then((s) => applyPreference(s.motion_pref))
    .catch(() => undefined)
})

onBeforeUnmount(() => {
  window.removeEventListener('mousemove', onMouseMove)
  window.clearTimeout(hideTimer)
})

function exit() {
  void router.push(`/class/${classId.value}`)
}

function reactionOf(s: Student): PetReaction | null {
  return reactions.value[s.id] ?? null
}

</script>

<template>
  <div class="display-page" @mousemove.passive="onMouseMove">
    <header class="display-topbar" :class="{ hidden: !topbarVisible }">
      <span class="display-class-name">{{ data?.class.name ?? '' }}</span>
      <span class="display-count">{{ students.length }} 名学生</span>
      <div class="display-controls">
        <button
          type="button"
          class="btn btn-small"
          @click="sortMode = sortMode === 'seat' ? 'score' : 'seat'"
        >
          {{ sortMode === 'seat' ? '按座位' : '按积分' }}
        </button>
        <button type="button" class="btn btn-small" @click="exit">退出大屏</button>
      </div>
    </header>

    <div v-if="failed" class="display-offline" role="status">连接中断，正在重试…</div>

    <main class="display-grid" :style="{ '--pet-size': `${petSize}px` }">
      <div v-for="s in students" :key="s.id" class="display-cell">
        <PetSprite
          :species="s.species"
          :level="s.level as PetLevel"
          :mood="s.mood"
          :reaction="reactionOf(s)"
          :seed="s.id"
          :size="petSize"
          decorative
        />
        <p class="display-name">{{ s.name }}</p>
        <p class="display-score num-display">{{ s.score }}</p>
        <span class="badge display-stage">L{{ s.level }} · {{ s.stage }}</span>
      </div>
    </main>
  </div>
</template>

<style scoped>
.display-page {
  min-height: 100vh;
  background: var(--paper);
}

.display-topbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px 20px;
  border-bottom: 1px solid var(--line);
  background: rgba(250, 246, 236, 0.96);
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.display-topbar.hidden {
  opacity: 0;
  pointer-events: none;
  transform: translateY(-100%);
}

.display-class-name {
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 700;
}

.display-count {
  color: var(--ink-soft);
  font-size: 14px;
}

.display-controls {
  margin-left: auto;
  display: flex;
  gap: 8px;
}

.display-offline {
  position: fixed;
  top: 54px;
  left: 50%;
  z-index: 30;
  padding: 6px 16px;
  border-radius: var(--radius-pill);
  background: var(--ink);
  color: var(--paper);
  font-size: 13px;
  transform: translateX(-50%);
}

.display-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(calc(var(--pet-size) + 60px), 1fr));
  gap: 10px;
  padding: 72px 28px 28px;
}

.display-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 8px;
}

.display-name {
  font-size: 24px;
  font-weight: 700;
}

.display-score {
  font-size: 34px;
  font-weight: 700;
  line-height: 1;
  transition: transform 0.22s ease;
}

.display-stage {
  font-size: 13px;
}
</style>