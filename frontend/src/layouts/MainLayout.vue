<template>
  <el-container class="main-layout">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="layout-aside">
      <div class="logo-container">
        <el-icon :size="32" color="#fff"><ChatDotRound /></el-icon>
        <span v-show="!isCollapse" class="logo-text">智扫通</span>
      </div>

      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :collapse-transition="false"
        :background-color="menuBgColor"
        :text-color="menuTextColor"
        active-text-color="#409EFF"
        router
        class="aside-menu"
      >
        <el-menu-item index="/dashboard" v-if="userStore.userInfo?.is_superuser">
          <el-icon><Monitor /></el-icon>
          <template #title>工作台</template>
        </el-menu-item>

        <el-menu-item index="/chat">
          <el-icon><ChatDotRound /></el-icon>
          <template #title>智能客服</template>
        </el-menu-item>

        <template v-if="userStore.userInfo?.is_superuser">
          <el-menu-item index="/knowledge">
            <el-icon><Collection /></el-icon>
            <template #title>知识库</template>
          </el-menu-item>

          <el-sub-menu index="system">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>系统管理</span>
            </template>
            <el-menu-item index="/system/users">
              <el-icon><User /></el-icon>
              <template #title>用户管理</template>
            </el-menu-item>
          </el-sub-menu>
        </template>
      </el-menu>

      <div class="aside-footer">
        <el-tooltip :content="isCollapse ? '展开' : '收起'" placement="right">
          <el-icon class="collapse-btn" @click="toggleCollapse">
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>
        </el-tooltip>
      </div>
    </el-aside>

    <el-container class="main-container">
      <el-header class="layout-header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="route.meta.title">
              {{ route.meta.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <el-input
            v-model="searchText"
            placeholder="搜索"
            :prefix-icon="Search"
            class="header-search"
            clearable
          />

          <el-tooltip content="全屏" placement="bottom">
            <el-icon class="header-icon" @click="toggleFullscreen">
              <FullScreen />
            </el-icon>
          </el-tooltip>

          <el-tooltip :content="themeStore.isDark ? '浅色模式' : '深色模式'" placement="bottom">
            <el-icon class="header-icon theme-icon" @click="themeStore.toggleTheme">
              <Moon v-if="!themeStore.isDark" />
              <Sunny v-else />
            </el-icon>
          </el-tooltip>

          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="32" class="user-avatar">
                {{ userStore.userInfo?.nickname?.charAt(0) || userStore.userInfo?.username?.charAt(0) || 'U' }}
              </el-avatar>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>个人中心
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <div class="tabs-container">
        <div class="tabs-scroll-area">
          <div
            v-for="tab in tabs"
            :key="tab.path"
            class="custom-tab"
            :class="{ 'is-active': route.path === tab.path }"
            @click="router.push(tab.path)"
          >
            <span class="tab-title">{{ tab.title }}</span>
            <el-icon 
              v-if="tabs.length > 1" 
              class="close-icon"
              @click.stop="closeTab(tab.path)"
            >
              <Close />
            </el-icon>
          </div>
        </div>
      </div>

      <el-main class="layout-main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import {
  ChatDotRound, Monitor, Setting, User, Fold, Expand,
  Search, FullScreen, ArrowDown, SwitchButton, Close, Moon, Sunny, Collection
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'
import { useThemeStore } from '@/stores/theme'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const userStore = useUserStore()
const themeStore = useThemeStore()

const isCollapse = ref(false)
const searchText = ref('')

// 标签页
interface Tab {
  path: string
  title: string
}
const tabs = ref<Tab[]>([])

const activeMenu = computed(() => route.path)

// 菜单颜色（根据主题动态变化）
const menuBgColor = computed(() => themeStore.isDark ? '#111827' : '#304156')
const menuTextColor = computed(() => themeStore.isDark ? '#d1d5db' : '#bfcbd9')

watch(() => route.path, (path) => {
  const title = route.meta.title as string
  if (title && !tabs.value.find(t => t.path === path)) {
    tabs.value.push({ path, title })
  }
}, { immediate: true })

function toggleCollapse() {
  isCollapse.value = !isCollapse.value
}

function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

function closeTab(path: string) {
  const index = tabs.value.findIndex(t => t.path === path)
  if (index > -1) {
    tabs.value.splice(index, 1)
    if (route.path === path && tabs.value.length > 0) {
      router.push(tabs.value[tabs.value.length - 1].path)
    }
  }
}

function handleCommand(command: string) {
  switch (command) {
    case 'profile':
      router.push('/user/profile')
      break
    case 'settings':
      router.push('/user/settings')
      break
    case 'logout':
      handleLogout()
      break
  }
}

async function handleLogout() {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    authStore.logout()
    userStore.clearUserInfo()
    ElMessage.success('已退出登录')
    router.push('/login')
  } catch {
    // 取消退出
  }
}

onMounted(async () => {
  // 初始化主题
  themeStore.initTheme()
  
  if (!userStore.userInfo) {
    await userStore.fetchUserInfo()
  }
})
</script>

<style lang="scss" scoped>
/* 整体布局 */
.main-layout { width: 100%; height: 100vh; }
.layout-aside {
  background: var(--aside-bg);
  transition: width 0.3s, background-color 0.3s;
  display: flex;
  flex-direction: column;
  .logo-container {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    border-bottom: 1px solid var(--aside-border);
    .logo-text { color: #fff; font-size: 20px; font-weight: 600; white-space: nowrap; }
  }
  .el-menu { flex: 1; border-right: none; }
  .aside-footer {
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-top: 1px solid var(--aside-border);
    .collapse-btn {
      color: var(--aside-text);
      font-size: 20px;
      cursor: pointer;
      transition: color 0.3s;
      &:hover { color: #409EFF; }
    }
  }
}
.main-container { display: flex; flex-direction: column; }
.layout-header {
  height: 60px;
  background: var(--bg-color-container);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: var(--box-shadow-light);
  z-index: 10;
  transition: background-color 0.3s;
  .header-left { display: flex; align-items: center; }
  .header-right {
    display: flex; align-items: center; gap: 15px;
    .header-search { width: 200px; :deep(.el-input__wrapper) { border-radius: 20px; } }
    .header-icon { 
      font-size: 20px; 
      color: var(--text-color-regular); 
      cursor: pointer; 
      transition: all 0.3s; 
      &:hover { color: #409EFF; }
      
      &.theme-icon {
        &:hover { color: #f5a623; }
      }
    }
    .user-info {
      display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 5px 10px; border-radius: 4px; transition: background 0.3s;
      &:hover { background: var(--bg-color-muted); }
      .user-avatar { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; }
      .user-name { color: var(--text-color-primary); font-size: 14px; }
    }
  }
}

/* --- 标签页样式 --- */
.tabs-container {
  background: var(--bg-color-container);
  padding: 0px 0px 0; 
  transition: background-color 0.3s;
  
  .tabs-scroll-area {
    display: flex;
    gap: 6px;
    overflow-x: auto;
    &::-webkit-scrollbar { height: 0; }
  }

  .custom-tab {
    position: relative;
    cursor: pointer;
    height: 30px;
    padding: 0 20px;
    font-size: 14px;
    color: var(--tab-text);
    background: var(--tab-bg);
    margin-right: 2px;
    transition: all 0.3s cubic-bezier(0.645, 0.045, 0.355, 1);
    display: flex;
    align-items: center;
    border: 1px solid transparent;
    user-select: none;
    flex-shrink: 0;
    
    &.is-active {
      background: var(--tab-bg-active);
      font-weight: 500;
      box-shadow: 0 -2px 5px rgba(0,0,0,0.02); 
    }

    .tab-title { margin-right: 8px; }

    .close-icon {
      font-size: 14px;
      width: 16px;
      height: 16px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s;
      color: var(--text-color-secondary);
      
      &:hover { background: #ff4d4f; color: #fff; }
    }
  }
}

.layout-main {
  background: var(--bg-color-container); 
  padding: 20px;
  overflow-y: auto;
  transition: background-color 0.3s;
}

// 过渡动画
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>