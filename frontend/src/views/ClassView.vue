<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { api, ApiError } from '../api/client'
import type { BulkPreviewItem, BulkResult, ClassSummary, Student } from '../api/types'
import EmptyState from '../components/EmptyState.vue'
import ReasonSheet from '../components/ReasonSheet.vue'
import RollcallOverlay from '../components/RollcallOverlay.vue'
import StudentCard from '../components/StudentCard.vue'
import StudentDrawer from '../components/StudentDrawer.vue'
import { useCatalogStore } from '../stores/catalog'
import { useRosterStore } from '../stores/roster'
import { useToastStore } from '../stores/toast'
import { useScoring } from '../composables/useScoring'
import { formatDelta } from '../utils/format'
import { LAST_CLASS_KEY, SORT_KEY_PREFIX } from '../utils/constants'

const route = useRoute()
const router = useRouter()
const roster = useRosterStore()
const catalog = useCatalogStore()
const toast = useToastStore()
const scoring = useScoring()

const classId = computed(() => Number(route.params.id))
const classInfo = ref<ClassSummary | null>(null)
const loading = ref(true)
const loadError = ref('')

const search = ref('')
const sort = ref('seat')
const drawerStudentId = ref<number | null>(null)
const drawerOpen = ref(false)
const rollcallOpen = ref(false)
const addOpen = ref(false)
const addTab = ref<'single' | 'bulk'>('single')
const reasonState = ref<{ student: Student; direction: 1 | -1 } | null>(null)

const singleName = ref('')
const singleNo = ref('')
const singleSeat = ref('')
const singleSpecies = ref('')
const bulkText = ref('')
const bulkPreview = ref<BulkResult | null>(null)
const adding = ref(false)

const motionPref = ref<'system' | 'reduced'>('system')

const students = computed(() => roster.studentsOf(classId.value))

let searchTimer: number | undefined

watch([search, sort], () => {
  window.clearTimeout(searchTimer)
  searchTimer = window.setTimeout(() => {
    localStorage.setItem(SORT_KEY_PREFIX + classId.value, sort.value)
    void refresh()
  }, 200)
})

async function refresh() {
  loadError.value = ''
  try {
    await roster.fetchStudents(classId.value, sort.value, search.value)
  } catch (err) {
    loadError.value = err instanceof ApiError ? err.message : '加载失败。'
  }
}

onMounted(async () => {
  loading.value = true
  try {
    const [clsRes] = await Promise.all([
      api.get<{ class: ClassSummary }>(`/api/classes/${classId.value}`),
      catalog.ensure(),
    ])
    classInfo.value = clsRes.class
    localStorage.setItem(LAST_CLASS_KEY, String(classId.value))
    sort.value = localStorage.getItem(SORT_KEY_PREFIX + classId.value) ?? 'seat'
    const settings = await api.get<{ motion_pref: 'system' | 'reduced' }>('/api/settings')
    motionPref.value = settings.motion_pref
    await refresh()
  } catch (err) {
    loadError.value = err instanceof ApiError ? err.message : '加载失败，请重试。'
  } finally {
    loading.value = false
  }
})

function onScore(student: Student, delta: number) {
  void scoring.apply(student, delta)
}

function onReason(student: Student, delta: number) {
  reasonState.value = { student, direction: delta > 0 ? 1 : -1 }
}

async function onReasonPick(reason: string) {
  const state = reasonState.value
  reasonState.value = null
  if (state) await scoring.apply(state.student, state.direction, reason)
}

function openDrawer(student: Student) {
  drawerStudentId.value = student.id
  drawerOpen.value = true
}

function openAdd() {
  addOpen.value = true
  addTab.value = 'single'
  singleName.value = ''
  singleNo.value = ''
  singleSeat.value = ''
  singleSpecies.value = ''
  bulkText.value = ''
  bulkPreview.value = null
}

async function addSingle() {
  if (!singleName.value.trim()) {
    toast.push('请填写姓名。', 'error')
    return
  }
  adding.value = true
  try {
    await api.post(`/api/classes/${classId.value}/students`, {
      name: singleName.value.trim(),
      student_no: singleNo.value.trim() || null,
      seat_no: singleSeat.value === '' ? null : Number(singleSeat.value),
      species: singleSpecies.value || null,
    })
    toast.push('学生已加入。', 'success')
    addOpen.value = false
    await refresh()
  } catch (err) {
    toast.push(err instanceof ApiError ? err.message : '添加失败。', 'error')
  } finally {
    adding.value = false
  }
}

async function previewBulk() {
  if (!bulkText.value.trim()) {
    toast.push('请粘贴学生名单。', 'error')
    return
  }
  adding.value = true
  try {
    bulkPreview.value = await api.post<BulkResult>(
      `/api/classes/${classId.value}/students/bulk`,
      { text: bulkText.value, preview: true },
    )
  } catch (err) {
    toast.push(err instanceof ApiError ? err.message : '解析失败。', 'error')
  } finally {
    adding.value = false
  }
}

