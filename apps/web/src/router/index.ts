import { createRouter, createWebHistory } from 'vue-router';

import HomeView from '@/views/HomeView.vue';
import TaskView from '@/views/TaskView.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/task/:taskId',
      name: 'task',
      component: TaskView,
      props: true
    }
  ]
});

export default router;

