<script setup lang="ts">
import { onBeforeUnmount, ref, watch } from 'vue'

import { api, ApiError } from '../api/client'
import type { RollcallResponse } from '../api/types'
import { useReducedMotion } from '../composables/useReducedMotion'
import PetSprite from './pets/PetSprite.vue'
import type { PetLevel } from './pets/types'

const props = defineProps<{
  open: boolean
  classId: number
  className: string
  motionPref: 'system' | 'reduced'
}>()

const emit = defineEmits<{ close: [] }>()

const { isReduced } = useReducedMotion()

const phase = ref<'idle' | 'rolling' | 'done'>('idle')
const result = ref<RollcallResponse | null>(null)
const rollingName = ref('')
const errorMsg = ref('')
const overlayRef = ref<HTMLElement | null>(null)
const announce = ref('')

let rollTimer: number | undefined
let previousFocus: HTMLElement | null = null

const NAMES_PLACEHOLDER = '正在抽取'

watch(
  () => props.open,
  async (v) => {
    if (!v) return
    previousFocus = document.activeElement as HTMLElement | null
    errorMsg.value = ''
    result.value = null
    phase.value = 'idle'
    await roll()
    overlayRef.value?.focus()
  },
)

async function roll() {
  phase.value = 'rolling'
  result.value = null
  announce.value = ''
  let response: RollcallResponse
  try {
    response = await api.post<RollcallResponse>(`/api/classes/${props.classId}/rollcall`, {
      mode: 'fair',
      exclude_absent: true,
    })
  } catch (err) {
    errorMsg.value = err instanceof ApiError ? err.message : '点名失败，请重试。'
    phase.value = 'idle'
    return
  }

  if (isReduced(props.motionPref)) {
    result.value = response
    phase.value = 'done'
    announce.value = `抽中了 ${response.student.name}`
    return
  }

  // 900ms 滚动定格动画：快速切换候选名字
  const started = performance.now()
  window.clearInterval(rollTimer)
  rollTimer = window.setInterval(() => {
    rollingName.value = response.student.name.slice(0, 1) + '??'
    if (performance.now() - started >= 900) {
      window.clearInterval(rollTimer)
      result.value = response
      phase.value = 'done'
      announce.value = `抽中了 ${response.student.name}`
    }
  }, 60)
}

function reroll() {
  if (phase.value === 'rolling') return
  void roll()
}

function close() {
  emit('close')
  window.clearInterval(rollTimer)
  previousFocus?.focus()
}

function onKeydown(e: KeyboardEvent) {
  if (!props.open) return
  if (e.key === 'Escape') {
    e.preventDefault()
    close()
  } else if (e.key === ' ' || e.key === 'Enter') {
    e.preventDefault()
    reroll()
  }
}

onBeforeUnmount(() => window.clearInterval(rollTimer))

watch(
  () => props.open,
  (v) => {
    if (v) window.addEventListener('keydown', onKeydown)
    else window.removeEventListener('keydown', onKeydown)
  },
  { immediate: true },
)

onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown))
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      ref="overlayRef"
      class="rollcall-overlay"
      role="dialog"
      aria-modal="true"
      aria-label="随机点名"
      tabindex="-1"
    >
      <p class="rollcall-title">今天会是谁呢？</p>
      <p class="rollcall-class">{{ className }}</p>

      <div v-if="errorMsg" class="rollcall-error">
        <p>{{ errorMsg }}</p>
        <button type="button" class="btn btn-primary" @click="reroll">重试</button>
      </div>

      <template v-else>
        <div class="rollcall-pet" :class="{ rolling: phase === 'rolling' }">
          <PetSprite
            v-if="result"
            :species="result.student.species"
            :level="result.student.level as PetLevel"
            :mood="result.student.mood"
            :seed="result.student.id"
            :size="220"
          />
          <div v-else class="rollcall-placeholder" aria-hidden="true">?</div>
        </div>
        <p class="rollcall-name num-display" aria-hidden="true">
          {{ phase === 'done' && result ? result.student.name : rollingName || NAMES_PLACEHOLDER }}
        </p>
        <p v-if="result" class="rollcall-pool">候选 {{ result.pool_size }} 人</p>
        <div class="rollcall-actions">
          <button type="button" class="btn btn-primary rollcall-again" @click="reroll">
            再抽一次（空格）
          </button>
          <button type="button" class="btn" @click="close">关闭（Esc）</button>
        </div>
      </template>

      <span class="visually-hidden" aria-live="polite">{{ announce }}</span>
    </div>
  </Teleport>
</template>

<style scoped>
.rollcall-overlay {
  position: fixed;
  inset: 0;
  z-index: 80;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background: var(--paper);
}

.rollcall-title {
  color: var(--ink-soft);
  font-size: 18px;
}

.rollcall-class {
  color: var(--ink-faint);
  font-size: 14px;
}

.rollcall-pet {
  min-height: 240px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.rollcall-pet.rolling {
  animation: rollcall-pulse 0.3s ease-in-out infinite;
}

@keyframes rollcall-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.04); }
}

.rollcall-placeholder {
  color: var(--line-strong);
  font-family: var(--font-display);
  font-size: 160px;
  line-height: 1;
}

.rollcall-name {
  font-size: 64px;
  font-weight: 700;
  line-height: 1.1;
}

.rollcall-pool {
  color: var(--ink-faint);
  font-size: 14px;
}

.rollcall-actions {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}

.rollcall-again {
  min-width: 220px;
  min-height: 56px;
  font-size: 18px;
}

.rollcall-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  color: var(--ink-soft);
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
}

@media (prefers-reduced-motion: reduce) {
  .rollcall-pet.rolling {
    animation: none;
  }
}

:root[data-motion='reduced'] .rollcall-pet.rolling {
  animation: none;
}
</style>