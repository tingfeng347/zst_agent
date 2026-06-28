<template>
  <div class="chat-page">
    <div class="chat-sidebar">
      <div class="sidebar-header">
        <div class="new-chat-card" @click="handleNewChat">
          <div class="icon-wrapper">
            <el-icon><Plus /></el-icon>
          </div>
          <span class="text">新建对话</span>
        </div>
      </div>

      <div class="session-list">
        <div
          v-for="session in chatStore.sessions"
          :key="session.session_id"
          class="session-item"
          :class="{ 
            active: session.session_id === chatStore.currentSessionId,
            responding: respondingSessionIds.has(session.session_id)
          }"
          @click="handleSelectSession(session.session_id)"
        >
          <el-icon v-if="respondingSessionIds.has(session.session_id)" class="session-icon responding-icon"><Loading /></el-icon>
          <el-icon v-else class="session-icon"><ChatLineRound /></el-icon>
          <span class="session-title">{{ session.title }}</span>
          <el-icon class="session-delete" @click.stop="handleDeleteSession(session.session_id)">
            <Delete />
          </el-icon>
        </div>

        <el-empty v-if="chatStore.sessions.length === 0" description="暂无对话" :image-size="60" />
      </div>
    </div>

    <div class="chat-main">
      <div class="messages-container" ref="messagesRef">
        <div class="messages-wrapper">
          <div v-if="messages.length === 0 && !isTyping" class="welcome-message">
            <div class="welcome-header">
              <div class="logo-box">
                <el-icon :size="40" color="#fff"><Service /></el-icon>
              </div>
              <h2>智扫通智能客服</h2>
              <p>你好！我是您的专属助手，请问有什么可以帮您？</p>
            </div>
            
            <div class="quick-questions-grid">
              <div
                v-for="(q, index) in quickQuestions"
                :key="index"
                class="quick-card"
                @click="sendQuickQuestion(q)"
              >
                <div class="card-icon" :class="`icon-style-${index % 4}`">
                  <el-icon><Document /></el-icon>
                </div>
                <div class="card-content">
                  <span class="card-text">{{ q }}</span>
                  <span class="card-sub">点击咨询</span>
                </div>
              </div>
            </div>
          </div>

          <div
            v-for="(msg, index) in messages"
            :key="index"
            class="message-item"
            :class="msg.role"
          >
            <div class="message-avatar">
              <el-avatar v-if="msg.role === 'user'" :size="40" class="user-avatar">
                {{ userStore.userInfo?.nickname?.charAt(0) || 'U' }}
              </el-avatar>
              <el-avatar v-else :size="40" class="bot-avatar">
                <el-icon><Service /></el-icon>
              </el-avatar>
            </div>

            <div class="message-content">
              <div class="message-header">
                <span class="message-role">{{ msg.role === 'user' ? '我' : '智能客服' }}</span>
                <span class="message-time">{{ formatTime(msg.created_at) }}</span>
              </div>
              <div class="message-bubble-wrapper">
                <div class="message-bubble" v-html="renderMarkdown(msg.content)"></div>
                <el-button 
                  v-if="msg.role === 'user'" 
                  size="small" 
                  type="primary" 
                  link 
                  class="repeat-button"
                  @click.stop="handleRepeatMessage(msg)"
                >
                  <el-icon><Refresh /></el-icon>
                </el-button>
              </div>
            </div>
          </div>

          <div v-if="isTyping" class="message-item assistant">
            <div class="message-avatar">
              <el-avatar :size="40" class="bot-avatar"><el-icon><Service /></el-icon></el-avatar>
            </div>
            <div class="message-content">
              <div class="message-header"><span class="message-role">智能客服</span></div>
              <div class="message-bubble">
                <span v-if="streamContent">{{ streamContent }}</span>
                <span v-else class="thinking-text">正在思考中</span>
                <span class="typing-cursor">|</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="input-container">
        <div class="input-box-shadow">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="1"
            :autosize="{ minRows: 1, maxRows: 4 }"
            placeholder="输入您的问题，按 Enter 发送..."
            resize="none"
            class="custom-input"
            @keydown.enter.exact.prevent="handleSend"
          />
          <el-button
            type="primary"
            :icon="Promotion"
            circle
            class="send-btn"
            :disabled="!inputMessage.trim() || isTyping"
            @click="handleSend"
          />
          <el-button
            type="danger"
            :icon="Delete"
            circle
            class="clear-btn"
            @click="handleClearSession"
          />
        </div>
        <div class="input-tips">
          <span>内容由 AI 生成，仅供参考</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, ChatLineRound, Delete, Service, Promotion, Document, Loading, Refresh } from '@element-plus/icons-vue'
