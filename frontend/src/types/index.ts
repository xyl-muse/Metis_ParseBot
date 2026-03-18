// 内容分类
export type ContentCategory =
  | 'academic_ai'
  | 'academic_security'
  | 'academic_cross'
  | 'news_ai'
  | 'news_security'
  | 'news_cross'

// 内容状态
export type ContentStatus = 'pending' | 'reviewed' | 'analyzed' | 'rejected'

// 内容
export interface Content {
  id: string
  title: string
  source: string
  source_url: string
  category: ContentCategory
  summary: string | null
  status: ContentStatus
  authors: string[] | null
  tags: string[] | null
  collected_at: string
  updated_at: string
}

// 评分详情
export interface ScoreDetail {
  novelty_score: number
  utility_score: number
  authority_score: number
  timeliness_score: number
  completeness_score: number
}

// 预审结果
export interface Review {
  id: string
  content_id: string
  total_score: number
  passed: boolean
  score_detail: ScoreDetail
  review_notes: string | null
  reviewed_at: string
}

// 知识关联
export interface KnowledgeLink {
  concept: string
  relation: string
  note: string
}

// 易混淆辨析
export interface ConfusionNote {
  item: string
  distinction: string
}

// 分析结果
export interface Analysis {
  id: string
  content_id: string
  summary: string
  key_points: string[]
  knowledge_links: KnowledgeLink[] | null
  confusion_notes: ConfusionNote[] | null
  learning_suggestions: string | null
  related_topics: string[] | null
  analyzed_at: string
}

// 学习记录
export interface LearningRecord {
  id: string
  title: string
  category: ContentCategory
  source: string
  source_url: string
  total_score: number
  summary: string
  key_points: string[]
  knowledge_links: KnowledgeLink[] | null
  confusion_notes: ConfusionNote[] | null
  learning_suggestions: string | null
  is_read: boolean
  is_bookmarked: boolean
  user_notes: string | null
  created_at: string
}

// 采集结果
export interface CollectResult {
  total_found: number
  total_collected: number
  total_deduplicated: number
  by_source: Record<string, { found: number; collected: number }>
  errors: string[]
}

// 系统状态
export interface SystemStatus {
  app_name: string
  version: string
  status: string
  database_connected: boolean
  llm_configured: boolean
}

// API 响应
export interface ApiResponse<T> {
  success: boolean
  message: string
  data?: T
}

// 分页列表响应
export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  page_size: number
}
