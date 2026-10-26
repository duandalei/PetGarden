<script setup lang="ts">
import { ref, watch } from 'vue'

const props = withDefaults(
  defineProps<{
    open: boolean
    title: string
    message: string
    confirmLabel?: string
    danger?: boolean
    requireText?: string
  }>(),
  { confirmLabel: '确定', danger: false, requireText: undefined },
)

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()

const input = ref('')

watch(
  () => props.open,
  (v) => {
    if (v) input.value = ''
  },
)

function onConfirm() {
  if (props.requireText && input.value !== props.requireText) return
  emit('confirm')
}
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="dialog-mask" @click.self="emit('cancel')">
      <div class="dialog" role="dialog" aria-modal="true" :aria-label="title">
        <h2>{{ title }}</h2>
        <p class="confirm-message">{{ message }}</p>
        <div v-if="requireText" class="field">
          <label :for="'confirm-input-' + title">请输入「{{ requireText }}」以确认</label>
          <input
            :id="'confirm-input-' + title"
            v-model="input"
            class="input"
            autocomplete="off"
          />
        </div>
        <div class="dialog-actions">
          <button type="button" class="btn" @click="emit('cancel')">取消</button>
          <button
            type="button"
            class="btn"
            :class="danger ? 'btn-danger' : 'btn-primary'"
            :disabled="requireText !== undefined && input !== requireText"
            @click="onConfirm"
          >
            {{ confirmLabel }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.confirm-message {
  color: var(--ink-soft);
  line-height: 1.7;
}
</style>