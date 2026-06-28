import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getUserInfo } from '@/api/user'
import type { UserInfo } from '@/types/auth'

export const useUserStore = defineStore('user', () => {
  // State
  const userInfo = ref<UserInfo | null>(null)

  // Actions
  async function fetchUserInfo() {
    try {
      const res = await getUserInfo()
      if (res.code === 200 && res.data) {
        userInfo.value = res.data
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }

  function setUserInfo(info: UserInfo) {
    userInfo.value = info
  }

  function clearUserInfo() {
    userInfo.value = null
  }

  return {
    userInfo,
    fetchUserInfo,
    setUserInfo,
    clearUserInfo
  }
}, {
  persist: {
    key: 'zst-user',
    storage: localStorage,
    paths: ['userInfo']
  }
})
