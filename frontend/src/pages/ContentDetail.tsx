import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  ExternalLink,
  Clock,
  Tag,
  Brain,
  Link2,
  AlertCircle,
  BookOpen,
  Trash2,
} from 'lucide-react'
import { Card, Button, Badge, ScoreDisplay } from '@/components'
import { contentApi, reviewApi, analyzeApi } from '@/services/api'
import type { Content, Review, Analysis } from '@/types'
import { format } from 'date-fns'
import { zhCN } from 'date-fns/locale'

export default function ContentDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  
  const [loading, setLoading] = useState(true)
  const [content, setContent] = useState<Content | null>(null)
  const [review, setReview] = useState<Review | null>(null)
  const [analysis, setAnalysis] = useState<Analysis | null>(null)

  useEffect(() => {
    if (id) {
      fetchContent(id)
    }
  }, [id])

  async function fetchContent(contentId: string) {
    try {
      setLoading(true)
      
      const contentRes = await contentApi.get(contentId)
      setContent(contentRes.data)

      if (contentRes.data.status === 'reviewed' || contentRes.data.status === 'analyzed') {
        const reviewRes = await reviewApi.getByContent(contentId)
        setReview(reviewRes.data)
      }

      if (contentRes.data.status === 'analyzed') {
        const analysisRes = await analyzeApi.getByContent(contentId)
        setAnalysis(analysisRes.data)
      }
    } catch (error) {
      console.error('Failed to fetch content:', error)
      navigate('/contents')
    } finally {
      setLoading(false)
    }
  }

  async function handleDelete() {
    if (!id || !confirm('确定要删除这条内容吗？')) return
    
    try {
      await contentApi.delete(id)
      navigate('/contents')
    } catch (error) {
      console.error('Failed to delete content:', error)
    }
  }

  if (loading || !content) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500" />
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 返回按钮 */}
      <Button
        variant="ghost"
        icon={<ArrowLeft className="w-4 h-4" />}
        onClick={() => navigate('/contents')}
      >
        返回列表
      </Button>

      {/* 主标题 */}
      <Card>
        <div className="space-y-4">
          <div className="flex items-start justify-between gap-4">
            <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
              {content.title}
            </h1>
            <a
              href={content.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-shrink-0"
            >
              <Button variant="outline" icon={<ExternalLink className="w-4 h-4" />}>
                查看原文
              </Button>
            </a>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Badge type="category" value={content.category} />
            <Badge type="status" value={content.status} />
            {content.tags?.map((tag) => (
              <span
                key={tag}
                className="px-2 py-0.5 rounded-full text-xs bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
              >
                {tag}
              </span>
            ))}
          </div>

          <div className="flex items-center gap-4 text-sm text-slate-500">
            <div className="flex items-center gap-1">
              <Clock className="w-4 h-4" />
              <span>
                {format(new Date(content.collected_at), 'PPP', { locale: zhCN })}
              </span>
            </div>
            <div className="flex items-center gap-1">
              <Tag className="w-4 h-4" />
              <span>{content.source}</span>
            </div>
            {content.authors && content.authors.length > 0 && (
              <span>作者: {content.authors.join(', ')}</span>
            )}
          </div>
        </div>
      </Card>

      {/* 原始摘要 */}
      {content.summary && (
        <Card>
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-3">
            原始摘要
          </h2>
          <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
            {content.summary}
          </p>
        </Card>
      )}

      {/* 预审评分 */}
      {review && (
        <Card>
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">
            价值评分
          </h2>
          <ScoreDisplay
            scores={review.score_detail}
            totalScore={review.total_score}
            passed={review.passed}
          />
          {review.review_notes && (
            <p className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700 text-sm text-slate-500">
              {review.review_notes}
            </p>
          )}
        </Card>
      )}

      {/* 分析结果 */}
      {analysis && (
        <>
          {/* 核心总结 */}
          <Card>
            <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-3 flex items-center gap-2">
              <Brain className="w-5 h-5 text-primary-500" />
              核心总结
            </h2>
            <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
              {analysis.summary}
            </p>
          </Card>

          {/* 关键要点 */}
          <Card>
            <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-3">
              关键要点
            </h2>
            <ul className="space-y-2">
              {analysis.key_points.map((point, index) => (
                <li
                  key={index}
                  className="flex items-start gap-2 text-slate-600 dark:text-slate-400"
                >
                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 flex items-center justify-center text-sm font-medium">
                    {index + 1}
                  </span>
                  <span>{point}</span>
                </li>
              ))}
            </ul>
          </Card>

          {/* 知识关联 */}
          {analysis.knowledge_links && analysis.knowledge_links.length > 0 && (
            <Card>
              <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-3 flex items-center gap-2">
                <Link2 className="w-5 h-5 text-accent-500" />
                知识关联
              </h2>
              <div className="space-y-3">
                {analysis.knowledge_links.map((link, index) => (
                  <div
                    key={index}
                    className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-slate-900 dark:text-slate-100">
                        {link.concept}
                      </span>
                      <span className="text-xs px-2 py-0.5 rounded-full bg-accent-100 dark:bg-accent-900/30 text-accent-600 dark:text-accent-400">
                        {link.relation}
                      </span>
                    </div>
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                      {link.note}
                    </p>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* 易混淆辨析 */}
          {analysis.confusion_notes && analysis.confusion_notes.length > 0 && (
            <Card>
              <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-3 flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-orange-500" />
                易混淆辨析
              </h2>
              <div className="space-y-3">
                {analysis.confusion_notes.map((note, index) => (
                  <div
                    key={index}
                    className="p-3 rounded-xl bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800"
                  >
                    <p className="font-medium text-orange-800 dark:text-orange-200 mb-1">
                      {note.item}
                    </p>
                    <p className="text-sm text-orange-600 dark:text-orange-400">
                      区分要点: {note.distinction}
                    </p>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* 学习建议 */}
          {analysis.learning_suggestions && (
            <Card>
              <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-3 flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-green-500" />
                学习建议
              </h2>
              <p className="text-slate-600 dark:text-slate-400">
                {analysis.learning_suggestions}
              </p>
            </Card>
          )}
        </>
      )}

      {/* 操作按钮 */}
      <Card>
        <div className="flex items-center justify-between">
          <Button
            variant="outline"
            icon={<Trash2 className="w-4 h-4" />}
            className="text-red-600 border-red-200 hover:bg-red-50 dark:border-red-800 dark:hover:bg-red-900/20"
            onClick={handleDelete}
          >
            删除内容
          </Button>
          <div className="text-sm text-slate-500">
            ID: {content.id}
          </div>
        </div>
      </Card>
    </div>
  )
}
