<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4 class="fw-bold mb-0">Accounts</h4>
      <button class="btn btn-primary btn-sm" @click="showModal = true">
        <i class="bi bi-plus-lg me-1"></i>New Account
      </button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary"></div>
    </div>

    <div v-else-if="accounts.length === 0" class="text-center py-5 text-muted">
      <i class="bi bi-bank fs-1 d-block mb-2"></i>
      No accounts yet. Create your first one.
    </div>

    <div v-else class="row g-3">
      <div v-for="acc in accounts" :key="acc.uuid" class="col-md-4">
        <div class="card p-3 h-100">
          <div class="d-flex justify-content-between align-items-start mb-3">
            <div class="d-flex align-items-center gap-2">
              <div class="rounded-circle bg-primary bg-opacity-10 p-2">
                <i :class="accountIcon(acc.type)" class="text-primary"></i>
              </div>
              <div>
                <div class="fw-semibold">{{ acc.name }}</div>
                <span class="badge bg-secondary bg-opacity-10 text-secondary" style="font-size: 11px">{{ acc.type }}</span>
              </div>
            </div>
            <button class="btn btn-sm text-danger p-0" @click="confirmDelete(acc)">
              <i class="bi bi-trash"></i>
            </button>
          </div>
          <div class="mt-auto">
            <div class="text-muted small mb-1">Balance</div>
            <div class="fw-bold fs-5">{{ formatCurrency(acc.balance, acc.currency) }}</div>
          </div>
          <RouterLink
            :to="`/accounts/${acc.uuid}/transactions`"
            class="btn btn-outline-primary btn-sm mt-3"
          >
            <i class="bi bi-list-ul me-1"></i>Transactions
          </RouterLink>
        </div>
      </div>
    </div>

    <!-- Create Modal -->
    <div v-if="showModal" class="modal d-block" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header border-0 pb-0">
            <h5 class="modal-title fw-bold">New Account</h5>
            <button class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <div v-if="error" class="alert alert-danger py-2 small">{{ error }}</div>
            <div class="mb-3">
              <label class="form-label small fw-semibold">Name</label>
              <input v-model="form.name" type="text" class="form-control" placeholder="e.g. Main Card" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-semibold">Type</label>
              <AppSelect v-model="form.type" :options="typeOptions" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-semibold">Currency</label>
              <AppSelect v-model="form.currency" :options="currencyOptions" />
            </div>
          </div>
          <div class="modal-footer border-0 pt-0">
            <button class="btn btn-secondary btn-sm" @click="closeModal">Cancel</button>
            <button class="btn btn-primary btn-sm" :disabled="submitting" @click="createAccount">
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
            <h5 class="modal-title fw-bold">Delete Account</h5>
            <button class="btn-close" @click="deleteTarget = null"></button>
          </div>
          <div class="modal-body">
            <p class="mb-0">Delete <strong>{{ deleteTarget.name }}</strong>? All transactions will be removed.</p>
          </div>
          <div class="modal-footer border-0 pt-0">
            <button class="btn btn-secondary btn-sm" @click="deleteTarget = null">Cancel</button>
            <button class="btn btn-danger btn-sm" :disabled="submitting" @click="deleteAccount">
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
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import api from '../services/api'
import AppSelect from '../components/AppSelect.vue'

const typeOptions = [
  { value: 'cash', label: 'Cash', icon: 'bi bi-cash' },
  { value: 'card', label: 'Card', icon: 'bi bi-credit-card' },
  { value: 'savings', label: 'Savings', icon: 'bi bi-piggy-bank' },
  { value: 'credit', label: 'Credit', icon: 'bi bi-credit-card-2-front' },
]

const currencyOptions = [
  { value: 'UAH', label: 'UAH — Ukrainian Hryvnia' },
  { value: 'USD', label: 'USD — US Dollar' },
  { value: 'EUR', label: 'EUR — Euro' },
]

const accounts = ref([])
const loading = ref(true)
const showModal = ref(false)
const deleteTarget = ref(null)
const submitting = ref(false)
const error = ref('')

const form = ref({ name: '', type: 'card', currency: 'UAH' })

onMounted(fetchAccounts)

async function fetchAccounts() {
  loading.value = true
  try {
    const { data } = await api.get('/accounts')
    accounts.value = data
  } finally {
    loading.value = false
  }
}

async function createAccount() {
  if (!form.value.name.trim()) return
  submitting.value = true
  error.value = ''
  try {
    await api.post('/accounts', form.value)
    await fetchAccounts()
    closeModal()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to create account'
  } finally {
    submitting.value = false
  }
}

function confirmDelete(acc) {
  deleteTarget.value = acc
}

async function deleteAccount() {
  submitting.value = true
  try {
    await api.delete(`/accounts/${deleteTarget.value.uuid}`)
    await fetchAccounts()
    deleteTarget.value = null
  } finally {
    submitting.value = false
  }
}

function closeModal() {
  showModal.value = false
  form.value = { name: '', type: 'card', currency: 'UAH' }
  error.value = ''
}

function formatCurrency(amount, currency = 'UAH') {
  return new Intl.NumberFormat('uk-UA', { style: 'currency', currency }).format(amount)
}

function accountIcon(type) {
  const icons = { cash: 'bi bi-cash', card: 'bi bi-credit-card', savings: 'bi bi-piggy-bank', credit: 'bi bi-credit-card-2-front' }
  return icons[type?.toLowerCase()] || 'bi bi-bank'
}
</script>
