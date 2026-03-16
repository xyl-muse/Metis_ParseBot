import clsx from 'clsx'

interface ScoreDisplayProps {
  scores: {
    novelty_score: number
    utility_score: number
    authority_score: number
    timeliness_score: number
    completeness_score: number
  }
  totalScore: number
  passed: boolean
  compact?: boolean
}

const scoreLabels: Record<string, string> = {
  novelty_score: '新颖性',
  utility_score: '实用性',
  authority_score: '权威性',
  timeliness_score: '时效性',
  completeness_score: '完整性',
}

export function ScoreDisplay({ scores, totalScore, passed, compact = false }: ScoreDisplayProps) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'bg-green-500'
    if (score >= 60) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  const getTotalColor = (score: number) => {
    if (score >= 80) return 'text-green-600 dark:text-green-400'
    if (score >= 60) return 'text-yellow-600 dark:text-yellow-400'
    return 'text-red-600 dark:text-red-400'
  }

  if (compact) {
    return (
      <div className="flex items-center gap-2">
        <span className={clsx('text-lg font-bold', getTotalColor(totalScore))}>
          {totalScore.toFixed(1)}
        </span>
        <span className={clsx(
          'px-2 py-0.5 rounded text-xs font-medium',
          passed
            ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
            : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
        )}>
          {passed ? '通过' : '未通过'}
        </span>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* 总分 */}
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-slate-600 dark:text-slate-400">总分</span>
        <div className="flex items-center gap-2">
          <span className={clsx('text-2xl font-bold', getTotalColor(totalScore))}>
            {totalScore.toFixed(1)}
          </span>
          <span className={clsx(
            'px-2 py-1 rounded-lg text-sm font-medium',
            passed
              ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
              : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
          )}>
            {passed ? '通过' : '未通过'}
          </span>
        </div>
      </div>

      {/* 分项得分 */}
      <div className="space-y-3">
        {Object.entries(scores).map(([key, value]) => (
          <div key={key}>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm text-slate-600 dark:text-slate-400">
                {scoreLabels[key]}
              </span>
              <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                {value}
              </span>
            </div>
            <div className="h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
              <div
                className={clsx('h-full score-bar rounded-full', getScoreColor(value))}
                style={{ width: `${value}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