async function commitBulk() {
  adding.value = true
  try {
    const res = await api.post<BulkResult>(`/api/classes/${classId.value}/students/bulk`, {
      text: bulkText.value,
      preview: false,
    })
    toast.push(`已新增 ${res.created.length} 名学生。`, 'success')
    addOpen.value = false
    await refresh()
  } catch (err) {
    toast.push(err instanceof ApiError ? err.message : '导入失败。', 'error')
  } finally {
    adding.value = false
  }
}

function previewLineLabel(item: BulkPreviewItem): string {
  return item.text ?? item.name ?? ''
}

const NORMAL_SPECIES = [
  { id: '', label: '随机' },
  { id: 'cat', label: '小猫' },
  { id: 'dog', label: '小狗' },
  { id: 'rabbit', label: '小兔' },
  { id: 'panda', label: '熊猫' },
  { id: 'fox', label: '小狐' },
]
</script>

<template>
  <div class="class-view">
    <header class="workbench-bar">
      <button type="button" class="btn btn-small" @click="router.push('/')">← 返回</button>
      <div class="workbench-title">
        <h1>{{ classInfo?.name ?? '班级' }}</h1>
        <span class="workbench-count">{{ students.length }} 名学生</span>
      </div>
      <input
        v-model="search" class="input workbench-search" type="search"
        placeholder="搜索姓名 / 学号" aria-label="搜索学生"
      />
      <select v-model="sort" class="select workbench-sort" aria-label="排序方式">
        <option value="seat">按座位</option>
        <option value="name">按姓名</option>
        <option value="score">按积分</option>
      </select>
      <button type="button" class="btn btn-small" @click="rollcallOpen = true">随机点名</button>
      <button
        type="button" class="btn btn-small"
        @click="router.push(`/display/${classId}`)"
      >
        大屏展示
      </button>
      <button type="button" class="btn btn-primary btn-small" @click="openAdd">添加学生</button>
    </header>

    <div v-if="loading" class="workbench-grid" aria-hidden="true">
      <div v-for="i in 8" :key="i" class="skeleton-card card" />
    </div>

    <div v-else-if="loadError" class="workbench-error">
      <p>{{ loadError }}</p>
      <button type="button" class="btn btn-primary" @click="refresh">重试</button>
    </div>

    <EmptyState
      v-else-if="students.length === 0 && !search"
      title="这个班级还没有学生"
      hint="先请第一位小伙伴进来吧。"
      action-label="添加学生"
      @action="openAdd"
    />

    <EmptyState
      v-else-if="students.length === 0"
      title="没有找到匹配的学生"
      hint="换个关键词试试。"
    />

    <div v-else class="workbench-grid">
      <StudentCard
        v-for="s in students"
        :key="s.id"
        :student="s"
        :reaction="roster.reactions[s.id] ?? null"
        :disabled="scoring.isPending(s.id)"
        @score="(delta) => onScore(s, delta)"
        @reason="(delta) => onReason(s, delta)"
        @open="openDrawer(s)"
      />
    </div>

    <Transition name="snackbar">
      <div v-if="scoring.lastAction.value" class="undo-bar" role="status">
        <span>
          {{ scoring.lastAction.value.studentName }}
          {{ formatDelta(scoring.lastAction.value.delta) }}
        </span>
        <button type="button" class="btn btn-small" @click="scoring.undo()">撤销</button>
      </div>
    </Transition>

    <Teleport to="body">
      <div v-if="addOpen" class="dialog-mask" @click.self="addOpen = false">
        <div class="dialog" role="dialog" aria-modal="true" aria-label="添加学生">
          <h2>添加学生</h2>
          <div class="add-tabs">
            <button
              type="button" class="add-tab" :class="{ active: addTab === 'single' }"
              @click="addTab = 'single'"
            >
              单个添加
            </button>
            <button
              type="button" class="add-tab" :class="{ active: addTab === 'bulk' }"
              @click="addTab = 'bulk'"
            >
              批量导入
            </button>
          </div>

          <template v-if="addTab === 'single'">
            <div class="field">
              <label for="stu-name">姓名</label>
              <input id="stu-name" v-model="singleName" class="input" maxlength="20" />
            </div>
            <div class="field">
              <label for="stu-no">学号（可选）</label>
              <input id="stu-no" v-model="singleNo" class="input" maxlength="20" />
            </div>
            <div class="field">
              <label for="stu-seat">座位号（可选）</label>
              <input id="stu-seat" v-model="singleSeat" class="input" type="number" min="1" max="99" />
            </div>
            <div class="field">
              <label for="stu-species">宠物（可选）</label>
              <select id="stu-species" v-model="singleSpecies" class="select">
                <option v-for="sp in NORMAL_SPECIES" :key="sp.id" :value="sp.id">
                  {{ sp.label }}
                </option>
              </select>
            </div>
            <div class="dialog-actions">
              <button type="button" class="btn" @click="addOpen = false">取消</button>
              <button type="button" class="btn btn-primary" :disabled="adding" @click="addSingle">
                添加
              </button>
            </div>
          </template>

          <template v-else>
            <div class="field">
              <label for="bulk-text">每行一个学生：姓名、姓名,学号 或 姓名[TAB]学号[TAB]座位号</label>
              <textarea
                id="bulk-text" v-model="bulkText" class="textarea"
                placeholder="林小满,03&#10;陈一诺,04&#10;王梓涵	05	5"
              />
            </div>
            <div v-if="bulkPreview" class="bulk-preview">
              <p>将新增 {{ bulkPreview.created.length }} 人，跳过 {{ bulkPreview.skipped.length }} 行，错误 {{ bulkPreview.errors.length }} 行。</p>
              <ul v-if="bulkPreview.skipped.length">
                <li v-for="item in bulkPreview.skipped" :key="'s' + item.line">
                  第 {{ item.line }} 行跳过（{{ item.reason }}）：{{ previewLineLabel(item) }}
                </li>
              </ul>
              <ul v-if="bulkPreview.errors.length" class="bulk-errors">
                <li v-for="item in bulkPreview.errors" :key="'e' + item.line">
                  第 {{ item.line }} 行错误（{{ item.reason }}）：{{ previewLineLabel(item) }}
                </li>
              </ul>
            </div>
            <div class="dialog-actions">
              <button type="button" class="btn" @click="addOpen = false">取消</button>
              <button v-if="!bulkPreview" type="button" class="btn" :disabled="adding" @click="previewBulk">
                预览
              </button>
              <button
                v-else type="button" class="btn btn-primary"
                :disabled="adding || bulkPreview.created.length === 0"
                @click="commitBulk"
              >
                确认导入 {{ bulkPreview.created.length }} 人
              </button>
            </div>
          </template>
        </div>
      </div>
    </Teleport>

    <ReasonSheet
      :open="reasonState !== null"
      :direction="reasonState?.direction ?? 1"
      :student-name="reasonState?.student.name ?? ''"
      @pick="onReasonPick"
      @cancel="reasonState = null"
    />

    <StudentDrawer
      :open="drawerOpen"
      :student-id="drawerStudentId"
      @close="drawerOpen = false"
      @deleted="refresh"
      @updated="refresh"
    />

    <RollcallOverlay
      :open="rollcallOpen"
      :class-id="classId"
      :class-name="classInfo?.name ?? ''"
      :motion-pref="motionPref"
      @close="rollcallOpen = false"
    />
  </div>
