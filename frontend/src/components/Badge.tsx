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
  pending: { label: '待预审', color: 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400' },
  reviewed: { label: '已预审', color: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400' },
  analyzed: { label: '已分析', color: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' },
  rejected: { label: '已拒绝', color: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' },
}

// 数据源友好名称配置
const sourceConfig: Record<string, { label: string; icon?: string }> = {
  // 学术论文源
  arxiv: { label: 'arXiv' },
  openreview: { label: 'OpenReview' },
  semantic_scholar: { label: 'Semantic Scholar' },
  papers_with_code: { label: 'Papers with Code' },
  // 新闻源
  hackernews: { label: 'Hacker News' },
  reddit_ml: { label: 'Reddit ML' },
  reddit_security: { label: 'Reddit Security' },
  reddit_ai: { label: 'Reddit AI' },
  // 技术源
  github_trending: { label: 'GitHub' },
  huggingface: { label: 'Hugging Face' },
  // 安全源
  freebuf: { label: 'FreeBuf' },
  aqniu: { label: '安全牛' },
  security_freebuf: { label: 'FreeBuf' },
  security_aqniu: { label: '安全牛' },
  // AI 公司博客
  blog_openai: { label: 'OpenAI' },
  blog_anthropic: { label: 'Anthropic' },
  blog_google_ai: { label: 'Google AI' },
  blog_deepmind: { label: 'DeepMind' },
  blog_byteDance: { label: '字节跳动' },
  blog_alibaba: { label: '阿里' },
  blog_baidu: { label: '百度' },
}

interface BadgeProps {
  type: 'category' | 'status' | 'source'
  value: string
}

export function Badge({ type, value }: BadgeProps) {
  let config: { label: string; color: string } | undefined

  if (type === 'category') {
    config = categoryConfig[value as ContentCategory]
  } else if (type === 'status') {
    config = statusConfig[value]
  } else if (type === 'source') {
    const sourceInfo = sourceConfig[value]
    if (sourceInfo) {
      return (
        <span className={clsx(
          'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium',
          'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300',
          'border border-slate-200 dark:border-slate-600'
        )}>
          {sourceInfo.label}
        </span>
      )
    }
    // 未配置的来源，显示原始值
    return (
      <span className={clsx(
        'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium',
        'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300',
        'border border-slate-200 dark:border-slate-600'
      )}>
        {value}
      </span>
    )
  }

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
