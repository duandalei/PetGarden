
export interface ClassSummary {
  id: number
  name: string
  grade: string | null
  color: string
  sort_order: number
  student_count: number
  average_score: number
  preview_species: string[]
  created_at: string
  updated_at: string
}

export interface Student {
  id: number
  class_id: number
  name: string
  student_no: string | null
  seat_no: number | null
  score: number
  level: number
  stage: string
  mood: 'happy' | 'neutral' | 'sad'
  score_percent: number
  species: 'cat' | 'dog' | 'rabbit' | 'panda' | 'fox' | 'dragon'
  species_name: string
  best_level: number
  can_switch_pet: boolean
  divine_unlocked: boolean
  is_present: boolean
  last_picked_at: string | null
  updated_at: string
}

export interface ScoreEvent {
  id: number
  class_id: number
  student_id: number
  delta: number
  score_before: number
  score_after: number
  reason: string | null
  created_at: string
  undone_at: string | null
}

export interface ScoreResponse {
  student: Student
  event: ScoreEvent
  level_up: boolean
  stage_changed: boolean
  can_undo: boolean
}

export interface PetSpeciesInfo {
  id: string
  name: string
  type: 'normal' | 'divine'
}

export interface PetCatalog {
  level_thresholds: number[]
  stage_names: string[]
  species: PetSpeciesInfo[]
}

export interface CollectionItem {
  species: 'cat' | 'dog' | 'rabbit' | 'panda' | 'fox' | 'dragon'
  name: string
  type: 'normal' | 'divine'
  best_level: number
  is_current: boolean
  unlocked: boolean
}

export interface Collection {
  student_id: number
  current_species: string
  can_switch_pet: boolean
  divine_unlocked: boolean
  items: CollectionItem[]
}

export interface SwitchPetResponse {
  student: Student
  previous_species: string
  previous_species_name: string
  previous_best_level: number
  graduated: boolean
  message: string
}

export interface RollcallResponse {
  student: Student
  pool_size: number
  mode: string
}

export interface DisplayData {
  class: ClassSummary
  students: Student[]
  server_time: string
}

export interface SettingsData {

  motion_pref: 'system' | 'reduced'
  display_sort: 'seat' | 'score'
  version: string
  build_time: string
  data_dir: string
}

export interface BulkPreviewItem {
  line: number
  reason?: string
  text?: string
  name?: string
  student_no?: string | null
  seat_no?: number | null
}

export interface BulkResult {
  preview: boolean
  created: Array<Student | BulkPreviewItem>
  skipped: BulkPreviewItem[]
  errors: BulkPreviewItem[]
}

export interface StudentDetail {
  student: Student
  recent_events: ScoreEvent[]
}