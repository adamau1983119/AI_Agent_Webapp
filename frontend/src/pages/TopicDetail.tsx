import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { topicsAPI, contentsAPI, imagesAPI, interactionsAPI } from '@/api/client'
import { showSuccess, showError } from '@/utils/toast'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import ErrorDisplay from '@/components/ui/ErrorDisplay'
import EmptyState from '@/components/ui/EmptyState'
import TopicEditor from '@/components/features/TopicEditor'
import ImageGallery from '@/components/features/ImageGallery'
import ImageSearch from '@/components/features/ImageSearch'
import InteractionButtons from '@/components/features/InteractionButtons'
import { usePageTitle } from '@/hooks/usePageTitle'

export default function TopicDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [showEditor, setShowEditor] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [showImageSearch, setShowImageSearch] = useState(false)
  const [viewStartTime, setViewStartTime] = useState<number | null>(null)

  const {
    data: topic,
    isLoading: topicLoading,
    error: topicError,
    refetch: refetchTopic,
  } = useQuery({
    queryKey: ['topic', id],
    queryFn: () => topicsAPI.getTopic(id!),
    enabled: !!id,
  })

  // 設定頁面標題
  usePageTitle(topic ? `${topic.title} - AI代理Web應用程式` : '主題詳情 - AI代理Web應用程式')

  const {
    data: content,
    isLoading: contentLoading,
    error: contentError,
  } = useQuery({
    queryKey: ['content', id],
    queryFn: () => contentsAPI.getContent(id!),
    enabled: !!id,
    retry: false, // 404 不重試
  })

  // 記錄瀏覽時間
  useEffect(() => {
    if (topic) {
      setViewStartTime(Date.now())
      
      return () => {
        // 組件卸載時記錄瀏覽時間
        if (viewStartTime) {
          const duration = Math.floor((Date.now() - viewStartTime) / 1000)
          if (duration > 5) {
            // 只記錄超過 5 秒的瀏覽
            interactionsAPI.createInteraction({
              user_id: 'user_default',
              topic_id: id!,
              article_id: content?.id,
              action: 'view',
              duration,
            }).catch(console.error)
          }
        }
      }
    }
  }, [topic, content, id, viewStartTime])

  // 生成內容的 mutation
  const generateContentMutation = useMutation({
    mutationFn: () => contentsAPI.generateContent(id!, {
      type: 'both',
      article_length: 500,
      script_duration: 30,
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['content', id] })
      showSuccess('內容生成成功')
    },
    onError: (error: any) => {
      showError(error?.message || '生成內容失敗')
    },
  })

  // 重新生成內容的 mutation
  const regenerateContentMutation = useMutation({
    mutationFn: () => contentsAPI.regenerateContent(id!, {
      type: 'both',
      article_length: 500,
      script_duration: 30,
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['content', id] })
      showSuccess('內容重新生成成功')
    },
    onError: (error: any) => {
      showError(error?.message || '重新生成內容失敗')
    },
  })

  const {
    data: images = [],
    isLoading: imagesLoading,
    error: imagesError,
  } = useQuery({
    queryKey: ['images', id],
    queryFn: () => imagesAPI.getImages(id!),
    enabled: !!id,
  })

  // 刪除主題
  const deleteMutation = useMutation({
    mutationFn: () => topicsAPI.deleteTopic(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['topics'] })
      showSuccess('主題已成功刪除')
      navigate('/topics')
    },
    onError: (error) => {
      showError('刪除主題失敗，請稍後再試')
      console.error('Failed to delete topic:', error)
    },
  })

  // 確認主題
  const confirmMutation = useMutation({
    mutationFn: () => topicsAPI.updateTopicStatus(id!, 'confirmed'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['topic', id] })
      queryClient.invalidateQueries({ queryKey: ['topics'] })
      showSuccess('主題已確認')
    },
    onError: (error) => {
      showError('確認主題失敗，請稍後再試')
      console.error('Failed to confirm topic:', error)
    },
  })

  if (topicLoading) {
    return (
      <div className="p-6">
        <LoadingSpinner />
      </div>
    )
  }

  if (topicError) {
    return (
      <div className="p-6">
        <ErrorDisplay error={topicError} onRetry={() => refetchTopic()} />
      </div>
    )
  }

  if (!topic) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <p className="text-gray-500 mb-4">找不到主題</p>
          <p className="text-sm text-gray-400 mb-4">主題 ID: {id}</p>
          {topicError && (
            <p className="text-sm text-red-500">
              錯誤: {String(topicError)}
            </p>
          )}
          <button
            onClick={() => navigate('/topics')}
            className="mt-4 px-4 py-2 text-sm font-medium text-white bg-primary rounded-md hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
          >
            返回主題列表
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6">
      {/* 標題和操作按鈕 */}
      <div className="flex justify-between items-start mb-6">
        <h1 className="text-2xl font-bold text-gray-800">{topic.title}</h1>
        <div className="flex gap-2">
          <button
            onClick={() => setShowEditor(true)}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
          >
            編輯
          </button>
          {topic.status !== 'confirmed' && (
            <button
              onClick={() => confirmMutation.mutate()}
              disabled={confirmMutation.isPending}
              className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {confirmMutation.isPending ? '確認中...' : '確認'}
            </button>
          )}
          <button
            onClick={() => setShowDeleteConfirm(true)}
            className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            刪除
          </button>
        </div>
      </div>

      {/* 編輯模態框 */}
      {showEditor && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <TopicEditor
              topic={topic}
              onClose={() => setShowEditor(false)}
              onSuccess={() => {
                // 編輯成功後的處理
              }}
            />
          </div>
        </div>
      )}

      {/* 刪除確認模態框 */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              確認刪除
            </h3>
            <p className="text-gray-600 mb-6">
              您確定要刪除主題「{topic.title}」嗎？此操作無法復原。
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
              >
                取消
              </button>
              <button
                onClick={() => {
                  deleteMutation.mutate()
                  setShowDeleteConfirm(false)
                }}
                disabled={deleteMutation.isPending}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {deleteMutation.isPending ? '刪除中...' : '確認刪除'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 圖片搜尋模態框 */}
      {showImageSearch && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <ImageSearch
            topicId={id!}
            topic={topic || null}
            content={content || null}
            onImageSelect={() => {
              setShowImageSearch(false)
            }}
            onClose={() => setShowImageSearch(false)}
          />
        </div>
      )}

             {/* 三欄式佈局 */}
             <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
               {/* 左欄：圖片區塊 */}
               <div className="lg:col-span-4">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-semibold text-gray-700">
                圖片（{images.length} 張）
              </h3>
              <button
                onClick={() => setShowImageSearch(true)}
                className="px-3 py-1 text-sm font-medium text-primary bg-primary/10 rounded-md hover:bg-primary/20 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
              >
                + 新增圖片
              </button>
            </div>
            {imagesLoading ? (
              <LoadingSpinner size="sm" text="載入圖片中..." />
            ) : imagesError ? (
              <ErrorDisplay error={imagesError} />
            ) : images.length === 0 ? (
              <div className="space-y-3">
                <EmptyState
                  message="沒有圖片"
                  size="sm"
                />
                <div className="flex gap-2">
                  <button
                    onClick={() => imagesAPI.matchPhotos(id!, 8).then(() => {
                      queryClient.invalidateQueries({ queryKey: ['images', id] })
                      showSuccess('正在智能匹配照片...')
                    }).catch((err) => {
                      showError(err?.message || '匹配照片失敗')
                    })}
                    className="flex-1 px-3 py-2 text-sm font-medium text-white bg-primary rounded-md hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
                  >
                    智能匹配照片（8張）
                  </button>
                  <button
                    onClick={() => setShowImageSearch(true)}
                    className="flex-1 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
                  >
                    手動搜尋
                  </button>
                </div>
              </div>
            ) : (
              <ImageGallery
                images={images}
                topicId={id!}
                onImageUpdate={() => {
                  queryClient.invalidateQueries({ queryKey: ['images', id] })
                }}
              />
            )}
          </div>
        </div>

        {/* 中欄：內容區塊 */}
        <div className="col-span-12 lg:col-span-5">
          <div className="bg-white rounded-lg shadow p-6 space-y-6">
            {contentLoading ? (
              <LoadingSpinner size="sm" text="載入內容中..." />
            ) : contentError && (contentError as any)?.status !== 404 ? (
              <ErrorDisplay error={contentError} />
            ) : content ? (
              <>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="font-semibold text-gray-700">內容</h3>
                  <button
                    onClick={() => regenerateContentMutation.mutate()}
                    disabled={regenerateContentMutation.isPending}
                    className="px-3 py-1 text-xs font-medium text-primary bg-primary/10 rounded-md hover:bg-primary/20 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {regenerateContentMutation.isPending ? '重新生成中...' : '🔄 重新生成'}
                  </button>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-700 mb-2">短文</h3>
                  <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                    <p className="text-gray-700 whitespace-pre-line text-sm leading-relaxed">
                      {content.article || '尚未生成內容'}
                    </p>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    字數：{content.wordCount} 字
                  </p>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-700 mb-2">腳本</h3>
                  <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
                    <p className="text-gray-700 whitespace-pre-line text-sm leading-relaxed">
                      {content.script || '尚未生成內容'}
                    </p>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    時長：約 {content.estimatedDuration} 秒
                  </p>
                </div>
              </>
            ) : (
              <div className="space-y-3">
                <EmptyState message="尚未生成內容" size="sm" />
                <button
                  onClick={() => generateContentMutation.mutate()}
                  disabled={generateContentMutation.isPending}
                  className="w-full px-4 py-2 text-sm font-medium text-white bg-primary rounded-md hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {generateContentMutation.isPending ? '生成中...' : '生成內容（500字文章 + 30秒腳本）'}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* 右欄：資訊區塊 */}
        <div className="col-span-12 lg:col-span-3">
          <div className="bg-white rounded-lg shadow p-6 space-y-4">
            {/* 互動按鈕 */}
            <div>
              <h3 className="font-semibold text-gray-700 mb-3">互動</h3>
              <InteractionButtons
                topicId={id!}
                articleId={content?.id}
                scriptId={content?.id}
                onEdit={() => setShowEditor(true)}
                onReplace={() => setShowImageSearch(true)}
              />
            </div>

            <div>
              <h3 className="font-semibold text-gray-700 mb-2">分類</h3>
              <span className="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm">
                {topic.category}
              </span>
            </div>
            <div>
              <h3 className="font-semibold text-gray-700 mb-2">狀態</h3>
              <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm">
                {topic.status}
              </span>
            </div>
            <div>
              <h3 className="font-semibold text-gray-700 mb-2">來源</h3>
              <p className="text-sm text-gray-600">{topic.source}</p>
            </div>
            <div>
              <h3 className="font-semibold text-gray-700 mb-2">生成時間</h3>
              <p className="text-sm text-gray-600">
                {new Date(topic.generatedAt).toLocaleString('zh-TW')}
              </p>
            </div>
            {content && (
              <div>
                <h3 className="font-semibold text-gray-700 mb-2">AI 模型</h3>
                <p className="text-sm text-gray-600">{content.modelUsed}</p>
              </div>
            )}
            <div>
              <h3 className="font-semibold text-gray-700 mb-2">統計</h3>
              <div className="space-y-1 text-sm text-gray-600">
                <p>圖片數量：{topic.imageCount} 張</p>
                <p>字數：{topic.wordCount} 字</p>
                {content && <p>預計時長：{content.estimatedDuration} 秒</p>}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

