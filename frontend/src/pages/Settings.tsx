import { useState, useEffect } from 'react'
import {
  Play,
  Pause,
  RefreshCw,
  Clock,
  Key,
  Database,
  Server,
  Save,
  AlertCircle,
  Settings as SettingsIcon,
} from 'lucide-react'
import { Card, Button } from '@/components'
import { systemApi, settingsApi } from '@/services/api'

interface SystemSettings {
  app_name: string
  version: string
  database: {
    type: string
    connected: boolean
    url_display: string
  }
  llm: {
    provider: string | null
    model: string | null
    configured: boolean
    api_base?: string
    temperature?: number
  }
  collect_interval_hours: number
  max_items_per_run: number
  passing_score: number
}

interface EnvConfig {
  openai_api_key: string
  openai_api_base: string
  model_name: string
  model_temperature: number
  passing_score: number
  collect_interval_hours: number
}

export default function Settings() {
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [systemStatus, setSystemStatus] = useState<SystemSettings | null>(null)
  const [schedulerRunning, setSchedulerRunning] = useState(false)
  const [envConfig, setEnvConfig] = useState<EnvConfig>({
    openai_api_key: '',
    openai_api_base: 'https://api.openai.com/v1',
    model_name: 'gpt-4',
    model_temperature: 0.2,
    passing_score: 60,
    collect_interval_hours: 6,
  })
  const [editMode, setEditMode] = useState(false)

  useEffect(() => {
    fetchSettings()
  }, [])

  async function fetchSettings() {
    try {
      setLoading(true)
      
      const [statusRes, jobsRes, envRes] = await Promise.all([
        settingsApi.get(),
        systemApi.getSchedulerJobs(),
        settingsApi.getEnv(),
      ])
      
      setSystemStatus(statusRes.data)
      setSchedulerRunning(jobsRes.data.is_running || false)
      setEnvConfig(envRes.data)
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

  async function saveEnvConfig() {
    try {
      setSaving(true)
      const res = await settingsApi.updateEnv(envConfig)
      alert(res.data.message || '配置已保存')
      setEditMode(false)
      fetchSettings()
    } catch (error) {
      console.error('Failed to save config:', error)
      alert('保存失败')
    } finally {
      setSaving(false)
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
            value={systemStatus?.app_name || 'Metis'}
          />
          <StatusItem
            label="版本"
            value={systemStatus?.version || '-'}
          />
          <StatusItem
            label="数据库"
            value={systemStatus?.database?.connected 
              ? `${systemStatus.database.type} (${systemStatus.database.url_display})` 
              : '未连接'}
            status={systemStatus?.database?.connected ? 'success' : 'error'}
            icon={<Database className="w-4 h-4" />}
          />
          <StatusItem
            label="LLM配置"
            value={systemStatus?.llm?.configured 
              ? `${systemStatus.llm.provider} (${systemStatus.llm.model})` 
              : '未配置'}
            status={systemStatus?.llm?.configured ? 'success' : 'error'}
            icon={<Key className="w-4 h-4" />}
          />
        </div>
      </Card>

      {/* LLM配置 */}
      <Card>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
            <SettingsIcon className="w-5 h-5" />
            LLM 配置
          </h2>
          <div className="flex gap-2">
            {editMode ? (
              <>
                <Button
                  variant="outline"
                  onClick={() => setEditMode(false)}
                >
                  取消
                </Button>
                <Button
                  variant="primary"
                  icon={<Save className="w-4 h-4" />}
                  onClick={saveEnvConfig}
                  loading={saving}
                >
                  保存配置
                </Button>
              </>
            ) : (
              <Button
                variant="outline"
                onClick={() => setEditMode(true)}
              >
                编辑配置
              </Button>
            )}
          </div>
        </div>

        <div className="space-y-4">
          <ConfigRow
            label="API Key"
            value={envConfig.openai_api_key || '未设置'}
            editMode={editMode}
            type="password"
            onChange={(v) => setEnvConfig({ ...envConfig, openai_api_key: v })}
          />
          <ConfigRow
            label="API Base URL"
            value={envConfig.openai_api_base}
            editMode={editMode}
            onChange={(v) => setEnvConfig({ ...envConfig, openai_api_base: v })}
          />
          <ConfigRow
            label="模型名称"
            value={envConfig.model_name}
            editMode={editMode}
            onChange={(v) => setEnvConfig({ ...envConfig, model_name: v })}
          />
          <ConfigRow
            label="Temperature"
            value={String(envConfig.model_temperature)}
            editMode={editMode}
            type="number"
            onChange={(v) => setEnvConfig({ ...envConfig, model_temperature: parseFloat(v) || 0.2 })}
          />
          <ConfigRow
            label="及格分数"
            value={String(envConfig.passing_score)}
            editMode={editMode}
            type="number"
            onChange={(v) => setEnvConfig({ ...envConfig, passing_score: parseInt(v) || 60 })}
          />
          <ConfigRow
            label="采集间隔 (小时)"
            value={String(envConfig.collect_interval_hours)}
            editMode={editMode}
            type="number"
            onChange={(v) => setEnvConfig({ ...envConfig, collect_interval_hours: parseInt(v) || 6 })}
          />
        </div>

        {editMode && (
          <div className="mt-4 p-3 rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800">
            <p className="text-sm text-amber-700 dark:text-amber-300">
              保存配置后需要重启后端服务才能生效
            </p>
          </div>
        )}
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

        {/* 调度器说明 */}
        <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50 text-sm text-slate-600 dark:text-slate-400">
          <p className="mb-2">
            <strong>功能说明：</strong>定时任务调度器用于自动执行周期性的知识采集任务。
          </p>
          <p className="mb-2">
            <strong>工作流程：</strong>每隔 {envConfig.collect_interval_hours} 小时自动执行一次采集→预审→分析的完整流水线，持续更新知识库。
          </p>
          <p>
            <strong>当前配置：</strong>采集间隔 {envConfig.collect_interval_hours} 小时，每次最多采集 {systemStatus?.max_items_per_run || 50} 条内容，预审及格线 {envConfig.passing_score} 分。
          </p>
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
              <li>• <strong>API Key</strong>：OpenAI 或兼容 API 的密钥，必填</li>
              <li>• <strong>API Base URL</strong>：API 端点地址，默认为 OpenAI 官方地址</li>
              <li>• <strong>模型名称</strong>：使用的 LLM 模型，推荐 gpt-4 或 gpt-3.5-turbo</li>
              <li>• <strong>Temperature</strong>：生成温度，值越低输出越稳定，推荐 0.2</li>
              <li>• <strong>及格分数</strong>：预审通过阈值，低于此分数的内容将被拒绝</li>
              <li>• <strong>采集间隔</strong>：自动采集的时间间隔（小时）</li>
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

function ConfigRow({
  label,
  value,
  editMode,
  type = 'text',
  onChange,
}: {
  label: string
  value: string
  editMode: boolean
  type?: 'text' | 'password' | 'number'
  onChange: (value: string) => void
}) {
  return (
    <div className="flex items-center gap-4">
      <label className="w-32 text-sm font-medium text-slate-700 dark:text-slate-300 flex-shrink-0">
        {label}
      </label>
      {editMode ? (
        <input
          type={type === 'password' ? 'password' : type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="flex-1 px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      ) : (
        <span className="flex-1 text-sm text-slate-600 dark:text-slate-400">
          {type === 'password' && value ? '••••••••' : value}
        </span>
      )}
    </div>
  )
}