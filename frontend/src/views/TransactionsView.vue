<template>
  <div>
    <div class="d-flex align-items-center gap-2 mb-4">
      <RouterLink to="/accounts" class="btn btn-sm btn-outline-secondary">
        <i class="bi bi-arrow-left"></i>
      </RouterLink>
      <div>
        <h4 class="fw-bold mb-0">{{ account?.name || 'Transactions' }}</h4>
        <span class="text-muted small">{{ formatCurrency(account?.balance, account?.currency) }}</span>
      </div>
      <button class="btn btn-primary btn-sm ms-auto" @click="showModal = true">
        <i class="bi bi-plus-lg me-1"></i>New Transaction
      </button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary"></div>
    </div>

    <div v-else-if="transactions.length === 0" class="text-center py-5 text-muted">
      <i class="bi bi-receipt fs-1 d-block mb-2"></i>
      No transactions yet.
    </div>

    <div v-else class="card">
      <ul class="list-group list-group-flush">
        <li
          v-for="tx in transactions"
          :key="tx.uuid"
          class="list-group-item d-flex align-items-center gap-3 px-4 py-3"
        >
          <div
            class="rounded-circle d-flex align-items-center justify-content-center flex-shrink-0"
            :class="tx.type?.toLowerCase() === 'income' ? 'bg-success bg-opacity-10' : 'bg-danger bg-opacity-10'"
            style="width: 40px; height: 40px"
          >
            <i
              class="bi"
              :class="tx.type?.toLowerCase() === 'income' ? 'bi-arrow-down-circle text-success' : 'bi-arrow-up-circle text-danger'"
            ></i>
          </div>
          <div class="flex-grow-1">
            <div class="fw-semibold small">{{ tx.description || tx.category?.name || '—' }}</div>
            <div class="text-muted" style="font-size: 12px">{{ formatDate(tx.date) }}</div>
          </div>
          <div class="text-end">
            <div class="fw-bold" :class="tx.type?.toLowerCase() === 'income' ? 'text-success' : 'text-danger'">
              {{ tx.type?.toLowerCase() === 'income' ? '+' : '-' }}{{ formatCurrency(tx.amount, account?.currency) }}
            </div>
            <div v-if="tx.category" class="text-muted" style="font-size: 11px">{{ tx.category.name }}</div>
          </div>
        </li>
      </ul>
    </div>

    <div v-if="hasMore" class="text-center mt-3">
      <button class="btn btn-outline-secondary btn-sm" :disabled="loadingMore" @click="loadMore">
        <span v-if="loadingMore" class="spinner-border spinner-border-sm me-1"></span>
        Load more
      </button>
    </div>

    <!-- Create Modal -->
    <div v-if="showModal" class="modal d-block" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header border-0 pb-0">
            <h5 class="modal-title fw-bold">New Transaction</h5>
            <button class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <div v-if="error" class="alert alert-danger py-2 small">{{ error }}</div>
            <div class="mb-3">
              <label class="form-label small fw-semibold">Type</label>
              <AppSelect v-model="form.type" :options="typeOptions" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-semibold">Amount</label>
              <input v-model.number="form.amount" type="number" min="0.01" step="0.01" class="form-control" placeholder="0.00" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-semibold">Category</label>
              <AppSelect v-model="form.category_id" :options="categoryOptions" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-semibold">
                Description <span class="text-muted fw-normal">(optional)</span>
              </label>
              <input v-model="form.description" type="text" class="form-control" placeholder="e.g. Grocery shopping" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-semibold">Date</label>
              <input v-model="form.date" type="date" class="form-control" />
            </div>
          </div>
          <div class="modal-footer border-0 pt-0">
            <button class="btn btn-secondary btn-sm" @click="closeModal">Cancel</button>
            <button class="btn btn-primary btn-sm" :disabled="submitting" @click="createTransaction">
              <span v-if="submitting" class="spinner-border spinner-border-sm me-1"></span>
              Add
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import api from '../services/api'
import AppSelect from '../components/AppSelect.vue'

const route = useRoute()
const accountId = route.params.id

const account = ref(null)
const transactions = ref([])
const categories = ref([])
const loading = ref(true)
const loadingMore = ref(false)
const showModal = ref(false)
const submitting = ref(false)
const error = ref('')
const offset = ref(0)
const LIMIT = 20
const hasMore = ref(false)

const today = new Date().toISOString().split('T')[0]
const form = ref({ type: 'expense', amount: '', category_id: '', description: '', date: today })

const typeOptions = [
  { value: 'expense', label: 'Expense', icon: 'bi bi-arrow-up-circle text-danger' },
  { value: 'income', label: 'Income', icon: 'bi bi-arrow-down-circle text-success' },
]

const categoryOptions = computed(() => [
  { value: '', label: 'No category' },
  ...categories.value.map((c) => ({ value: c.uuid, label: c.name })),
])

onMounted(async () => {
  try {
    const [accRes, txRes, catRes] = await Promise.all([
      api.get(`/accounts/${accountId}`),
      api.get(`/transactions/account/${accountId}?limit=${LIMIT}&offset=0`),
      api.get('/categories'),
    ])
    account.value = accRes.data
    transactions.value = txRes.data
    categories.value = catRes.data
    hasMore.value = txRes.data.length === LIMIT
  } finally {
    loading.value = false
  }
})

async function loadMore() {
  loadingMore.value = true
  offset.value += LIMIT
  try {
    const { data } = await api.get(`/transactions/account/${accountId}?limit=${LIMIT}&offset=${offset.value}`)
    transactions.value.push(...data)
    hasMore.value = data.length === LIMIT
  } finally {
    loadingMore.value = false
  }
}

async function createTransaction() {
  if (!form.value.amount || form.value.amount <= 0) return
  submitting.value = true
  error.value = ''
  try {
    await api.post('/transactions', {
      account_id: accountId,
      amount: form.value.amount,
      type: form.value.type,
      description: form.value.description || null,
      date: form.value.date,
      category_id: form.value.category_id || null,
    })
    const [txRes, accRes] = await Promise.all([
      api.get(`/transactions/account/${accountId}?limit=${LIMIT}&offset=0`),
      api.get(`/accounts/${accountId}`),
    ])
    transactions.value = txRes.data
    account.value = accRes.data
    offset.value = 0
    hasMore.value = txRes.data.length === LIMIT
    closeModal()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to add transaction'
  } finally {
    submitting.value = false
  }
}

function closeModal() {
  showModal.value = false
  form.value = { type: 'expense', amount: '', category_id: '', description: '', date: today }
  error.value = ''
}

function formatCurrency(amount, currency = 'UAH') {
  if (amount == null) return ''
  return new Intl.NumberFormat('uk-UA', { style: 'currency', currency }).format(amount)
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('uk-UA', { day: 'numeric', month: 'short', year: 'numeric' })
}
</script>
