<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import { api, ApiError } from '../api/client'
import type { ScoreEvent, Student, StudentDetail } from '../api/types'
import { useRosterStore } from '../stores/roster'
import { useToastStore } from '../stores/toast'
import { formatDelta } from '../utils/format'
import ConfirmDialog from './ConfirmDialog.vue'
import PetCollection from './PetCollection.vue'
import PetSprite from './pets/PetSprite.vue'
import type { PetLevel } from './pets/types'

const props = defineProps<{
  open: boolean
  studentId: number | null
}>()

const emit = defineEmits<{
  close: []
  deleted: [classId: number]
  updated: [student: Student]
}>()

const roster = useRosterStore()
const toast = useToastStore()

const student = ref<Student | null>(null)
const events = ref<ScoreEvent[]>([])
const loading = ref(false)
const editing = ref(false)
const editName = ref('')
const editNo = ref('')
const editSeat = ref<string>('')
const collectionOpen = ref(false)
const confirmDelete = ref(false)
const undoing = ref(false)

const latestUndoneEvent = computed(() =>
  events.value.find((e) => e.undone_at === null) ?? null,
)

watch(
  () => [props.open, props.studentId],
  async () => {
    if (!props.open || props.studentId === null) return
    loading.value = true
    editing.value = false
    try {
      const data = await api.get<StudentDetail>(`/api/students/${props.studentId}`)
      student.value = data.student
      events.value = data.recent_events
      editName.value = data.student.name
      editNo.value = data.student.student_no ?? ''
      editSeat.value = data.student.seat_no === null ? '' : String(data.student.seat_no)
    } catch (err) {
      toast.push(err instanceof ApiError ? err.message : '加载失败。', 'error')
      emit('close')
    } finally {
      loading.value = false
    }
  },
  { immediate: true },
)

async function undoLatest() {
  const ev = latestUndoneEvent.value
  if (!ev || !student.value) return
  undoing.value = true
  try {
    const res = await api.post<{ student: Student; event: ScoreEvent }>(
      `/api/score-events/${ev.id}/undo`,
    )
    roster.replaceStudent(res.student)
    student.value = res.student
    events.value = events.value.map((e) => (e.id === ev.id ? res.event : e))
    toast.push(`已撤销：${res.student.name} ${formatDelta(ev.delta)}`, 'success')
    emit('updated', res.student)
  } catch (err) {
    toast.push(err instanceof ApiError ? err.message : '撤销失败。', 'error')
  } finally {
    undoing.value = false
  }
}

async function saveEdit() {
  if (!student.value) return
  try {
    const seat = editSeat.value === '' ? null : Number(editSeat.value)
    const res = await api.patch<{ student: Student }>(`/api/students/${student.value.id}`, {
      name: editName.value.trim(),
      student_no: editNo.value.trim() || null,
      seat_no: seat,
    })
    student.value = res.student
    roster.replaceStudent(res.student)
    editing.value = false
    toast.push('已保存。', 'success')
    emit('updated', res.student)
  } catch (err) {
    toast.push(err instanceof ApiError ? err.message : '保存失败。', 'error')
  }
}

async function doDelete() {
  if (!student.value) return
  try {
    await api.delete(`/api/students/${student.value.id}`)
    const classId = student.value.class_id
    roster.removeStudent(classId, student.value.id)
    toast.push('已删除。', 'success')
    confirmDelete.value = false
    emit('deleted', classId)
    emit('close')
  } catch (err) {
    toast.push(err instanceof ApiError ? err.message : '删除失败。', 'error')
  }
}

