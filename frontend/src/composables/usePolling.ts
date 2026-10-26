import { onBeforeUnmount, onMounted, ref } from 'vue'

/** 定时轮询：页面隐藏时暂停、恢复立即拉取、失败退避（3s→5s→10s）。 */
export function usePolling(
  task: () => Promise<void>,
  intervalMs = 3000,
) {
  const failed = ref(false)
  let timer: number | undefined
  let running = false
  let currentInterval = intervalMs

  async function tick() {
    if (running) return
    running = true
    try {
      await task()
      failed.value = false
      currentInterval = intervalMs
    } catch {
      failed.value = true
      currentInterval = currentInterval >= 10000 ? 10000 : currentInterval + 2000
    } finally {
      running = false
    }
    schedule()
  }

  function schedule() {
    window.clearTimeout(timer)
    timer = window.setTimeout(tick, currentInterval)
  }

  function onVisibility() {
    if (document.hidden) {
      window.clearTimeout(timer)
    } else {
      void tick()
    }
  }

  onMounted(() => {
    void tick()
    document.addEventListener('visibilitychange', onVisibility)
  })

  onBeforeUnmount(() => {
    window.clearTimeout(timer)
    document.removeEventListener('visibilitychange', onVisibility)
  })

  return { failed }
}