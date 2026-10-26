<script setup lang="ts">
withDefaults(
  defineProps<{
    title: string
    hint?: string
    actionLabel?: string
  }>(),
  { hint: undefined, actionLabel: undefined },
)

const emit = defineEmits<{ action: [] }>()
</script>

<template>
  <div class="empty-state">
    <svg viewBox="0 0 120 120" width="96" height="96" aria-hidden="true">
      <ellipse cx="60" cy="104" rx="40" ry="6" fill="#252A26" opacity="0.08" />
      <path
        d="M38 104 L38 66 Q38 46 60 46 Q82 46 82 66 L82 104 Z"
        fill="var(--surface-sunken)" stroke="var(--line-strong)" stroke-width="2" stroke-linejoin="round"
      />
      <path d="M48 104 L48 74 Q48 58 60 58 Q72 58 72 74 L72 104" fill="var(--surface)" stroke="var(--line-strong)" stroke-width="2" />
      <circle cx="60" cy="34" r="10" fill="var(--moss-soft)" stroke="var(--moss)" stroke-width="2" />
      <path d="M60 24 L60 14 M52 30 L44 24 M68 30 L76 24" stroke="var(--moss)" stroke-width="2" stroke-linecap="round" />
    </svg>
    <p class="empty-title">{{ title }}</p>
    <p v-if="hint" class="empty-hint">{{ hint }}</p>
    <button v-if="actionLabel" type="button" class="btn btn-primary" @click="emit('action')">
      {{ actionLabel }}
    </button>
  </div>
</template>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 48px 24px;
  text-align: center;
}

.empty-title {
  font-size: 17px;
  font-weight: 700;
}

.empty-hint {
  max-width: 380px;
  color: var(--ink-soft);
  font-size: 14px;
}

.empty-state .btn {
  margin-top: 8px;
}
</style>