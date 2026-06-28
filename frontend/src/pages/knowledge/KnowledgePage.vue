<template>
  <div class="knowledge-page">
    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon files-icon">
          <el-icon :size="28"><Folder /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.file_count }}</div>
          <div class="stat-label">知识文件</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon vectorized-icon">
          <el-icon :size="28"><Collection /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.vectorized_count }}</div>
          <div class="stat-label">已向量化</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon size-icon">
          <el-icon :size="28"><DataLine /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ formatSize(stats.total_size) }}</div>
          <div class="stat-label">文件大小</div>
        </div>
      </div>

      
      <div class="stat-card">
        <div class="stat-icon chroma-icon">
          <el-icon :size="28"><Cpu /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ formatSize(stats.chroma_size) }}</div>
          <div class="stat-label">向量库大小</div>
        </div>
      </div>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <div class="action-left">
        <el-upload
          :show-file-list="false"
          :before-upload="handleBeforeUpload"
          :http-request="handleUpload"
          accept=".txt,.pdf,.csv,.md"
          multiple
        >
          <el-button type="primary" :icon="Upload">上传文件</el-button>
        </el-upload>
        
        <el-button 
          type="success" 
          :icon="Promotion" 
          :loading="vectorizing"
          @click="handleVectorize"
        >
          {{ vectorizing ? '向量化中...' : '向量化知识库' }}
        </el-button>
        
        <el-button 
          type="warning" 
          :icon="MagicStick" 
          :loading="optimizing"
          @click="handleOptimize"
        >
          {{ optimizing ? '优化中...' : '优化数据库' }}
        </el-button>
        
        <el-button :icon="Refresh" @click="loadFiles">刷新</el-button>
      </div>
      
      <div class="action-right">
        <el-input
          v-model="searchText"
          placeholder="搜索文件..."
          :prefix-icon="Search"
          clearable
          style="width: 240px"
        />
      </div>
    </div>

    <!-- 文件列表 -->
    <el-card class="files-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>知识库文件</span>
          <span class="file-count">共 {{ filteredFiles.length }} 个文件</span>
        </div>
      </template>
      
      <el-table 
        :data="filteredFiles" 
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column label="文件名" min-width="280">
          <template #default="{ row }">
            <div class="file-name">
              <el-icon class="file-icon" :class="getFileIconClass(row.type)">
                <Document v-if="row.type === '.txt'" />
                <Document v-else-if="row.type === '.pdf'" />
                <Grid v-else-if="row.type === '.csv'" />
                <Document v-else />
              </el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="getFileTagType(row.type)">
              {{ row.type.replace('.', '').toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="大小" width="120" align="center">
          <template #default="{ row }">
            {{ formatSize(row.size) }}
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag 
              :type="row.is_vectorized ? 'success' : 'info'" 
              size="small"
              effect="light"
              style="white-space: nowrap;"
            >
              <span style="display: inline-flex; align-items: center;">
                <el-icon v-if="row.is_vectorized" style="margin-right: 4px"><Check /></el-icon>
                {{ row.is_vectorized ? '已向量化' : '未处理' }}
              </span>
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="修改时间" width="180" align="center">
          <template #default="{ row }">
            {{ formatTime(row.modified_time) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="100" align="center" fixed="right">
          <template #default="{ row }">
            <el-popconfirm
              title="确定要删除这个文件吗？"
              confirm-button-text="确定"
              cancel-button-text="取消"
              @confirm="handleDelete(row.name)"
            >
              <template #reference>
                <el-button type="danger" :icon="Delete" link size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
        
        <template #empty>
          <el-empty description="暂无知识库文件">
            <el-upload
              :show-file-list="false"
              :before-upload="handleBeforeUpload"
              :http-request="handleUpload"
              accept=".txt,.pdf,.csv,.md"
            >
              <el-button type="primary">上传第一个文件</el-button>
            </el-upload>
          </el-empty>
        </template>
      </el-table>
    </el-card>

    <!-- 使用说明 -->
    <el-card class="tips-card" shadow="never">
      <template #header>
        <div class="card-header">
          <el-icon><InfoFilled /></el-icon>
          <span>使用说明</span>
        </div>
      </template>
      <div class="tips-content">
        <div class="tip-item">
          <el-icon class="tip-icon"><Upload /></el-icon>
          <div class="tip-text">
            <strong>上传文件</strong>：支持 TXT、PDF、CSV、MD格式的知识库文件
          </div>
        </div>
        <div class="tip-item">
          <el-icon class="tip-icon"><Promotion /></el-icon>
          <div class="tip-text">
            <strong>向量化</strong>：将新上传的文件转换为向量，供智能客服检索使用
          </div>
        </div>
        <div class="tip-item">
          <el-icon class="tip-icon"><ChatDotRound /></el-icon>
          <div class="tip-text">
            <strong>智能问答</strong>：向量化后的知识库将自动用于智能客服的回答
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Folder, Collection, DataLine, Cpu, Upload, Promotion, Refresh, Search,
  Document, Grid, Delete, Check, InfoFilled, ChatDotRound, MagicStick, Connection
} from '@element-plus/icons-vue'
import { 
  getKnowledgeFiles, uploadKnowledgeFile, deleteKnowledgeFile, 
  vectorizeKnowledge, getKnowledgeStats, optimizeVectorDb,
  type KnowledgeFile, type KnowledgeStats
} from '@/api/knowledge'

const loading = ref(false)
const vectorizing = ref(false)
const optimizing = ref(false)
const searchText = ref('')
const files = ref<KnowledgeFile[]>([])
const stats = ref<KnowledgeStats>({
  file_count: 0,
  total_size: 0,
  vectorized_count: 0,
  chroma_size: 0
})

// 过滤后的文件列表
const filteredFiles = computed(() => {
  if (!searchText.value) return files.value
  const keyword = searchText.value.toLowerCase()
  return files.value.filter(f => f.name.toLowerCase().includes(keyword))
})

// 格式化文件大小
function formatSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 格式化时间
function formatTime(timestamp: number): string {
  const date = new Date(timestamp * 1000)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取文件图标样式
function getFileIconClass(type: string): string {
  const map: Record<string, string> = {
    '.txt': 'txt-icon',
    '.pdf': 'pdf-icon',
    '.csv': 'csv-icon'
  }
  return map[type] || ''
}

// 获取文件标签类型
function getFileTagType(type: string): '' | 'success' | 'warning' | 'info' | 'danger' {
  const map: Record<string, '' | 'success' | 'warning' | 'info' | 'danger'> = {
    '.txt': '',
    '.pdf': 'danger',
    '.csv': 'success'
  }
  return map[type] || 'info'
}

// 加载文件列表
async function loadFiles() {
  loading.value = true
  try {
    const [filesRes, statsRes] = await Promise.all([
      getKnowledgeFiles(),
      getKnowledgeStats()
    ])
    if (filesRes.data) {
      files.value = filesRes.data.files
    }
    if (statsRes.data) {
      stats.value = statsRes.data
    }
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 上传前检查
function handleBeforeUpload(file: File) {
  const allowedTypes = ['.txt', '.pdf', '.csv', '.md']
  const ext = '.' + file.name.split('.').pop()?.toLowerCase()
  
  if (!allowedTypes.includes(ext)) {
    ElMessage.error('仅支持 TXT、PDF、CSV、MD 格式的文件')
    return false
  }
  
  const maxSize = 50 * 1024 * 1024 // 50MB
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 50MB')
    return false
  }
  
  return true
}

// 上传文件
async function handleUpload(options: any) {
  try {
    await uploadKnowledgeFile(options.file)
    ElMessage.success('上传成功')
    loadFiles()
  } catch (error: any) {
    ElMessage.error(error.message || '上传失败')
  }
}

// 删除文件
async function handleDelete(filename: string) {
  try {
    await deleteKnowledgeFile(filename)
    ElMessage.success('删除成功')
    loadFiles()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

// 向量化
async function handleVectorize() {
  vectorizing.value = true
  try {
    const res = await vectorizeKnowledge()
    ElMessage.success(`向量化完成，共 ${res.data?.vectorized_count || 0} 个文件`)
    loadFiles()
  } catch (error: any) {
    ElMessage.error(error.message || '向量化失败')
  } finally {
    vectorizing.value = false
  }
}

// 优化数据库
async function handleOptimize() {
  optimizing.value = true
  try {
    const res = await optimizeVectorDb()
    ElMessage.success(`优化完成，当前向量库大小: ${formatSize(res.data?.new_size || 0)}`)
    loadFiles()
  } catch (error: any) {
    ElMessage.error(error.message || '优化失败')
  } finally {
    optimizing.value = false
  }
}

onMounted(() => {
  loadFiles()
})
</script>

<style lang="scss" scoped>
.knowledge-page {
  padding: 20px;
  
  .stats-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
    margin-bottom: 20px;
    
    .stat-card {
      background: var(--bg-color-container);
      border: 1px solid var(--border-color-light);
      border-radius: 12px;
      padding: 20px;
      display: flex;
      align-items: center;
      gap: 16px;
      transition: all 0.3s;
      
      &:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        transform: translateY(-2px);
      }
      
      .stat-icon {
        width: 56px;
        height: 56px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #fff;
        
        &.files-icon { background: linear-gradient(135deg, #667eea, #764ba2); }
        &.vectorized-icon { background: linear-gradient(135deg, #11998e, #38ef7d); }
        &.size-icon { background: linear-gradient(135deg, #f093fb, #f5576c); }
        &.vector-icon { background: linear-gradient(135deg, #ff9a9e, #fecfef); }
        &.chroma-icon { background: linear-gradient(135deg, #4facfe, #00f2fe); }
      }
      
      .stat-info {
        .stat-value {
          font-size: 24px;
          font-weight: 600;
          color: var(--text-color-primary);
        }
        .stat-label {
          font-size: 14px;
          color: var(--text-color-secondary);
          margin-top: 4px;
        }
      }
    }
  }
  
  .action-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    .action-left {
      display: flex;
      gap: 12px;
    }
  }
  
  .files-card {
    margin-bottom: 20px;
    border-radius: 12px;
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .file-count {
        font-size: 14px;
        color: var(--text-color-secondary);
      }
    }
    
    .file-name {
      display: flex;
      align-items: center;
      gap: 10px;
      
      .file-icon {
        font-size: 20px;
        
        &.txt-icon { color: #409EFF; }
        &.pdf-icon { color: #F56C6C; }
        &.csv-icon { color: #67C23A; }
      }
    }
  }
  
  .tips-card {
    border-radius: 12px;
    
    .card-header {
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--text-color-primary);
    }
    
    .tips-content {
      display: flex;
      flex-direction: column;
      gap: 16px;
      
      .tip-item {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        
        .tip-icon {
          font-size: 20px;
          color: #409EFF;
          margin-top: 2px;
        }
        
        .tip-text {
          color: var(--text-color-regular);
          line-height: 1.6;
          
          strong {
            color: var(--text-color-primary);
          }
        }
      }
    }
  }
}

@media (max-width: 1400px) {
  .knowledge-page .stats-row {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 1000px) {
  .knowledge-page .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .knowledge-page {
    .stats-row {
      grid-template-columns: 1fr;
    }
    
    .action-bar {
      flex-direction: column;
      gap: 12px;
      
      .action-left, .action-right {
        width: 100%;
      }
    }
  }
}
</style>
