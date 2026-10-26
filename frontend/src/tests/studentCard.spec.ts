import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import type { Student } from '../api/types'
import StudentCard from '../components/StudentCard.vue'

const student: Student = {
  id: 1,
  class_id: 1,
  name: '林小满',
  student_no: '03',
  seat_no: 3,
  score: 64,
  level: 4,
  stage: '蜕变',
  mood: 'happy',
  score_percent: 64,
  species: 'cat',
  species_name: '小猫',
  best_level: 4,
  can_switch_pet: false,
  divine_unlocked: false,
  is_present: true,
  last_picked_at: null,
  updated_at: '2026-10-25T08:30:00Z',
}

describe('StudentCard', () => {
  it('渲染姓名、积分、阶段徽章', () => {
    const wrapper = mount(StudentCard, { props: { student } })
    expect(wrapper.text()).toContain('林小满')
    expect(wrapper.text()).toContain('64')
    expect(wrapper.text()).toContain('L4 · 蜕变')
  })

  it('点击 +1/-1 触发 score 事件', async () => {
    const wrapper = mount(StudentCard, { props: { student } })
    const buttons = wrapper.findAll('button')
    await buttons[0]?.trigger('click')
    await buttons[1]?.trigger('click')
    const events = wrapper.emitted('score')
    expect(events).toEqual([[-1], [1]])
  })

  it('点击卡片空白处触发 open', async () => {
    const wrapper = mount(StudentCard, { props: { student } })
    await wrapper.find('article').trigger('click')
    expect(wrapper.emitted('open')).toBeTruthy()
  })
})