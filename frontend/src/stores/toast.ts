import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface ToastItem {
  id: number
  message: string
  kind: 'info' | 'success' | 'error'
}

let nextId = 0

export const useToastStore = defineStore('toast', () => {
  const toasts = ref<ToastItem[]>([])

  function push(message: string, kind: ToastItem['kind'] = 'info', duration = 3000) {
    nextId += 1
    const id = nextId
    toasts.value.push({ id, message, kind })
    if (toasts.value.length > 3) toasts.value.shift()
    window.setTimeout(() => {
      toasts.value = toasts.value.filter((t) => t.id !== id)
    }, duration)
  }

  return { toasts, push }
})