</template>

<style scoped>
.class-view {
  padding: 20px 24px 40px;
}

.workbench-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  margin-bottom: 18px;
}

.workbench-title {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-right: auto;
}

.workbench-title h1 {
  font-family: var(--font-display);
  font-size: 24px;
}

.workbench-count {
  color: var(--ink-faint);
  font-size: 13px;
}

.workbench-search {
  width: 200px;
}

.workbench-sort {
  width: 110px;
}

.workbench-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(168px, 1fr));
  gap: 14px;
}

.skeleton-card {
  height: 280px;
  background: var(--surface-sunken);
  animation: skeleton 1.2s ease-in-out infinite;
}

@keyframes skeleton {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.55; }
}

@media (prefers-reduced-motion: reduce) {
  .skeleton-card { animation: none; }
}

:root[data-motion='reduced'] .skeleton-card {
  animation: none;
}

.workbench-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 60px 0;
  color: var(--ink-soft);
}

.undo-bar {
  position: fixed;
  bottom: 24px;
  left: 50%;
  z-index: 70;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 10px 10px 10px 18px;
  border: 1px solid var(--line);
  border-radius: var(--radius-pill);
  background: var(--ink);
  color: var(--paper);
  transform: translateX(-50%);
  box-shadow: var(--shadow-pop);
}

.undo-bar .btn {
  min-height: 32px;
}

.snackbar-enter-active,
.snackbar-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.snackbar-enter-from,
.snackbar-leave-to {
  opacity: 0;
  transform: translate(-50%, 8px);
}

.add-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 16px;
  padding: 4px;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: var(--surface-sunken);
}

.add-tab {
  flex: 1;
  min-height: 36px;
  border: 0;
  border-radius: 8px;
  background: transparent;
  color: var(--ink-soft);
  font-weight: 600;
}

.add-tab.active {
  background: var(--surface);
  color: var(--moss-deep);
}

.bulk-preview {
  max-height: 180px;
  overflow-y: auto;
  padding: 10px 12px;
  border: 1px dashed var(--line);
  border-radius: var(--radius-sm);
  font-size: 13px;
}

.bulk-preview ul {
  margin: 6px 0 0;
  padding-left: 18px;
}

.bulk-errors li {
  color: var(--danger);
}

@media (max-width: 599px) {
  .workbench-search {
    width: 100%;
  }
}
</style>