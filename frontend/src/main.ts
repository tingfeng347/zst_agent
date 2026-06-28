import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import router from './router'
import App from './App.vue'

// 样式
import 'element-plus/dist/index.css'
import 'virtual:uno.css'
import './styles/index.scss'

// 初始化主题（在创建 Vue 应用之前）
function initThemeEarly() {
  const saved = localStorage.getItem('theme-dark')
  const isDark = saved !== null 
    ? saved === 'true' 
    : window.matchMedia('(prefers-color-scheme: dark)').matches
  
  if (isDark) {
    document.documentElement.classList.add('dark')
  }
}
initThemeEarly()

const app = createApp(App)

// Pinia
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)
app.use(pinia)

// Router
app.use(router)

// Element Plus
app.use(ElementPlus, {
  locale: zhCn,
})

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount('#app')
