<template>
  <div class="dashboard-page">
    <!-- 欢迎卡片 -->
    <div class="welcome-card">
      <div class="welcome-content">
        <div class="welcome-info">
          <el-tag type="danger" effect="dark" class="role-tag">
            {{ dashboardInfo.role }}
          </el-tag>
          <span class="department">{{ dashboardInfo.department }}</span>
        </div>
        <h1 class="welcome-title">{{ dashboardInfo.greeting }}，{{ dashboardInfo.username }}！</h1>
        <div class="time-info">
          <span class="time">{{ currentTime }}</span>
          <span class="date">{{ dashboardInfo.current_date }}</span>
        </div>
      </div>
      <div class="welcome-decoration">
        <el-icon :size="120" color="rgba(255,255,255,0.2)">
          <Service/>
        </el-icon>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ statistics.today_login_count }}</div>
          <div class="stat-label">今日登录</div>
        </div>
        <div class="stat-icon" style="background: rgba(103, 194, 58, 0.1);">
          <el-icon :size="28" color="#67C23A">
            <User/>
          </el-icon>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ statistics.today_operations }}</div>
          <div class="stat-label">今日操作</div>
        </div>
        <div class="stat-icon" style="background: rgba(0, 206, 209, 0.1);">
          <el-icon :size="28" color="#00CED1">
            <Document/>
          </el-icon>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-row">
      <!-- 聊天统计 -->
      <div class="chart-card">
        <div class="card-header">
          <h3>聊天统计</h3>
        </div>
        <div class="chart-content">
          <div class="chat-stats">
            <div class="chat-stat-item">
              <div class="stat-circle sessions">
                <span class="number">{{ chatStats.total_sessions }}</span>
              </div>
              <span class="label">会话总数</span>
            </div>
            <div class="chat-stat-item">
              <div class="stat-circle messages">
                <span class="number">{{ chatStats.total_messages }}</span>
              </div>
              <span class="label">消息总数</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 快捷入口 -->
      <div class="chart-card">
        <div class="card-header">
          <h3>快捷入口</h3>
        </div>
        <div class="quick-links">
          <div class="quick-link-item" @click="router.push('/user/profile')">
            <div class="link-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
              <el-icon :size="24" color="#fff">
                <User/>
              </el-icon>
            </div>
            <span>个人中心</span>
          </div>
          <div class="quick-link-item" @click="router.push('/chat')">
            <div class="link-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
              <el-icon :size="24" color="#fff">
                <ChatDotRound/>
              </el-icon>
            </div>
            <span>智能客服</span>
          </div>
          <div class="quick-link-item" @click="router.push('/knowledge')">
            <div class="link-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
              <el-icon :size="24" color="#fff">
                <Document/>
              </el-icon>
            </div>
            <span>知识库</span>
          </div>
          <div class="quick-link-item" @click="router.push('/system/users')">
            <div class="link-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
              <el-icon :size="24" color="#fff">
                <QuestionFilled/>
              </el-icon>
            </div>
            <span>用户管理</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 最近活动 -->
    <div class="activity-card">
      <div class="card-header">
        <h3>最近活动</h3>
        <el-link type="primary">查看更多</el-link>
      </div>
      <div class="activity-list">
        <div
            v-for="(activity, index) in recentActivities"
            :key="index"
            class="activity-item"
        >
          <div class="activity-icon">
            <el-icon :size="16" color="#409EFF">
              <ChatLineRound/>
            </el-icon>
          </div>
          <div class="activity-content">
            <div class="activity-title">{{ activity.title }}</div>
            <div class="activity-desc">{{ activity.content }}</div>
          </div>
          <div class="activity-time">{{ formatTime(activity.created_at) }}</div>
        </div>

        <el-empty v-if="recentActivities.length === 0" description="暂无活动记录"/>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {ref, reactive, onMounted, onUnmounted} from 'vue'
import {useRouter} from 'vue-router'
import {
  Service, Bell, Message, User, Document, ChatDotRound,
  QuestionFilled, ChatLineRound
} from '@element-plus/icons-vue'
import {getDashboardStatistics, getDashboardUserInfo, getRecentActivities} from '@/api/dashboard'
import {getChatStatistics} from '@/api/chat'

const router = useRouter()

// 当前时间
const currentTime = ref('')
let timeInterval: number | null = null

// 仪表盘信息
const dashboardInfo = reactive({
  greeting: '下午好',
  username: '用户',
  role: '普通用户',
  department: '智能客服中心',
  current_date: ''
})

// 统计数据
const statistics = reactive({
  unread_notifications: 0,
  total_notifications: 0,
  today_login_count: 0,
  today_operations: 0
})

// 聊天统计
const chatStats = reactive({
  total_sessions: 0,
  total_messages: 0
})

// 最近活动
const recentActivities = ref<any[]>([])

// 格式化时间
function formatTime(time: string): string {
  if (!time) return ''
  const date = new Date(time)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return date.toLocaleDateString('zh-CN')
}

