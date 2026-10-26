import type { SpeciesId } from './types'

export interface SpeciesVisual {
  id: SpeciesId
  name: string
  body: string
  belly: string
  accent: string
  inner: string
  ink: string
  tailX: number
  tailY: number
}

export const SPECIES_VISUALS: Record<SpeciesId, SpeciesVisual> = {
  cat: {
    id: 'cat', name: '小猫',
    body: '#F4D6B4', belly: '#FFF2DF', accent: '#D98A4F', inner: '#F2B39A', ink: '#252A26',
    tailX: 140, tailY: 150,
  },
  dog: {
    id: 'dog', name: '小狗',
    body: '#E7BC8C', belly: '#FFF3E2', accent: '#A56A3D', inner: '#C98C61', ink: '#252A26',
    tailX: 140, tailY: 148,
  },
  rabbit: {
    id: 'rabbit', name: '小兔',
    body: '#F6E7E8', belly: '#FFFAFA', accent: '#D88FA4', inner: '#F2BCCB', ink: '#4A3438',
    tailX: 146, tailY: 160,
  },
  panda: {
    id: 'panda', name: '熊猫',
    body: '#F5F1E7', belly: '#FFFFFF', accent: '#3B413C', inner: '#D9D4C9', ink: '#2B302C',
    tailX: 146, tailY: 160,
  },
  fox: {
    id: 'fox', name: '小狐',
    body: '#E79A5C', belly: '#FFF3DF', accent: '#B85C3E', inner: '#F6D3B6', ink: '#3B2A22',
    tailX: 138, tailY: 150,
  },
  dragon: {
    id: 'dragon', name: '青龙',
    body: '#7EC2B8', belly: '#DDF4EE', accent: '#2E6E68', inner: '#A9DCD4', ink: '#1F3A37',
    tailX: 138, tailY: 156,
  },
}

export const LEVEL_SCALES: readonly number[] = [0.88, 0.94, 1.0, 1.05, 1.12]

export const MOOD_WORDS: Record<string, string> = {
  happy: '开心',
  neutral: '平静',
  sad: '有点低落',
}