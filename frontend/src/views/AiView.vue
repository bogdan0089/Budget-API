<template>
  <div class="d-flex flex-column h-100">
    <h4 class="fw-bold mb-4">AI Insights</h4>

    <div class="row g-3 mb-4">
      <div class="col-12">
        <div class="card p-3">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <span class="fw-semibold small">Spending Analysis</span>
            <button class="btn btn-outline-primary btn-sm" :disabled="analyzing" @click="analyze">
              <span v-if="analyzing" class="spinner-border spinner-border-sm me-1"></span>
              <i v-else class="bi bi-lightning me-1"></i>
              Analyze
            </button>
          </div>
          <div v-if="analysis" class="text-muted small" style="white-space: pre-wrap">{{ analysis }}</div>
          <div v-else class="text-muted small">Click Analyze to get AI-powered insights about your spending habits.</div>
        </div>
      </div>
    </div>

    <div class="card flex-grow-1 d-flex flex-column" style="min-height: 0">
      <div class="card-header py-3 px-3">
        <span class="fw-semibold small">Chat with AI</span>
      </div>

      <div ref="messagesEl" class="flex-grow-1 overflow-auto p-3" style="min-height: 0">
        <div v-if="messages.length === 0" class="text-center text-muted small py-4">
          Ask anything about your finances
        </div>
        <div v-for="(msg, i) in messages" :key="i" class="mb-3">
          <div :class="msg.role === 'user' ? 'd-flex justify-content-end' : 'd-flex justify-content-start'">
            <div
              class="px-3 py-2 rounded-3 small"
              :class="msg.role === 'user' ? 'bg-primary text-white' : 'bg-light text-dark'"
              style="max-width: 75%; white-space: pre-wrap"
            >
              {{ msg.content }}
            </div>
          </div>
        </div>
        <div v-if="chatLoading" class="d-flex justify-content-start mb-3">
          <div class="px-3 py-2 rounded-3 small bg-light text-muted">
            <span class="spinner-border spinner-border-sm me-1"></span>Thinking...
          </div>
        </div>
      </div>

      <div class="card-footer border-0 p-3">
        <div class="input-group">
          <input
            v-model="input"
            type="text"
            class="form-control form-control-sm"
            placeholder="Ask about your budget..."
            @keydown.enter="sendMessage"
          />
          <button class="btn btn-primary btn-sm" :disabled="chatLoading || !input.trim()" @click="sendMessage">
            <i class="bi bi-send"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import api from '../services/api'

const analysis = ref('')
const analyzing = ref(false)
const messages = ref([])
const input = ref('')
const chatLoading = ref(false)
const messagesEl = ref(null)

async function analyze() {
  analyzing.value = true
  try {
    const { data } = await api.get('/ai/analyze')
    analysis.value = typeof data === 'string' ? data : JSON.stringify(data)
  } catch (e) {
    analysis.value = e.response?.data?.detail || 'Failed to get analysis'
  } finally {
    analyzing.value = false
  }
}

async function sendMessage() {
  const text = input.value.trim()
  if (!text) return

  messages.value.push({ role: 'user', content: text })
  input.value = ''
  chatLoading.value = true
  await scrollToBottom()

  try {
    const { data } = await api.post('/ai/chat', { message: text })
    messages.value.push({ role: 'assistant', content: typeof data === 'string' ? data : JSON.stringify(data) })
  } catch (e) {
    messages.value.push({ role: 'assistant', content: e.response?.data?.detail || 'Error occurred' })
  } finally {
    chatLoading.value = false
    await scrollToBottom()
  }
}

async function scrollToBottom() {
  await nextTick()
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  }
}
</script>