import { marked } from 'marked'
import { useChatStore } from '@/stores/chat'
import { useUserStore } from '@/stores/user'
import { sendMessageStream } from '@/api/chat'
import type { ChatMessage } from '@/types/chat'

const chatStore = useChatStore()
const userStore = useUserStore()

const messagesRef = ref<HTMLElement>()
const inputMessage = ref('')

// 每个会话的消息缓存 Map<sessionId, messages[]>
const sessionMessagesCache = ref<Map<string, ChatMessage[]>>(new Map())

// 每个会话的流式内容 Map<sessionId, streamContent>
const sessionStreamContent = ref<Map<string, string>>(new Map())

// 正在响应的会话ID集合
const respondingSessionIds = ref<Set<string>>(new Set())

// 当前会话的消息列表（计算属性）
const messages = computed(() => {
  const sessionId = chatStore.currentSessionId
  if (!sessionId) return []
  return sessionMessagesCache.value.get(sessionId) || []
})

// 当前会话的流式内容（计算属性）
const streamContent = computed(() => {
  const sessionId = chatStore.currentSessionId
  if (!sessionId) return ''
  return sessionStreamContent.value.get(sessionId) || ''
})

// 当前会话是否正在输入（计算属性）
const isTyping = computed(() => {
  const sessionId = chatStore.currentSessionId
  if (!sessionId) return false
  return respondingSessionIds.value.has(sessionId)
})

// 快捷问题
const quickQuestions = [
  '小户型适合哪种扫地机器人？',
  '扫地机器人如何维护保养？',
  '机器人充不上电怎么办？',
  '如何清理尘盒和滤网？'
]

// 渲染 Markdown
function renderMarkdown(content: string): string {
  if (!content) return ''
  return marked.parse(content) as string
}

