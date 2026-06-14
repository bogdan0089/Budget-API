import { defineStore } from 'pinia'
import api from '../services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('access_token') || null,
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
  },

  actions: {
    async login(email, password) {
      const { data } = await api.post('/auth/login', { email, password })
      this.token = data.access_token
      localStorage.setItem('access_token', data.access_token)
    },

    async register(email, password, full_name) {
      await api.post('/auth/register', { email, password, full_name })
    },

    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('access_token')
    },
  },
})
