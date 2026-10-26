<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { api, ApiError } from '../api/client'
import type { SettingsData } from '../api/types'
import { useToastStore } from '../stores/toast'
import { useReducedMotion } from '../composables/useReducedMotion'

const toast = useToastStore()
const { applyPreference } = useReducedMotion()

const settings = ref<SettingsData | null>(null)
const motionPref = ref<'system' | 'reduced'>('system')
const displaySort = ref<'seat' | 'score'>('seat')

const importFile = ref<File | null>(null)
const importConfirm = ref('')
const importing = ref(false)

onMounted(async () => {
  try {
    const data = await api.get<SettingsData>('/api/settings')
    settings.value = data
    motionPref.value = data.motion_pref
    displaySort.value = data.display_sort
  } catch (err) {
    toast.push(err instanceof ApiError ? err.message : '加载设置失败。', 'error')
  }
})

async function saveProfile() {
  try {
    const data = await api.patch<SettingsData>('/api/settings', {
      motion_pref: motionPref.value,
      display_sort: displaySort.value,
    })
    settings.value = data
    applyPreference(data.motion_pref)
    toast.push('设置已保存。', 'success')
  } catch (err) {
    toast.push(err instanceof ApiError ? err.message : '保存失败。', 'error')
  }
}

async function exportData() {
  try {
    const res = await fetch('/api/export')
    if (!res.ok) throw new Error('export failed')
    const blob = await res.blob()
    const disposition = res.headers.get('Content-Disposition') ?? ''
    const match = /filename="([^"]+)"/.exec(disposition)
    const filename = match?.[1] ?? 'petgarden-backup.json'
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
    toast.push('已导出。文件包含学生姓名，请妥善保管。', 'success', 4000)
  } catch {
    toast.push('导出失败，请重试。', 'error')
  }
}

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  importFile.value = input.files?.[0] ?? null
}

async function importData() {
  if (!importFile.value) {
    toast.push('请先选择备份文件。', 'error')
    return
  }
  if (importConfirm.value !== 'REPLACE') {
    toast.push('请输入 REPLACE 确认替换全部数据。', 'error')
    return
  }
  importing.value = true
  try {
    const text = await importFile.value.text()
    const backup = JSON.parse(text) as unknown
    await api.post('/api/import', { confirm: 'REPLACE', backup })
    toast.push('导入完成，即将刷新页面。', 'success')
    window.setTimeout(() => window.location.reload(), 800)
  } catch (err) {
    if (err instanceof SyntaxError) {
      toast.push('文件不是有效的 JSON。', 'error')
    } else {
      toast.push(err instanceof ApiError ? err.message : '导入失败。', 'error')
    }
  } finally {
    importing.value = false
  }
}

</script>

<template>
  <div class="settings-page">
    <h1>设置</h1>

    <section class="card settings-section">
      <h2>偏好</h2>
      <div class="field">
        <label for="motion-pref">动效</label>
        <select id="motion-pref" v-model="motionPref" class="select">
          <option value="system">跟随系统</option>
          <option value="reduced">减少动效</option>
        </select>
      </div>
      <div class="field">
        <label for="display-sort">大屏默认排序</label>
        <select id="display-sort" v-model="displaySort" class="select">
          <option value="seat">按座位</option>
          <option value="score">按积分</option>
        </select>
      </div>
      <button type="button" class="btn btn-primary" @click="saveProfile">保存</button>
    </section>

    <section class="card settings-section">
      <h2>数据</h2>
      <p class="settings-note">数据保存在本机：<code>{{ settings?.data_dir }}</code></p>
      <div class="settings-row">
        <button type="button" class="btn" @click="exportData">导出 JSON 备份</button>
      </div>
      <div class="import-box">
        <p class="settings-note">导入会替换当前全部数据，建议先导出备份。导入前会自动备份当前数据。</p>
        <input type="file" accept="application/json,.json" aria-label="选择备份文件" @change="onFileChange" />
        <div class="field" style="margin-top: 10px">
          <label for="import-confirm">输入 REPLACE 以确认</label>
          <input id="import-confirm" v-model="importConfirm" class="input" autocomplete="off" />
        </div>
        <button type="button" class="btn btn-danger" :disabled="importing" @click="importData">
          导入并替换
        </button>
      </div>
    </section>

    <section class="card settings-section">
      <h2>关于</h2>
      <p class="settings-note">
        PetGarden v{{ settings?.version }}（构建于 {{ settings?.build_time }}）。
        数据仅保存在这台电脑上，不联网、不上传。
      </p>
    </section>
  </div>
</template>

<style scoped>
.settings-page {
  max-width: 640px;
  padding: 28px;
}

.settings-page h1 {
  margin-bottom: 20px;
  font-family: var(--font-display);
  font-size: 30px;
}

.settings-section {
  margin-bottom: 18px;
  padding: 20px;
}

.settings-section h2 {
  margin-bottom: 14px;
  font-size: 17px;
}

.settings-note {
  margin-bottom: 12px;
  color: var(--ink-soft);
  font-size: 13px;
  line-height: 1.7;
}

.settings-note code {
  padding: 1px 6px;
  border-radius: 6px;
  background: var(--surface-sunken);
  font-size: 12px;
}

.settings-row {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}

.import-box {
  padding: 14px;
  border: 1px dashed var(--line);
  border-radius: var(--radius-md);
}
</style>