export const CLASS_COLORS: Array<{ id: string; label: string; hex: string }> = [
  { id: 'moss', label: '苔绿', hex: '#4F6F52' },
  { id: 'clay', label: '陶土', hex: '#B85C3E' },
  { id: 'honey', label: '蜂蜜', hex: '#D99B2B' },
  { id: 'sky', label: '天蓝', hex: '#6BA6BC' },
  { id: 'rose', label: '蔷薇', hex: '#B45F72' },
  { id: 'plum', label: '梅子', hex: '#7B5E7B' },
]

export function classColorHex(id: string): string {
  return CLASS_COLORS.find((c) => c.id === id)?.hex ?? '#4F6F52'
}

export const PLUS_REASONS = ['课堂积极', '朗读优秀', '作业优秀', '帮助同学', '进步明显']
export const MINUS_REASONS = ['作业未完成', '课堂分心', '未准备学具', '需要改进']

export const LAST_CLASS_KEY = 'petgarden.lastClassId'
export const SORT_KEY_PREFIX = 'petgarden.sort.'