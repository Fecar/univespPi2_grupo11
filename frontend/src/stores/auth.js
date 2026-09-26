import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token') || null)

  async function login(email, senha) {
    const resposta = await api.post('/auth/login', { email, senha })
    token.value = resposta.data.access_token
    localStorage.setItem('access_token', token.value)
  }

  function logout() {
    token.value = null
    localStorage.removeItem('access_token')
  }

  function isAuthenticated() {
    return !!token.value
  }

  return { token, login, logout, isAuthenticated }
})
