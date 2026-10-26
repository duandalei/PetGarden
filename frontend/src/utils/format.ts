export function formatAverage(value: number): string {
  return Number.isInteger(value) ? String(value) : value.toFixed(1)
}

export function formatDelta(delta: number): string {
  return delta > 0 ? `+${delta}` : String(delta)
}