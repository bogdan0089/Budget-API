<template>
  <div>
    <h4 class="fw-bold mb-4">Dashboard</h4>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary"></div>
    </div>

    <template v-else>
      <!-- Summary cards -->
      <div class="row g-3 mb-4">
        <div class="col-md-3">
          <div class="card p-3">
            <div class="d-flex align-items-center gap-3">
              <div class="rounded-circle bg-primary bg-opacity-10 p-3">
                <i class="bi bi-bank text-primary fs-5"></i>
              </div>
              <div>
                <p class="text-muted small mb-0">Total Balance</p>
                <h5 class="fw-bold mb-0">{{ formatCurrency(totalBalance) }}</h5>
              </div>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card p-3">
            <div class="d-flex align-items-center gap-3">
              <div class="rounded-circle bg-success bg-opacity-10 p-3">
                <i class="bi bi-arrow-down-circle text-success fs-5"></i>
              </div>
              <div>
                <p class="text-muted small mb-0">Income this month</p>
                <h5 class="fw-bold mb-0 text-success">+{{ formatCurrency(monthIncome) }}</h5>
              </div>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card p-3">
            <div class="d-flex align-items-center gap-3">
              <div class="rounded-circle bg-danger bg-opacity-10 p-3">
                <i class="bi bi-arrow-up-circle text-danger fs-5"></i>
              </div>
              <div>
                <p class="text-muted small mb-0">Expenses this month</p>
                <h5 class="fw-bold mb-0 text-danger">-{{ formatCurrency(monthExpenses) }}</h5>
              </div>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card p-3">
            <div class="d-flex align-items-center gap-3">
              <div class="rounded-circle bg-warning bg-opacity-10 p-3">
                <i class="bi bi-trophy text-warning fs-5"></i>
              </div>
              <div>
                <p class="text-muted small mb-0">Active Goals</p>
                <h5 class="fw-bold mb-0">{{ activeGoals }}</h5>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-3">
        <!-- Accounts -->
        <div class="col-md-5">
          <div class="card h-100">
            <div class="card-header d-flex justify-content-between align-items-center py-3 px-3">
              <span>My Accounts</span>
              <RouterLink to="/accounts" class="btn btn-sm btn-outline-primary">View all</RouterLink>
            </div>
            <div class="card-body p-0">
              <div v-if="accounts.length === 0" class="text-center py-5 text-muted small">
                No accounts yet
              </div>
              <ul class="list-group list-group-flush">
                <li
                  v-for="acc in accounts"
                  :key="acc.uuid"
                  class="list-group-item d-flex justify-content-between align-items-center px-3"
                >
                  <div class="d-flex align-items-center gap-2">
                    <i :class="accountIcon(acc.type)" class="text-muted"></i>
                    <span class="small">{{ acc.name }}</span>
                    <span class="badge bg-secondary bg-opacity-10 text-secondary small">{{ acc.type }}</span>
                  </div>
                  <span class="fw-semibold small">{{ formatCurrency(acc.balance, acc.currency) }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Goals progress -->
        <div class="col-md-7">
          <div class="card h-100">
            <div class="card-header d-flex justify-content-between align-items-center py-3 px-3">
              <span>Goals Progress</span>
              <RouterLink to="/goals" class="btn btn-sm btn-outline-primary">View all</RouterLink>
            </div>
            <div class="card-body">
              <div v-if="goals.length === 0" class="text-center py-4 text-muted small">
                No goals yet
              </div>
              <div v-for="goal in goals.slice(0, 4)" :key="goal.uuid" class="mb-3">
                <div class="d-flex justify-content-between small mb-1">
                  <span class="fw-semibold">{{ goal.name }}</span>
                  <span class="text-muted">
                    {{ formatCurrency(goal.current_amount) }} / {{ formatCurrency(goal.target_amount) }}
                  </span>
                </div>
                <div class="progress" style="height: 8px">
                  <div
                    class="progress-bar"
                    :class="goal.is_completed ? 'bg-success' : 'bg-primary'"
                    :style="{ width: Math.min(goal.progress_percent, 100) + '%' }"
                  ></div>
                </div>
                <div class="d-flex justify-content-between mt-1">
                  <span class="text-muted" style="font-size: 11px">
                    {{ goal.is_completed ? '✓ Completed' : goal.progress_percent.toFixed(0) + '%' }}
                  </span>
                  <span v-if="goal.deadline" class="text-muted" style="font-size: 11px">
                    Due {{ formatDate(goal.deadline) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Budgets -->
        <div class="col-12">
          <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center py-3 px-3">
              <span>Budget Overview</span>
              <RouterLink to="/budgets" class="btn btn-sm btn-outline-primary">Manage</RouterLink>
            </div>
            <div class="card-body">
              <div v-if="budgets.length === 0" class="text-center py-3 text-muted small">
                No budgets set
              </div>
              <div class="row g-3">
                <div v-for="b in budgets.slice(0, 6)" :key="b.uuid" class="col-md-4">
                  <div class="d-flex justify-content-between small mb-1">
                    <span class="fw-semibold">{{ b.category_name }}</span>
                    <span :class="b.remaining < 0 ? 'text-danger' : 'text-muted'">
                      {{ formatCurrency(b.remaining) }} left
                    </span>
                  </div>
                  <div class="progress" style="height: 6px">
                    <div
                      class="progress-bar"
                      :class="budgetBarClass(b)"
                      :style="{ width: Math.min((b.spent_amount / b.limit_amount) * 100, 100) + '%' }"
                    ></div>
                  </div>
                  <div class="text-muted mt-1" style="font-size: 11px">
                    {{ formatCurrency(b.spent_amount) }} / {{ formatCurrency(b.limit_amount) }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import api from '../services/api'

const loading = ref(true)
const accounts = ref([])
const goals = ref([])
const budgets = ref([])

const totalBalance = computed(() => accounts.value.reduce((s, a) => s + a.balance, 0))
const activeGoals = computed(() => goals.value.filter((g) => !g.is_completed).length)

const monthIncome = computed(() => {
  const now = new Date()
  return allTransactions.value
    .filter((t) => {
      const d = new Date(t.date)
      return t.type === 'INCOME' && d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear()
    })
    .reduce((s, t) => s + t.amount, 0)
})

const monthExpenses = computed(() => {
  const now = new Date()
  return allTransactions.value
    .filter((t) => {
      const d = new Date(t.date)
      return t.type === 'EXPENSE' && d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear()
    })
    .reduce((s, t) => s + t.amount, 0)
})

const allTransactions = ref([])

onMounted(async () => {
  try {
    const [accRes, goalsRes, budgetsRes] = await Promise.all([
      api.get('/accounts'),
      api.get('/goals'),
      api.get('/budgets'),
    ])
    accounts.value = accRes.data
    goals.value = goalsRes.data
    budgets.value = budgetsRes.data

    if (accounts.value.length > 0) {
      const txRes = await Promise.all(
        accounts.value.map((a) => api.get(`/transactions/account/${a.uuid}?limit=50`)),
      )
      allTransactions.value = txRes.flatMap((r) => r.data)
    }
  } finally {
    loading.value = false
  }
})

function formatCurrency(amount, currency = 'UAH') {
  return new Intl.NumberFormat('uk-UA', { style: 'currency', currency }).format(amount)
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('uk-UA', { day: 'numeric', month: 'short' })
}

function accountIcon(type) {
  const icons = { CASH: 'bi bi-cash', CARD: 'bi bi-credit-card', SAVINGS: 'bi bi-piggy-bank', CREDIT: 'bi bi-credit-card-2-front' }
  return icons[type] || 'bi bi-bank'
}

function budgetBarClass(b) {
  const pct = (b.spent_amount / b.limit_amount) * 100
  if (pct >= 100) return 'bg-danger'
  if (pct >= 80) return 'bg-warning'
  return 'bg-success'
}
</script>
