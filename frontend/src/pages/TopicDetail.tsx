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
import ContentGenerationPanel from '@/components/features/ContentGenerationPanel'
import type { GenerationSettings } from '@/components/features/ContentGenerationPanel'
import { usePageTitle } from '@/hooks/usePageTitle'
import { useAuthStore } from '@/stores/authStore'
import { useTranslation } from '@/i18n'

export default function TopicDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { t } = useTranslation()
  const { isAuthenticated } = useAuthStore()
  const [showEditor, setShowEditor] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [showImageSearch, setShowImageSearch] = useState(false)
  const [showLoginPrompt, setShowLoginPrompt] = useState(false)
  const [viewStartTime, setViewStartTime] = useState<number | null>(null)

  // 檢查是否需要登入才能執行操作
  const requireAuth = (action: () => void) => {
    if (!isAuthenticated) {
      setShowLoginPrompt(true)
      return
    }
    action()
  }

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
  usePageTitle(topic ? topic.title : t('nav.topics'))

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

  // 生成內容的 mutation（支援自訂設定）
  const generateContentMutation = useMutation({
    mutationFn: (settings?: GenerationSettings) => {
      console.log('🚀 開始生成內容，主題 ID:', id, '設定:', settings)
      return contentsAPI.generateContent(id!, {
        type: settings?.outputFormat || 'both',
        article_length: settings?.articleLength || 500,
        script_duration: settings?.scriptDuration || 30,
      })
    },
    onSuccess: (data) => {
      console.log('✅ 內容生成成功:', data)
      queryClient.invalidateQueries({ queryKey: ['content', id] })
      queryClient.invalidateQueries({ queryKey: ['topic', id] })
      showSuccess(t('common.success'))
    },
    onError: (error: any) => {
      console.error('❌ 生成內容失敗:', error)
      console.error('錯誤詳情:', {
        message: error?.message,
        status: error?.status,
        code: error?.code,
        details: error?.details,
      })
      
      // 根據錯誤類型顯示不同的錯誤訊息
      let errorMessage = t('error.generateFailed')
      
      if (error?.status === 400) {
        // 處理 API Key 未設定的錯誤
        const errorDetail = error?.details?.detail || error?.message || ''
        if (typeof errorDetail === 'string' && (errorDetail.includes('API Key') || errorDetail.includes('not configured') || errorDetail.includes('not set'))) {
          errorMessage = t('error.apiKeyNotSet')
        } else if (error?.details?.suggestion) {
          errorMessage = error?.message || error?.details?.detail || t('error.badRequest')
          if (typeof error?.details?.suggestion === 'string') {
            errorMessage = `${errorMessage}\n\n${error.details.suggestion}`
          }
        } else {
          errorMessage = error?.message || error?.details?.detail || t('error.badRequest')
        }
      } else if (error?.status === 404) {
        errorMessage = t('error.topicNotFound')
      } else if (error?.status === 500) {
        errorMessage = error?.message || t('error.serverError')
      } else if (error?.message) {
        errorMessage = error.message
      } else if (error?.details?.detail) {
        errorMessage = error.details.detail
      }
      
      showError(errorMessage)
    },
  })

  // 重新生成內容的 mutation（支援自訂設定）
  const regenerateContentMutation = useMutation({
    mutationFn: (settings?: GenerationSettings) => {
      console.log('🔄 開始重新生成內容，主題 ID:', id, '設定:', settings)
      return contentsAPI.regenerateContent(id!, {
        type: settings?.outputFormat || 'both',
        article_length: settings?.articleLength || 500,
        script_duration: settings?.scriptDuration || 30,
      })
    },
    onSuccess: (data) => {
      console.log('✅ 內容重新生成成功:', data)
      queryClient.invalidateQueries({ queryKey: ['content', id] })
      queryClient.invalidateQueries({ queryKey: ['topic', id] })
      showSuccess(t('common.success'))
    },
    onError: (error: any) => {
      console.error('❌ 重新生成內容失敗:', error)
      console.error('錯誤詳情:', {
        message: error?.message,
        status: error?.status,
        code: error?.code,
        details: error?.details,
      })
      
      // 根據錯誤類型顯示不同的錯誤訊息
      let errorMessage = t('error.regenerateFailed')
      
      if (error?.status === 400) {
        errorMessage = error?.message || error?.details?.detail || t('error.badRequest')
      } else if (error?.status === 404) {
        errorMessage = t('error.topicNotFound')
      } else if (error?.status === 500) {
        errorMessage = error?.message || t('error.serverError')
      } else if (error?.message) {
        errorMessage = error.message
      } else if (error?.details?.detail) {
        errorMessage = error.details.detail
      }
      
      showError(errorMessage)
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

  // 智能匹配照片的 mutation
  const matchPhotosMutation = useMutation({
    mutationFn: (minCount: number) => imagesAPI.matchPhotos(id!, minCount),
    onMutate: () => {
      showSuccess(t('common.loading'))
    },
    onSuccess: async (data) => {
      // 立即重新獲取圖片列表，確保UI更新
      await queryClient.refetchQueries({ queryKey: ['images', id] })
      queryClient.invalidateQueries({ queryKey: ['topic', id] })
      showSuccess(t('common.success'))
    },
    onError: (error: any) => {
      // 檢查是否為 404 錯誤（內容不存在）
      const status = error?.status || error?.response?.status
      if (status === 404) {
        showError(t('common.failed'))
      } else {
        const errorMessage = error?.response?.data?.detail || error?.message || t('common.failed')
        showError(errorMessage)
      }
      console.error('匹配照片失敗:', error)
    },
  })

  // 刪除主題
  const deleteMutation = useMutation({
    mutationFn: () => topicsAPI.deleteTopic(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['topics'] })
      showSuccess(t('common.success'))
      navigate('/topics')
    },
    onError: (error) => {
      showError(t('common.failed'))
      console.error('Failed to delete topic:', error)
    },
  })

  // 確認主題
  const confirmMutation = useMutation({
    mutationFn: () => topicsAPI.updateTopicStatus(id!, 'confirmed'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['topic', id] })
      queryClient.invalidateQueries({ queryKey: ['topics'] })
      showSuccess(t('common.success'))
    },
    onError: (error) => {
      showError(t('common.failed'))
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
          <p className="text-gray-500 dark:text-gray-400 mb-4">{t('topics.notFound')}</p>
          <p className="text-sm text-gray-400 dark:text-gray-500 mb-4">{t('topics.topicId')}: {id}</p>
          {topicError && (
            <p className="text-sm text-red-500 dark:text-red-400">
              {t('common.error')}: {String(topicError)}
            </p>
          )}
          <button
            onClick={() => navigate('/topics')}
            data-testid="btn-topic-detail-back"
            className="mt-4 px-4 py-2 text-sm font-medium text-white bg-primary rounded-md hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary min-h-[44px]"
          >
            {t('common.back')}
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="p-4 sm:p-6 min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* 標題和操作按鈕 */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white break-words flex-1">{topic.title}</h1>
        <div className="flex flex-wrap gap-2 w-full sm:w-auto">
          <button
            onClick={() => requireAuth(() => setShowEditor(true))}
            data-testid="btn-topic-detail-edit"
            className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary min-h-[44px]"
          >
            {t('common.edit')}
          </button>
          {topic.status !== 'confirmed' && (
            <button
              onClick={() => requireAuth(() => confirmMutation.mutate())}
              disabled={confirmMutation.isPending}
              data-testid="btn-topic-detail-confirm"
              className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed min-h-[44px]"
            >
              {confirmMutation.isPending ? t('common.loading') : t('common.confirm')}
            </button>
          )}
          <button
            onClick={() => requireAuth(() => setShowDeleteConfirm(true))}
            data-testid="btn-topic-detail-delete"
            className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 min-h-[44px]"
          >
            {t('common.delete')}
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
              {t('common.confirmDelete')}
            </h3>
            <p className="text-gray-600 mb-6">
              {t('topics.deleteConfirmMessage')}
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
              >
                {t('common.cancel')}
              </button>
              <button
                onClick={() => {
                  deleteMutation.mutate()
                  setShowDeleteConfirm(false)
                }}
                disabled={deleteMutation.isPending}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {deleteMutation.isPending ? t('common.loading') : t('common.confirmDelete')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 登入提示模態框 */}
      {showLoginPrompt && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg p-6 max-w-md w-full mx-4">
            <div className="text-center">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-primary/10 mb-4">
                <svg className="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {t('auth.loginRequired')}
              </h3>
              <p className="text-gray-600 mb-6">
                {t('auth.loginRequiredMessage')}
              </p>
              <div className="flex gap-3 justify-center">
                <button
                  onClick={() => setShowLoginPrompt(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
                >
                  {t('common.cancel')}
                </button>
                <button
                  onClick={() => navigate('/login')}
                  className="px-4 py-2 text-sm font-medium text-white bg-primary rounded-md hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
                >
                  {t('auth.login.title')}
                </button>
                <button
                  onClick={() => navigate('/register')}
                  className="px-4 py-2 text-sm font-medium text-primary bg-primary/10 rounded-md hover:bg-primary/20 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
                >
                  {t('auth.register.title')}
                </button>
              </div>
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
             <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 sm:gap-6">
               {/* 左欄：圖片區塊 */}
               <div className="lg:col-span-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 sm:p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-semibold text-gray-700 dark:text-gray-200">
                {t('images.title')}（{images.length} {t('common.count')}）
              </h3>
              <button
                onClick={() => requireAuth(() => setShowImageSearch(true))}
                data-testid="btn-topic-detail-add-image"
                className="px-3 py-2 text-sm font-medium text-primary bg-primary/10 rounded-md hover:bg-primary/20 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary min-h-[44px]"
              >
                {t('images.upload')}
              </button>
            </div>
            {imagesLoading ? (
              <LoadingSpinner size="sm" text={t('images.loading')} />
            ) : imagesError ? (
              <ErrorDisplay error={imagesError} />
            ) : images.length === 0 ? (
              <div className="space-y-3">
                <EmptyState
                  message={t('images.noImages')}
                  size="sm"
                />
                <div className="flex gap-2">
                  <button
                    onClick={() => requireAuth(() => matchPhotosMutation.mutate(8))}
                    disabled={matchPhotosMutation.isPending || !content || !content?.article}
                    data-testid="btn-topic-detail-match-photos"
                    className="flex-1 px-3 py-2 text-sm font-medium text-white bg-primary rounded-md hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed min-h-[44px]"
                    title={!content || !content?.article ? t('images.generateContentFirst') : t('images.matchPhotosTitle')}
                  >
                    {matchPhotosMutation.isPending ? t('common.matching') : t('images.smartMatchPhotos')}
                  </button>
                  <button
                    onClick={() => requireAuth(() => setShowImageSearch(true))}
                    data-testid="btn-topic-detail-search-images"
                    className="flex-1 px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 min-h-[44px]"
                  >
                    {t('images.search')}
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
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 sm:p-6 space-y-6">
            {contentLoading ? (
              <LoadingSpinner size="sm" text={t('common.loadingContent')} />
            ) : contentError && (contentError as any)?.status !== 404 ? (
              <ErrorDisplay error={contentError} />
            ) : content ? (
              <>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="font-semibold text-gray-700 dark:text-gray-200">{t('content.title')}</h3>
                </div>

                {/* 重新生成面板 */}
                <ContentGenerationPanel
                  onGenerate={(settings) => requireAuth(() => regenerateContentMutation.mutate(settings))}
                  isGenerating={regenerateContentMutation.isPending}
                  hasExistingContent={true}
                />
                <div>
                  <h3 className="font-semibold text-gray-700 dark:text-gray-200 mb-2">{t('content.article')}</h3>
                  <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 max-h-96 overflow-y-auto">
                    <p className="text-gray-700 dark:text-gray-300 whitespace-pre-line text-sm leading-relaxed">
                      {content.article || t('common.noContent')}
                    </p>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                    {t('content.wordCount')}: {content.wordCount} {t('common.words')}
                  </p>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-700 dark:text-gray-200 mb-2">{t('content.script')}</h3>
                  <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 max-h-64 overflow-y-auto">
                    <p className="text-gray-700 dark:text-gray-300 whitespace-pre-line text-sm leading-relaxed">
                      {content.script || t('common.noContent')}
                    </p>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                    {t('content.duration')}: {t('common.about')} {content.estimatedDuration} {t('common.seconds')}
                  </p>
                </div>
              </>
            ) : (
              <div className="space-y-4">
                <EmptyState message={t('common.noContent')} size="sm" />
                {/* 內容生成設定面板 */}
                <ContentGenerationPanel
                  onGenerate={(settings) => requireAuth(() => generateContentMutation.mutate(settings))}
                  isGenerating={generateContentMutation.isPending}
                  hasExistingContent={false}
                />
              </div>
            )}
          </div>
        </div>

        {/* 右欄：資訊區塊 */}
        <div className="col-span-12 lg:col-span-3">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 sm:p-6 space-y-4">
            {/* 互動按鈕 */}
            <div>
              <h3 className="font-semibold text-gray-700 dark:text-gray-200 mb-3">{t('common.interaction')}</h3>
              <InteractionButtons
                topicId={id!}
                articleId={content?.id}
                scriptId={content?.id}
                onEdit={() => setShowEditor(true)}
                onReplace={() => setShowImageSearch(true)}
              />
            </div>

            <div>
              <h3 className="font-semibold text-gray-700 dark:text-gray-200 mb-2">{t('topics.category')}</h3>
              <span className="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm">
                {topic.category}
              </span>
            </div>
            <div>
              <h3 className="font-semibold text-gray-700 dark:text-gray-200 mb-2">{t('topics.status')}</h3>
              <span className="px-3 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300 rounded-full text-sm">
                {topic.status}
              </span>
            </div>
            <div>
              <h3 className="font-semibold text-gray-700 dark:text-gray-200 mb-2">{t('topics.source')}</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">{topic.source}</p>
            </div>
            <div>
              <h3 className="font-semibold text-gray-700 dark:text-gray-200 mb-2">{t('topics.generatedAt')}</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {new Date(topic.generatedAt).toLocaleString()}
              </p>
            </div>
            {/* 語言資訊區塊 */}
            {(topic.displayLanguage || topic.originalTitle) && (
              <div>
                <h3 className="font-semibold text-gray-700 dark:text-gray-200 mb-2">{t('topics.languageInfo')}</h3>
                <div className="space-y-2 text-sm">
                  {topic.displayLanguage && (
                    <div className="flex items-center gap-2">
                      <span className="text-gray-500 dark:text-gray-400">{t('topics.displayLanguage')}:</span>
                      <span className="px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded text-xs font-medium">
                        {t(`language.${topic.displayLanguage}`)}
                      </span>
                    </div>
                  )}
                  {topic.originalTitle && topic.originalTitle !== topic.title && (
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">{t('topics.originalTitle')}:</span>
                      <p className="text-gray-600 dark:text-gray-300 mt-1 text-xs italic break-words">
                        {topic.originalTitle}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}
            {content && (
              <div>
                <h3 className="font-semibold text-gray-700 dark:text-gray-200 mb-2">{t('content.model')}</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">{content.modelUsed}</p>
              </div>
            )}
            <div>
              <h3 className="font-semibold text-gray-700 dark:text-gray-200 mb-2">{t('common.statistics')}</h3>
              <div className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
                <p>{t('images.count')}: {topic.imageCount} {t('common.count')}</p>
                <p>{t('content.wordCount')}: {topic.wordCount} {t('common.words')}</p>
                {content && <p>{t('content.estimatedDuration')}: {content.estimatedDuration} {t('common.seconds')}</p>}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

