import { createRouter, createWebHistory } from 'vue-router'
import AssistantView from '../views/AssistantView.vue'
import NewsView from '../views/NewsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/assistant',
      name: 'assistant',
      component: AssistantView,
    },
    {
      path: '/news',
      name: 'news',
      component: NewsView,
    },
  ],
})

export default router
