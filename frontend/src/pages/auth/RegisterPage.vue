<template>
  <div class="register-container">
    <!-- 左侧装饰区域 -->
    <div class="register-left">
      <div class="decoration-content">
        <div class="logo-area">
          <el-icon :size="64" color="#fff"><ChatDotRound /></el-icon>
          <h1>智扫通</h1>
          <p>智能客服管理系统</p>
        </div>
        <div class="welcome-text">
          <h3>开启智能客服之旅</h3>
          <p>注册账号，体验 AI 驱动的智能对话服务</p>
        </div>
      </div>
      <div class="decoration-circles">
        <div class="circle circle-1"></div>
        <div class="circle circle-2"></div>
        <div class="circle circle-3"></div>
      </div>
    </div>

    <!-- 右侧注册表单 -->
    <div class="register-right">
      <div class="register-form-container">
        <div class="form-header">
          <h2>创建账号</h2>
          <p>请填写以下信息完成注册</p>
        </div>

        <el-form
          ref="formRef"
          :model="registerForm"
          :rules="rules"
          class="register-form"
          size="large"
        >
          <el-form-item prop="username">
            <el-input
              v-model="registerForm.username"
              placeholder="请输入用户名"
              :prefix-icon="User"
              clearable
            />
          </el-form-item>

          <el-form-item prop="email">
            <el-input
              v-model="registerForm.email"
              placeholder="请输入邮箱"
              :prefix-icon="Message"
              clearable
            />
          </el-form-item>

          <el-form-item prop="nickname">
            <el-input
              v-model="registerForm.nickname"
              placeholder="请输入昵称（选填）"
              :prefix-icon="UserFilled"
              clearable
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="registerForm.password"
              type="password"
              placeholder="请输入密码"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>

          <el-form-item prop="confirmPassword">
            <el-input
              v-model="registerForm.confirmPassword"
              type="password"
              placeholder="请确认密码"
              :prefix-icon="Lock"
              show-password
              @keyup.enter="handleRegister"
            />
          </el-form-item>

          <el-form-item prop="agreement">
            <el-checkbox v-model="registerForm.agreement">
              我已阅读并同意
              <el-link type="primary" :underline="false">用户协议</el-link>
              和
              <el-link type="primary" :underline="false">隐私政策</el-link>
            </el-checkbox>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              class="register-btn"
              :loading="loading"
              @click="handleRegister"
            >
              {{ loading ? '注册中...' : '立即注册' }}
            </el-button>
          </el-form-item>
        </el-form>

        <div class="form-footer">
          <span>已有账号？</span>
          <el-link type="primary" @click="router.push('/login')">立即登录</el-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { User, UserFilled, Lock, Message, ChatDotRound } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref<FormInstance>()
const loading = ref(false)

const registerForm = reactive({
  username: '',
  email: '',
  nickname: '',
  password: '',
  confirmPassword: '',
  agreement: false
})

// 自定义验证器
const validatePassword = (rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请输入密码'))
  } else if (value.length < 6) {
    callback(new Error('密码长度至少为6位'))
  } else {
    if (registerForm.confirmPassword !== '') {
      formRef.value?.validateField('confirmPassword')
    }
    callback()
  }
}

const validateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const validateAgreement = (rule: any, value: boolean, callback: any) => {
  if (!value) {
    callback(new Error('请阅读并同意用户协议'))
  } else {
    callback()
  }
}

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, validator: validatePassword, trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, validator: validateConfirmPassword, trigger: 'blur' }
  ],
  agreement: [
    { validator: validateAgreement, trigger: 'change' }
  ]
}

async function handleRegister() {
  const valid = await formRef.value?.validate()
  if (!valid) return

  loading.value = true
  try {
    await authStore.register({
      username: registerForm.username,
      email: registerForm.email,
      password: registerForm.password,
      nickname: registerForm.nickname || undefined
    })
    
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (error) {
    // 错误已在响应拦截器中处理，这里不需要重复提示
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.register-container {
  width: 100%;
  height: 100vh;
  display: flex;
  background: #f0f2f5;
}

.register-left {
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

    .welcome-text {
      h3 {
        font-size: 24px;
        margin-bottom: 15px;
      }

      p {
        font-size: 16px;
        opacity: 0.85;
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

.register-right {
  width: 520px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-color-container);
  transition: background-color 0.3s;

  .register-form-container {
    width: 400px;
    padding: 40px;

    .form-header {
      text-align: center;
      margin-bottom: 30px;

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

    .register-form {
      .el-form-item {
        margin-bottom: 20px;
      }

      :deep(.el-input__wrapper) {
        padding: 0 15px;
        height: 44px;
        border-radius: 8px;
      }
    }

    .register-btn {
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
  }
}

// 响应式
@media (max-width: 992px) {
  .register-left {
    display: none;
  }

  .register-right {
    width: 100%;
  }
}
</style>
