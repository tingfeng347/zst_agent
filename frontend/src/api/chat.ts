import { get, post, del } from './index'
import type { ApiResponse } from '@/types/api'
import type { ChatSession, ChatMessage, SearchMode } from '@/types/chat'
import { useAuthStore } from '@/stores/auth'

/**
 * 获取会话列表
 */
export function getSessions(limit: number = 20): Promise<ApiResponse<ChatSession[]>> {
  return get<ChatSession[]>('/chat/sessions', { limit })
}

/**
 * 创建新会话
 */
export function createSession(title?: string): Promise<ApiResponse<ChatSession>> {
  return post<ChatSession>('/chat/sessions', { title: title || '新对话' })
}

/**
 * 获取会话详情
 */
export function getSessionDetail(sessionId: string): Promise<ApiResponse<{ session: ChatSession; messages: ChatMessage[] }>> {
  return get(`/chat/sessions/${sessionId}`)
}

/**
 * 删除会话
 */
export function deleteSession(sessionId: string): Promise<ApiResponse<void>> {
  return del(`/chat/sessions/${sessionId}`)
}


/**
 * SSE 数据类型
 */
export interface SSEChunk {
  type: 'content' | 'done' | 'session_id'
  data: any
}

/**
 * 流式发送消息回调类型
 */
export interface StreamCallbacks {
  onContent?: (char: string) => void
  onDone?: () => void
  onSessionId?: (sessionId: string) => void
  onError?: (error: Error) => void
}

/**
 * 流式发送消息（SSE）
 * @param message 消息内容
 * @param sessionId 会话ID
 * @param callbacks 回调函数
 * @param searchMode 检索模式：vector=向量检索，hybrid=混合检索
 */
export async function sendMessageStream(
  message: string, 
  sessionId: string | undefined,
  callbacks: StreamCallbacks,
  searchMode: SearchMode = 'vector'
): Promise<void> {
  const authStore = useAuthStore()
  const token = authStore.getToken()
  
  try {
    const response = await fetch('/api/v1/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        message,
        session_id: sessionId,
        search_mode: searchMode
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error('No reader available')
    }

    const decoder = new TextDecoder()
    let buffer = ''

    try {
      while (true) {
        const { done, value } = await reader.read()
        
        if (done) break
        
        buffer += decoder.decode(value, { stream: true })
        
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim()
            
            if (data === '[DONE]') {
              return
            }
            
            try {
              const parsed: SSEChunk = JSON.parse(data)
              
              switch (parsed.type) {
                case 'content':
                  callbacks.onContent?.(parsed.data as string)
                  break
                case 'done':
                  callbacks.onDone?.()
                  break
                case 'session_id':
                  callbacks.onSessionId?.(parsed.data as string)
                  break
              }
            } catch {
              // 忽略解析错误
            }
          }
        }
      }
    } finally {
      // 确保释放 reader
      reader.releaseLock()
    }
  } catch (error: any) {
    callbacks.onError?.(error as Error)
  }
}

/**
 * 获取聊天统计
 */
export function getChatStatistics(): Promise<ApiResponse<{ total_sessions: number; total_messages: number }>> {
  return get('/chat/statistics')
}
