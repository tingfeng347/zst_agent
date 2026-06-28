import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'
import type { ApiResponse } from '@/types/api'

// 创建 axios 实例
const request: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 300000,
  headers: {
    'Content-Type': 'application/json'
  }
})

type RetryableRequestConfig = AxiosRequestConfig & {
  _retry?: boolean
}

function redirectToLogin() {
  const currentRoute = router.currentRoute.value

  if (currentRoute.path === '/login') return

  router.replace({
    path: '/login',
    query: currentRoute.meta.requiresAuth === false ? {} : { redirect: currentRoute.fullPath }
  })
}

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    const token = authStore.getToken()
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const res = response.data
    
    // 业务错误处理
    if (res.code !== 200) {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    
    return response
  },
  async (error) => {
    const { response, config } = error
    const retryConfig = config as RetryableRequestConfig | undefined
    
    if (response) {
      const requestUrl = retryConfig?.url || ''
      const isLoginRequest = requestUrl.includes('/auth/login')
      const isRefreshRequest = requestUrl.includes('/auth/refresh')
      
      switch (response.status) {
        case 400:
          // 400 错误，显示后端返回的详细错误信息
          ElMessage.error(response.data?.detail || '请求参数错误')
          break
        case 401:
          // 如果是登录接口的 401 错误，直接显示后端返回的错误信息
          if (isLoginRequest) {
            ElMessage.error(response.data?.detail || '用户名或密码错误')
          } else if (isRefreshRequest) {
            // refresh token 自身失效时不能再次刷新，否则会形成 401 循环
            const authStore = useAuthStore()
            authStore.logout()
            ElMessage.error('登录已过期，请重新登录')
            redirectToLogin()
          } else {
            // Token 过期，尝试刷新
            const authStore = useAuthStore()
            if (retryConfig?._retry) {
              authStore.logout()
              ElMessage.error('登录已过期，请重新登录')
              redirectToLogin()
              break
            }

            if (retryConfig) {
              retryConfig._retry = true
            }

            const refreshed = await authStore.refresh()
            
            if (!refreshed) {
              ElMessage.error('登录已过期，请重新登录')
              authStore.logout()
              redirectToLogin()
              break
            }

            if (retryConfig) {
              return request(retryConfig)
            }
          }
          break
        case 403:
          ElMessage.error('没有权限访问')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(response.data?.detail || response.data?.message || '请求失败')
      }
    } else {
      ElMessage.error('网络错误，请检查网络连接')
    }
    
    return Promise.reject(error)
  }
)

// 封装请求方法
export async function get<T>(url: string, params?: object): Promise<ApiResponse<T>> {
  const response = await request.get<ApiResponse<T>>(url, { params })
  return response.data
}

export async function post<T>(url: string, data?: object): Promise<ApiResponse<T>> {
  const response = await request.post<ApiResponse<T>>(url, data)
  return response.data
}

export async function put<T>(url: string, data?: object): Promise<ApiResponse<T>> {
  const response = await request.put<ApiResponse<T>>(url, data)
  return response.data
}

export async function del<T>(url: string, params?: object): Promise<ApiResponse<T>> {
  const response = await request.delete<ApiResponse<T>>(url, { params })
  return response.data
}

export default request
