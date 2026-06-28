import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  // 是否是暗黑模式
  const isDark = ref(false)

  // 初始化：从 localStorage 读取或检测系统偏好
  function initTheme() {
    const saved = localStorage.getItem('theme-dark')
    if (saved !== null) {
      isDark.value = saved === 'true'
    } else {
      // 检测系统偏好
      isDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    applyTheme()
  }

  // 切换主题
  function toggleTheme() {
    isDark.value = !isDark.value
    localStorage.setItem('theme-dark', String(isDark.value))
    applyTheme()
  }

  // 设置主题
  function setTheme(dark: boolean) {
    isDark.value = dark
    localStorage.setItem('theme-dark', String(dark))
    applyTheme()
  }

  // 应用主题到 DOM
  function applyTheme() {
    const html = document.documentElement
    if (isDark.value) {
      html.classList.add('dark')
    } else {
      html.classList.remove('dark')
    }
  }

  // 监听系统主题变化
  if (typeof window !== 'undefined') {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (localStorage.getItem('theme-dark') === null) {
        isDark.value = e.matches
        applyTheme()
      }
    })
  }

  return {
    isDark,
    initTheme,
    toggleTheme,
    setTheme
  }
})
