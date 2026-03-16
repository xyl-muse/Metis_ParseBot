import { Clock, ExternalLink, ChevronRight } from 'lucide-react'
import { format, formatDistanceToNow } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import { Badge } from './Badge'
import { ScoreDisplay } from './ScoreDisplay'
import type { Content, Review } from '@/types'

interface ContentListItemProps {
  content: Content
  review?: Review
  onClick?: () => void
}

export function ContentListItem({ content, review, onClick }: ContentListItemProps) {
  const timeAgo = formatDistanceToNow(new Date(content.collected_at), {
    addSuffix: true,
    locale: zhCN,
  })

  return (
    <div
      onClick={onClick}
      className="flex items-center gap-4 p-4 border-b border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors cursor-pointer"
    >
      {/* 评分显示 - 如果有评分 */}
      {review && (
        <div className="w-20 flex-shrink-0">
          <ScoreDisplay
            scores={review.score_detail}
            totalScore={review.total_score}
            passed={review.passed}
            compact
          />
        </div>
      )}
      
      {/* 内容信息 */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start gap-2">
          <h3 className="flex-1 text-base font-medium text-slate-900 dark:text-slate-100 truncate">
            {content.title}
          </h3>
          <ChevronRight className="w-5 h-5 text-slate-400 flex-shrink-0" />
        </div>
        
        <div className="flex flex-wrap items-center gap-2 mt-1">
          <Badge type="category" value={content.category} />
          <Badge type="status" value={content.status} />
          <span className="text-xs px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-700">
            {content.source}
          </span>
        </div>
        
        {/* 摘要预览 */}
        {content.summary && (
          <p className="mt-1 text-sm text-slate-600 dark:text-slate-400 line-clamp-1">
            {content.summary}
          </p>
        )}
      </div>
      
      {/* 时间信息 */}
      <div className="flex-shrink-0 text-right text-sm text-slate-500 dark:text-slate-500">
        <div className="flex items-center gap-1 justify-end">
          <Clock className="w-4 h-4" />
          <span>{timeAgo}</span>
        </div>
      </div>
    </div>
  )
}