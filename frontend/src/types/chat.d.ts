// 聊天会话
export interface ChatSession {
  id: number
  session_id: string
  title: string
  is_active: boolean
  message_count: number
  created_at: string
  updated_at: string
}

// 聊天消息
export interface ChatMessage {
  id?: number
  role: 'user' | 'assistant' | 'system'
  content: string
  tokens?: number
  created_at?: string
}

// 检索模式类型
export type SearchMode = 'vector' | 'hybrid'

// 聊天请求
export interface ChatRequest {
  message: string
  session_id?: string
  search_mode?: SearchMode
}

// 思考步骤
export interface ThinkingStep {
  step: number
  thought?: string
  action?: string
  action_input?: string
  observation?: string
}

// SSE 数据
export interface SSEData {
  type: 'thinking' | 'content' | 'done' | 'session_id'
  data?: any
}
