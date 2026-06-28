import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getSessions, getSessionDetail, createSession, deleteSession } from '@/api/chat'
import type { ChatSession, ChatMessage } from '@/types/chat'

export const useChatStore = defineStore('chat', () => {
  // State
  const sessions = ref<ChatSession[]>([])
  const currentSessionId = ref<string>('')
  const messages = ref<ChatMessage[]>([])
  const isLoading = ref(false)

  // Getters
  const currentSession = computed(() => 
    sessions.value.find(s => s.session_id === currentSessionId.value)
  )

  // Actions
  async function fetchSessions() {
    try {
      const res = await getSessions()
      if (res.code === 200 && res.data) {
        sessions.value = res.data
      }
    } catch (error) {
      console.error('获取会话列表失败:', error)
    }
  }

  async function loadSession(sessionId: string) {
    currentSessionId.value = sessionId
    try {
      const res = await getSessionDetail(sessionId)
      if (res.code === 200 && res.data) {
        messages.value = res.data.messages || []
      }
    } catch (error) {
      console.error('加载会话失败:', error)
    }
  }

  async function newSession(title?: string) {
    try {
      const res = await createSession(title)
      if (res.code === 200 && res.data) {
        const session = res.data as ChatSession
        sessions.value.unshift(session)
        currentSessionId.value = session.session_id
        messages.value = []
        return session.session_id
      }
    } catch (error) {
      console.error('创建会话失败:', error)
    }
    return ''
  }

  async function removeSession(sessionId: string) {
    try {
      const res = await deleteSession(sessionId)
      if (res.code === 200) {
        sessions.value = sessions.value.filter(s => s.session_id !== sessionId)
        if (currentSessionId.value === sessionId) {
          currentSessionId.value = sessions.value[0]?.session_id || ''
          messages.value = []
        }
      }
    } catch (error) {
      console.error('删除会话失败:', error)
    }
  }

  function addMessage(message: ChatMessage) {
    messages.value.push(message)
  }

  function updateLastMessage(content: string) {
    if (messages.value.length > 0) {
      const lastMsg = messages.value[messages.value.length - 1]
      if (lastMsg.role === 'assistant') {
        lastMsg.content = content
      }
    }
  }

  function setSessionId(sessionId: string) {
    currentSessionId.value = sessionId
  }

  function clearMessages() {
    messages.value = []
  }

  return {
    sessions,
    currentSessionId,
    messages,
    isLoading,
    currentSession,
    fetchSessions,
    loadSession,
    newSession,
    removeSession,
    addMessage,
    updateLastMessage,
    setSessionId,
    clearMessages
  }
})
