/**
 * 互動按鈕組件
 * 提供 Like/Dislike/Edit/Replace 功能
 */
import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { interactionsAPI } from '@/api/client'
import { ThumbsUp, ThumbsDown, Pencil, Image as ImageIcon, History } from 'lucide-react'
import toast from 'react-hot-toast'

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
  userId = 'user_default',
}: InteractionButtonsProps) {
  const queryClient = useQueryClient()
  const [isLiked, setIsLiked] = useState(false)
  const [isDisliked, setIsDisliked] = useState(false)

  // Like mutation
  const likeMutation = useMutation({
    mutationFn: () =>
      interactionsAPI.createInteraction({
        user_id: userId,
        topic_id: topicId,
        article_id: articleId,
        script_id: scriptId,
        action: 'like',
      }),
    onSuccess: () => {
      setIsLiked(true)
      setIsDisliked(false)
      toast.success('已記錄您的喜好')
      // 更新偏好模型
      queryClient.invalidateQueries({ queryKey: ['user', 'preferences'] })
    },
    onError: (error: any) => {
      toast.error(error?.message || '記錄互動失敗')
    },
  })

  // Dislike mutation
  const dislikeMutation = useMutation({
    mutationFn: () =>
      interactionsAPI.createInteraction({
        user_id: userId,
        topic_id: topicId,
        article_id: articleId,
        script_id: scriptId,
        action: 'dislike',
      }),
    onSuccess: () => {
      setIsDisliked(true)
      setIsLiked(false)
      toast.success('已記錄您的反饋')
      // 更新偏好模型
      queryClient.invalidateQueries({ queryKey: ['user', 'preferences'] })
    },
    onError: (error: any) => {
      toast.error(error?.message || '記錄互動失敗')
    },
  })

  const handleLike = () => {
    if (isLiked) return
    likeMutation.mutate()
  }

  const handleDislike = () => {
    if (isDisliked) return
    dislikeMutation.mutate()
  }

  return (
    <div className="flex flex-wrap gap-2">
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
          <span className="text-sm font-medium">喜歡</span>
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
          <span className="text-sm font-medium">不喜歡</span>
        </button>

        {onEdit && (
          <button
            onClick={onEdit}
            className="flex items-center gap-2 px-4 py-2 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg transition-colors touch-manipulation min-w-[44px] min-h-[44px]"
          >
            <Pencil className="w-5 h-5" />
            <span className="text-sm font-medium">編輯</span>
          </button>
        )}

        {onReplace && (
          <button
            onClick={onReplace}
            className="flex items-center gap-2 px-4 py-2 bg-purple-50 hover:bg-purple-100 text-purple-700 rounded-lg transition-colors touch-manipulation min-w-[44px] min-h-[44px]"
          >
            <ImageIcon className="w-5 h-5" />
            <span className="text-sm font-medium">替換照片</span>
          </button>
        )}

        {onViewHistory && (
          <button
            onClick={onViewHistory}
            className="flex items-center gap-2 px-4 py-2 bg-gray-50 hover:bg-gray-100 text-gray-700 rounded-lg transition-colors touch-manipulation min-w-[44px] min-h-[44px]"
          >
            <History className="w-5 h-5" />
            <span className="text-sm font-medium">版本歷史</span>
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
            <span className="text-xs text-gray-600 font-medium">喜歡</span>
          </button>

          <button
            onClick={handleDislike}
            disabled={dislikeMutation.isPending || isDisliked}
            className={`flex flex-col items-center gap-1 min-w-[60px] min-h-[60px] p-2 rounded-lg touch-manipulation ${
              isDisliked ? 'bg-red-100' : 'active:bg-red-50'
            } disabled:opacity-50`}
          >
            <ThumbsDown className={`w-6 h-6 ${isDisliked ? 'text-red-600' : 'text-red-600'}`} />
            <span className="text-xs text-gray-600 font-medium">不喜歡</span>
          </button>

          {onEdit && (
            <button
              onClick={onEdit}
              className="flex flex-col items-center gap-1 min-w-[60px] min-h-[60px] p-2 rounded-lg active:bg-blue-50 touch-manipulation"
            >
              <Pencil className="w-6 h-6 text-blue-600" />
              <span className="text-xs text-gray-600 font-medium">編輯</span>
            </button>
          )}

          {onReplace && (
            <button
              onClick={onReplace}
              className="flex flex-col items-center gap-1 min-w-[60px] min-h-[60px] p-2 rounded-lg active:bg-purple-50 touch-manipulation"
            >
              <ImageIcon className="w-6 h-6 text-purple-600" />
              <span className="text-xs text-gray-600 font-medium">照片</span>
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

