import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Search, Filter, Bookmark, CheckCircle } from 'lucide-react'
import { Card, Button } from '@/components'
import { learningApi } from '@/services/api'
import type { LearningRecord } from '@/types'
import { format } from 'date-fns'
import { zhCN } from 'date-fns/locale'

export default function LearningRecords() {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  
  const [loading, setLoading] = useState(true)
  const [records, setRecords] = useState<LearningRecord[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  
  const [categoryFilter, setCategoryFilter] = useState(searchParams.get('category') || '')
  const [readFilter, setReadFilter] = useState<string>(searchParams.get('is_read') || '')
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    fetchRecords()
  }, [page, categoryFilter, readFilter])

  async function fetchRecords() {
    try {
      setLoading(true)
      const res = await learningApi.list({
        category: categoryFilter || undefined,
        is_read: readFilter === 'true' ? true : readFilter === 'false' ? false : undefined,
        page,
        page_size: 10,
      })
      
      setRecords(res.data.data)
      setTotal(res.data.total)
    } catch (error) {
      console.error('Failed to fetch learning records:', error)
    } finally {
      setLoading(false)
    }
  }

  async function toggleBookmark(id: string, currentState: boolean) {
    try {
      await learningApi.update(id, { is_bookmarked: !currentState })
      fetchRecords()
    } catch (error) {
      console.error('Failed to update record:', error)
    }
  }

  async function markAsRead(id: string) {
    try {
      await learningApi.update(id, { is_read: true })
      fetchRecords()
    } catch (error) {
      console.error('Failed to update record:', error)
    }
  }

  const filteredRecords = searchQuery
    ? records.filter((r) =>
        r.title.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : records

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 搜索和筛选 */}
      <Card>
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="text"
              placeholder="搜索学习记录..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-slate-400" />
            <select
              value={categoryFilter}
              onChange={(e) => {
                setCategoryFilter(e.target.value)
                setPage(1)
              }}
              className="px-3 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">全部分类</option>
              <option value="academic_ai">AI论文</option>
              <option value="academic_security">安全论文</option>
              <option value="academic_cross">交叉论文</option>
              <option value="news_ai">AI新闻</option>
              <option value="news_security">安全新闻</option>
              <option value="news_cross">交叉新闻</option>
            </select>

            <select
              value={readFilter}
              onChange={(e) => {
                setReadFilter(e.target.value)
                setPage(1)
              }}
              className="px-3 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">全部状态</option>
              <option value="false">未读</option>
              <option value="true">已读</option>
            </select>
          </div>
        </div>
      </Card>

      {/* 统计 */}
      <p className="text-sm text-slate-500 dark:text-slate-400">
        共 <span className="font-medium text-slate-700 dark:text-slate-300">{total}</span> 条学习记录
      </p>

      {/* 记录列表 */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500" />
        </div>
      ) : filteredRecords.length > 0 ? (
        <div className="space-y-4">
          {filteredRecords.map((record) => (
            <LearningRecordCard
              key={record.id}
              record={record}
              onToggleBookmark={() => toggleBookmark(record.id, record.is_bookmarked)}
              onMarkAsRead={() => markAsRead(record.id)}
              onClick={() => navigate(`/contents/${record.id}`)}
            />
          ))}
        </div>
      ) : (
        <Card>
          <div className="text-center py-12">
            <p className="text-slate-500 dark:text-slate-400">暂无学习记录</p>
          </div>
        </Card>
      )}

      {/* 分页 */}
      {total > 10 && (
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="outline"
            disabled={page === 1}
            onClick={() => setPage((p) => p - 1)}
          >
            上一页
          </Button>
          <span className="px-4 py-2 text-sm text-slate-600 dark:text-slate-400">
            第 {page} 页
          </span>
          <Button
            variant="outline"
            disabled={page * 10 >= total}
            onClick={() => setPage((p) => p + 1)}
          >
            下一页
          </Button>
        </div>
      )}
    </div>
  )
}

function LearningRecordCard({
  record,
  onToggleBookmark,
  onMarkAsRead,
  onClick,
}: {
  record: LearningRecord
  onToggleBookmark: () => void
  onMarkAsRead: () => void
  onClick: () => void
}) {
  const categoryLabels: Record<string, string> = {
    academic_ai: 'AI论文',
    academic_security: '安全论文',
    academic_cross: '交叉论文',
    news_ai: 'AI新闻',
    news_security: '安全新闻',
    news_cross: '交叉新闻',
  }

  return (
    <Card hover className="group">
      <div className="space-y-3">
        {/* 标题行 */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              {record.is_bookmarked && (
                <Bookmark className="w-4 h-4 text-yellow-500 fill-yellow-500" />
              )}
              {record.is_read && (
                <CheckCircle className="w-4 h-4 text-green-500" />
              )}
            </div>
            <h3
              className="text-lg font-semibold text-slate-900 dark:text-slate-100 cursor-pointer hover:text-primary-600 dark:hover:text-primary-400 line-clamp-2"
              onClick={onClick}
            >
              {record.title}
            </h3>
          </div>
          <span className="text-lg font-bold text-primary-500">
            {record.total_score.toFixed(1)}
          </span>
        </div>

        {/* 标签 */}
        <div className="flex items-center gap-2 text-sm">
          <span className="px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
            {categoryLabels[record.category]}
          </span>
          <span className="text-slate-500">{record.source}</span>
          <span className="text-slate-400">•</span>
          <span className="text-slate-500">
            {format(new Date(record.created_at), 'PPP', { locale: zhCN })}
          </span>
        </div>

        {/* 总结 */}
        <p className="text-sm text-slate-600 dark:text-slate-400 line-clamp-2">
          {record.summary}
        </p>

        {/* 关键要点 */}
        <div className="flex flex-wrap gap-2">
          {record.key_points.slice(0, 3).map((point, index) => (
            <span
              key={index}
              className="px-2 py-0.5 rounded bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400 text-xs"
            >
              {point.length > 30 ? point.slice(0, 30) + '...' : point}
            </span>
          ))}
        </div>

        {/* 操作按钮 */}
        <div className="flex items-center gap-2 pt-2 border-t border-slate-200 dark:border-slate-700">
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation()
              onToggleBookmark()
            }}
          >
            <Bookmark
              className={`w-4 h-4 ${
                record.is_bookmarked
                  ? 'text-yellow-500 fill-yellow-500'
                  : 'text-slate-400'
              }`}
            />
          </Button>
          {!record.is_read && (
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation()
                onMarkAsRead()
              }}
            >
              <CheckCircle className="w-4 h-4 text-slate-400" />
              标记已读
            </Button>
          )}
        </div>
      </div>
    </Card>
  )
}
