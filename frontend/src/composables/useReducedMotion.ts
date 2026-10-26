import { onBeforeUnmount, onMounted, ref } from 'vue'

/** 监听系统 prefers-reduced-motion，并同步应用内 data-motion 属性。 */
export function useReducedMotion() {
  const media = window.matchMedia('(prefers-reduced-motion: reduce)')
  const systemReduced = ref(media.matches)

  function onChange(e: MediaQueryListEvent) {
    systemReduced.value = e.matches
  }

  onMounted(() => media.addEventListener('change', onChange))
  onBeforeUnmount(() => media.removeEventListener('change', onChange))

  function applyPreference(pref: 'system' | 'reduced') {
    const reduced = pref === 'reduced' || (pref === 'system' && media.matches)
    document.documentElement.dataset.motion = reduced ? 'reduced' : 'normal'
    return reduced
  }

  function isReduced(pref: 'system' | 'reduced'): boolean {
    return pref === 'reduced' || (pref === 'system' && systemReduced.value)
  }

  return { systemReduced, applyPreference, isReduced }
}