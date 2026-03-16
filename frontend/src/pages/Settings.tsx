import { useState, useEffect } from 'react'
import {
  Play,
  Pause,
  RefreshCw,
  Clock,
  CheckCircle,
  AlertCircle,
  Key,
  Database,
  Server,
} from 'lucide-react'
import { Card, Button, StatCard } from '@/components'
import { systemApi, collectApi } from '@/services/api'
import type { SystemStatus } from '@/types'

export default function Settings() {
  const [loading, setLoading] = useState(true)
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)
  const [schedulerRunning, setSchedulerRunning] = useState(false)
  const [jobs, setJobs] = useState<any[]>([])
  const [sources, setSources] = useState<any[]>([])

  useEffect(() => {
    fetchSettings()
  }, [])

  async function fetchSettings() {
    try {
      setLoading(true)
      
      const [statusRes, jobsRes, sourcesRes] = await Promise.all([
        systemApi.getStatus(),
        systemApi.getSchedulerJobs(),
        collectApi.getSources(),
      ])
      
      setSystemStatus(statusRes.data)
      setJobs(jobsRes.data.jobs || [])
      setSchedulerRunning(jobsRes.data.is_running || false)
      setSources(sourcesRes.data.sources || [])
    } catch (error) {
      console.error('Failed to fetch settings:', error)
    } finally {
      setLoading(false)
    }
  }

  async function toggleScheduler() {
    try {
      if (schedulerRunning) {
        await systemApi.stopScheduler()
      } else {
        await systemApi.startScheduler()
      }
      setSchedulerRunning(!schedulerRunning)
    } catch (error) {
      console.error('Failed to toggle scheduler:', error)
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
      <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
        系统设置
      </h1>

      {/* 系统状态 */}
      <Card>
        <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4 flex items-center gap-2">
          <Server className="w-5 h-5" />
          系统状态
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatusItem
            label="应用名称"
            value={systemStatus?.app_name || '-'}
          />
          <StatusItem
            label="版本"
            value={systemStatus?.version || '-'}
          />
          <StatusItem
            label="数据库"
            value={systemStatus?.database_connected ? '已连接' : '未连接'}
            status={systemStatus?.database_connected ? 'success' : 'error'}
            icon={<Database className="w-4 h-4" />}
          />
          <StatusItem
            label="LLM配置"
            value={systemStatus?.llm_configured ? '已配置' : '未配置'}
            status={systemStatus?.llm_configured ? 'success' : 'error'}
            icon={<Key className="w-4 h-4" />}
          />
        </div>
      </Card>

      {/* 调度器 */}
      <Card>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
            <Clock className="w-5 h-5" />
            定时任务调度器
          </h2>
          <Button
            variant={schedulerRunning ? 'secondary' : 'primary'}
            icon={schedulerRunning ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            onClick={toggleScheduler}
          >
            {schedulerRunning ? '停止调度' : '启动调度'}
          </Button>
        </div>

        <div className="flex items-center gap-2 mb-4">
          <div
            className={`w-2 h-2 rounded-full ${
              schedulerRunning ? 'bg-green-500 animate-pulse' : 'bg-slate-400'
            }`}
          />
          <span className="text-sm text-slate-500">
            状态: {schedulerRunning ? '运行中' : '已停止'}
          </span>
        </div>

        {jobs.length > 0 && (
          <div className="space-y-2">
            <h3 className="text-sm font-medium text-slate-700 dark:text-slate-300">
              已调度任务
            </h3>
            {jobs.map((job) => (
              <div
                key={job.id}
                className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800"
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium text-slate-900 dark:text-slate-100">
                    {job.name}
                  </span>
                  <span className="text-xs text-slate-500">
                    {job.trigger}
                  </span>
                </div>
                {job.next_run_time && (
                  <p className="text-sm text-slate-500 mt-1">
                    下次执行: {new Date(job.next_run_time).toLocaleString('zh-CN')}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* 数据源 */}
      <Card>
        <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">
          数据源配置
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {sources.map((source) => (
            <div
              key={source.name}
              className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-slate-900 dark:text-slate-100">
                  {source.description}
                </span>
                <span
                  className={`px-2 py-0.5 rounded-full text-xs ${
                    source.type === 'academic'
                      ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
                      : 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400'
                  }`}
                >
                  {source.type === 'academic' ? '学术' : '新闻'}
                </span>
              </div>
              <p className="text-sm text-slate-500">{source.name}</p>
              {source.categories && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {source.categories.map((cat: string) => (
                    <span
                      key={cat}
                      className="px-1.5 py-0.5 rounded text-xs bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-400"
                    >
                      {cat}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </Card>

      {/* 快捷操作 */}
      <Card>
        <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">
          快捷操作
        </h2>
        <div className="flex flex-wrap gap-3">
          <Button
            variant="outline"
            icon={<RefreshCw className="w-4 h-4" />}
            onClick={() => collectApi.trigger()}
          >
            手动采集
          </Button>
          <Button
            variant="outline"
            onClick={() => systemApi.runPipeline({ limit: 10 })}
          >
            运行流水线
          </Button>
          <Button
            variant="outline"
            onClick={fetchSettings}
          >
            刷新状态
          </Button>
        </div>
      </Card>

      {/* 配置说明 */}
      <Card className="bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800">
        <div className="flex gap-3">
          <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-medium text-amber-800 dark:text-amber-200 mb-1">
              配置说明
            </h3>
            <ul className="text-sm text-amber-700 dark:text-amber-300 space-y-1">
              <li>• API Key 配置: 在后端 .env 文件中设置 OPENAI_API_KEY</li>
              <li>• 采集间隔: 默认每 6 小时自动采集一次</li>
              <li>• 评分阈值: 默认 60 分及格，可在后端配置</li>
              <li>• 数据存储: SQLite 数据库，位于 data/metis.db</li>
            </ul>
          </div>
        </div>
      </Card>
    </div>
  )
}

function StatusItem({
  label,
  value,
  status,
  icon,
}: {
  label: string
  value: string
  status?: 'success' | 'error'
  icon?: React.ReactNode
}) {
  return (
    <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800">
      <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
        {icon}
        {label}
      </div>
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
