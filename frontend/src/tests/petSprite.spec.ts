import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import PetSprite from '../components/pets/PetSprite.vue'
import type { PetLevel, PetMood, SpeciesId } from '../components/pets/types'
import { SPECIES_VISUALS } from '../components/pets/visuals'

const SPECIES: SpeciesId[] = ['cat', 'dog', 'rabbit', 'panda', 'fox', 'dragon']
const LEVELS: PetLevel[] = [1, 2, 3, 4, 5]
const MOODS: PetMood[] = ['happy', 'neutral', 'sad']

describe('PetSprite', () => {
  it('6 物种 × 5 等级 × 3 心情都能渲染 <svg>，且不含 <img>', () => {
    for (const species of SPECIES) {
      for (const level of LEVELS) {
        for (const mood of MOODS) {
          const wrapper = mount(PetSprite, {
            props: { species, level, mood, seed: 1 },
          })
          const svg = wrapper.find('svg')
          expect(svg.exists(), `${species} L${level} ${mood}`).toBe(true)
          expect(wrapper.find('img').exists()).toBe(false)
          expect(wrapper.html()).not.toContain('<img')
          expect(wrapper.html()).not.toContain('<image')
          wrapper.unmount()
        }
      }
    }
  })

  it('decorative=true 时 aria-hidden，否则 role=img 带标签', () => {
    const deco = mount(PetSprite, {
      props: { species: 'cat', level: 1, mood: 'happy', seed: 1, decorative: true },
    })
    expect(deco.find('svg').attributes('aria-hidden')).toBe('true')

    const named = mount(PetSprite, {
      props: { species: 'cat', level: 3, mood: 'happy', seed: 1 },
    })
    const svg = named.find('svg')
    expect(svg.attributes('role')).toBe('img')
    expect(svg.attributes('aria-label')).toContain('小猫')
    expect(svg.attributes('aria-label')).toContain('3')
  })

  it('L4/L5 渲染光环，L5 渲染粒子与皇冠', () => {
    const l3 = mount(PetSprite, { props: { species: 'fox', level: 3, mood: 'neutral', seed: 1 } })
    expect(l3.find('.pet-aura').exists()).toBe(false)
    const l5 = mount(PetSprite, { props: { species: 'fox', level: 5, mood: 'happy', seed: 1 } })
    expect(l5.find('.pet-aura').exists()).toBe(true)
    expect(l5.findAll('.pet-particle').length).toBe(8)
  })

  it('reaction nonce 变化时添加反应类', async () => {
    const wrapper = mount(PetSprite, {
      props: { species: 'cat', level: 1, mood: 'neutral', seed: 1 },
    })
    await wrapper.setProps({ reaction: { type: 'cheer', nonce: 1 } })
    expect(wrapper.find('.reaction-cheer').exists()).toBe(true)
  })

  it('相位抖动变量写入根节点样式', () => {
    const wrapper = mount(PetSprite, { props: { species: 'cat', level: 1, mood: 'neutral', seed: 42 } })
    const style = wrapper.find('.pet-root').attributes('style') ?? ''
    expect(style).toContain('--blink-duration')
    expect(style).toContain('--sway-delay')
  })

  it('物种配色来自 visuals', () => {
    for (const species of SPECIES) {
      expect(SPECIES_VISUALS[species].body).toMatch(/^#/)
      expect(SPECIES_VISUALS[species].name).toBeTruthy()
    }
  })
})