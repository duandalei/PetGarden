<script setup lang="ts">
import { MINUS_REASONS, PLUS_REASONS } from '../utils/constants'

defineProps<{
  open: boolean
  direction: 1 | -1
  studentName: string
}>()

const emit = defineEmits<{
  pick: [reason: string]
  cancel: []
}>()
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="dialog-mask" @click.self="emit('cancel')">
      <div class="dialog" role="dialog" aria-modal="true" aria-label="选择原因">
        <h2>{{ direction > 0 ? '加分原因' : '减分原因' }} · {{ studentName }}</h2>
        <div class="reason-grid">
          <button
            v-for="reason in direction > 0 ? PLUS_REASONS : MINUS_REASONS"
            :key="reason"
            type="button"
            class="btn reason-btn"
            @click="emit('pick', reason)"
          >
            {{ reason }}
          </button>
        </div>
        <div class="dialog-actions">
          <button type="button" class="btn" @click="emit('cancel')">取消</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.reason-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 10px;
}

.reason-btn {
  justify-content: flex-start;
}
</style>