import { get } from './index'
import type { ApiResponse, DashboardStatistics, DashboardUserInfo } from '@/types/api'

/**
 * 获取仪表盘统计数据
 */
export function getDashboardStatistics(): Promise<ApiResponse<DashboardStatistics>> {
  return get<DashboardStatistics>('/dashboard/statistics')
}

/**
 * 获取仪表盘用户信息
 */
export function getDashboardUserInfo(): Promise<ApiResponse<DashboardUserInfo>> {
  return get<DashboardUserInfo>('/dashboard/user-info')
}

/**
 * 获取最近活动
 */
export function getRecentActivities(limit: number = 10): Promise<ApiResponse<any[]>> {
  return get('/dashboard/recent-activities', { limit })
}