function onSwitched(s: Student) {
  student.value = s
  emit('updated', s)
}
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="drawer-mask" @click.self="emit('close')">
      <aside class="drawer" role="dialog" aria-modal="true" :aria-label="student?.name ?? '学生详情'">
        <template v-if="student">
          <div class="drawer-head">
            <h2>{{ student.name }}</h2>
            <button type="button" class="btn btn-small" @click="emit('close')">关闭</button>
          </div>
          <div class="drawer-pet">
            <PetSprite
              :species="student.species"
              :level="student.level as PetLevel"
              :mood="student.mood"
              :reaction="roster.reactions[student.id] ?? null"
              :seed="student.id"
              :size="160"
            />
          </div>
          <div class="drawer-score">
            <span class="num-display drawer-score-num">{{ student.score }}</span>
            <span class="drawer-score-unit">/100</span>
            <span class="badge">L{{ student.level }} · {{ student.stage }}</span>
          </div>
          <p class="drawer-meta">
            {{ student.species_name }} · 图鉴最高 L{{ student.best_level }}
            <template v-if="student.student_no"> · 学号 {{ student.student_no }}</template>
            <template v-if="student.seat_no"> · 座位 {{ student.seat_no }}</template>
          </p>

          <section class="drawer-section">
            <h3>最近事件</h3>
            <ul v-if="events.length" class="event-list">
              <li v-for="e in events" :key="e.id" :class="{ undone: e.undone_at }">
                <span class="event-delta num-display">{{ formatDelta(e.delta) }}</span>
                <span class="event-reason">{{ e.reason || '快捷评分' }}</span>
                <span v-if="e.undone_at" class="event-undone">已撤销</span>
              </li>
            </ul>
            <p v-else class="drawer-meta">还没有评分记录。</p>
            <button
              type="button"
              class="btn btn-small"
              :disabled="!latestUndoneEvent || undoing"
              @click="undoLatest"
            >
              撤销最近一次
            </button>
          </section>

          <section class="drawer-section">
            <h3>管理</h3>
            <div class="drawer-actions">
              <button type="button" class="btn" @click="collectionOpen = true">查看图鉴 / 换宠</button>
              <button type="button" class="btn" @click="editing = !editing">
                {{ editing ? '收起编辑' : '编辑信息' }}
              </button>
              <button type="button" class="btn btn-danger" @click="confirmDelete = true">删除学生</button>
            </div>
            <div v-if="editing" class="edit-form">
              <div class="field">
                <label for="edit-name">姓名</label>
                <input id="edit-name" v-model="editName" class="input" maxlength="20" />
              </div>
              <div class="field">
                <label for="edit-no">学号</label>
                <input id="edit-no" v-model="editNo" class="input" maxlength="20" />
              </div>
              <div class="field">
                <label for="edit-seat">座位号</label>
                <input id="edit-seat" v-model="editSeat" class="input" type="number" min="1" max="99" />
              </div>
              <button type="button" class="btn btn-primary btn-small" @click="saveEdit">保存</button>
            </div>
          </section>
        </template>
        <p v-else-if="loading" class="drawer-meta">加载中…</p>
      </aside>
    </div>
  </Teleport>

  <PetCollection
    :open="collectionOpen"
    :student="student"
    @close="collectionOpen = false"
    @switched="onSwitched"
  />
  <ConfirmDialog
    :open="confirmDelete"
    title="删除学生"
    :message="`确定删除 ${student?.name} 吗？相关积分事件和图鉴进度会一并删除，此操作不可恢复。`"
    confirm-label="确认删除"
    danger
    @confirm="doDelete"
    @cancel="confirmDelete = false"
  />
</template>

<style scoped>
.drawer-mask {
  position: fixed;
  inset: 0;
  z-index: 60;
  display: flex;
  justify-content: flex-end;
  background: rgba(37, 42, 38, 0.38);
}

.drawer {
  width: min(420px, 100vw);
  height: 100%;
  overflow-y: auto;
  padding: 22px;
  border-left: 1px solid var(--line);
  background: var(--surface);
  box-shadow: var(--shadow-pop);
}

.drawer-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.drawer-head h2 {
  font-size: 22px;
}

.drawer-pet {
  display: flex;
  justify-content: center;
  padding: 12px;
  border-radius: var(--radius-lg);
  background: var(--surface-sunken);
}

.drawer-score {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-top: 14px;
}

.drawer-score-num {
  font-size: 44px;
  font-weight: 700;
  line-height: 1;
}

.drawer-score-unit {
  color: var(--ink-faint);
}

.drawer-meta {
  margin-top: 6px;
  color: var(--ink-soft);
  font-size: 13px;
}

.drawer-section {
  margin-top: 20px;
  padding-top: 14px;
  border-top: 1px dashed var(--line);
}

.drawer-section h3 {
  margin-bottom: 10px;
  font-size: 15px;
}

.event-list {
  margin: 0 0 10px;
  padding: 0;
  list-style: none;
}

.event-list li {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 0;
  border-bottom: 1px dashed var(--line);
  font-size: 14px;
}

.event-list li.undone {
  opacity: 0.5;
}

.event-delta {
  min-width: 36px;
  font-size: 18px;
  font-weight: 700;
}

.event-reason {
  flex: 1;
}

.event-undone {
  color: var(--ink-faint);
  font-size: 12px;
}

.drawer-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.edit-form {
  margin-top: 14px;
}
</style>