import { describe, expect, it } from 'vitest'

import { hash, usePetMotionStyle } from '../components/pets/usePetMotion'

describe('hash', () => {
  it('对同一 seed 稳定', () => {
    expect(hash(1)).toBe(hash(1))
    expect(hash('abc')).toBe(hash('abc'))
  })

  it('不同 seed 产生不同抖动', () => {
    const a = hash(1)
    const b = hash(2)
    expect(a).not.toBe(b)
  })
})

describe('usePetMotionStyle', () => {
  it('生成眨眼/摇尾 CSS 变量', () => {
    const style = usePetMotionStyle(1, 'cat', 'neutral') as Record<string, string>
    expect(style['--blink-duration']).toMatch(/^\d+(\.\d)?s$/)
    expect(style['--sway-duration']).toMatch(/^\d+(\.\d)?s$/)
    expect(style['--pet-accent']).toBe('#D98A4F')
  })

  it('心情影响摇尾速度', () => {
    const happy = usePetMotionStyle(1, 'cat', 'happy') as Record<string, string>
    const sad = usePetMotionStyle(1, 'cat', 'sad') as Record<string, string>
    const parse = (s: string) => parseFloat(s)
    expect(parse(happy['--sway-duration'])).toBeLessThan(parse(sad['--sway-duration']))
  })
})