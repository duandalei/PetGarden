import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { api } from '../api/client'
import type { PetReaction } from '../components/pets/types'
import type { ScoreResponse, Student } from '../api/types'

export const useRosterStore = defineStore('roster', () => {
  const studentsByClass = ref<Record<number, Student[]>>({})
  const reactions = ref<Record<number, PetReaction>>({})
  let nonce = 0

  const byId = computed(() => {
    const map: Record<number, Student> = {}
    for (const list of Object.values(studentsByClass.value)) {
      for (const s of list) map[s.id] = s
    }
    return map
  })

  async function fetchStudents(classId: number, sort = 'seat', q = '') {
    const params = new URLSearchParams({ sort })
    if (q) params.set('q', q)
    const data = await api.get<{ students: Student[] }>(
      `/api/classes/${classId}/students?${params.toString()}`,
    )
    studentsByClass.value[classId] = data.students
    return data.students
  }

  function studentsOf(classId: number): Student[] {
    return studentsByClass.value[classId] ?? []
  }

  function replaceStudent(student: Student) {
    const list = studentsByClass.value[student.class_id]
    if (!list) return
    const idx = list.findIndex((s) => s.id === student.id)
    if (idx >= 0) list[idx] = student
    else list.push(student)
  }

  function removeStudent(classId: number, studentId: number) {
    const list = studentsByClass.value[classId]
    if (list) {
      studentsByClass.value[classId] = list.filter((s) => s.id !== studentId)
    }
  }

  function patchLocal(studentId: number, patch: Partial<Student>) {
    const s = byId.value[studentId]
    if (!s) return
    Object.assign(s, patch)
  }

  function setReaction(studentId: number, type: PetReaction['type']) {
    nonce += 1
    reactions.value[studentId] = { type, nonce }
  }

  function applyScoreResponse(res: ScoreResponse) {
    replaceStudent(res.student)
    if (res.level_up) setReaction(res.student.id, 'evolve')
    else if (res.event.delta > 0) setReaction(res.student.id, 'cheer')
    else setReaction(res.student.id, 'comfort')
  }

  return {
    studentsByClass,
    reactions,
    byId,
    fetchStudents,
    studentsOf,
    replaceStudent,
    removeStudent,
    patchLocal,
    setReaction,
    applyScoreResponse,
  }
})