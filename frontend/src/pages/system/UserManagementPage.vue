<template>
  <div class="user-management-page">
    <el-card class="search-card" shadow="never">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="搜索">
          <el-input
            v-model="searchForm.keyword"
            placeholder="用户名/邮箱/昵称"
            clearable
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><RefreshLeft /></el-icon>重置
          </el-button>
          <el-button type="success" @click="handleAdd">
            <el-icon><Plus /></el-icon>新增用户
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card" shadow="never">
      <el-table
        v-loading="loading"
        :data="tableData"
        stripe
        style="width: 100%"
        @sort-change="handleSortChange"
      >
        <el-table-column label="序号" width="80" type="index" :index="indexMethod" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column prop="nickname" label="昵称" width="120">
          <template #default="{ row }">
            {{ row.nickname || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="手机号" width="130">
          <template #default="{ row }">
            {{ row.phone || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="is_superuser" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_superuser ? 'danger' : 'info'" size="small">
              {{ row.is_superuser ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="login_count" label="登录次数" width="100" sortable />
        <el-table-column prop="last_login" label="最后登录" width="180" sortable>
          <template #default="{ row }">
            {{ formatDate(row.last_login) }}
          </template>
        </el-table-column>
   <!-- 创建时间     <el-table-column prop="created_at" label="创建时间" width="180" sortable>
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column> --->
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button link type="warning" size="small" @click="handleResetPassword(row)">
              重置密码
            </el-button>
            <el-button
              link
              :type="row.is_active ? 'danger' : 'success'"
              size="small"
              @click="handleToggleStatus(row)"
            >
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
        class="pagination"
      />
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="formData.username"
            placeholder="请输入用户名"
            :disabled="isEdit"
          />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="formData.email"
            placeholder="请输入邮箱"
            :disabled="isEdit"
          />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input
            v-model="formData.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="formData.nickname" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="formData.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="角色" prop="is_superuser">
          <el-radio-group v-model="formData.is_superuser">
            <el-radio :label="false">普通用户</el-radio>
            <el-radio :label="true">管理员</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="状态" prop="is_active" v-if="isEdit">
          <el-switch v-model="formData.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 重置密码对话框 -->
    <el-dialog
      v-model="resetPasswordDialogVisible"
      title="重置密码"
      width="400px"
      @close="handleResetPasswordClose"
    >
      <el-form
        ref="resetPasswordFormRef"
        :model="resetPasswordForm"
        :rules="resetPasswordRules"
        label-width="100px"
      >
        <el-form-item label="用户名">
          <el-input v-model="resetPasswordForm.username" disabled />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input
            v-model="resetPasswordForm.new_password"
            type="password"
            placeholder="请输入新密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input
            v-model="resetPasswordForm.confirm_password"
            type="password"
            placeholder="请确认新密码"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetPasswordDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="resetPasswordLoading" @click="handleResetPasswordSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Search, RefreshLeft, Plus } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { getUserList, createUser, updateUser, deleteUser, resetUserPassword } from '@/api/admin'
import { getUserInfo } from '@/api/user'
import { useAuthStore } from '@/stores/auth'
import type { UserManagementItem, UserCreateParams, UserUpdateParams } from '@/api/admin'

const loading = ref(false)
const submitLoading = ref(false)
const resetPasswordLoading = ref(false)
const tableData = ref<UserManagementItem[]>([])
const dialogVisible = ref(false)
const resetPasswordDialogVisible = ref(false)
const isEdit = ref(false)
const currentUserId = ref<number | null>(null)
const formRef = ref<FormInstance>()
const resetPasswordFormRef = ref<FormInstance>()
const router = useRouter()
const authStore = useAuthStore()
const currentUserInfo = ref<{ id: number; is_superuser: boolean } | null>(null)

const searchForm = reactive({
  keyword: ''
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const sortInfo = reactive({
  sort_by: 'created_at',
  sort_order: 'ascending'
})

const formData = reactive<UserCreateParams & { is_active?: boolean }>({
  username: '',
  email: '',
  password: '',
  nickname: '',
  phone: '',
  is_superuser: false,
  is_active: true
})

const resetPasswordForm = reactive({
  username: '',
  user_id: 0,
  new_password: '',
  confirm_password: ''
})

const dialogTitle = computed(() => isEdit.value ? '编辑用户' : '新增用户')

const formRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在3-50个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度在6-50个字符', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ]
}

const validateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (value !== resetPasswordForm.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const resetPasswordRules: FormRules = {
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度在6-50个字符', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

function formatDate(date?: string): string {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

async function fetchCurrentUserInfo() {
  try {
    const res = await getUserInfo()
    if (res.code === 200 && res.data) {
      currentUserInfo.value = {
        id: res.data.id,
        is_superuser: res.data.is_superuser
      }
    }
  } catch (error) {
    console.error('获取当前用户信息失败:', error)
  }
}

async function fetchData() {
  loading.value = true
  try {
    const res = await getUserList({
      page: pagination.page,
      page_size: pagination.page_size,
      keyword: searchForm.keyword || undefined,
      sort_by: sortInfo.sort_by,
      sort_order: sortInfo.sort_order
    })
    if (res.code === 200 && res.data) {
      tableData.value = res.data.items
      pagination.total = res.data.total
    }
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  fetchData()
}

function handleReset() {
  searchForm.keyword = ''
  pagination.page = 1
  fetchData()
}

function handleAdd() {
  isEdit.value = false
  currentUserId.value = null
  Object.assign(formData, {
    username: '',
    email: '',
    password: '',
    nickname: '',
    phone: '',
    is_superuser: false,
    is_active: true
  })
  dialogVisible.value = true
}

function handleEdit(row: UserManagementItem) {
  isEdit.value = true
  currentUserId.value = row.id
  Object.assign(formData, {
    username: row.username,
    email: row.email,
    password: '',
    nickname: row.nickname || '',
    phone: row.phone || '',
    is_superuser: row.is_superuser,
    is_active: row.is_active
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  const valid = await formRef.value?.validate()
  if (!valid) return

  submitLoading.value = true
  try {
    if (isEdit.value && currentUserId.value) {
        // 检查是否是更新自己的信息
        const isUpdatingSelf = currentUserInfo.value && currentUserId.value === currentUserInfo.value.id
        
        const updateData: UserUpdateParams = {
          nickname: formData.nickname,
          phone: formData.phone,
          is_superuser: formData.is_superuser,
          is_active: formData.is_active
        }
        
        const res = await updateUser(currentUserId.value, updateData)
        if (res.code === 200) {
          dialogVisible.value = false
          
          // 如果更新的是自己的角色或状态，跳转到登录页面重新登录
          if (isUpdatingSelf) {
            ElMessage.info('您的账户信息已更新，请重新登录')
            authStore.logout()
            router.push('/login')
          } else {
            ElMessage.success('更新成功')
            fetchData()
          }
        }
      } else {
        const res = await createUser(formData)
        if (res.code === 200) {
          ElMessage.success('创建成功')
          dialogVisible.value = false
          fetchData()
        }
      }
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    submitLoading.value = false
  }
}

function handleDialogClose() {
  formRef.value?.resetFields()
}

function handleResetPassword(row: UserManagementItem) {
  resetPasswordForm.username = row.username
  resetPasswordForm.user_id = row.id
  resetPasswordForm.new_password = ''
  resetPasswordForm.confirm_password = ''
  resetPasswordDialogVisible.value = true
}

async function handleResetPasswordSubmit() {
  const valid = await resetPasswordFormRef.value?.validate()
  if (!valid) return

  resetPasswordLoading.value = true
  try {
    const res = await resetUserPassword(resetPasswordForm.user_id, resetPasswordForm.new_password)
    if (res.code === 200) {
      ElMessage.success('密码重置成功')
      resetPasswordDialogVisible.value = false
    }
  } catch (error: any) {
    ElMessage.error(error.message || '重置密码失败')
  } finally {
    resetPasswordLoading.value = false
  }
}

function handleResetPasswordClose() {
  resetPasswordFormRef.value?.resetFields()
}

async function handleToggleStatus(row: UserManagementItem) {
  const action = row.is_active ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(`确定要${action}用户 "${row.username}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const isUpdatingSelf = currentUserInfo.value && row.id === currentUserInfo.value.id
    
    const res = await updateUser(row.id, { is_active: !row.is_active })
    if (res.code === 200) {
      if (isUpdatingSelf) {
        ElMessage.info('您的账户状态已更新，请重新登录')
        authStore.logout()
        router.push('/login')
      } else {
        ElMessage.success(`${action}成功`)
        fetchData()
      }
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '操作失败')
    }
  }
}

async function handleDelete(row: UserManagementItem) {
  try {
    await ElMessageBox.confirm(`确定要删除用户 "${row.username}" 吗？此操作不可恢复！`, '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'error'
    })

    const res = await deleteUser(row.id)
    if (res.code === 200) {
      ElMessage.success('删除成功')
      if (tableData.value.length === 1 && pagination.page > 1) {
        pagination.page--
      }
      fetchData()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

function handlePageChange(page: number) {
  pagination.page = page
  fetchData()
}

function handleSizeChange(size: number) {
  pagination.page_size = size
  pagination.page = 1
  fetchData()
}

function handleSortChange({ prop, order }: { prop: string; order: string | null }) {
  if (prop) {
    sortInfo.sort_by = prop
    sortInfo.sort_order = order === 'ascending' ? 'ascending' : 'descending'
  } else {
    sortInfo.sort_by = 'created_at'
    sortInfo.sort_order = 'ascending'
  }
  fetchData()
}

function indexMethod(index: number) {
  return (pagination.page - 1) * pagination.page_size + index + 1
}

onMounted(async () => {
  await fetchCurrentUserInfo()
  fetchData()
})
</script>

<style lang="scss" scoped>
.user-management-page {
  .search-card {
    margin-bottom: 20px;
    transition: background-color 0.3s;
  }

  .table-card {
    transition: background-color 0.3s;
  }

  .search-form {
    margin-bottom: 0;
  }

  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>