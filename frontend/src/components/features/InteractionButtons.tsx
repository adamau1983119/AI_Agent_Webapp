/**
 * 互動按鈕組件
 * 提供 Like/Dislike/Edit/Replace 功能
 */
import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { interactionsAPI } from '@/api/client'
import { ThumbsUp, ThumbsDown, Pencil, Image as ImageIcon, History } from 'lucide-react'
import { useTranslation } from '@/i18n'
import toast from 'react-hot-toast'
import { RatingReason, positiveReasons, negativeReasons, ratingReasonI18nKeys } from '@/api/ratings'
import { useAuthStore } from '@/stores/authStore'
import { APIError } from '@/api/errors'

type InteractionSubmitVars = {
  reasons?: RatingReason[]
  comment?: string
}

interface InteractionButtonsProps {
  topicId: string
  articleId?: string
  scriptId?: string
  onEdit?: () => void
  onReplace?: () => void
  onViewHistory?: () => void
  userId?: string
}

export default function InteractionButtons({
  topicId,
  articleId,
  scriptId,
  onEdit,
  onReplace,
  onViewHistory,
  userId,
}: InteractionButtonsProps) {
  const { t } = useTranslation()
  const { user } = useAuthStore()
  const effectiveUserId = userId ?? user?.id ?? 'user_default'
  const queryClient = useQueryClient()
  const [isLiked, setIsLiked] = useState(false)
  const [isDisliked, setIsDisliked] = useState(false)
  const [showReasonPanel, setShowReasonPanel] = useState(false)
  const [selectedAction, setSelectedAction] = useState<'like' | 'dislike' | null>(null)
  const [selectedReasons, setSelectedReasons] = useState<RatingReason[]>([])
  const [comment, setComment] = useState('')

  const submitInteraction = (action: 'like' | 'dislike', vars: InteractionSubmitVars) =>
    interactionsAPI.createInteraction({
      user_id: effectiveUserId,
      topic_id: topicId,
      article_id: articleId,
      script_id: scriptId,
      action,
      reasons: vars.reasons,
      comment: vars.comment,
    })

  const formatInteractionError = (error: unknown) => {
    if (error instanceof APIError) return error.message
    if (error instanceof Error) return error.message
    return t('common.failed')
  }

  // Like mutation
  const likeMutation = useMutation({
    mutationFn: (vars: InteractionSubmitVars) => submitInteraction('like', vars),
    onSuccess: () => {
      setIsLiked(true)
      setIsDisliked(false)
      setShowReasonPanel(false)
      setSelectedAction(null)
      setSelectedReasons([])
      setComment('')
      toast.success(t('common.success'))
      // 更新偏好模型
      queryClient.invalidateQueries({ queryKey: ['user', 'preferences'] })
    },
    onError: (error: unknown) => {
      toast.error(formatInteractionError(error))
    },
  })

  // Dislike mutation
  const dislikeMutation = useMutation({
    mutationFn: (vars: InteractionSubmitVars) => submitInteraction('dislike', vars),
    onSuccess: () => {
      setIsDisliked(true)
      setIsLiked(false)
      setShowReasonPanel(false)
      setSelectedAction(null)
      setSelectedReasons([])
      setComment('')
      toast.success(t('common.success'))
      // 更新偏好模型
      queryClient.invalidateQueries({ queryKey: ['user', 'preferences'] })
    },
    onError: (error: unknown) => {
      toast.error(formatInteractionError(error))
    },
  })

  const handleLike = () => {
    if (isLiked) return
    // 顯示原因選擇面板
    setSelectedAction('like')
    setShowReasonPanel(true)
    setSelectedReasons([])
    setComment('')
  }

  const handleDislike = () => {
    if (isDisliked) return
    // 顯示原因選擇面板
    setSelectedAction('dislike')
    setShowReasonPanel(true)
    setSelectedReasons([])
    setComment('')
  }

  const toggleReason = (reason: RatingReason) => {
    setSelectedReasons((prev) =>
      prev.includes(reason)
        ? prev.filter((r) => r !== reason)
        : [...prev, reason]
    )
  }

  const handleSubmitReason = () => {
    const payload: InteractionSubmitVars = {
      reasons: selectedReasons.length > 0 ? selectedReasons : undefined,
      comment: comment.trim() || undefined,
    }
    if (selectedAction === 'like') {
      likeMutation.mutate(payload)
    } else if (selectedAction === 'dislike') {
      dislikeMutation.mutate(payload)
    }
  }

  const handleCancelReason = () => {
    setShowReasonPanel(false)
    setSelectedAction(null)
    setSelectedReasons([])
    setComment('')
  }

  const reasons = selectedAction === 'like' ? positiveReasons : negativeReasons

  return (
    <div className="flex flex-wrap gap-2">
      {/* 原因選擇面板 */}
      {showReasonPanel && selectedAction && (
        <div className="w-full mb-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="mb-3">
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {selectedAction === 'like' ? t('interaction.selectLikeReasons') : t('interaction.selectDislikeReasons')}
            </h4>
            <div className="flex flex-wrap gap-2 mb-3">
              {reasons.map((reason) => (
                <button
                  key={reason}
                  onClick={() => toggleReason(reason)}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                    selectedReasons.includes(reason)
                      ? selectedAction === 'like'
                        ? 'bg-green-500 text-white'
                        : 'bg-red-500 text-white'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                  }`}
                >
                  {t(ratingReasonI18nKeys[reason])}
                </button>
              ))}
            </div>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder={t('interaction.additionalComments')}
              className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary resize-none"
              rows={2}
            />
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleSubmitReason}
              disabled={likeMutation.isPending || dislikeMutation.isPending}
              className={`px-4 py-2 text-sm font-medium text-white rounded-md transition-colors ${
                selectedAction === 'like'
                  ? 'bg-green-600 hover:bg-green-700'
                  : 'bg-red-600 hover:bg-red-700'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              {t('common.submit')}
            </button>
            <button
              onClick={handleCancelReason}
              disabled={likeMutation.isPending || dislikeMutation.isPending}
              className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {t('common.cancel')}
            </button>
          </div>
        </div>
      )}

      {/* 桌面版：水平排列 */}
      <div className="hidden lg:flex gap-2">
        <button
          onClick={handleLike}
          disabled={likeMutation.isPending || isLiked}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors touch-manipulation min-w-[44px] min-h-[44px] ${
            isLiked
              ? 'bg-green-100 text-green-700 border-2 border-green-500'
              : 'bg-green-50 hover:bg-green-100 text-green-700'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          <ThumbsUp className="w-5 h-5" />
          <span className="text-sm font-medium">{t('style.like')}</span>
        </button>

        <button
          onClick={handleDislike}
          disabled={dislikeMutation.isPending || isDisliked}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors touch-manipulation min-w-[44px] min-h-[44px] ${
            isDisliked
              ? 'bg-red-100 text-red-700 border-2 border-red-500'
              : 'bg-red-50 hover:bg-red-100 text-red-700'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          <ThumbsDown className="w-5 h-5" />
          <span className="text-sm font-medium">{t('style.dislike')}</span>
        </button>

        {onEdit && (
          <button
            onClick={onEdit}
            className="flex items-center gap-2 px-4 py-2 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg transition-colors touch-manipulation min-w-[44px] min-h-[44px]"
          >
            <Pencil className="w-5 h-5" />
            <span className="text-sm font-medium">{t('common.edit')}</span>
          </button>
        )}

        {onReplace && (
          <button
            onClick={onReplace}
            className="flex items-center gap-2 px-4 py-2 bg-purple-50 hover:bg-purple-100 text-purple-700 rounded-lg transition-colors touch-manipulation min-w-[44px] min-h-[44px]"
          >
            <ImageIcon className="w-5 h-5" />
            <span className="text-sm font-medium">{t('images.replacePhoto')}</span>
          </button>
        )}

        {onViewHistory && (
          <button
            onClick={onViewHistory}
            className="flex items-center gap-2 px-4 py-2 bg-gray-50 hover:bg-gray-100 text-gray-700 rounded-lg transition-colors touch-manipulation min-w-[44px] min-h-[44px]"
          >
            <History className="w-5 h-5" />
            <span className="text-sm font-medium">{t('common.history')}</span>
          </button>
        )}
      </div>

      {/* 手機版：固定底部欄 */}
      <div className="lg:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg z-50 safe-area-bottom">
        <div className="flex items-center justify-around px-4 py-3">
          <button
            onClick={handleLike}
            disabled={likeMutation.isPending || isLiked}
            className={`flex flex-col items-center gap-1 min-w-[60px] min-h-[60px] p-2 rounded-lg touch-manipulation ${
              isLiked ? 'bg-green-100' : 'active:bg-green-50'
            } disabled:opacity-50`}
          >
            <ThumbsUp className={`w-6 h-6 ${isLiked ? 'text-green-600' : 'text-green-600'}`} />
            <span className="text-xs text-gray-600 font-medium">{t('style.like')}</span>
          </button>

          <button
            onClick={handleDislike}
            disabled={dislikeMutation.isPending || isDisliked}
            className={`flex flex-col items-center gap-1 min-w-[60px] min-h-[60px] p-2 rounded-lg touch-manipulation ${
              isDisliked ? 'bg-red-100' : 'active:bg-red-50'
            } disabled:opacity-50`}
          >
            <ThumbsDown className={`w-6 h-6 ${isDisliked ? 'text-red-600' : 'text-red-600'}`} />
            <span className="text-xs text-gray-600 font-medium">{t('style.dislike')}</span>
          </button>

          {onEdit && (
            <button
              onClick={onEdit}
              className="flex flex-col items-center gap-1 min-w-[60px] min-h-[60px] p-2 rounded-lg active:bg-blue-50 touch-manipulation"
            >
              <Pencil className="w-6 h-6 text-blue-600" />
              <span className="text-xs text-gray-600 font-medium">{t('common.edit')}</span>
            </button>
          )}

          {onReplace && (
            <button
              onClick={onReplace}
              className="flex flex-col items-center gap-1 min-w-[60px] min-h-[60px] p-2 rounded-lg active:bg-purple-50 touch-manipulation"
            >
              <ImageIcon className="w-6 h-6 text-purple-600" />
              <span className="text-xs text-gray-600 font-medium">{t('images.photo')}</span>
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

