import { get, put, post } from './index'
import type { ApiResponse } from '@/types/api'
import type { UserInfo } from '@/types/auth'

/**
 * 获取当前用户信息
 */
export function getUserInfo(): Promise<ApiResponse<UserInfo>> {
  return get<UserInfo>('/user/me')
}

/**
 * 更新用户信息
 */
export function updateUserInfo(data: Partial<UserInfo>): Promise<ApiResponse<UserInfo>> {
  return put<UserInfo>('/user/me', data)
}

/**
 * 修改密码
 */
export function changePassword(data: { old_password: string; new_password: string }): Promise<ApiResponse<void>> {
  return post('/user/change-password', data)
}

/**
 * 获取登录日志
 */
export function getLoginLogs(limit: number = 10): Promise<ApiResponse<any[]>> {
  return get('/user/login-logs', { limit })
}
