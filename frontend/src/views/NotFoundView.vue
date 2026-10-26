<script setup lang="ts">
import EmptyState from '../components/EmptyState.vue'
</script>

<template>
  <div class="not-found">
    <EmptyState
      title="这一页不存在"
      hint="可能链接输错了，回到班级列表继续吧。"
      action-label="回到首页"
      @action="$router.push('/')"
    />
  </div>
</template>

<style scoped>
.not-found {
  display: flex;
  min-height: 100vh;
  align-items: center;
  justify-content: center;
}
</style>