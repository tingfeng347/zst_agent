import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

// 配置 NProgress
NProgress.configure({ showSpinner: false })

// 路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/auth/LoginPage.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/pages/auth/RegisterPage.vue'),
    meta: { title: '注册', requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/pages/dashboard/DashboardPage.vue'),
        meta: { title: '工作台', icon: 'Monitor' }
      },
      {
        path: 'chat',
        name: 'Chat',
        component: () => import('@/pages/chat/ChatPage.vue'),
        meta: { title: '智能客服', icon: 'ChatDotRound' }
      },
      {
        path: 'knowledge',
        name: 'Knowledge',
        component: () => import('@/pages/knowledge/KnowledgePage.vue'),
        meta: { title: '知识库', icon: 'Collection' }
      },
      {
        path: 'user/profile',
        name: 'UserProfile',
        component: () => import('@/pages/user/ProfilePage.vue'),
        meta: { title: '个人中心', icon: 'User' }
      },
      {
        path: 'system/users',
        name: 'UserManagement',
        component: () => import('@/pages/system/UserManagementPage.vue'),
        meta: { title: '用户管理', icon: 'User', requiresAdmin: true }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/pages/error/404.vue'),
    meta: { title: '404' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ left: 0, top: 0 })
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  NProgress.start()
  
  // 设置页面标题
  const title = to.meta.title as string
  document.title = title ? `${title} - 智扫通智能客服` : '智扫通智能客服'
  
  const authStore = useAuthStore()
  const userStore = useUserStore()
  const requiresAuth = to.meta.requiresAuth !== false
  const requiresAdmin = to.meta.requiresAdmin === true
  
  if (requiresAuth && !authStore.isLoggedIn) {
    // 需要认证但未登录，跳转到登录页
    next({ path: '/login', query: { redirect: to.fullPath } })
  } else if (!requiresAuth && authStore.isLoggedIn && (to.path === '/login' || to.path === '/register')) {
    // 已登录但访问登录/注册页，跳转到首页
    next({ path: '/' })
  } else if (to.path === '/') {
    // 访问根路径，根据用户角色重定向
    const defaultPath = userStore.userInfo?.is_superuser ? '/dashboard' : '/chat'
    next({ path: defaultPath })
  } else if (requiresAdmin) {
    // 需要管理员权限
    if (!userStore.userInfo) {
      // 用户信息未加载，先加载用户信息
      await userStore.fetchUserInfo()
    }
    
    if (!userStore.userInfo?.is_superuser) {
      // 不是管理员，跳转到智能客服页面
      next({ path: '/chat' })
    } else {
      next()
    }
  } else {
    next()
  }
})

router.afterEach(() => {
  NProgress.done()
})

export default router
