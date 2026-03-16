import clsx from 'clsx'
import type { ContentCategory } from '@/types'

const categoryConfig: Record<ContentCategory, { label: string; color: string }> = {
  academic_ai: { label: 'AI论文', color: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' },
  academic_security: { label: '安全论文', color: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' },
  academic_cross: { label: '交叉论文', color: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400' },
  news_ai: { label: 'AI新闻', color: 'bg-cyan-100 text-cyan-700 dark:bg-cyan-900/30 dark:text-cyan-400' },
  news_security: { label: '安全新闻', color: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400' },
  news_cross: { label: '交叉新闻', color: 'bg-pink-100 text-pink-700 dark:bg-pink-900/30 dark:text-pink-400' },
}

const statusConfig: Record<string, { label: string; color: string }> = {
  pending: { label: '待处理', color: 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400' },
  reviewed: { label: '已预审', color: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400' },
  analyzed: { label: '已分析', color: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' },
  rejected: { label: '已拒绝', color: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' },
}

interface BadgeProps {
  type: 'category' | 'status'
  value: string
}

export function Badge({ type, value }: BadgeProps) {
  const config = type === 'category'
    ? categoryConfig[value as ContentCategory]
    : statusConfig[value]

  if (!config) return null

  return (
    <span className={clsx(
      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
      config.color
    )}>
      {config.label}
    </span>
  )
}
