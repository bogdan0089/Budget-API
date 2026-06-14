<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center bg-light">
    <div class="card p-4" style="width: 420px">
      <h4 class="fw-bold mb-1">Create account</h4>
      <p class="text-muted mb-4 small">Start tracking your finances today</p>

      <div v-if="error" class="alert alert-danger py-2 small">{{ error }}</div>
      <div v-if="success" class="alert alert-success py-2 small">Account created! Redirecting to login...</div>

      <form @submit.prevent="handleRegister">
        <div class="mb-3">
          <label class="form-label small fw-semibold">Full name</label>
          <input v-model="form.full_name" type="text" class="form-control" placeholder="John Doe" required />
        </div>
        <div class="mb-3">
          <label class="form-label small fw-semibold">Email</label>
          <input v-model="form.email" type="email" class="form-control" placeholder="you@example.com" required />
        </div>
        <div class="mb-4">
          <label class="form-label small fw-semibold">Password</label>
          <input v-model="form.password" type="password" class="form-control" placeholder="Min 8 characters" required minlength="8" />
        </div>
        <button type="submit" class="btn btn-primary w-100" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>
          Create account
        </button>
      </form>

      <p class="text-center mt-3 mb-0 small text-muted">
        Already have an account?
        <RouterLink to="/login" class="text-primary">Sign in</RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

const form = ref({ full_name: '', email: '', password: '' })
const loading = ref(false)
const error = ref('')
const success = ref(false)

async function handleRegister() {
  loading.value = true
  error.value = ''
  try {
    await auth.register(form.value.email, form.value.password, form.value.full_name)
    success.value = true
    setTimeout(() => router.push('/login'), 1500)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>
