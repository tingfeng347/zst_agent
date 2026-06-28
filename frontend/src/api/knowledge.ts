import { get, post, del } from './index'
import type { ApiResponse } from '@/types/api'

export interface KnowledgeFile {
  name: string
  size: number
  modified_time: number
  md5: string
  is_vectorized: boolean
  type: string
}

export interface KnowledgeFilesResponse {
  files: KnowledgeFile[]
  total_count: number
  vectorized_count: number
}

export interface KnowledgeStats {
  file_count: number
  total_size: number
  vectorized_count: number
  chroma_size: number
}

/**
 * 获取知识库文件列表
 */
export function getKnowledgeFiles(): Promise<ApiResponse<KnowledgeFilesResponse>> {
  return get<KnowledgeFilesResponse>('/knowledge/files')
}

/**
 * 上传知识库文件
 */
export async function uploadKnowledgeFile(file: File): Promise<ApiResponse<any>> {
  const formData = new FormData()
  formData.append('file', file)
  
  // 从 pinia persist 的存储中获取 token
  const authData = localStorage.getItem('zst-auth')
  let token = ''
  if (authData) {
    try {
      const parsed = JSON.parse(authData)
      token = parsed.token || ''
    } catch {
      token = ''
    }
  }
  
  const response = await fetch('/api/v1/knowledge/upload', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  })
  
  const data = await response.json()
  
  if (!response.ok) {
    throw new Error(data.detail || '上传失败')
  }
  
  // 后端返回的已经是 ResponseModel 格式
  return data
}

/**
 * 删除知识库文件
 */
export function deleteKnowledgeFile(filename: string): Promise<ApiResponse<void>> {
  return del(`/knowledge/files/${encodeURIComponent(filename)}`)
}

/**
 * 执行向量化
 */
export function vectorizeKnowledge(): Promise<ApiResponse<{ message: string; vectorized_count: number }>> {
  return post('/knowledge/vectorize', {})
}

/**
 * 获取知识库统计
 */
export function getKnowledgeStats(): Promise<ApiResponse<KnowledgeStats>> {
  return get<KnowledgeStats>('/knowledge/stats')
}

/**
 * 优化向量数据库
 */
export function optimizeVectorDb(): Promise<ApiResponse<{ new_size: number }>> {
  return post('/knowledge/optimize', {})
}
