import axios from 'axios'
import type {
  Content,
  Review,
  Analysis,
  LearningRecord,
  CollectResult,
  SystemStatus,
  PaginatedResponse,
  ApiResponse,
} from '@/types'

// 默认超时时间（30秒）
const DEFAULT_TIMEOUT = 30000
// 长时间操作超时时间（10分钟）
const LONG_TIMEOUT = 600000

const api = axios.create({
  baseURL: '/api',
  timeout: DEFAULT_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 响应拦截器
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// ==================== 内容相关 ====================

export const contentApi = {
  list: (params?: {
    status?: string
    category?: string
    page?: number
    page_size?: number
  }) => api.get<PaginatedResponse<Content>>('/contents', { params }),

  get: (id: string) => api.get<Content>(`/contents/${id}`),

  delete: (id: string) => api.delete(`/contents/${id}`),
}

// ==================== 采集相关 ====================

export const collectApi = {
  trigger: (params?: { sources?: string[]; limit_per_source?: number }) =>
    api.post<ApiResponse<CollectResult>>('/collect', params, { timeout: LONG_TIMEOUT }),

  getSources: () => api.get('/collect/sources'),
}

// ==================== 预审相关 ====================

export const reviewApi = {
  trigger: (params?: { content_id?: string; limit?: number }) =>
    api.post<ApiResponse>('/review', params, { timeout: LONG_TIMEOUT }),

  getProgress: () =>
    api.get<{
      status: string
      total: number
      processed: number
      passed: number
      rejected: number
      current_item: string | null
      percentage: number
    }>('/review/progress'),

  getPending: (limit?: number) =>
    api.get('/review/pending', { params: { limit } }),

  getPassed: (limit?: number) =>
    api.get('/review/passed', { params: { limit } }),

  getByContent: (contentId: string) =>
    api.get<Review>(`/review/${contentId}`),
}

// ==================== 分析相关 ====================

export const analyzeApi = {
  trigger: (params?: { content_id?: string; limit?: number }) =>
    api.post<ApiResponse>('/analyze', params, { timeout: LONG_TIMEOUT }),

  getProgress: () =>
    api.get<{
      status: string
      total: number
      processed: number
      success: number
      failed: number
      current_item: string | null
      percentage: number
    }>('/analyze/progress'),

  getAnalyzed: (params?: { category?: string; limit?: number }) =>
    api.get('/analyze/analyzed', { params }),

  getByContent: (contentId: string) =>
    api.get<Analysis>(`/analyze/${contentId}`),
}

// ==================== 学习记录相关 ====================

export const learningApi = {
  list: (params?: {
    category?: string
    is_read?: boolean
    is_bookmarked?: boolean
    page?: number
    page_size?: number
  }) => api.get<PaginatedResponse<LearningRecord>>('/learning', { params }),

  get: (id: string) => api.get<LearningRecord>(`/learning/${id}`),

  update: (id: string, data: {
    is_read?: boolean
    is_bookmarked?: boolean
    user_notes?: string
  }) => api.patch<ApiResponse>(`/learning/${id}`, data),

  delete: (id: string) => api.delete(`/learning/${id}`),

  checkConsistency: () => api.get<{
    analyzed_content_count: number
    learning_record_count: number
    missing_learning_records: Array<{ id: string; title: string }>
    orphan_learning_records: Array<{ id: string; title: string; content_status: string }>
    is_consistent: boolean
  }>('/learning/check-consistency'),

  fixConsistency: () => api.post<ApiResponse>('/learning/fix-consistency'),
}

// ==================== 系统相关 ====================

export const systemApi = {
  getStatus: () => api.get<SystemStatus>('/status'),

  healthCheck: () => api.get('/health'),

  runPipeline: (params?: { collect?: boolean; review?: boolean; analyze?: boolean; limit?: number }) =>
    api.post<ApiResponse>('/pipeline', params, { timeout: LONG_TIMEOUT }),

  getSchedulerJobs: () => api.get('/scheduler/jobs'),

  startScheduler: () => api.post('/scheduler/start'),

  stopScheduler: () => api.post('/scheduler/stop'),
}

export default api
