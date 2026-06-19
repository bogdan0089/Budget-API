<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4 class="fw-bold mb-0">Budgets</h4>
      <button class="btn btn-primary btn-sm" @click="showModal = true">
        <i class="bi bi-plus-lg me-1"></i>New Budget
      </button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary"></div>
    </div>

    <div v-else-if="budgets.length === 0" class="text-center py-5 text-muted">
      <i class="bi bi-pie-chart fs-1 d-block mb-2"></i>
      No budgets yet. Set a monthly limit for a category.
    </div>

    <div v-else class="row g-3">
      <div v-for="b in budgets" :key="b.uuid" class="col-md-4">
        <div class="card p-3 h-100">
          <div class="d-flex justify-content-between align-items-start mb-3">
            <div>
              <div class="fw-semibold">{{ b.category_name }}</div>
              <div class="text-muted small">{{ formatMonth(b.month) }}</div>
            </div>
            <button class="btn btn-sm text-danger p-0" @click="confirmDelete(b)">
              <i class="bi bi-trash"></i>
            </button>
          </div>
          <div class="mb-2">
            <div class="d-flex justify-content-between small mb-1">
              <span>{{ formatCurrency(b.spent_amount) }} spent</span>
              <span :class="b.remaining <= 0 ? 'text-danger fw-semibold' : 'text-muted'">
                {{ b.remaining <= 0 ? 'Over limit' : formatCurrency(b.remaining) + ' left' }}
              </span>
            </div>
            <div class="progress" style="height: 8px">
              <div
                class="progress-bar"
                :class="barClass(b)"
                :style="{ width: Math.min((b.spent_amount / b.limit_amount) * 100, 100) + '%' }"
              ></div>
            </div>
          </div>
          <div class="text-muted small mt-auto">Limit: {{ formatCurrency(b.limit_amount) }}</div>
        </div>
      </div>
    </div>

    <!-- Create Modal -->
    <div v-if="showModal" class="modal d-block" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header border-0 pb-0">
            <h5 class="modal-title fw-bold">New Budget</h5>
            <button class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <div v-if="error" class="alert alert-danger py-2 small">{{ error }}</div>
            <div class="mb-3">
              <label class="form-label small fw-semibold">Category</label>
              <AppSelect v-model="form.category_id" :options="categoryOptions" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-semibold">Month</label>
              <input v-model="form.month" type="month" class="form-control" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-semibold">Limit (UAH)</label>
              <input v-model.number="form.limit_amount" type="number" min="1" step="1" class="form-control" placeholder="e.g. 5000" />
            </div>
          </div>
          <div class="modal-footer border-0 pt-0">
            <button class="btn btn-secondary btn-sm" @click="closeModal">Cancel</button>
            <button class="btn btn-primary btn-sm" :disabled="submitting" @click="createBudget">
              <span v-if="submitting" class="spinner-border spinner-border-sm me-1"></span>
              Create
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirm Modal -->
    <div v-if="deleteTarget" class="modal d-block" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header border-0 pb-0">
            <h5 class="modal-title fw-bold">Delete Budget</h5>
            <button class="btn-close" @click="deleteTarget = null"></button>
          </div>
          <div class="modal-body">
            <p class="mb-0">Delete budget for <strong>{{ deleteTarget.category_name }}</strong>?</p>
          </div>
          <div class="modal-footer border-0 pt-0">
            <button class="btn btn-secondary btn-sm" @click="deleteTarget = null">Cancel</button>
            <button class="btn btn-danger btn-sm" :disabled="submitting" @click="deleteBudget">
              <span v-if="submitting" class="spinner-border spinner-border-sm me-1"></span>
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'
import AppSelect from '../components/AppSelect.vue'

const budgets = ref([])
const categories = ref([])
const loading = ref(true)
const showModal = ref(false)
const deleteTarget = ref(null)
const submitting = ref(false)
const error = ref('')

const currentMonth = new Date().toISOString().slice(0, 7)
const form = ref({ category_id: '', month: currentMonth, limit_amount: '' })

const categoryOptions = computed(() => [
  { value: '', label: 'Select category' },
  ...categories.value.filter((c) => c.type === 'EXPENSE').map((c) => ({ value: c.uuid, label: `${c.icon || ''} ${c.name}`.trim() })),
])

onMounted(async () => {
  try {
    const [budgetsRes, catRes] = await Promise.all([api.get('/budgets'), api.get('/categories')])
    budgets.value = budgetsRes.data
    categories.value = catRes.data
  } finally {
    loading.value = false
  }
})

async function createBudget() {
  if (!form.value.category_id || !form.value.limit_amount) return
  submitting.value = true
  error.value = ''
  try {
    await api.post('/budgets', {
      category_id: form.value.category_id,
      month: form.value.month + '-01',
      limit_amount: form.value.limit_amount,
    })
    const { data } = await api.get('/budgets')
    budgets.value = data
    closeModal()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to create budget'
  } finally {
    submitting.value = false
  }
}

function confirmDelete(b) {
  deleteTarget.value = b
}

async function deleteBudget() {
  submitting.value = true
  try {
    await api.delete(`/budgets/${deleteTarget.value.uuid}`)
    budgets.value = budgets.value.filter((b) => b.uuid !== deleteTarget.value.uuid)
    deleteTarget.value = null
  } finally {
    submitting.value = false
  }
}

function closeModal() {
  showModal.value = false
  form.value = { category_id: '', month: currentMonth, limit_amount: '' }
  error.value = ''
}

function formatCurrency(amount) {
  return new Intl.NumberFormat('uk-UA', { style: 'currency', currency: 'UAH' }).format(amount)
}

function formatMonth(dateStr) {
  return new Date(dateStr).toLocaleDateString('uk-UA', { month: 'long', year: 'numeric' })
}

function barClass(b) {
  const pct = (b.spent_amount / b.limit_amount) * 100
  if (pct >= 100) return 'bg-danger'
  if (pct >= 80) return 'bg-warning'
  return 'bg-success'
}
</script>
