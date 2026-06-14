import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { guest: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/RegisterView.vue'),
    meta: { guest: true },
  },
  {
    path: '/',
    component: () => import('../components/layout/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('../views/DashboardView.vue'),
      },
      {
        path: 'accounts',
        name: 'Accounts',
        component: () => import('../views/AccountsView.vue'),
      },
      {
        path: 'accounts/:id/transactions',
        name: 'Transactions',
        component: () => import('../views/TransactionsView.vue'),
      },
      {
        path: 'budgets',
        name: 'Budgets',
        component: () => import('../views/BudgetsView.vue'),
      },
      {
        path: 'goals',
        name: 'Goals',
        component: () => import('../views/GoalsView.vue'),
      },
      {
        path: 'ai',
        name: 'AI',
        component: () => import('../views/AiView.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const isLoggedIn = !!localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !isLoggedIn) return { name: 'Login' }
  if (to.meta.guest && isLoggedIn) return { name: 'Dashboard' }
})

export default router
