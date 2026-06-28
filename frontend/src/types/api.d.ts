// 统一响应格式
export interface ApiResponse<T = any> {
  code: number
  message: string
  data?: T
}

// 分页信息
export interface PageInfo {
  page: number
  page_size: number
  total: number
  total_pages: number
}

// 分页响应
export interface PageResponse<T = any> {
  code: number
  message: string
  data?: T[]
  page_info?: PageInfo
}

// 仪表盘统计
export interface DashboardStatistics {
  unread_notifications: number
  total_notifications: number
  today_login_count: number
  today_operations: number
  total_sessions: number
  total_messages: number
}

// 仪表盘用户信息
export interface DashboardUserInfo {
  greeting: string
  username: string
  role: string
  department: string
  current_time: string
  current_date: string
}
