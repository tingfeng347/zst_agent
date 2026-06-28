// 登录表单
export interface LoginForm {
  username: string
  password: string
}

// 注册表单
export interface RegisterForm {
  username: string
  email: string
  password: string
  nickname?: string
}

// Token 响应
export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

// 用户信息
export interface UserInfo {
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
}