// 更新时间
function updateTime() {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 获取数据
async function fetchData() {
  try {
    // 获取用户信息
    const userRes = await getDashboardUserInfo()
    if (userRes.code === 200 && userRes.data) {
      Object.assign(dashboardInfo, userRes.data)
    }

    // 获取统计数据
    const statsRes = await getDashboardStatistics()
    if (statsRes.code === 200 && statsRes.data) {
      Object.assign(statistics, statsRes.data)
    }

    // 获取聊天统计
    const chatRes = await getChatStatistics()
    if (chatRes.code === 200 && chatRes.data) {
      Object.assign(chatStats, chatRes.data)
    }

    // 获取最近活动
    const activityRes = await getRecentActivities(5)
    if (activityRes.code === 200 && activityRes.data) {
      recentActivities.value = activityRes.data
    }
  } catch (error) {
    console.error('获取仪表盘数据失败:', error)
  }
}

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  fetchData()
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})
</script>

<style lang="scss" scoped>
.dashboard-page {
  max-width: 1400px;
  margin: 0 auto;
}

.welcome-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 30px;
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  position: relative;
  overflow: hidden;

  .welcome-content {
    position: relative;
    z-index: 1;

    .welcome-info {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 12px;

      .role-tag {
        font-size: 12px;
      }

      .department {
        font-size: 14px;
        opacity: 0.9;
      }
    }

    .welcome-title {
      font-size: 28px;
      font-weight: 600;
      margin: 0 0 15px;
    }

    .time-info {
      display: flex;
      align-items: center;
      gap: 20px;
      font-size: 14px;

      .time {
        font-size: 24px;
        font-weight: 500;
        font-family: 'Consolas', monospace;
      }

      .date {
        opacity: 0.85;
      }
    }
  }

  .welcome-decoration {
    position: absolute;
    right: 30px;
    bottom: -20px;
  }
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 20px;

  .stat-card {
    background: var(--bg-color-container);
    border-radius: 12px;
    padding: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: var(--box-shadow);
    transition: background-color 0.3s;

    .stat-content {
      .stat-number {
        font-size: 32px;
        font-weight: 600;
        color: var(--text-color-primary);
        margin-bottom: 8px;
      }

      .stat-label {
        font-size: 14px;
        color: var(--text-color-secondary);
      }
    }

    .stat-icon {
      width: 56px;
      height: 56px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  }
}

.charts-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 20px;

  .chart-card {
    background: var(--bg-color-container);
    border-radius: 12px;
    padding: 24px;
    box-shadow: var(--box-shadow);
    transition: background-color 0.3s;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;

      h3 {
        font-size: 16px;
        font-weight: 600;
        color: var(--text-color-primary);
        margin: 0;
      }
    }

    .chart-content {
      min-height: 200px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .chat-stats {
      display: flex;
      justify-content: center;
      gap: 60px;

      .chat-stat-item {
        text-align: center;

        .stat-circle {
          width: 120px;
          height: 120px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-bottom: 12px;

          &.sessions {
            background: linear-gradient(135deg, rgba(103, 194, 58, 0.1) 0%, rgba(103, 194, 58, 0.2) 100%);
            border: 3px solid #67C23A;
          }

          &.messages {
            background: linear-gradient(135deg, rgba(64, 158, 255, 0.1) 0%, rgba(64, 158, 255, 0.2) 100%);
            border: 3px solid #409EFF;
          }

          .number {
            font-size: 32px;
            font-weight: 600;
            color: var(--text-color-primary);
          }
        }

        .label {
          font-size: 14px;
          color: var(--text-color-secondary);
        }
      }
    }

    .quick-links {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 20px;

      .quick-link-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 10px;
        padding: 20px;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s;

        &:hover {
          background: var(--bg-color-muted);
          transform: translateY(-2px);
        }

        .link-icon {
          width: 56px;
          height: 56px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        span {
          font-size: 14px;
          color: var(--text-color-regular);
        }
      }
    }
  }
}

.activity-card {
  background: var(--bg-color-container);
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--box-shadow);
  transition: background-color 0.3s;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    h3 {
      font-size: 16px;
      font-weight: 600;
      color: var(--text-color-primary);
      margin: 0;
    }
  }

  .activity-list {
    .activity-item {
      display: flex;
      align-items: flex-start;
      gap: 12px;
      padding: 16px 0;
      border-bottom: 1px solid var(--border-color-light);

      &:last-child {
        border-bottom: none;
      }

      .activity-icon {
        width: 32px;
        height: 32px;
        background: rgba(64, 158, 255, 0.1);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
      }

      .activity-content {
        flex: 1;
        min-width: 0;

        .activity-title {
          font-size: 14px;
          color: var(--text-color-primary);
          margin-bottom: 4px;
        }

        .activity-desc {
          font-size: 13px;
          color: var(--text-color-secondary);
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
      }

      .activity-time {
        font-size: 12px;
        color: var(--text-color-placeholder);
        flex-shrink: 0;
      }
    }
  }
}

// 响应式
@media (max-width: 1200px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: 1fr;
  }
}
</style>
