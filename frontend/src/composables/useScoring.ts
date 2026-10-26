import { onBeforeUnmount, ref } from 'vue'

import { api, ApiError } from '../api/client'
import type { ScoreResponse, Student } from '../api/types'

import { useCatalogStore } from '../stores/catalog'
import { useRosterStore } from '../stores/roster'
import { useToastStore } from '../stores/toast'

export interface LastAction {
  studentId: number
  studentName: string
  delta: number
  eventId: number
}

/** 评分乐观更新 / 回滚 / 最近一次撤销。 */
export function useScoring() {
  const roster = useRosterStore()
  const catalog = useCatalogStore()
  const toast = useToastStore()


  const pending = ref<Set<number>>(new Set())
  const lastAction = ref<LastAction | null>(null)
  let dismissTimer: number | undefined

  function isPending(studentId: number): boolean {
    return pending.value.has(studentId)
  }

  function scheduleDismiss() {
    window.clearTimeout(dismissTimer)
    dismissTimer = window.setTimeout(() => {
      lastAction.value = null
    }, 6000)
  }

  onBeforeUnmount(() => window.clearTimeout(dismissTimer))

  async function apply(student: Student, delta: number, reason?: string): Promise<boolean> {
    if (pending.value.has(student.id)) return false
    pending.value.add(student.id)
    window.setTimeout(() => pending.value.delete(student.id), 200)

    const snapshot = { ...student }
    const clamped = Math.max(0, Math.min(100, student.score + delta))
    if (clamped === student.score) {
      toast.push(
        delta > 0 ? '已经满 100 分啦，可以准备换一位新伙伴了。' : '现在是 0 分，先给一个鼓励吧。',
        'info',
      )
      return false
    }
    // 乐观更新（展示用派生值来自服务端 catalog 阈值配置）
    roster.patchLocal(student.id, {
      score: clamped,
      score_percent: clamped,
      level: catalog.levelFromScore(clamped),
      mood: catalog.moodFromScore(clamped),
    })
    roster.setReaction(student.id, delta > 0 ? 'cheer' : 'comfort')

    try {
      const res = await api.post<ScoreResponse>(`/api/students/${student.id}/score`, {
        delta,
        reason: reason ?? null,
      })
      roster.applyScoreResponse(res)
      lastAction.value = {
        studentId: student.id,
        studentName: res.student.name,
        delta,
        eventId: res.event.id,
      }
      scheduleDismiss()
      return true
    } catch (err) {
      roster.patchLocal(student.id, snapshot)
      if (err instanceof ApiError) {

        toast.push(err.message, 'error', 4000)
      } else {
        toast.push('操作失败，请重试。', 'error', 4000)
      }
      return false
    }
  }

  async function undo(): Promise<boolean> {
    const action = lastAction.value
    if (!action) return false
    try {
      const res = await api.post<{ student: Student }>(
        `/api/score-events/${action.eventId}/undo`,
      )
      roster.replaceStudent(res.student)
      toast.push(`已撤销：${action.studentName} ${action.delta > 0 ? '+1' : '-1'}`, 'success')
      lastAction.value = null
      return true
    } catch (err) {
      if (err instanceof ApiError) toast.push(err.message, 'error', 4000)
      lastAction.value = null
      return false
    }
  }

  return { pending, isPending, lastAction, apply, undo }
}