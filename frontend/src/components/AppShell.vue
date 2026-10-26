<script setup lang="ts">
import { useRouter } from 'vue-router'

import { useClassesStore } from '../stores/classes'

const classesStore = useClassesStore()
const router = useRouter()
</script>

<template>
  <div class="shell">
    <aside class="shell-sidebar">
      <div class="shell-logo" @click="router.push('/')">
        <svg viewBox="0 0 32 32" width="28" height="28" aria-hidden="true">
          <circle cx="16" cy="18" r="10" fill="var(--moss)" />
          <circle cx="9" cy="10" r="4" fill="var(--moss)" />
          <circle cx="23" cy="10" r="4" fill="var(--moss)" />
          <circle cx="13" cy="17" r="1.6" fill="#FFFDF7" />
          <circle cx="19" cy="17" r="1.6" fill="#FFFDF7" />
          <path d="M14 21 Q16 23 18 21" stroke="#FFFDF7" stroke-width="1.6" fill="none" stroke-linecap="round" />
        </svg>
        <span>PetGarden</span>
      </div>
      <nav class="shell-nav">
        <RouterLink to="/" class="shell-link">班级</RouterLink>
        <RouterLink
          v-for="c in classesStore.classes"
          :key="c.id"
          :to="`/class/${c.id}`"
          class="shell-link shell-class-link"
        >
          {{ c.name }}
        </RouterLink>
      </nav>
      <div class="shell-foot">
        <RouterLink to="/settings" class="shell-link">设置</RouterLink>

      </div>
    </aside>
    <main class="shell-main">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.shell {
  display: flex;
  min-height: 100vh;
}

.shell-sidebar {
  display: flex;
  flex-direction: column;
  width: 232px;
  flex-shrink: 0;
  border-right: 1px solid var(--line);
  background: var(--surface-sunken);
}

.shell-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 18px;
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 700;
  cursor: pointer;
}

.shell-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  padding: 0 10px;
  overflow-y: auto;
}

.shell-link {
  display: block;
  padding: 9px 12px;
  border-radius: var(--radius-sm);
  color: var(--ink-soft);
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
}

.shell-link:hover {
  background: var(--surface);
  color: var(--ink);
}

.shell-link.router-link-active {
  background: var(--surface);
  color: var(--moss-deep);
}

.shell-class-link {
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.shell-foot {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 10px;
  border-top: 1px solid var(--line);
}


.shell-main {
  flex: 1;
  min-width: 0;
}

@media (max-width: 899px) {
  .shell-sidebar {
    width: 180px;
  }
}

@media (max-width: 599px) {
  .shell-sidebar {
    display: none;
  }
}
</style>