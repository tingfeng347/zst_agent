<template>
  <div class="profile-page">
    <el-row :gutter="20">
      <!-- 左侧用户信息卡片 -->
      <el-col :xs="24" :sm="24" :md="8" :lg="6">
        <div class="user-card">
          <div class="user-header">
            <el-avatar :size="100" class="user-avatar">
              {{ userStore.userInfo?.nickname?.charAt(0) || userStore.userInfo?.username?.charAt(0) || 'U' }}
            </el-avatar>
            <h2 class="user-name">{{ userStore.userInfo?.nickname || userStore.userInfo?.username }}</h2>
            <el-tag :type="userStore.userInfo?.is_superuser ? 'danger' : 'info'" size="small">
              {{ userStore.userInfo?.is_superuser ? '超级管理员' : '普通用户' }}
            </el-tag>
          </div>

          <el-divider />

          <div class="user-info-list">
            <div class="info-item">
              <el-icon><User /></el-icon>
              <span class="label">用户名</span>
              <span class="value">{{ userStore.userInfo?.username }}</span>
            </div>
            <div class="info-item">
              <el-icon><Message /></el-icon>
              <span class="label">邮箱</span>
              <span class="value">{{ userStore.userInfo?.email }}</span>
            </div>
            <div class="info-item">
              <el-icon><Phone /></el-icon>
              <span class="label">手机</span>
              <span class="value">{{ userStore.userInfo?.phone || '未设置' }}</span>
            </div>
            <div class="info-item">
              <el-icon><Calendar /></el-icon>
              <span class="label">注册时间</span>
              <span class="value">{{ formatDate(userStore.userInfo?.created_at) }}</span>
            </div>
            <div class="info-item">
              <el-icon><Clock /></el-icon>
              <span class="label">最后登录</span>
              <span class="value">{{ formatDate(userStore.userInfo?.last_login) }}</span>
            </div>
          </div>
        </div>
      </el-col>

      <!-- 右侧设置区域 -->
      <el-col :xs="24" :sm="24" :md="16" :lg="18">
        <el-tabs v-model="activeTab" class="profile-tabs">
          <!-- 基本信息 -->
          <el-tab-pane label="基本信息" name="basic">
            <div class="tab-content">
              <el-form
                ref="basicFormRef"
                :model="basicForm"
                :rules="basicRules"
                label-width="100px"
                class="profile-form"
              >
                <el-form-item label="昵称" prop="nickname">
                  <el-input v-model="basicForm.nickname" placeholder="请输入昵称" />
                </el-form-item>

                <el-form-item label="头像URL" prop="avatar">
                  <el-input v-model="basicForm.avatar" placeholder="请输入头像URL" />
                </el-form-item>

                <el-form-item label="手机号" prop="phone">
                  <el-input v-model="basicForm.phone" placeholder="请输入手机号" />
                </el-form-item>

                <el-form-item>
                  <el-button type="primary" :loading="basicLoading" @click="handleUpdateBasic">
                    保存修改
                  </el-button>
                </el-form-item>
              </el-form>
            </div>
          </el-tab-pane>

          <!-- 修改密码 -->
          <el-tab-pane label="修改密码" name="password">
            <div class="tab-content">
              <el-form
                ref="passwordFormRef"
                :model="passwordForm"
                :rules="passwordRules"
                label-width="100px"
                class="profile-form"
              >
                <el-form-item label="旧密码" prop="old_password">
                  <el-input
                    v-model="passwordForm.old_password"
                    type="password"
                    placeholder="请输入旧密码"
                    show-password
                  />
                </el-form-item>

                <el-form-item label="新密码" prop="new_password">
                  <el-input
                    v-model="passwordForm.new_password"
                    type="password"
                    placeholder="请输入新密码"
                    show-password
                  />
                </el-form-item>

                <el-form-item label="确认密码" prop="confirm_password">
                  <el-input
                    v-model="passwordForm.confirm_password"
                    type="password"
                    placeholder="请确认新密码"
                    show-password
                  />
                </el-form-item>

                <el-form-item>
                  <el-button type="primary" :loading="passwordLoading" @click="handleChangePassword">
                    修改密码
                  </el-button>
                </el-form-item>
              </el-form>
            </div>
          </el-tab-pane>

          <!-- 登录日志 -->
          <el-tab-pane label="登录日志" name="logs">
            <div class="tab-content">
              <el-table :data="loginLogs" stripe style="width: 100%">
                <el-table-column prop="ip_address" label="IP地址" width="150" />
                <el-table-column prop="location" label="登录地点" width="150">
                  <template #default="{ row }">
                    {{ row.location || '未知' }}
                  </template>
                </el-table-column>
                <el-table-column prop="browser" label="浏览器" width="120">
                  <template #default="{ row }">
                    {{ row.browser || '未知' }}
                  </template>
                </el-table-column>
                <el-table-column prop="os" label="操作系统" width="120">
                  <template #default="{ row }">
                    {{ row.os || '未知' }}
                  </template>
                </el-table-column>
                <el-table-column prop="status" label="状态" width="80">
                  <template #default="{ row }">
                    <el-tag :type="row.status ? 'success' : 'danger'" size="small">
                      {{ row.status ? '成功' : '失败' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="created_at" label="登录时间" min-width="180">
                  <template #default="{ row }">
                    {{ formatDate(row.created_at) }}
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { User, Message, Phone, Calendar, Clock } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { updateUserInfo, changePassword, getLoginLogs } from '@/api/user'

const userStore = useUserStore()

const activeTab = ref('basic')
const basicFormRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()
const basicLoading = ref(false)
const passwordLoading = ref(false)
const loginLogs = ref<any[]>([])

// 基本信息表单
const basicForm = reactive({
  nickname: '',
  avatar: '',
  phone: ''
})

// 密码表单
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// 验证规则
const basicRules: FormRules = {
  nickname: [
    { max: 50, message: '昵称不能超过50个字符', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ]
}

const validateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (value !== passwordForm.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules: FormRules = {
  old_password: [
    { required: true, message: '请输入旧密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 格式化日期
function formatDate(date?: string): string {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

// 初始化表单数据
function initFormData() {
  if (userStore.userInfo) {
    basicForm.nickname = userStore.userInfo.nickname || ''
    basicForm.avatar = userStore.userInfo.avatar || ''
    basicForm.phone = userStore.userInfo.phone || ''
  }
}

// 更新基本信息
async function handleUpdateBasic() {
  const valid = await basicFormRef.value?.validate()
  if (!valid) return

  basicLoading.value = true
  try {
    const res = await updateUserInfo(basicForm)
    if (res.code === 200) {
      ElMessage.success('更新成功')
      await userStore.fetchUserInfo()
    }
  } catch (error: any) {
    ElMessage.error(error.message || '更新失败')
  } finally {
    basicLoading.value = false
  }
}

// 修改密码
async function handleChangePassword() {
  const valid = await passwordFormRef.value?.validate()
  if (!valid) return

  passwordLoading.value = true
  try {
    const res = await changePassword({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password
    })
    if (res.code === 200) {
      ElMessage.success('密码修改成功')
      passwordFormRef.value?.resetFields()
    }
  } catch (error: any) {
    ElMessage.error(error.message || '修改失败')
  } finally {
    passwordLoading.value = false
  }
}

// 获取登录日志
async function fetchLoginLogs() {
  try {
    const res = await getLoginLogs(20)
    if (res.code === 200 && res.data) {
      loginLogs.value = res.data
    }
  } catch (error) {
    console.error('获取登录日志失败:', error)
  }
}

// 监听用户信息变化
watch(() => userStore.userInfo, () => {
  initFormData()
}, { immediate: true })

// 监听标签页切换
watch(activeTab, (tab) => {
  if (tab === 'logs' && loginLogs.value.length === 0) {
    fetchLoginLogs()
  }
})

onMounted(() => {
  if (!userStore.userInfo) {
    userStore.fetchUserInfo()
  }
})
</script>

<style lang="scss" scoped>
.profile-page {
  .user-card {
    position: relative;
    overflow: hidden;
    background: var(--bg-color-container);
    border-radius: 12px;
    padding: 24px;
    box-shadow: var(--box-shadow);
    border: 1px solid var(--border-color-light);
    transition: background-color 0.3s;

    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 86px;
      background: linear-gradient(135deg, rgba(64, 158, 255, 0.18), rgba(103, 194, 58, 0.08));
      pointer-events: none;
    }

    .user-header {
      text-align: center;
      padding: 24px 0 16px;
      position: relative;
      z-index: 1;

      .user-avatar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #fff;
        font-size: 36px;
        margin-bottom: 16px;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
      }

      .user-name {
        font-size: 20px;
        font-weight: 600;
        color: var(--text-color-primary);
        margin: 0 0 12px;
      }
    }

    .user-info-list {
      margin-top: 10px;
      .info-item {
        display: flex;
        align-items: center;
        padding: 10px 12px;
        border: 1px solid var(--border-color-light);
        border-radius: 8px;
        background: var(--bg-color-muted);
        margin-bottom: 10px;
        transition: background-color 0.3s, border-color 0.3s;

        &:last-child { margin-bottom: 0; }

        .el-icon {
          color: var(--text-color-secondary);
          margin-right: 12px;
        }

        .label {
          color: var(--text-color-secondary);
          font-size: 14px;
          width: 70px;
        }

        .value {
          flex: 1;
          color: var(--text-color-primary);
          font-size: 14px;
          text-align: right;
        }
      }
    }
  }

  .profile-tabs {
    background: var(--bg-color-container);
    border-radius: 12px;
    box-shadow: var(--box-shadow);
    border: 1px solid var(--border-color-light);
    transition: background-color 0.3s;

    :deep(.el-tabs__header) {
      padding: 0 20px;
      margin: 0;
      background: var(--bg-color-container);
      border-radius: 12px 12px 0 0;
    }
    
    :deep(.el-tabs__item) {
      color: var(--text-color-regular);
      
      &.is-active {
        color: var(--el-color-primary);
      }
      
      &:hover {
        color: var(--el-color-primary);
      }
    }
    
    :deep(.el-tabs__nav-wrap::after) {
      background-color: var(--border-color-light);
    }

    :deep(.el-tabs__content) {
      padding: 0;
    }
  }

  .tab-content {
    padding: 24px;
    background: var(--bg-color-container);

    .profile-form {
      max-width: 500px;
    }
  }
}
</style>
