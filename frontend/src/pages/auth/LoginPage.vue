<template>
  <div class="login-container">
    <!-- 左侧装饰区域 -->
    <div class="login-left">
      <div class="decoration-content">
        <div class="logo-area">
          <el-icon :size="64" color="#fff"><ChatDotRound /></el-icon>
          <h1>智扫通</h1>
          <p>智能客服管理系统</p>
        </div>
        <div class="feature-list">
          <div class="feature-item">
            <el-icon><CircleCheck /></el-icon>
            <span>AI智能对话，精准解答</span>
          </div>
          <div class="feature-item">
            <el-icon><CircleCheck /></el-icon>
            <span>知识库检索，快速响应</span>
          </div>
          <div class="feature-item">
            <el-icon><CircleCheck /></el-icon>
            <span>多轮对话，上下文理解</span>
          </div>
        </div>
      </div>
      <div class="decoration-circles">
        <div class="circle circle-1"></div>
        <div class="circle circle-2"></div>
        <div class="circle circle-3"></div>
      </div>
    </div>

    <!-- 右侧登录表单 -->
    <div class="login-right">
      <div class="login-form-container">
        <div class="form-header">
          <h2>欢迎登录</h2>
          <p>请输入您的账户信息</p>
        </div>

        <el-form
          ref="formRef"
          :model="loginForm"
          :rules="rules"
          class="login-form"
          size="large"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名或邮箱"
              :prefix-icon="User"
              clearable
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              :prefix-icon="Lock"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>

          <div class="form-options">
            <el-checkbox v-model="rememberMe">记住我</el-checkbox>
            <el-link type="primary" :underline="false">忘记密码？</el-link>
          </div>

          <el-form-item>
            <el-button
              type="primary"
              class="login-btn"
              :loading="loading"
              @click="handleLogin"
            >
              {{ loading ? '登录中...' : '登 录' }}
            </el-button>
          </el-form-item>
        </el-form>

        <div class="form-footer">
          <span>还没有账号？</span>
          <el-link type="primary" @click="router.push('/register')">立即注册</el-link>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { User, Lock, ChatDotRound, CircleCheck, Message, ChatDotSquare, Promotion } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const userStore = useUserStore()

const formRef = ref<FormInstance>()
const loading = ref(false)
const rememberMe = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
  ]
}

async function handleLogin() {
  const valid = await formRef.value?.validate()
  if (!valid) return

  loading.value = true
  try {
    await authStore.login(loginForm)
    await userStore.fetchUserInfo()
    
    ElMessage.success('登录成功')
    
    // 跳转到之前的页面或根据用户角色跳转
    const redirect = route.query.redirect as string
    if (redirect) {
      router.push(redirect)
    } else {
      // 根据用户角色跳转到不同页面
      const defaultPath = userStore.userInfo?.is_superuser ? '/dashboard' : '/chat'
      router.push(defaultPath)
    }
  } catch (error) {
    // 错误已在响应拦截器中处理，这里不需要重复提示
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.login-container {
  width: 100%;
  height: 100vh;
  display: flex;
  background: #f0f2f5;
}

.login-left {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;

  .decoration-content {
    position: relative;
    z-index: 10;
    color: #fff;
    text-align: center;
    padding: 40px;

    .logo-area {
      margin-bottom: 60px;

      h1 {
        font-size: 42px;
        font-weight: 600;
        margin: 20px 0 10px;
      }

      p {
        font-size: 18px;
        opacity: 0.9;
      }
    }

    .feature-list {
      .feature-item {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        margin-bottom: 20px;
        font-size: 16px;

        .el-icon {
          font-size: 20px;
        }
      }
    }
  }

  .decoration-circles {
    position: absolute;
    inset: 0;

    .circle {
      position: absolute;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.1);
    }

    .circle-1 {
      width: 400px;
      height: 400px;
      top: -100px;
      right: -100px;
    }

    .circle-2 {
      width: 300px;
      height: 300px;
      bottom: -50px;
      left: -100px;
    }

    .circle-3 {
      width: 200px;
      height: 200px;
      top: 50%;
      left: 20%;
    }
  }
}

.login-right {
  width: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-color-container);
  transition: background-color 0.3s;

  .login-form-container {
    width: 380px;
    padding: 40px;

    .form-header {
      text-align: center;
      margin-bottom: 40px;

      h2 {
        font-size: 28px;
        font-weight: 600;
        color: var(--text-color-primary);
        margin: 0 0 10px;
      }

      p {
        color: var(--text-color-secondary);
        font-size: 14px;
        margin: 0;
      }
    }

    .login-form {
      .el-form-item {
        margin-bottom: 24px;
      }

      :deep(.el-input__wrapper) {
        padding: 0 15px;
        height: 48px;
        border-radius: 8px;
      }
    }

    .form-options {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
    }

    .login-btn {
      width: 100%;
      height: 48px;
      font-size: 16px;
      border-radius: 8px;
    }

    .form-footer {
      text-align: center;
      margin-top: 20px;
      color: var(--text-color-secondary);
      font-size: 14px;
    }

    .other-login {
      display: flex;
      justify-content: center;
      gap: 20px;

      .el-button {
        width: 44px;
        height: 44px;
      }
    }
  }
}

// 响应式
@media (max-width: 992px) {
  .login-left {
    display: none;
  }

  .login-right {
    width: 100%;
  }
}
</style>
