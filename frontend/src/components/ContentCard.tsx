import { Clock, ExternalLink } from 'lucide-react'
import { format, formatDistanceToNow } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import { Card } from './Card'
import { Badge } from './Badge'
import { ScoreDisplay } from './ScoreDisplay'
import type { Content, Review } from '@/types'

interface ContentCardProps {
  content: Content
  review?: Review
  onClick?: () => void
}

export function ContentCard({ content, review, onClick }: ContentCardProps) {
  const timeAgo = formatDistanceToNow(new Date(content.collected_at), {
    addSuffix: true,
    locale: zhCN,
  })

  return (
    <Card hover onClick={onClick} className="group">
      <div className="space-y-4">
        {/* 标题和分类 */}
        <div>
          <div className="flex items-start justify-between gap-3">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 line-clamp-2 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
              {content.title}
            </h3>
            <ExternalLink
              className="w-4 h-4 text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0"
            />
          </div>
          <div className="flex items-center gap-2 mt-2">
            <Badge type="source" value={content.source} />
            <Badge type="category" value={content.category} />
            <Badge type="status" value={content.status} />
          </div>
        </div>

        {/* 摘要 */}
        {content.summary && (
          <p className="text-sm text-slate-600 dark:text-slate-400 line-clamp-3">
            {content.summary}
          </p>
        )}

        {/* 元信息 */}
        <div className="flex items-center justify-between text-sm text-slate-500 dark:text-slate-500">
          <div className="flex items-center gap-1">
            <Clock className="w-4 h-4" />
            <span>{timeAgo}</span>
          </div>
          <span className="px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-xs">
            {content.source}
          </span>
        </div>

        {/* 评分（如果有） */}
        {review && (
          <div className="pt-3 border-t border-slate-200 dark:border-slate-700">
            <ScoreDisplay
              scores={review.score_detail}
              totalScore={review.total_score}
              passed={review.passed}
              compact
            />
          </div>
        )}
      </div>
    </Card>
  )
}
