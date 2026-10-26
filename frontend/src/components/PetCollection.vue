<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import { api, ApiError } from '../api/client'
import type { Collection, Student, SwitchPetResponse } from '../api/types'
import { useRosterStore } from '../stores/roster'
import { useToastStore } from '../stores/toast'
import ConfirmDialog from './ConfirmDialog.vue'
import PetSprite from './pets/PetSprite.vue'
import type { PetLevel } from './pets/types'

const props = defineProps<{
  open: boolean
  student: Student | null
}>()

const emit = defineEmits<{
  close: []
  switched: [student: Student]
}>()

const roster = useRosterStore()
const toast = useToastStore()

const collection = ref<Collection | null>(null)
const loading = ref(false)
const confirmTarget = ref<string | null>(null)
const switching = ref(false)

const currentStudentId = computed(() => props.student?.id ?? null)

watch(
  () => [props.open, currentStudentId.value],
  async () => {
    if (!props.open || currentStudentId.value === null) return
    loading.value = true
    try {
      collection.value = await api.get<Collection>(
        `/api/students/${currentStudentId.value}/collection`,
      )
    } catch (err) {
      toast.push(err instanceof ApiError ? err.message : '加载图鉴失败。', 'error')
    } finally {
      loading.value = false
    }
  },
  { immediate: true },
)

function previewLevel(best: number): PetLevel {
  return (Math.max(1, Math.min(5, best)) as PetLevel)
}

function askSwitch(species: string) {
  confirmTarget.value = species
}

async function doSwitch() {
  if (!confirmTarget.value || currentStudentId.value === null) return
  switching.value = true
  try {
    const res = await api.post<SwitchPetResponse>(
      `/api/students/${currentStudentId.value}/switch-pet`,
      { species: confirmTarget.value },
    )
    roster.replaceStudent(res.student)
    roster.setReaction(res.student.id, 'evolve')
    toast.push(res.message, 'success', 4000)
    emit('switched', res.student)
    collection.value = await api.get<Collection>(
      `/api/students/${res.student.id}/collection`,
    )
    confirmTarget.value = null
  } catch (err) {
    toast.push(err instanceof ApiError ? err.message : '换宠失败。', 'error')
  } finally {
    switching.value = false
  }
}
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="dialog-mask" @click.self="emit('close')">
      <div class="dialog collection-dialog" role="dialog" aria-modal="true" aria-label="宠物图鉴">
        <h2>宠物图鉴 · {{ student?.name }}</h2>
        <p class="collection-hint">
          当前宠物达到 L5 满级后可以换宠；任意普通宠物达到 L5 即可解锁神兽。
        </p>
        <div v-if="loading" class="collection-loading">加载中…</div>
        <div v-else-if="collection" class="collection-grid">
          <div
            v-for="item in collection.items"
            :key="item.species"
            class="collection-item"
            :class="{ current: item.is_current, locked: !item.unlocked }"
          >
            <div class="collection-pet" :class="{ grey: item.best_level === 0 }">
              <PetSprite
                :species="item.species"
                :level="previewLevel(item.best_level)"
                mood="neutral"
                :seed="item.species"
                :size="88"
                decorative
              />
            </div>
            <div class="collection-name">
              {{ item.name }}
              <span v-if="item.is_current" class="badge">当前</span>
            </div>
            <div class="dots" :aria-label="`最高等级 ${item.best_level}`">
              <span
                v-for="n in 5"
                :key="n"
                class="dot"
                :class="{ on: n <= item.best_level }"
              />
            </div>
            <p v-if="item.type === 'divine' && !item.unlocked" class="lock-hint">
              任意普通宠物达到 L5 解锁
            </p>
            <button
              v-else
              type="button"
              class="btn btn-small"
              :disabled="!collection.can_switch_pet || item.is_current || switching"
              @click="askSwitch(item.species)"
            >
              {{ item.is_current ? '正在陪伴' : collection.can_switch_pet ? '换宠' : '需要 L5' }}
            </button>
          </div>
        </div>
        <div class="dialog-actions">
          <button type="button" class="btn" @click="emit('close')">关闭</button>
        </div>
      </div>
    </div>
  </Teleport>
  <ConfirmDialog
    :open="confirmTarget !== null"
    title="确认换宠"
    message="换宠后当前积分会归零，新伙伴从 L1 开始成长。旧伙伴的图鉴进度会保留。确定吗？"
    confirm-label="确定换宠"
    @confirm="doSwitch"
    @cancel="confirmTarget = null"
  />
</template>

<style scoped>
.collection-dialog {
  max-width: 640px;
}

.collection-hint {
  margin-bottom: 14px;
  color: var(--ink-soft);
  font-size: 13px;
}

.collection-loading {
  padding: 40px 0;
  color: var(--ink-faint);
  text-align: center;
}

.collection-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.collection-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 12px 8px;
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  background: var(--surface);
}

.collection-item.current {
  border-color: var(--moss);
}

.collection-item.locked .collection-pet {
  opacity: 0.35;
}

.collection-pet.grey {
  opacity: 0.5;
}

.collection-name {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 700;
}

.dots {
  display: flex;
  gap: 4px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--surface-sunken);
}

.dot.on {
  background: var(--moss);
}

.lock-hint {
  color: var(--ink-faint);
  font-size: 11px;
  text-align: center;
}
</style>