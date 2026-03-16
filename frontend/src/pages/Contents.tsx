import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Search, Filter, RefreshCw, Clock, CheckCircle, XCircle, FileText, List, Grid } from 'lucide-react'
import { Card, ContentCard, ContentListItem, Button, Badge } from '@/components'
import { contentApi, reviewApi } from '@/services/api'
import type { Content, Review } from '@/types'

export default function Contents() {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  
  const [loading, setLoading] = useState(true)
  const [contents, setContents] = useState<Record<string, Content[]>>({
    pending: [],
    reviewed: [],
    analyzed: [],
    rejected: [],
  })
  const [reviews, setReviews] = useState<Record<string, Review>>({})
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  
  const [statusFilter, setStatusFilter] = useState(searchParams.get('status') || '')
  const [categoryFilter, setCategoryFilter] = useState(searchParams.get('category') || '')
  const [searchQuery, setSearchQuery] = useState('')
  const [activeTab, setActiveTab] = useState(searchParams.get('tab') || 'reviewed') // 默认显示已采纳(待分析)
  const [viewMode, setViewMode] = useState<'list' | 'grid'>('list') // 默认列表视图

  useEffect(() => {
    fetchContents()
  }, [page, activeTab, categoryFilter])

  async function fetchContents() {
    try {
      setLoading(true)
      
      // 获取所有内容，根据当前标签页筛选
      const res = await contentApi.list({
        status: activeTab || undefined,
        category: categoryFilter || undefined,
        page,
        page_size: 20, // 增加每页数量，因为现在按状态分页
      })
      
      // 根据状态分组内容
      const groupedContents: Record<string, Content[]> = {
        pending: [],
        reviewed: [],
        analyzed: [],
        rejected: [],
      }
      
      res.data.data.forEach((content: Content) => {
        if (groupedContents[content.status]) {
          groupedContents[content.status].push(content)
        }
      })
      
      setContents(groupedContents)
      setTotal(res.data.total)

      // 获取已预审内容的评分
      const reviewedIds = res.data.data
        .filter((c: Content) => c.status === 'reviewed' || c.status === 'analyzed')
        .map((c: Content) => c.id)
      
      if (reviewedIds.length > 0) {
        const reviewPromises = reviewedIds.map((id: string) => reviewApi.getByContent(id))
        const reviewResults = await Promise.all(reviewPromises)
        const reviewMap: Record<string, Review> = {}
        reviewResults.forEach((res) => {
          if (res.data) {
            reviewMap[res.data.content_id] = res.data
          }
        })
        setReviews(reviewMap)
      }
    } catch (error) {
      console.error('Failed to fetch contents:', error)
    } finally {
      setLoading(false)
    }
  }

  function handleFilterChange(key: string, value: string) {
    if (key === 'status') {
      setStatusFilter(value)
    } else if (key === 'category') {
      setCategoryFilter(value)
    } else if (key === 'tab') {
      setActiveTab(value)
    }
    setPage(1)
    
    const params = new URLSearchParams(searchParams)
    if (value) {
      params.set(key, value)
    } else {
      params.delete(key)
    }
    setSearchParams(params)
  }

  function handleTabChange(tab: string) {
    setActiveTab(tab)
    setPage(1)
    
    const params = new URLSearchParams(searchParams)
    params.set('tab', tab)
    setSearchParams(params)
  }

  const currentContents = contents[activeTab] || []
  const filteredContents = searchQuery
    ? currentContents.filter((c) =>
        c.title.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : currentContents

  // 获取各状态的数量
  const statusCounts = {
    reviewed: contents.reviewed?.length || 0,
    analyzed: contents.analyzed?.length || 0,
    rejected: contents.rejected?.length || 0,
    pending: contents.pending?.length || 0,
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 标签页导航 */}
      <Card>
        <div className="flex flex-wrap gap-1">
          <button
            onClick={() => handleTabChange('reviewed')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'reviewed'
                ? 'bg-primary-500 text-white'
                : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-700'
            }`}
          >
            <CheckCircle className="w-4 h-4" />
            已采纳 <span className="ml-1 bg-slate-200 dark:bg-slate-700 rounded-full px-2 py-0.5 text-xs">
              {statusCounts.reviewed}
            </span>
          </button>
          <button
            onClick={() => handleTabChange('analyzed')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'analyzed'
                ? 'bg-primary-500 text-white'
                : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-700'
            }`}
          >
            <FileText className="w-4 h-4" />
            已分析 <span className="ml-1 bg-slate-200 dark:bg-slate-700 rounded-full px-2 py-0.5 text-xs">
              {statusCounts.analyzed}
            </span>
          </button>
          <button
            onClick={() => handleTabChange('rejected')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'rejected'
                ? 'bg-primary-500 text-white'
                : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-700'
            }`}
          >
            <XCircle className="w-4 h-4" />
            已拒绝 <span className="ml-1 bg-slate-200 dark:bg-slate-700 rounded-full px-2 py-0.5 text-xs">
              {statusCounts.rejected}
            </span>
          </button>
          <button
            onClick={() => handleTabChange('pending')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'pending'
                ? 'bg-primary-500 text-white'
                : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-700'
            }`}
          >
            <Clock className="w-4 h-4" />
            待处理 <span className="ml-1 bg-slate-200 dark:bg-slate-700 rounded-full px-2 py-0.5 text-xs">
              {statusCounts.pending}
            </span>
          </button>
        </div>
      </Card>

      {/* 搜索和筛选 */}
      <Card>
        <div className="flex flex-col md:flex-row gap-4">
          {/* 搜索框 */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="text"
              placeholder="搜索内容..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          {/* 视图模式和分类筛选 */}
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-slate-400" />
            
            {/* 分类筛选 */}
            <select
              value={categoryFilter}
              onChange={(e) => handleFilterChange('category', e.target.value)}
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

            {/* 视图模式切换 */}
            <div className="flex border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 ${viewMode === 'list' ? 'bg-primary-500 text-white' : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700'}`}
              >
                <List className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 ${viewMode === 'grid' ? 'bg-primary-500 text-white' : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700'}`}
              >
                <Grid className="w-4 h-4" />
              </button>
            </div>

            <Button
              variant="outline"
              size="md"
              icon={<RefreshCw className="w-4 h-4" />}
              onClick={fetchContents}
            >
              刷新
            </Button>
          </div>
        </div>
      </Card>

      {/* 当前标签页的统计信息 */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-500 dark:text-slate-400">
          共 <span className="font-medium text-slate-700 dark:text-slate-300">{filteredContents.length}</span> 条内容
        </p>
        <div className="flex gap-2">
          {categoryFilter && (
            <Badge type="category" value={categoryFilter} />
          )}
        </div>
      </div>

      {/* 内容列表 */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500" />
        </div>
      ) : filteredContents.length > 0 ? (
        viewMode === 'list' ? (
          <Card className="p-0">
            {filteredContents.map((content) => (
              <ContentListItem
                key={content.id}
                content={content}
                review={reviews[content.id]}
                onClick={() => navigate(`/contents/${content.id}`)}
              />
            ))}
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredContents.map((content) => (
              <ContentCard
                key={content.id}
                content={content}
                review={reviews[content.id]}
                onClick={() => navigate(`/contents/${content.id}`)}
              />
            ))}
          </div>
        )
      ) : (
        <Card>
          <div className="text-center py-12">
            <p className="text-slate-500 dark:text-slate-400">
              {searchQuery ? '未找到匹配的内容' : '暂无内容'}
            </p>
            <Button
              variant="primary"
              className="mt-4"
              onClick={() => navigate('/')}
            >
              去采集
            </Button>
          </div>
        </Card>
      )}

      {/* 分页 */}
      {filteredContents.length > 0 && (
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
            disabled={page * 20 >= (filteredContents.length || 1)}
            onClick={() => setPage((p) => p + 1)}
          >
            下一页
          </Button>
        </div>
      )}
    </div>
  )
}
