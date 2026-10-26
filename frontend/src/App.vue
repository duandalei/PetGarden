<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

import { api } from './api/client'
import AppShell from './components/AppShell.vue'
import ToastHost from './components/ToastHost.vue'
import { useReducedMotion } from './composables/useReducedMotion'

const route = useRoute()
const { applyPreference, systemReduced } = useReducedMotion()

const bare = computed(() => route.meta.bare === true)

onMounted(async () => {
  try {
    const settings = await api.get<{ motion_pref: 'system' | 'reduced' }>('/api/settings')
    applyPreference(settings.motion_pref)
    return
  } catch {
    // 忽略，退回系统偏好
  }
  document.documentElement.dataset.motion = systemReduced.value ? 'reduced' : 'normal'
})
</script>

<template>
  <AppShell v-if="!bare">
    <RouterView />
  </AppShell>
  <RouterView v-else />
  <ToastHost />
</template>
