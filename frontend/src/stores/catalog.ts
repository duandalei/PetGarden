import { defineStore } from 'pinia'
import { ref } from 'vue'

import { api } from '../api/client'
import type { PetCatalog } from '../api/types'

export const useCatalogStore = defineStore('catalog', () => {
  const catalog = ref<PetCatalog | null>(null)

  async function ensure(): Promise<PetCatalog> {
    if (!catalog.value) {
      catalog.value = await api.get<PetCatalog>('/api/pets')
    }
    return catalog.value
  }

  function levelFromScore(score: number): number {
    const thresholds = catalog.value?.level_thresholds ?? [0, 20, 40, 60, 80]
    let level = 1
    for (let i = 0; i < thresholds.length; i++) {
      if (score >= (thresholds[i] ?? 0)) level = i + 1
    }
    return Math.min(5, level)
  }

  function moodFromScore(score: number): 'happy' | 'neutral' | 'sad' {
    const thresholds = catalog.value?.level_thresholds ?? [0, 20, 40, 60, 80]
    const t1 = thresholds[1] ?? 20
    const t3 = thresholds[3] ?? 60
    if (score >= t3) return 'happy'
    if (score >= t1) return 'neutral'
    return 'sad'
  }

  return { catalog, ensure, levelFromScore, moodFromScore }
})