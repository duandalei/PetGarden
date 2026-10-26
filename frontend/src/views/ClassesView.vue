<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { ApiError } from '../api/client'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import EmptyState from '../components/EmptyState.vue'
import PetSprite from '../components/pets/PetSprite.vue'
import type { SpeciesId } from '../components/pets/types'
import { useClassesStore } from '../stores/classes'
import { useToastStore } from '../stores/toast'
import { classColorHex, CLASS_COLORS, LAST_CLASS_KEY } from '../utils/constants'
import { formatAverage } from '../utils/format'

const classesStore = useClassesStore()
const toast = useToastStore()
const router = useRouter()

const lastClassId = ref<number | null>(null)

const dialogOpen = ref(false)
const editingId = ref<number | null>(null)
const formName = ref('')
const formGrade = ref('')
const formColor = ref('moss')
const saving = ref(false)

const deleteTarget = ref<number | null>(null)

const isEmpty = computed(() => classesStore.loaded && classesStore.classes.length === 0)

onMounted(async () => {
  lastClassId.value = Number(localStorage.getItem(LAST_CLASS_KEY)) || null
  try {
    await classesStore.fetchAll()
  } catch (err) {
    toast.push(err instanceof ApiError ? err.message : '加载班级失败。', 'error')
  }
})

function openCreate() {
  editingId.value = null
  formName.value = ''
  formGrade.value = ''
  formColor.value = 'moss'
  dialogOpen.value = true
}

function openEdit(id: number) {
  const cls = classesStore.classes.find((c) => c.id === id)
  if (!cls) return
  editingId.value = id
  formName.value = cls.name
  formGrade.value = cls.grade ?? ''
  formColor.value = cls.color
  dialogOpen.value = true
}

async function save() {
  if (!formName.value.trim()) {
    toast.push('请填写班级名称。', 'error')
    return
  }
  saving.value = true
  try {
    if (editingId.value === null) {
      await classesStore.create(formName.value.trim(), formGrade.value.trim() || null, formColor.value)
      toast.push('班级已创建。', 'success')
    } else {
      await classesStore.update(editingId.value, {
        name: formName.value.trim(),
        grade: formGrade.value.trim() || null,
        color: formColor.value,
      })
      toast.push('已保存。', 'success')
    }
    dialogOpen.value = false
  } catch (err) {
    toast.push(err instanceof ApiError ? err.message : '保存失败。', 'error')
  } finally {
    saving.value = false
  }
}

async function doDelete() {
  if (deleteTarget.value === null) return
  const cls = classesStore.classes.find((c) => c.id === deleteTarget.value)
  if (!cls) return
  try {
    await classesStore.remove(cls.id, cls.name)
    toast.push('班级已删除。', 'success')
    deleteTarget.value = null
  } catch (err) {
    toast.push(err instanceof ApiError ? err.message : '删除失败。', 'error')
  }
}

function enterClass(id: number) {
  localStorage.setItem(LAST_CLASS_KEY, String(id))
  void router.push(`/class/${id}`)
}
</script>

