
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import LoginView from '@/views/LoginView.vue'
import MainLayout from '@/layouts/MainLayout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),

  routes: [
    {
      path: '/',
      name: 'login',
      component: LoginView,
    },

    {
      path: '/',
      component: MainLayout,
      meta: { requiresAuth: true },

      children: [
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('@/views/DashboardView.vue'),
        },

        {
          path: 'turmas-cursos',
          name: 'turmas-cursos',
          component: () => import('@/views/TurmasCursosView.vue'),
        },

        {
          path: 'alunos',
          name: 'alunos',
          component: () => import('@/views/AlunosView.vue'),
        },

        {
          path: 'professores',
          name: 'professores',
          component: () => import('@/views/ProfessoresView.vue'),
        },
{
  path: 'avaliacoes',
  name: 'avaliacoes',
  component: () => import('@/views/AvaliacoesView.vue'),
},

{
  path: 'aulas-horarios',
  name: 'aulas-horarios',
  component: () => import('@/views/AulasHorariosView.vue'),
},

      ],
    },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated()) {
    return { name: 'login' }
  }
})

export default router