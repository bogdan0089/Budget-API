<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4 class="fw-bold mb-0">Goals</h4>
      <button class="btn btn-primary btn-sm" @click="showModal = true">
        <i class="bi bi-plus-lg me-1"></i>New Goal
      </button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary"></div>
    </div>

    <div v-else-if="goals.length === 0" class="text-center py-5 text-muted">
      <i class="bi bi-trophy fs-1 d-block mb-2"></i>
      No goals yet. Create your first savings goal.
    </div>

    <div v-else class="row g-3">
      <div v-for="g in goals" :key="g.uuid" class="col-md-4">
        <div class="card p-3 h-100">
          <div class="d-flex justify-content-between align-items-start mb-3">
            <div>
              <div class="fw-semibold">{{ g.name }}</div>
              <div v-if="g.deadline" class="text-muted small">Due {{ formatDate(g.deadline) }}</div>
            </div>
            <div class="d-flex gap-2 align-items-center">
              <span v-if="g.is_completed" class="badge bg-success">Done</span>
              <button class="btn btn-sm text-danger p-0" @click="confirmDelete(g)">
                <i class="bi bi-trash"></i>
              </button>
            </div>
          </div>

          <div class="mb-2">
            <div class="d-flex justify-content-between small mb-1">
              <span>{{ formatCurrency(g.current_amount) }}</span>
              <span class="text-muted">{{ formatCurrency(g.target_amount) }}</span>
            </div>
            <div class="progress" style="height: 8px">
              <div
                class="progress-bar"
                :class="g.is_completed ? 'bg-success' : 'bg-primary'"
                :style="{ width: Math.min(g.progress_percent, 100) + '%' }"
              ></div>
            </div>
            <div class="text-muted small mt-1">{{ g.progress_percent.toFixed(0) }}%</div>
          </div>

          <button
            v-if="!g.is_completed"
            class="btn btn-outline-primary btn-sm mt-auto"
            @click="openDeposit(g)"
          >
            <i class="bi bi-plus-circle me-1"></i>Deposit
          </button>
        </div>
      </div>
    </div>

    <!-- Create Modal -->
    <div v-if="showModal" class="modal d-block" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header border-0 pb-0">
            <h5 class="modal-title fw-bold">New Goal</h5>
            <button class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <div v-if="error" class="alert alert-danger py-2 small">{{ error }}</div>
            <div class="mb-3">
              <label class="form-label small fw-semibold">Name</label>
              <input v-model="form.name" type="text" class="form-control" placeholder="e.g. New laptop" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-semibold">Target amount (UAH)</label>
              <input v-model.number="form.target_amount" type="number" min="1" step="1" class="form-control" placeholder="e.g. 30000" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-semibold">
                Deadline <span class="text-muted fw-normal">(optional)</span>
              </label>
              <input v-model="form.deadline" type="date" class="form-control" />
            </div>
          </div>
          <div class="modal-footer border-0 pt-0">
            <button class="btn btn-secondary btn-sm" @click="closeModal">Cancel</button>
            <button class="btn btn-primary btn-sm" :disabled="submitting" @click="createGoal">
              <span v-if="submitting" class="spinner-border spinner-border-sm me-1"></span>
              Create
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Deposit Modal -->
    <div v-if="depositTarget" class="modal d-block" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header border-0 pb-0">
            <h5 class="modal-title fw-bold">Deposit to "{{ depositTarget.name }}"</h5>
            <button class="btn-close" @click="depositTarget = null"></button>
          </div>
          <div class="modal-body">
            <div v-if="error" class="alert alert-danger py-2 small">{{ error }}</div>
            <div class="mb-3">
              <label class="form-label small fw-semibold">Amount (UAH)</label>
              <input v-model.number="depositAmount" type="number" min="1" step="1" class="form-control" placeholder="e.g. 1000" />
            </div>
          </div>
          <div class="modal-footer border-0 pt-0">
            <button class="btn btn-secondary btn-sm" @click="depositTarget = null">Cancel</button>
            <button class="btn btn-primary btn-sm" :disabled="submitting" @click="deposit">
              <span v-if="submitting" class="spinner-border spinner-border-sm me-1"></span>
              Deposit
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
            <h5 class="modal-title fw-bold">Delete Goal</h5>
            <button class="btn-close" @click="deleteTarget = null"></button>
          </div>
          <div class="modal-body">
            <p class="mb-0">Delete goal <strong>{{ deleteTarget.name }}</strong>?</p>
          </div>
          <div class="modal-footer border-0 pt-0">
            <button class="btn btn-secondary btn-sm" @click="deleteTarget = null">Cancel</button>
            <button class="btn btn-danger btn-sm" :disabled="submitting" @click="deleteGoal">
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
import api from '../services/api'

const goals = ref([])
const loading = ref(true)
const showModal = ref(false)
const deleteTarget = ref(null)
const depositTarget = ref(null)
const depositAmount = ref('')
const submitting = ref(false)
const error = ref('')

const form = ref({ name: '', target_amount: '', deadline: '' })

onMounted(async () => {
  try {
    const { data } = await api.get('/goals')
    goals.value = data
  } finally {
    loading.value = false
  }
})

async function createGoal() {
  if (!form.value.name || !form.value.target_amount) return
  submitting.value = true
  error.value = ''
  try {
    await api.post('/goals', {
      name: form.value.name,
      target_amount: form.value.target_amount,
      deadline: form.value.deadline || null,
    })
    const { data } = await api.get('/goals')
    goals.value = data
    closeModal()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to create goal'
  } finally {
    submitting.value = false
  }
}

function openDeposit(g) {
  depositTarget.value = g
  depositAmount.value = ''
  error.value = ''
}

async function deposit() {
  if (!depositAmount.value || depositAmount.value <= 0) return
  submitting.value = true
  error.value = ''
  try {
    await api.post(`/goals/${depositTarget.value.uuid}/deposit`, { amount: depositAmount.value })
    const { data } = await api.get('/goals')
    goals.value = data
    depositTarget.value = null
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to deposit'
  } finally {
    submitting.value = false
  }
}

function confirmDelete(g) {
  deleteTarget.value = g
}

async function deleteGoal() {
  submitting.value = true
  try {
    await api.delete(`/goals/${deleteTarget.value.uuid}`)
    goals.value = goals.value.filter((g) => g.uuid !== deleteTarget.value.uuid)
    deleteTarget.value = null
  } finally {
    submitting.value = false
  }
}

function closeModal() {
  showModal.value = false
  form.value = { name: '', target_amount: '', deadline: '' }
  error.value = ''
}

function formatCurrency(amount) {
  return new Intl.NumberFormat('uk-UA', { style: 'currency', currency: 'UAH' }).format(amount)
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('uk-UA', { day: 'numeric', month: 'short', year: 'numeric' })
}
</script>