// 格式化时间
function formatTime(time?: string): string {
  if (!time) return ''
  const date = new Date(time)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

// 滚动到底部
function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

// 获取或初始化会话消息
function getOrInitSessionMessages(sessionId: string): ChatMessage[] {
  if (!sessionMessagesCache.value.has(sessionId)) {
    sessionMessagesCache.value.set(sessionId, [])
  }
  return sessionMessagesCache.value.get(sessionId)!
}

// 创建新对话
async function handleNewChat() {
  await chatStore.newSession()
  const sessionId = chatStore.currentSessionId
  if (sessionId) {
    sessionMessagesCache.value.set(sessionId, [])
  }
}

// 选择会话
async function handleSelectSession(sessionId: string) {
  // 如果切换到同一个会话，不做处理
  if (sessionId === chatStore.currentSessionId) return
  
  await chatStore.loadSession(sessionId)
  
  // 如果该会话没有缓存，从 store 加载
  if (!sessionMessagesCache.value.has(sessionId)) {
    sessionMessagesCache.value.set(sessionId, [...chatStore.messages])
  }
  
  scrollToBottom()
}

// 删除会话
async function handleDeleteSession(sessionId: string) {
  try {
    await ElMessageBox.confirm('确定要删除这个对话吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    // 清理该会话的缓存
    sessionMessagesCache.value.delete(sessionId)
    sessionStreamContent.value.delete(sessionId)
    respondingSessionIds.value.delete(sessionId)
    
    await chatStore.removeSession(sessionId)
    
    // 如果删除的是当前会话，清空显示
    if (chatStore.currentSessionId === '' || chatStore.sessions.length === 0) {
      // 会话已被删除，chatStore 会处理
    }
    
    ElMessage.success('删除成功')
  } catch {
    // 取消删除
  }
}

// 发送快捷问题
function sendQuickQuestion(question: string) {
  inputMessage.value = question
  handleSend()
}

// 重复发送消息
async function handleRepeatMessage(msg: ChatMessage) {
  const message = msg.content.trim()
  if (!message) return
  
  // 获取当前会话ID，如果没有则需要创建
  let targetSessionId = chatStore.currentSessionId
  
  // 如果当前会话正在响应，不允许发送新消息
  if (targetSessionId && respondingSessionIds.value.has(targetSessionId)) {
    ElMessage.warning('请等待当前回复完成')
    return
  }

  try {
    // 获取目标会话的消息列表
    const targetMessages = getOrInitSessionMessages(targetSessionId || 'temp')
    
    // 流式接收响应，直接使用原消息内容
    await sendMessageStream(message, targetSessionId || undefined, {
      onContent: (char) => {
        // 获取实际的会话ID（可能在 onSessionId 中更新）
        const actualSessionId = targetSessionId || 'temp'
        
        // 更新该会话的流式内容
        const currentContent = sessionStreamContent.value.get(actualSessionId) || ''
        sessionStreamContent.value.set(actualSessionId, currentContent + char)
        
        // 只有当前显示的会话才滚动
        if (actualSessionId === chatStore.currentSessionId) {
          scrollToBottom()
        }
      },
      onDone: () => {
        const actualSessionId = targetSessionId || 'temp'
        const finalContent = sessionStreamContent.value.get(actualSessionId) || ''
        
        // 获取该会话的消息列表
        const sessionMessages = sessionMessagesCache.value.get(actualSessionId)
        if (sessionMessages) {
          const assistantMessage: ChatMessage = {
            role: 'assistant',
            content: finalContent,
            created_at: new Date().toISOString()
          }
          sessionMessages.push(assistantMessage)
        }
        
        // 清理状态
        sessionStreamContent.value.delete(actualSessionId)
        respondingSessionIds.value.delete(actualSessionId)
        
        // 刷新会话列表以获取更新后的标题
        chatStore.fetchSessions()
        
        // 只有当前显示的会话才滚动
        if (actualSessionId === chatStore.currentSessionId) {
          scrollToBottom()
        }
      },
      onSessionId: (sessionId) => {
        // 更新目标会话ID
        const oldSessionId = targetSessionId || 'temp'
        targetSessionId = sessionId
        
        // 如果之前是临时会话，需要迁移数据
        if (oldSessionId === 'temp' || oldSessionId !== sessionId) {
          // 迁移流式内容
          const oldContent = sessionStreamContent.value.get(oldSessionId)
          if (oldContent) {
            sessionStreamContent.value.set(sessionId, oldContent)
            sessionStreamContent.value.delete(oldSessionId)
          }
          
          // 迁移响应状态
          if (respondingSessionIds.value.has(oldSessionId)) {
            respondingSessionIds.value.delete(oldSessionId)
          }
        }
        
        // 标记该会话正在响应
        respondingSessionIds.value.add(sessionId)
        
        // 更新 store 中的会话ID 并刷新会话列表（获取更新后的标题）
        if (!chatStore.currentSessionId) {
          chatStore.setSessionId(sessionId)
        }
        // 刷新会话列表以获取新标题
        chatStore.fetchSessions()
      },
      onError: (error) => {
        console.error('发送消息失败:', error)
        
        const actualSessionId = targetSessionId || 'temp'
        
        // 获取该会话的消息列表
        const sessionMessages = sessionMessagesCache.value.get(actualSessionId)
        if (sessionMessages) {
          const errorMessage: ChatMessage = {
            role: 'assistant',
            content: '抱歉，发送消息时出现错误，请稍后重试。',
            created_at: new Date().toISOString()
          }
          sessionMessages.push(errorMessage)
        }
        
        // 清理状态
        sessionStreamContent.value.delete(actualSessionId)
        respondingSessionIds.value.delete(actualSessionId)
        
        if (actualSessionId === chatStore.currentSessionId) {
          scrollToBottom()
        }
      }
    })
  } catch (error: any) {
    console.error('发送消息失败:', error)
    
    const actualSessionId = targetSessionId || 'temp'
    sessionStreamContent.value.delete(actualSessionId)
    respondingSessionIds.value.delete(actualSessionId)
  }
}

// 发送消息
async function handleSend() {
  const message = inputMessage.value.trim()
  if (!message) return
  
  // 获取当前会话ID，如果没有则需要创建
  let targetSessionId = chatStore.currentSessionId
  
  // 如果当前会话正在响应，不允许发送新消息
  if (targetSessionId && respondingSessionIds.value.has(targetSessionId)) {
    ElMessage.warning('请等待当前回复完成')
    return
  }

  inputMessage.value = ''
  
  // 获取目标会话的消息列表
  const targetMessages = getOrInitSessionMessages(targetSessionId || 'temp')

  // 添加用户消息
  const userMessage: ChatMessage = {
    role: 'user',
    content: message,
    created_at: new Date().toISOString()
  }
  targetMessages.push(userMessage)
  scrollToBottom()

  try {
    // 流式接收响应
    await sendMessageStream(message, targetSessionId || undefined, {
      onContent: (char) => {
        // 获取实际的会话ID（可能在 onSessionId 中更新）
        const actualSessionId = targetSessionId || 'temp'
        
        // 更新该会话的流式内容
        const currentContent = sessionStreamContent.value.get(actualSessionId) || ''
        sessionStreamContent.value.set(actualSessionId, currentContent + char)
        
        // 只有当前显示的会话才滚动
        if (actualSessionId === chatStore.currentSessionId) {
          scrollToBottom()
        }
      },
      onDone: () => {
        const actualSessionId = targetSessionId || 'temp'
        const finalContent = sessionStreamContent.value.get(actualSessionId) || ''
        
        // 获取该会话的消息列表
        const sessionMessages = sessionMessagesCache.value.get(actualSessionId)
        if (sessionMessages) {
          const assistantMessage: ChatMessage = {
            role: 'assistant',
            content: finalContent,
            created_at: new Date().toISOString()
          }
          sessionMessages.push(assistantMessage)
        }
        
        // 清理状态
        sessionStreamContent.value.delete(actualSessionId)
        respondingSessionIds.value.delete(actualSessionId)
        
        // 刷新会话列表以获取更新后的标题
        chatStore.fetchSessions()
        
        // 只有当前显示的会话才滚动
        if (actualSessionId === chatStore.currentSessionId) {
          scrollToBottom()
        }
      },
      onSessionId: (sessionId) => {
        // 更新目标会话ID
        const oldSessionId = targetSessionId || 'temp'
        targetSessionId = sessionId
        
        // 如果之前是临时会话，需要迁移数据
        if (oldSessionId === 'temp' || oldSessionId !== sessionId) {
          // 迁移消息
          const oldMessages = sessionMessagesCache.value.get(oldSessionId)
          if (oldMessages) {
            sessionMessagesCache.value.set(sessionId, oldMessages)
            sessionMessagesCache.value.delete(oldSessionId)
          }
          
          // 迁移流式内容
          const oldContent = sessionStreamContent.value.get(oldSessionId)
          if (oldContent) {
            sessionStreamContent.value.set(sessionId, oldContent)
            sessionStreamContent.value.delete(oldSessionId)
          }
          
          // 迁移响应状态
          if (respondingSessionIds.value.has(oldSessionId)) {
            respondingSessionIds.value.delete(oldSessionId)
          }
        }
        
        // 标记该会话正在响应
        respondingSessionIds.value.add(sessionId)
        
        // 更新 store 中的会话ID 并刷新会话列表（获取更新后的标题）
        if (!chatStore.currentSessionId) {
          chatStore.setSessionId(sessionId)
        }
        // 刷新会话列表以获取新标题
        chatStore.fetchSessions()
      },
      onError: (error) => {
        console.error('发送消息失败:', error)
        
        const actualSessionId = targetSessionId || 'temp'
        
        // 获取该会话的消息列表
        const sessionMessages = sessionMessagesCache.value.get(actualSessionId)
        if (sessionMessages) {
          const errorMessage: ChatMessage = {
            role: 'assistant',
            content: '抱歉，发送消息时出现错误，请稍后重试。',
            created_at: new Date().toISOString()
          }
          sessionMessages.push(errorMessage)
        }
        
        // 清理状态
        sessionStreamContent.value.delete(actualSessionId)
        respondingSessionIds.value.delete(actualSessionId)
        
        if (actualSessionId === chatStore.currentSessionId) {
          scrollToBottom()
        }
      }
    })
  } catch (error: any) {
    console.error('发送消息失败:', error)
    
    const actualSessionId = targetSessionId || 'temp'
    sessionStreamContent.value.delete(actualSessionId)
    respondingSessionIds.value.delete(actualSessionId)
  }
}

// 监听消息变化
watch(messages, () => {
  scrollToBottom()
}, { deep: true })

// 清空当前会话
async function handleClearSession() {
  try {
    await ElMessageBox.confirm('确定要清空当前对话吗？此操作不可恢复！', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'error'
    })
    
    const currentSessionId = chatStore.currentSessionId
    if (currentSessionId) {
      // 清理缓存
      sessionMessagesCache.value.delete(currentSessionId)
      sessionStreamContent.value.delete(currentSessionId)
      respondingSessionIds.value.delete(currentSessionId)
      
      // 删除会话
      await chatStore.removeSession(currentSessionId)
      
      // 创建新会话
      await chatStore.newSession()
      const newSessionId = chatStore.currentSessionId
      if (newSessionId) {
        sessionMessagesCache.value.set(newSessionId, [])
      }
      
      ElMessage.success('会话已清空')
    }
  } catch {
    // 取消操作
  }
}

// 初始化
onMounted(async () => {
  await chatStore.fetchSessions()
  
  if (chatStore.sessions.length === 0) {
    await chatStore.newSession()
    const sessionId = chatStore.currentSessionId
    if (sessionId) {
      sessionMessagesCache.value.set(sessionId, [])
    }
  } else if (!chatStore.currentSessionId) {
    await chatStore.loadSession(chatStore.sessions[0].session_id)
    const sessionId = chatStore.currentSessionId
    if (sessionId) {
      sessionMessagesCache.value.set(sessionId, [...chatStore.messages])
    }
  } else {
    // 如果已有当前会话ID，确保加载其消息
    await chatStore.loadSession(chatStore.currentSessionId)
    const sessionId = chatStore.currentSessionId
    if (sessionId) {
      sessionMessagesCache.value.set(sessionId, [...chatStore.messages])
    }
  }
})
</script>

<style lang="scss" scoped>
/* 柔和的阴影变量 */
$card-shadow: var(--box-shadow);
$card-hover-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
$radius: 12px;

.chat-page {
  display: flex;
  height: 100%;
  background: var(--bg-color-container);
  overflow: hidden;
  transition: background-color 0.3s;
}

/* 侧边栏 */
.chat-sidebar {
  width: 250px;
  background: var(--bg-color-overlay);
  border: 1px solid var(--border-color-light);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  transition: background-color 0.3s, border-color 0.3s;

  .sidebar-header {
    padding: 15px;
    
    .new-chat-card {
      background: var(--bg-color-container);
      height: 46px;
      border-radius: $radius;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      cursor: pointer;
      box-shadow: $card-shadow;
      transition: all 0.3s;
      border: 1px solid transparent;

      .icon-wrapper {
        width: 25px;
        height: 25px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #fff;
        font-size: 14px;
      }

      .text {
        font-weight: 600;
        color: var(--text-color-primary);
        font-size: 15px;
      }

      &:hover {
        transform: translateY(-2px);
        box-shadow: $card-hover-shadow;
        border-color: var(--border-color);
      }
      
      &:active {
        transform: scale(0.98);
      }
    }
  }

  .session-list {
    flex: 1;
    overflow-y: auto;
    padding: 0 12px 12px;

    .session-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px 16px;
      border-radius: 10px;
      cursor: pointer;
      transition: all 0.2s;
      margin-bottom: 6px;
      color: var(--text-color-regular);

      &:hover {
        background: var(--bg-color-container);
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
      }

      &.active {
        background: var(--bg-color-container);
        color: #409EFF;
        box-shadow: 0 2px 12px rgba(64, 158, 255, 0.15);
        font-weight: 500;
        
        .session-icon { color: #409EFF; }
      }
      
      &.responding {
        .session-title {
          &::after {
            content: '...';
            animation: dots 1.5s infinite;
          }
        }
      }

      .session-icon { 
        font-size: 16px; 
        color: var(--text-color-primary);
      }
      
      .responding-icon {
        animation: spin 1s linear infinite;
        color: #67C23A;
      }
      .session-title { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 14px; }
      .session-delete {
        font-size: 14px;
        opacity: 0;
        transition: opacity 0.3s;
        color: var(--text-color-secondary);
        &:hover { color: #F56C6C; }
      }
      
      &:hover .session-delete { opacity: 1; }
    }
  }
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: var(--bg-color-container);
  transition: background-color 0.3s;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 0px;

  .messages-wrapper {
    max-width: 1000px;
    margin: 0 auto;
  }
}

/* 欢迎页 */
.welcome-message {
  padding: 40px 20px;

  .welcome-header {
    text-align: center;
    margin-bottom: 40px;
    
    .logo-box {
      width: 64px;
      height: 64px;
      background: linear-gradient(135deg, #409EFF, #00B4DB);
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 20px;
      box-shadow: 0 10px 20px rgba(64, 158, 255, 0.3);
    }
    
    h2 { font-size: 24px; color: var(--text-color-primary); margin-bottom: 8px; }
    p { color: var(--text-color-secondary); font-size: 14px; }
  }

  .quick-questions-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;

    .quick-card {
      background: var(--bg-color-container);
      border: 1px solid var(--border-color-light);
      border-radius: $radius;
      padding: 20px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 16px;
      transition: all 0.3s ease;
      box-shadow: 0 2px 8px rgba(0,0,0,0.02);

      &:hover {
        transform: translateY(-3px);
        box-shadow: $card-hover-shadow;
        border-color: #409EFF;
      }

      .card-icon {
        width: 44px;
        height: 44px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        
        &.icon-style-0 { background: rgba(64, 158, 255, 0.1); color: #409EFF; }
        &.icon-style-1 { background: rgba(103, 194, 58, 0.1); color: #67C23A; }
        &.icon-style-2 { background: rgba(230, 162, 60, 0.1); color: #E6A23C; }
        &.icon-style-3 { background: rgba(245, 108, 108, 0.1); color: #F56C6C; }
      }

      .card-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        
        .card-text { font-size: 14px; color: var(--text-color-primary); font-weight: 500; margin-bottom: 4px; }
        .card-sub { font-size: 12px; color: var(--text-color-secondary); }
      }
    }
  }
}

.message-item {
  display: flex;
  gap: 0px;
  margin-bottom: 30px;

  &.user {
    flex-direction: row-reverse;
    padding-left: 30px;
    
    .message-content { 
      align-items: flex-end; 
      
      .message-bubble { 
        background: var(--chat-bg-user); 
        color: var(--chat-text-user); 
        border-radius: 16px 16px 16px 16px;
        box-shadow: 0 2px 12px rgba(64, 158, 255, 0.15);
      }
      
      .message-bubble-wrapper {
        align-self: flex-end;
      }
    }
  }

  &.assistant {
    padding-right: 30px;
    
    .message-content {
      align-items: flex-start;
      
      .message-bubble { 
        background: var(--chat-bg-assistant); 
        color: var(--chat-text-assistant);
        border-radius: 16px 16px 16px 16px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
      }
    }
  }

  .message-avatar {
    flex-shrink: 0;
    .user-avatar { background: var(--user-avatar-bg); color: #fff; }
    .bot-avatar { background: #409EFF; color: #fff; }
  }

  .message-content {
      display: flex;
      flex-direction: column;
      max-width: 75%;

      .message-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 6px;
        font-size: 12px;
        .message-role { color: var(--text-color-regular); font-weight: 500; }
        .message-time { color: var(--text-color-secondary); }
      }

      .message-bubble-wrapper {
        position: relative;
        display: inline-block;

        .repeat-button {
          position: absolute;
          bottom: -24px;
          right: 0;
          font-size: 12px;
          padding: 0;
          margin: 0;
          opacity: 0.7;
          
          &:hover {
            opacity: 1;
          }
        }
      }

      .message-bubble {
        padding: 14px 18px;
        line-height: 1.6;
        font-size: 15px;
        transition: background-color 0.3s, color 0.3s;

        :deep(p) { margin: 0; &:not(:last-child) { margin-bottom: 10px; } }
        :deep(pre) {
          background: #282c34;
          color: #abb2bf;
          padding: 12px;
          border-radius: 8px;
          overflow-x: auto;
          margin: 10px 0;
        }
      }
    }
}

/* 正在思考中文字 */
.thinking-text {
  color: var(--text-color-secondary);
  font-style: italic;
}

/* 底部输入框 */
.input-container {
  padding: 0px 30px;
  background: var(--bg-color-container);
  position: relative;
  transition: background-color 0.3s;
  
  .input-box-shadow {
    background: var(--bg-color-container);
    border-radius: 24px;
    padding: 6px;
    display: flex;
    align-items: flex-end;
    box-shadow: var(--box-shadow);
    border: 1px solid var(--border-color-light);
    transition: all 0.3s;

    &:focus-within {
      box-shadow: 0 6px 20px rgba(64, 158, 255, 0.15);
      border-color: #409EFF;
    }

    .custom-input {
      flex: 1;
      :deep(.el-textarea__inner) {
        border: none;
        box-shadow: none;
        background: transparent;
        padding: 10px 16px;
        font-size: 15px;
        color: var(--text-color-primary);
      }
    }

    .send-btn {
      margin: 0 4px 4px 0;
      width: 36px;
      height: 36px;
      transition: transform 0.2s;
      
      &:hover { transform: scale(1.05); }
    }
    
    .clear-btn {
      margin: 0 0 4px 0;
      width: 36px;
      height: 36px;
      transition: transform 0.2s;
      
      &:hover { transform: scale(1.05); }
    }
  }

  .input-tips {
    text-align: center;
    margin-top: 10px;
    font-size: 12px;
    color: var(--text-color-placeholder);
  }
}

/* 动画 */
.typing-cursor { 
  animation: blink 0.8s infinite; 
  margin-left: 2px;
  color: #409EFF;
  font-weight: bold;
}
@keyframes blink { 
  0%, 100% { opacity: 1; }
  50% { opacity: 0; } 
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
@keyframes dots {
  0%, 20% { content: '.'; }
  40% { content: '..'; }
  60%, 100% { content: '...'; }
}

/* 响应式 */
@media (max-width: 768px) {
  .welcome-message .quick-questions-grid { grid-template-columns: 1fr; }
  .chat-sidebar { width: 64px; }
  .sidebar-header .new-chat-card .text { display: none; }
  .sidebar-header .new-chat-card { width: 36px; height: 36px; padding: 0; border-radius: 50%; }
  .session-title, .session-delete { display: none; }
  .messages-container { padding: 12px; }
}
</style>