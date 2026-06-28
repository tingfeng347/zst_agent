import { post } from './index'
import type { ApiResponse } from '@/types/api'
import type { LoginForm, RegisterForm, TokenResponse } from '@/types/auth'

/**
 * 用户登录
 */
export function login(data: LoginForm): Promise<ApiResponse<TokenResponse>> {
  return post<TokenResponse>('/auth/login', data)
}

/**
 * 用户注册
 */
export function register(data: RegisterForm): Promise<ApiResponse<{ user_id: number; username: string }>> {
  return post('/auth/register', data)
}

/**
 * 刷新 Token
 */
export function refreshToken(refresh_token: string): Promise<ApiResponse<TokenResponse>> {
  return post<TokenResponse>('/auth/refresh', { refresh_token })
}

/**
 * 退出登录
 */
export function logout(): Promise<ApiResponse<void>> {
  return post('/auth/logout')
}
