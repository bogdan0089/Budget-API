<template>
  <div class="d-flex">
    <nav class="sidebar d-flex flex-column p-3">
      <div class="mb-4 px-2">
        <h5 class="fw-bold mb-0 text-white">
          <i class="bi bi-wallet2 me-2"></i>SmartBudget
        </h5>
      </div>

      <ul class="nav flex-column flex-grow-1">
        <li class="nav-item">
          <RouterLink to="/" class="nav-link px-2 py-2" exact-active-class="active">
            <i class="bi bi-grid me-2"></i>Dashboard
          </RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink to="/accounts" class="nav-link px-2 py-2" active-class="active">
            <i class="bi bi-bank me-2"></i>Accounts
          </RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink to="/budgets" class="nav-link px-2 py-2" active-class="active">
            <i class="bi bi-pie-chart me-2"></i>Budgets
          </RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink to="/goals" class="nav-link px-2 py-2" active-class="active">
            <i class="bi bi-trophy me-2"></i>Goals
          </RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink to="/ai" class="nav-link px-2 py-2" active-class="active">
            <i class="bi bi-stars me-2"></i>AI Insights
          </RouterLink>
        </li>
      </ul>

      <button class="btn btn-outline-light btn-sm w-100 mt-auto" @click="handleLogout">
        <i class="bi bi-box-arrow-left me-1"></i>Logout
      </button>
    </nav>

    <main class="main-content flex-grow-1">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const router = useRouter()

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>
