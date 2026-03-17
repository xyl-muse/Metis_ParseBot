import { useState, useEffect } from 'react'
import { Search, Filter, CheckCircle, BookOpen, Star, Clock, ExternalLink, ChevronDown, ChevronUp } from 'lucide-react'
import { Card, Button } from '@/components'
import { learningApi } from '@/services/api'
import type { LearningRecord } from '@/types'
import { format } from 'date-fns'
import { zhCN } from 'date-fns/locale'

type TabType = 'unread' | 'read' | 'bookmarked'

export default function LearningRecords() {
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<TabType>('unread')
  const [counts, setCounts] = useState({ unread: 0, read: 0, bookmarked: 0 })
  const [records, setRecords] = useState<LearningRecord[]>([])
  const [page, setPage] = useState(1)
  
  const [categoryFilter, setCategoryFilter] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  
  // 展开的学习记录ID
  const [expandedId, setExpandedId] = useState<string | null>(null)
  // 编辑笔记的记录ID
  const [editingNotesId, setEditingNotesId] = useState<string | null>(null)
  const [notesValue, setNotesValue] = useState('')

  useEffect(() => {
    fetchCounts()
  }, [])

  useEffect(() => {
    setPage(1)
    fetchRecords()
  }, [activeTab, categoryFilter])

  useEffect(() => {
    if (page > 1) fetchRecords()
  }, [page])

  async function fetchCounts() {
    try {
      const [unreadRes, readRes, bookmarkedRes] = await Promise.all([
        learningApi.list({ is_read: false, page_size: 1 }),
        learningApi.list({ is_read: true, page_size: 1 }),
        learningApi.list({ is_bookmarked: true, page_size: 1 }),
      ])
      
      setCounts({
        unread: unreadRes.data.total,
        read: readRes.data.total,
        bookmarked: bookmarkedRes.data.total,
      })
    } catch (error) {
      console.error('Failed to fetch counts:', error)
    }
  }

  async function fetchRecords() {
    try {
      setLoading(true)
      
      const params: any = {
        page,
        page_size: 10,
        category: categoryFilter || undefined,
      }
      
      if (activeTab === 'unread') {
        params.is_read = false
      } else if (activeTab === 'read') {
        params.is_read = true
      } else if (activeTab === 'bookmarked') {
        params.is_bookmarked = true
      }
      
      const res = await learningApi.list(params)
      setRecords(res.data.data)
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
      fetchCounts()
    } catch (error) {
      console.error('Failed to update record:', error)
    }
  }

  async function markAsRead(id: string) {
    try {
      await learningApi.update(id, { is_read: true })
      setExpandedId(null)
      fetchRecords()
      fetchCounts()
    } catch (error) {
      console.error('Failed to update record:', error)
    }
  }

  async function saveNotes(id: string) {
    try {
      await learningApi.update(id, { user_notes: notesValue })
      setEditingNotesId(null)
      fetchRecords()
    } catch (error) {
      console.error('Failed to save notes:', error)
    }
  }

  function toggleExpand(record: LearningRecord) {
    if (expandedId === record.id) {
      setExpandedId(null)
    } else {
      setExpandedId(record.id)
      setNotesValue(record.user_notes || '')
    }
    setEditingNotesId(null)
  }

  async function fixDataConsistency() {
    if (!confirm('确定要修复数据一致性问题吗？这将清理孤立的学习记录并为缺失的内容创建记录。')) {
      return
    }
    try {
      const res = await fetch('/api/learning/fix-consistency', { method: 'POST' })
      const data = await res.json()
      alert(data.message || '修复完成')
      fetchCounts()
      fetchRecords()
    } catch (error) {
      console.error('Failed to fix data consistency:', error)
      alert('修复失败')
    }
  }

  const filteredRecords = searchQuery
    ? records.filter((r) =>
        r.title.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : records

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 标签页导航 */}
      <Card>
        <div className="flex flex-wrap gap-1">
          <button
            onClick={() => setActiveTab('unread')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'unread'
                ? 'bg-primary-500 text-white'
                : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-700'
            }`}
          >
            <Clock className="w-4 h-4" />
            未学习 <span className="ml-1 bg-slate-200 dark:bg-slate-700 rounded-full px-2 py-0.5 text-xs">
              {counts.unread}
            </span>
          </button>
          <button
            onClick={() => setActiveTab('read')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'read'
                ? 'bg-primary-500 text-white'
                : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-700'
            }`}
          >
            <CheckCircle className="w-4 h-4" />
            已学习 <span className="ml-1 bg-slate-200 dark:bg-slate-700 rounded-full px-2 py-0.5 text-xs">
              {counts.read}
            </span>
          </button>
          <button
            onClick={() => setActiveTab('bookmarked')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'bookmarked'
                ? 'bg-primary-500 text-white'
                : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-700'
            }`}
          >
            <Star className="w-4 h-4" />
            收藏 <span className="ml-1 bg-slate-200 dark:bg-slate-700 rounded-full px-2 py-0.5 text-xs">
              {counts.bookmarked}
            </span>
          </button>
        </div>
      </Card>

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
            
            <Button
              variant="outline"
              size="md"
              onClick={fixDataConsistency}
              className="text-orange-600 border-orange-300 hover:bg-orange-50"
            >
              修复数据
            </Button>
          </div>
        </div>
      </Card>

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
              isExpanded={expandedId === record.id}
              isEditingNotes={editingNotesId === record.id}
              notesValue={notesValue}
              onToggleExpand={() => toggleExpand(record)}
              onToggleBookmark={() => toggleBookmark(record.id, record.is_bookmarked)}
              onMarkAsRead={() => markAsRead(record.id)}
              onStartEditNotes={() => {
                setEditingNotesId(record.id)
                setNotesValue(record.user_notes || '')
              }}
              onCancelEditNotes={() => setEditingNotesId(null)}
              onSaveNotes={() => saveNotes(record.id)}
              onNotesChange={setNotesValue}
            />
          ))}
        </div>
      ) : (
        <Card>
          <div className="text-center py-12">
            <BookOpen className="w-12 h-12 mx-auto text-slate-300 dark:text-slate-600 mb-4" />
            <p className="text-slate-500 dark:text-slate-400">
              {activeTab === 'unread' && '暂无待学习内容'}
              {activeTab === 'read' && '暂无已学习内容'}
              {activeTab === 'bookmarked' && '暂无收藏内容'}
            </p>
          </div>
        </Card>
      )}

      {/* 分页 */}
      {filteredRecords.length === 10 && (
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
  isExpanded,
  isEditingNotes,
  notesValue,
  onToggleExpand,
  onToggleBookmark,
  onMarkAsRead,
  onStartEditNotes,
  onCancelEditNotes,
  onSaveNotes,
  onNotesChange,
}: {
  record: LearningRecord
  isExpanded: boolean
  isEditingNotes: boolean
  notesValue: string
  onToggleExpand: () => void
  onToggleBookmark: () => void
  onMarkAsRead: () => void
  onStartEditNotes: () => void
  onCancelEditNotes: () => void
  onSaveNotes: () => void
  onNotesChange: (value: string) => void
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
                <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
              )}
              {record.is_read && (
                <CheckCircle className="w-4 h-4 text-green-500" />
              )}
            </div>
            <h3
              className="text-lg font-semibold text-slate-900 dark:text-slate-100 cursor-pointer hover:text-primary-600 dark:hover:text-primary-400 line-clamp-2"
              onClick={onToggleExpand}
            >
              {record.title}
            </h3>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-2xl font-bold text-primary-500">
              {record.total_score.toFixed(1)}
            </span>
            <span className="text-xs text-slate-400">分</span>
            <button
              onClick={onToggleExpand}
              className="p-1 rounded hover:bg-slate-100 dark:hover:bg-slate-700"
            >
              {isExpanded ? (
                <ChevronUp className="w-5 h-5 text-slate-400" />
              ) : (
                <ChevronDown className="w-5 h-5 text-slate-400" />
              )}
            </button>
          </div>
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

        {/* 展开的详情内容 */}
        {isExpanded && (
          <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700 space-y-4">
            {/* 完整总结 */}
            <div>
              <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">核心总结</h4>
              <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                {record.summary}
              </p>
            </div>

            {/* 所有关键要点 */}
            <div>
              <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">关键要点</h4>
              <ul className="space-y-2">
                {record.key_points.map((point, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                    <span className="w-5 h-5 rounded-full bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 flex items-center justify-center text-xs flex-shrink-0 mt-0.5">
                      {index + 1}
                    </span>
                    <span>{point}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* 知识关联 */}
            {record.knowledge_links && record.knowledge_links.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">知识关联</h4>
                <div className="space-y-2">
                  {record.knowledge_links.map((link, index) => (
                    <div key={index} className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-slate-700 dark:text-slate-300">{link.concept}</span>
                        <span className="text-xs px-2 py-0.5 rounded bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400">
                          {link.relation}
                        </span>
                      </div>
                      <p className="text-sm text-slate-500 dark:text-slate-400">{link.note}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 易混淆辨析 */}
            {record.confusion_notes && record.confusion_notes.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">易混淆辨析</h4>
                <div className="space-y-2">
                  {record.confusion_notes.map((note, index) => (
                    <div key={index} className="p-3 rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800">
                      <p className="text-sm font-medium text-amber-700 dark:text-amber-400">{note.item}</p>
                      <p className="text-sm text-amber-600 dark:text-amber-300 mt-1">{note.distinction}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 学习建议 */}
            {record.learning_suggestions && (
              <div>
                <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">学习建议</h4>
                <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                  {record.learning_suggestions}
                </p>
              </div>
            )}

            {/* 学习笔记 */}
            <div>
              <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">我的笔记</h4>
              {isEditingNotes ? (
                <div className="space-y-2">
                  <textarea
                    value={notesValue}
                    onChange={(e) => onNotesChange(e.target.value)}
                    placeholder="记录你的学习心得..."
                    className="w-full p-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm text-slate-700 dark:text-slate-300 focus:outline-none focus:ring-2 focus:ring-primary-500"
                    rows={3}
                  />
                  <div className="flex justify-end gap-2">
                    <Button variant="ghost" size="sm" onClick={onCancelEditNotes}>取消</Button>
                    <Button variant="primary" size="sm" onClick={onSaveNotes}>保存笔记</Button>
                  </div>
                </div>
              ) : (
                <div 
                  className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50 cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800"
                  onClick={onStartEditNotes}
                >
                  {record.user_notes ? (
                    <p className="text-sm text-slate-600 dark:text-slate-400">{record.user_notes}</p>
                  ) : (
                    <p className="text-sm text-slate-400 dark:text-slate-500 italic">点击添加学习笔记...</p>
                  )}
                </div>
              )}
            </div>

            {/* 原文链接 */}
            <div>
              <a
                href={record.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-sm text-primary-600 dark:text-primary-400 hover:underline"
              >
                <ExternalLink className="w-4 h-4" />
                查看原文
              </a>
            </div>

            {/* 操作按钮 */}
            <div className="flex items-center gap-2 pt-2 border-t border-slate-200 dark:border-slate-700">
              <Button
                variant="ghost"
                size="sm"
                onClick={onToggleBookmark}
              >
                <Star
                  className={`w-4 h-4 ${
                    record.is_bookmarked
                      ? 'text-yellow-500 fill-yellow-500'
                      : 'text-slate-400'
                  }`}
                />
                <span className="ml-1">{record.is_bookmarked ? '取消收藏' : '收藏'}</span>
              </Button>
              {!record.is_read && (
                <Button
                  variant="primary"
                  size="sm"
                  onClick={onMarkAsRead}
                >
                  <CheckCircle className="w-4 h-4" />
                  <span className="ml-1">标记已读</span>
                </Button>
              )}
            </div>
          </div>
        )}

        {/* 收起时的操作按钮 */}
        {!isExpanded && (
          <div className="flex items-center gap-2 pt-2 border-t border-slate-200 dark:border-slate-700">
            <Button
              variant="ghost"
              size="sm"
              onClick={onToggleBookmark}
            >
              <Star
                className={`w-4 h-4 ${
                  record.is_bookmarked
                    ? 'text-yellow-500 fill-yellow-500'
                    : 'text-slate-400'
                }`}
              />
              <span className="ml-1">{record.is_bookmarked ? '取消收藏' : '收藏'}</span>
            </Button>
            {!record.is_read && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onMarkAsRead}
              >
                <CheckCircle className="w-4 h-4 text-slate-400" />
                <span className="ml-1">标记已读</span>
              </Button>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={onToggleExpand}
            >
              <BookOpen className="w-4 h-4 text-slate-400" />
              <span className="ml-1">展开学习</span>
            </Button>
          </div>
        )}
      </div>
    </Card>
  )
}