import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: () => import('./views/ClassesView.vue') },
    {
      path: '/class/:id',
      component: () => import('./views/ClassView.vue'),
    },
    {
      path: '/display/:id',
      component: () => import('./views/DisplayView.vue'),
      meta: { bare: true },
    },
    {
      path: '/settings',
      component: () => import('./views/SettingsView.vue'),
    },
    {
      path: '/:pathMatch(.*)*',
      component: () => import('./views/NotFoundView.vue'),
      meta: { bare: true },
    },
  ],
})

export default router