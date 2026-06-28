import { get, post, put, del } from './index'
import type { ApiResponse } from '@/types/api'

export interface UserManagementItem {
  id: number
  username: string
  email: string
  nickname?: string
  avatar?: string
  phone?: string
  is_active: boolean
  is_superuser: boolean
  login_count: number
  last_login?: string
  created_at: string
  updated_at?: string
}

export interface UserListResponse {
  total: number
  page: number
  page_size: number
  items: UserManagementItem[]
}

export interface UserCreateParams {
  username: string
  email: string
  password: string
  nickname?: string
  phone?: string
  is_superuser: boolean
}

export interface UserUpdateParams {
  nickname?: string
  avatar?: string
  phone?: string
  is_active?: boolean
  is_superuser?: boolean
}

export interface UserListParams {
  page: number
  page_size: number
  keyword?: string
  sort_by?: string
  sort_order?: string
}

/**
 * 获取用户列表
 */
export function getUserList(params: UserListParams): Promise<ApiResponse<UserListResponse>> {
  return get('/admin/users/list', params)
}

/**
 * 获取用户详情
 */
export function getUserDetail(userId: number): Promise<ApiResponse<UserManagementItem>> {
  return get(`/admin/users/${userId}`)
}

/**
 * 创建用户
 */
export function createUser(data: UserCreateParams): Promise<ApiResponse<UserManagementItem>> {
  return post('/admin/users', data)
}

/**
 * 更新用户
 */
export function updateUser(userId: number, data: UserUpdateParams): Promise<ApiResponse<UserManagementItem>> {
  return put(`/admin/users/${userId}`, data)
}

/**
 * 删除用户
 */
export function deleteUser(userId: number): Promise<ApiResponse<void>> {
  return del(`/admin/users/${userId}`)
}

/**
 * 重置用户密码
 */
export function resetUserPassword(userId: number, new_password: string): Promise<ApiResponse<void>> {
  return post(`/admin/users/${userId}/reset-password`, { new_password })
}