import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  FileText,
  CheckCircle,
  XCircle,
  Brain,
  TrendingUp,
  RefreshCw,
  Zap,
} from 'lucide-react'
import { StatCard, Card, Button, ContentCard } from '@/components'
import { contentApi, collectApi, reviewApi, analyzeApi, systemApi } from '@/services/api'
import type { Content, SystemStatus, CollectResult } from '@/types'

export default function Dashboard() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    reviewed: 0,
    analyzed: 0,
  })
  const [recentContents, setRecentContents] = useState<Content[]>([])
  const [pipelineLoading, setPipelineLoading] = useState(false)
  const [pipelineResult, setPipelineResult] = useState<CollectResult | null>(null)
  const [collectLoading, setCollectLoading] = useState(false)
  const [reviewLoading, setReviewLoading] = useState(false)
  const [analyzeLoading, setAnalyzeLoading] = useState(false)
  const [actionMessage, setActionMessage] = useState<string | null>(null)
  const [actionStatus, setActionStatus] = useState<'success' | 'error' | null>(null)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  async function fetchDashboardData() {
    try {
      setLoading(true)
      
      // 获取系统状态
      const statusRes = await systemApi.getStatus()
      setSystemStatus(statusRes.data)

      // 使用 dashboard API 获取统计数据
      const dashboardRes = await fetch('/api/contents/dashboard')
      const dashboardData = await dashboardRes.json()
      
      setStats({
        total: dashboardData.total,
        pending: dashboardData.status_counts?.pending || 0,
        reviewed: dashboardData.status_counts?.reviewed || 0,
        analyzed: dashboardData.status_counts?.analyzed || 0,
      })

      setRecentContents(dashboardData.recent_contents || [])
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  async function runPipeline() {
    try {
      setPipelineLoading(true)
      setActionMessage(null)
      const res = await systemApi.runPipeline({ limit: 20 })
      if (res.data.success) {
        setActionStatus('success')
        setActionMessage('流水线执行成功！')
      }
      fetchDashboardData()
    } catch (error) {
      console.error('Failed to run pipeline:', error)
      setActionStatus('error')
      setActionMessage('流水线执行失败')
    } finally {
      setPipelineLoading(false)
    }
  }

  async function handleCollect() {
    try {
      setCollectLoading(true)
      setActionMessage(null)
      const res = await collectApi.trigger()
      if (res.data.success && res.data.data) {
        const result = res.data.data as unknown as CollectResult
        setActionStatus('success')
        setActionMessage(`采集成功！发现 ${result.total_found} 条，采集 ${result.total_collected} 条`)
        fetchDashboardData()
      }
    } catch (error) {
      console.error('Failed to collect:', error)
      setActionStatus('error')
      setActionMessage('采集失败，请查看控制台日志')
    } finally {
      setCollectLoading(false)
    }
  }

  async function handleReview() {
    try {
      setReviewLoading(true)
      setActionMessage(null)
      const res = await reviewApi.trigger({ limit: 10 })
      if (res.data.success) {
        setActionStatus('success')
        setActionMessage('预审完成！')
        fetchDashboardData()
      }
    } catch (error) {
      console.error('Failed to review:', error)
      setActionStatus('error')
      setActionMessage('预审失败，请查看控制台日志')
    } finally {
      setReviewLoading(false)
    }
  }

  async function handleAnalyze() {
    try {
      setAnalyzeLoading(true)
      setActionMessage(null)
      const res = await analyzeApi.trigger({ limit: 5 })
      if (res.data.success) {
        setActionStatus('success')
        setActionMessage('分析完成！')
        fetchDashboardData()
      }
    } catch (error) {
      console.error('Failed to analyze:', error)
      setActionStatus('error')
      setActionMessage('分析失败，请查看控制台日志')
    } finally {
      setAnalyzeLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500" />
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 欢迎区域 */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
            欢迎使用 Metis_ParseBot
          </h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">
            智能知识采集与分析系统
          </p>
        </div>
        <Button
          onClick={runPipeline}
          loading={pipelineLoading}
          icon={<Zap className="w-4 h-4" />}
          size="lg"
        >
          一键运行流水线
        </Button>
      </div>

      {/* 操作结果提示 */}
      {actionMessage && (
        <Card className={`${actionStatus === 'success' ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800' : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'}`}>
          <div className="flex items-center gap-3">
            {actionStatus === 'success' ? (
              <CheckCircle className="w-5 h-5 text-green-600" />
            ) : (
              <XCircle className="w-5 h-5 text-red-600" />
            )}
            <p className={`font-medium ${actionStatus === 'success' ? 'text-green-800 dark:text-green-200' : 'text-red-800 dark:text-red-200'}`}>
              {actionMessage}
            </p>
          </div>
        </Card>
      )}

      {/* 流水线结果 */}
      {pipelineResult && (
        <Card className="bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800">
          <div className="flex items-center gap-3">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <div>
              <p className="font-medium text-green-800 dark:text-green-200">
                流水线执行成功
              </p>
              <p className="text-sm text-green-600 dark:text-green-400">
                发现 {pipelineResult.total_found} 条，采集 {pipelineResult.total_collected} 条
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="总内容数"
          value={stats.total}
          icon={<FileText className="w-5 h-5" />}
          color="primary"
        />
        <StatCard
          title="待处理"
          value={stats.pending}
          icon={<RefreshCw className="w-5 h-5" />}
          color="orange"
        />
        <StatCard
          title="已预审"
          value={stats.reviewed}
          icon={<CheckCircle className="w-5 h-5" />}
          color="accent"
        />
        <StatCard
          title="已分析"
          value={stats.analyzed}
          icon={<Brain className="w-5 h-5" />}
          color="green"
        />
      </div>

      {/* 快捷操作 */}
      <Card>
        <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">
          快捷操作
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <QuickAction
            icon={<RefreshCw className="w-5 h-5" />}
            label="采集内容"
            onClick={handleCollect}
            loading={collectLoading}
          />
          <QuickAction
            icon={<TrendingUp className="w-5 h-5" />}
            label="预审评分"
            onClick={handleReview}
            loading={reviewLoading}
          />
          <QuickAction
            icon={<Brain className="w-5 h-5" />}
            label="分析内容"
            onClick={handleAnalyze}
            loading={analyzeLoading}
          />
          <QuickAction
            icon={<Zap className="w-5 h-5" />}
            label="完整流水线"
            onClick={runPipeline}
            loading={pipelineLoading}
          />
        </div>
      </Card>

      {/* 最近内容 */}
      <Card>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
            最近采集
          </h2>
          <Button variant="ghost" size="sm" onClick={() => navigate('/contents')}>
            查看全部
          </Button>
        </div>
        <div className="space-y-4">
          {recentContents.length > 0 ? (
            recentContents.map((content) => (
              <ContentCard
                key={content.id}
                content={content}
                onClick={() => navigate(`/contents/${content.id}`)}
              />
            ))
          ) : (
            <div className="text-center py-8 text-slate-500">
              暂无内容，点击"采集内容"开始采集
            </div>
          )}
        </div>
      </Card>

      {/* 系统状态 */}
      {systemStatus && (
        <Card>
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">
            系统状态
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatusItem label="应用名称" value={systemStatus.app_name} />
            <StatusItem label="版本" value={systemStatus.version} />
            <StatusItem
              label="数据库"
              value={systemStatus.database_connected ? '已连接' : '未连接'}
              status={systemStatus.database_connected ? 'success' : 'error'}
            />
            <StatusItem
              label="LLM配置"
              value={systemStatus.llm_configured ? '已配置' : '未配置'}
              status={systemStatus.llm_configured ? 'success' : 'error'}
            />
          </div>
        </Card>
      )}
    </div>
  )
}

function QuickAction({
  icon,
  label,
  onClick,
  loading,
}: {
  icon: React.ReactNode
  label: string
  onClick: () => void
  loading?: boolean
}) {
  return (
    <button
      onClick={onClick}
      disabled={loading}
      className={`flex flex-col items-center gap-2 p-4 rounded-xl bg-slate-50 dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
    >
      <div className="text-primary-500">
        {loading ? <div className="w-5 h-5 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" /> : icon}
      </div>
      <span className="text-sm font-medium text-slate-700 dark:text-slate-300">{loading ? '处理中...' : label}</span>
    </button>
  )
}

function StatusItem({
  label,
  value,
  status,
}: {
  label: string
  value: string
  status?: 'success' | 'error'
}) {
  return (
    <div>
      <p className="text-sm text-slate-500 dark:text-slate-400">{label}</p>
      <p
        className={`mt-1 font-medium ${
          status === 'success'
            ? 'text-green-600 dark:text-green-400'
            : status === 'error'
            ? 'text-red-600 dark:text-red-400'
            : 'text-slate-900 dark:text-slate-100'
        }`}
      >
        {value}
      </p>
    </div>
  )
}