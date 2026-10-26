<script setup lang="ts">
defineProps<{
  disabled: boolean
  name: string
}>()

const emit = defineEmits<{
  minus: []
  plus: []
  longMinus: []
  longPlus: []
}>()
</script>

<template>
  <div class="score-buttons">
    <button
      type="button"
      class="score-btn score-down"
      :disabled="disabled"
      :aria-label="`给${name}减 1 分`"
      @click="emit('minus')"
      @contextmenu.prevent="emit('longMinus')"
    >
      −1
    </button>
    <button
      type="button"
      class="score-btn score-up"
      :disabled="disabled"
      :aria-label="`给${name}加 1 分`"
      @click="emit('plus')"
      @contextmenu.prevent="emit('longPlus')"
    >
      +1
    </button>
  </div>
</template>

<style scoped>
.score-buttons {
  display: flex;
  gap: 8px;
}

.score-btn {
  flex: 1;
  min-height: 44px;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: var(--surface);
  color: var(--ink-soft);
  font-size: 15px;
  font-weight: 700;
  transition:
    transform 0.12s ease,
    background 0.12s ease;
}

.score-btn:hover:not(:disabled) {
  transform: translateY(-1px);
}

.score-btn:active:not(:disabled) {
  transform: translateY(1px);
}

.score-up {
  border-color: var(--moss);
  background: var(--moss);
  color: #fffdf7;
}

.score-up:hover:not(:disabled) {
  background: var(--moss-deep);
}

.score-down:hover:not(:disabled) {
  background: var(--surface-sunken);
}
</style>