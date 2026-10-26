import { defineStore } from 'pinia'
import { ref } from 'vue'

import { api } from '../api/client'
import type { ClassSummary } from '../api/types'

export const useClassesStore = defineStore('classes', () => {
  const classes = ref<ClassSummary[]>([])
  const loaded = ref(false)

  async function fetchAll() {
    const data = await api.get<{ classes: ClassSummary[] }>('/api/classes')
    classes.value = data.classes
    loaded.value = true
  }

  async function create(name: string, grade: string | null, color: string) {
    const data = await api.post<{ class: ClassSummary }>('/api/classes', { name, grade, color })
    classes.value.push(data.class)
    return data.class
  }

  async function update(id: number, patch: Partial<Pick<ClassSummary, 'name' | 'grade' | 'color'>>) {
    const data = await api.patch<{ class: ClassSummary }>(`/api/classes/${id}`, patch)
    const idx = classes.value.findIndex((c) => c.id === id)
    if (idx >= 0) classes.value[idx] = data.class
    return data.class
  }

  async function remove(id: number, confirmName: string) {
    await api.delete(`/api/classes/${id}`, { confirm_name: confirmName })
    classes.value = classes.value.filter((c) => c.id !== id)
  }

  function upsertLocal(cls: ClassSummary) {
    const idx = classes.value.findIndex((c) => c.id === cls.id)
    if (idx >= 0) classes.value[idx] = cls
    else classes.value.push(cls)
  }

  return { classes, loaded, fetchAll, create, update, remove, upsertLocal }
})