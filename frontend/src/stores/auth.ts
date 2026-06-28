import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, register as registerApi, refreshToken as refreshApi } from '@/api/auth'
import type { LoginForm, RegisterForm, TokenResponse } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref<string>('')
  const refreshToken = ref<string>('')

  // Getters
  const isLoggedIn = computed(() => !!token.value)

  // Actions
  async function login(form: LoginForm): Promise<TokenResponse> {
    const res = await loginApi(form)
    if (res.code === 200 && res.data) {
      token.value = res.data.access_token
      refreshToken.value = res.data.refresh_token
    }
    return res.data!
  }

  async function register(form: RegisterForm) {
    return await registerApi(form)
  }

  async function refresh() {
    if (!refreshToken.value) return false
    try {
      const res = await refreshApi(refreshToken.value)
      if (res.code === 200 && res.data) {
        token.value = res.data.access_token
        refreshToken.value = res.data.refresh_token
        return true
      }
    } catch {
      logout()
    }
    return false
  }

  function logout() {
    token.value = ''
    refreshToken.value = ''
  }

  function getToken() {
    return token.value
  }

  return {
    token,
    refreshToken,
    isLoggedIn,
    login,
    register,
    refresh,
    logout,
    getToken
  }
}, {
  persist: {
    key: 'zst-auth',
    storage: localStorage,
    paths: ['token', 'refreshToken']
  }
})