<template>
  <div class="classes-page">
    <header class="classes-head">
      <h1>我的班级</h1>
      <button type="button" class="btn btn-primary" @click="openCreate">新建班级</button>
    </header>

    <EmptyState
      v-if="isEmpty"
      title="这个花园还没有班级"
      hint="创建第一个班级，把学生请进来，他们的宠物就会开始成长。"
      action-label="创建第一个班级"
      @action="openCreate"
    />

    <div v-else class="classes-grid">
      <article
        v-for="cls in classesStore.classes"
        :key="cls.id"
        class="class-card card"
        :class="{ last: cls.id === lastClassId }"
        :style="{ borderTopColor: classColorHex(cls.color) }"
        tabindex="0"
        @click="enterClass(cls.id)"
        @keydown.enter="enterClass(cls.id)"
      >
        <div class="class-card-head">
          <h2>{{ cls.name }}</h2>
          <span v-if="cls.id === lastClassId" class="badge">上次使用</span>
        </div>
        <p class="class-grade">{{ cls.grade || '未设置年级' }}</p>
        <div class="class-stats">
          <span>{{ cls.student_count }} 名学生</span>
          <span>平均分 {{ formatAverage(cls.average_score) }}</span>
        </div>
        <div class="class-previews" aria-hidden="true">
          <PetSprite
            v-for="sp in cls.preview_species"
            :key="sp"
            :species="sp as SpeciesId"
            :level="2"
            mood="neutral"
            :seed="`${cls.id}-${sp}`"
            :size="40"
            decorative
          />
        </div>
        <div class="class-actions" @click.stop>
          <button type="button" class="btn btn-small" @click="openEdit(cls.id)">编辑</button>
          <button
            type="button" class="btn btn-small btn-danger"
            @click="deleteTarget = cls.id"
          >
            删除
          </button>
        </div>
      </article>
    </div>

    <Teleport to="body">
      <div v-if="dialogOpen" class="dialog-mask" @click.self="dialogOpen = false">
        <div class="dialog" role="dialog" aria-modal="true" :aria-label="editingId ? '编辑班级' : '新建班级'">
          <h2>{{ editingId ? '编辑班级' : '新建班级' }}</h2>
          <div class="field">
            <label for="class-name">班级名称</label>
            <input id="class-name" v-model="formName" class="input" maxlength="30" />
          </div>
          <div class="field">
            <label for="class-grade">年级（可选）</label>
            <input id="class-grade" v-model="formGrade" class="input" maxlength="30" placeholder="例如：三年级" />
          </div>
          <div class="field">
            <label>班级颜色</label>
            <div class="color-row">
              <button
                v-for="c in CLASS_COLORS"
                :key="c.id"
                type="button"
                class="color-chip"
                :class="{ active: formColor === c.id }"
                :style="{ background: c.hex }"
                :aria-label="c.label"
                @click="formColor = c.id"
              />
            </div>
          </div>
          <div class="dialog-actions">
            <button type="button" class="btn" @click="dialogOpen = false">取消</button>
            <button type="button" class="btn btn-primary" :disabled="saving" @click="save">
              保存
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <ConfirmDialog
      :open="deleteTarget !== null"
      title="删除班级"
      message="删除班级会一并删除所有学生、积分事件和图鉴进度，此操作不可恢复。建议先在设置页导出备份。"
      confirm-label="确认删除"
      danger
      :require-text="classesStore.classes.find((c) => c.id === deleteTarget)?.name"
      @confirm="doDelete"
      @cancel="deleteTarget = null"
    />
  </div>
</template>

<style scoped>
.classes-page {
  padding: 28px;
}

.classes-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 22px;
}

.classes-head h1 {
  font-family: var(--font-display);
  font-size: 30px;
}

.classes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}

.class-card {
  position: relative;
  padding: 18px;
  border-top: 4px solid var(--moss);
  cursor: pointer;
  transition: transform 0.16s ease, box-shadow 0.16s ease;
}

.class-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-pop);
}

.class-card.last {
  outline: 2px solid var(--moss);
  outline-offset: 1px;
}

.class-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.class-card-head h2 {
  font-family: var(--font-display);
  font-size: 21px;
}

.class-grade {
  margin-top: 2px;
  color: var(--ink-faint);
  font-size: 13px;
}

.class-stats {
  display: flex;
  gap: 14px;
  margin-top: 10px;
  color: var(--ink-soft);
  font-size: 14px;
}

.class-previews {
  display: flex;
  gap: 4px;
  margin-top: 10px;
  min-height: 44px;
}

.class-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.color-row {
  display: flex;
  gap: 8px;
}

.color-chip {
  width: 36px;
  height: 36px;
  border: 2px solid transparent;
  border-radius: 50%;
  cursor: pointer;
}

.color-chip.active {
  border-color: var(--ink);
}
</style>