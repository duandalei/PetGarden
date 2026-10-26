import type { CSSProperties } from 'vue'

import { SPECIES_VISUALS } from './visuals'
import type { PetMood, SpeciesId } from './types'

export function hash(seed: number | string): number {
  const s = String(seed)
  let h = 2166136261
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i)
    h = Math.imul(h, 16777619)
  }
  return Math.abs(h)
}

/** 由 seed 生成动画相位抖动的 CSS 变量，保证全班宠物不同步。 */
export function usePetMotionStyle(
  seed: number | string,
  species: SpeciesId,
  mood: PetMood,
): CSSProperties {
  const h = hash(seed)
  const visual = SPECIES_VISUALS[species]
  const swayBase = mood === 'happy' ? 1.5 : mood === 'sad' ? 4.2 : 2.7
  return {
    '--blink-duration': `${(4 + (h % 30) / 10).toFixed(1)}s`,
    '--blink-delay': `${(-(h % 50) / 10).toFixed(1)}s`,
    '--sway-duration': `${(swayBase + (h % 9) / 10).toFixed(1)}s`,
    '--sway-delay': `${(-(h % 20) / 10).toFixed(1)}s`,
    '--ear-delay': `${(-(h % 30) / 10).toFixed(1)}s`,
    '--bob-delay': `${(-(h % 28) / 10).toFixed(1)}s`,
    '--tail-x': `${visual.tailX}px`,
    '--tail-y': `${visual.tailY}px`,
    '--pet-body': visual.body,
    '--pet-belly': visual.belly,
    '--pet-accent': visual.accent,
    '--pet-inner': visual.inner,
    '--pet-ink': visual.ink,
  } as CSSProperties
}