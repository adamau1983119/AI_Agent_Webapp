import { useState, useEffect, useMemo, useRef } from 'react'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { topicsAPI, contentsAPI, imagesAPI, interactionsAPI, API_BASE_URL } from '@/api/client'
import { showSuccess, showError } from '@/utils/toast'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import ErrorDisplay from '@/components/ui/ErrorDisplay'
import EmptyState from '@/components/ui/EmptyState'
import ImageGallery from '@/components/features/ImageGallery'
import ImageSearch from '@/components/features/ImageSearch'
import InteractionButtons from '@/components/features/InteractionButtons'
import ContentGenerationPanel from '@/components/features/ContentGenerationPanel'
import PostKitPanel from '@/components/features/PostKitPanel'
import PostComposerPanel from '@/components/features/PostComposerPanel'
import type { GenerationSettings } from '@/components/features/ContentGenerationPanel'
import { usePageTitle } from '@/hooks/usePageTitle'
import { useAuthStore } from '@/stores/authStore'
import { useTranslation } from '@/i18n'
import TopicTranslateDisplayButton, {
  type TopicDisplayOverride,
} from '@/components/ui/TopicTranslateDisplayButton'
import {
  getCollectionLanguage,
  getOriginalTitleLine,
  needsTranslateToCurrentLanguage,
  normalizeUiLanguage,
  resolveTopicDisplayCopy,
} from '@/lib/topicDisplay'
import { titleScriptMismatch } from '@/lib/topicLanguages'
import { copyToClipboard } from '@/utils/copyToClipboard'
import { Copy, Sparkles, Image as ImageIcon, Search, ExternalLink, ArrowDownCircle, ArrowLeft } from 'lucide-react'
import { markTopicRead } from '@/lib/topicReadState'

function getProxyImageUrl(imageUrl: string): string {
  if (!imageUrl) return ''
  if (imageUrl.includes('/images/proxy') || imageUrl.startsWith('/')) return imageUrl
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
    return `${API_BASE_URL}/images/proxy?url=${encodeURIComponent(imageUrl)}`
  }
  return imageUrl
}

export default function TopicDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const location = useLocation()
  const queryClient = useQueryClient()
  const { t, language } = useTranslation()
  const { isAuthenticated, user } = useAuthStore()
  const [showImageSearch, setShowImageSearch] = useState(false)
  const [showLoginPrompt, setShowLoginPrompt] = useState(false)
  const [viewStartTime, setViewStartTime] = useState<number | null>(null)
  const [displayOverride, setDisplayOverride] = useState<TopicDisplayOverride | null>(null)
  const [showCollectionTitle, setShowCollectionTitle] = useState(false)
  const [sourceViewMode, setSourceViewMode] = useState<'translated' | 'original'>('translated')
  const postKitRef = useRef<HTMLDivElement>(null)

  const requireAuth = (action: () => void) => {
    if (!isAuthenticated) {
      setShowLoginPrompt(true)
      return
    }
    action()
  }

  const goBackToHeadlines = () => {
    if (location.key !== 'default') {
      navigate(-1)
      return
    }
    navigate('/dashboard')
  }

  const {
    data: topic,
    isLoading: topicLoading,
    error: topicError,
  } = useQuery({
    queryKey: ['topic', id, language],
    queryFn: () => topicsAPI.getTopic(id!, language),
    enabled: !!id,
  })

  const {
    data: content,
    isLoading: contentLoading,
  } = useQuery({
    queryKey: ['content', id, language],
    queryFn: () => contentsAPI.getContent(id!, language),
    enabled: !!id,
    retry: false,
    refetchInterval: (query) => {
      if ((query.state.dataUpdateCount ?? 0) >= 10) return false
      const data = query.state.data
      if (!data) return false
      if (data.translationPending) return 2500
      const ui = normalizeUiLanguage(language)
      if (
        data.contentLanguage &&
        normalizeUiLanguage(data.contentLanguage) !== ui
      ) {
        return 2500
      }
      if (
        (data.script && titleScriptMismatch(data.script.slice(0, 800), language)) ||
        (data.article && titleScriptMismatch(data.article.slice(0, 800), language))
      ) {
        return 2500
      }
      return false
    },
  })

  const contentBodyMismatch = Boolean(
    content &&
      topic &&
      normalizeUiLanguage(language) !== getCollectionLanguage(topic) &&
      ((content.script &&
        titleScriptMismatch(content.script.slice(0, 800), language)) ||
        (content.article &&
          titleScriptMismatch(content.article.slice(0, 800), language)))
  )

  const contentTranslating = Boolean(
    content &&
      (content.translationPending ||
        contentBodyMismatch ||
        (content.contentLanguage &&
          normalizeUiLanguage(content.contentLanguage) !== normalizeUiLanguage(language)))
  )

  const displayCopy = useMemo(() => {
    if (!topic) return null
    if (showCollectionTitle) {
      return {
        title: topic.title,
        description: topic.description,
        usingTranslation: false,
        fromCache: false,
        localePending: false,
      }
    }
    return resolveTopicDisplayCopy(topic, language, displayOverride)
  }, [topic, language, displayOverride, showCollectionTitle])

  const originalContentText = useMemo(() => {
    if (!topic) return ''
    const raw = topic.sources?.[0]?.original_content || topic.sources?.[0]?.originalContent || ''
    return raw.trim()
  }, [topic])

  const translatedContentText = useMemo(() => {
    if (!topic) return ''
    const translated =
      topic.translatedSourceContent ||
      topic.translated_source_content ||
      topic.sourceContentI18n?.[language] ||
      topic.source_content_i18n?.[language] ||
      displayCopy?.description ||
      topic.summaryFlash ||
      topic.summary_flash ||
      topic.description ||
      ''
    return translated.trim()
  }, [topic, language, displayCopy])

  const hasOriginalContent = Boolean(
    originalContentText &&
      translatedContentText &&
      originalContentText !== translatedContentText
  )

  const sourceDisplayContent =
    sourceViewMode === 'original' && hasOriginalContent
      ? originalContentText
      : (translatedContentText || originalContentText)

  useEffect(() => {
    setDisplayOverride(null)
    setShowCollectionTitle(false)
  }, [id, language])

  usePageTitle(
    displayCopy?.localePending
      ? t('topics.translating')
      : displayCopy?.title || (topic ? topic.title : t('nav.topics'))
  )

  useEffect(() => {
    if (id) markTopicRead(id)
  }, [id])

  useEffect(() => {
    if (topic) {
      setViewStartTime(Date.now())
      
      return () => {
        if (viewStartTime) {
          const duration = Math.floor((Date.now() - viewStartTime) / 1000)
          if (duration > 5) {
            interactionsAPI.createInteraction({
              user_id: user?.id ?? 'user_default',
              topic_id: id!,
              article_id: content?.id,
              action: 'view',
              duration,
            }).catch(console.error)
          }
        }
      }
    }
  }, [topic, content, id, viewStartTime, user?.id])

  const generateContentMutation = useMutation({
    mutationFn: (settings?: GenerationSettings) => {
      const userLanguage = language || 'zh-TW'
      return contentsAPI.generateContent(id!, {
        type: 'article',
        article_length: settings?.articleLength || 300,
        script_duration: 30,
        language: userLanguage,
      })
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['content', id] })
      queryClient.invalidateQueries({ queryKey: ['topic', id] })
      showSuccess(t('common.success'))
    },
    onError: (error: any) => {
      let errorMessage = t('error.generateFailed')
      if (error?.status === 400) {
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

  const regenerateContentMutation = useMutation({
    mutationFn: (settings?: GenerationSettings) => {
      const userLanguage = language || 'zh-TW'
      return contentsAPI.regenerateContent(id!, {
        type: 'article',
        article_length: settings?.articleLength || 300,
        script_duration: 30,
        language: userLanguage,
      })
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['content', id] })
      queryClient.invalidateQueries({ queryKey: ['topic', id] })
      showSuccess(t('common.success'))
    },
    onError: (error: any) => {
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

  const matchPhotosMutation = useMutation({
    mutationFn: (minCount: number) => imagesAPI.matchPhotos(id!, minCount),
    onMutate: () => {
      showSuccess(t('common.loading'))
    },
    onSuccess: async () => {
      await queryClient.refetchQueries({ queryKey: ['images', id] })
      queryClient.invalidateQueries({ queryKey: ['topic', id] })
      showSuccess(t('common.success'))
    },
    onError: (error: any) => {
      const status = error?.status || error?.response?.status
      if (status === 404) {
        showError(t('common.failed'))
      } else {
        const errorMessage = error?.response?.data?.detail || error?.message || t('common.failed')
        showError(errorMessage)
      }
    },
  })

  const handleCopyArticle = async (text: string) => {
    if (!text) return
    const ok = await copyToClipboard(text)
    if (ok) {
      showSuccess(t('content.copied'))
    } else {
      showError(t('common.failed'))
    }
  }

  const handleJumpToPostKit = () => {
    if (postKitRef.current) {
      postKitRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }

  const heroImageUrl = useMemo(() => {
    if (images && images.length > 0 && images[0]?.url) {
      return getProxyImageUrl(images[0].url)
    }
    if (topic?.previewImages && topic.previewImages.length > 0 && topic.previewImages[0]) {
      return getProxyImageUrl(topic.previewImages[0])
    }
    return ''
  }, [images, topic])

  if (topicLoading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <LoadingSpinner size="lg" text={t('common.loading')} />
      </div>
    )
  }

  if (topicError || !topic) {
    return (
      <div className="p-6">
        <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow">
          <p className="text-gray-500 dark:text-gray-400 mb-4">{t('topics.notFound')}</p>
          <p className="text-sm text-gray-400 dark:text-gray-500 mb-4">{t('topics.topicId')}: {id}</p>
          {topicError && (
            <p className="text-sm text-red-500 dark:text-red-400">
              {t('common.error')}: {String(topicError)}
            </p>
          )}
          <button
            type="button"
            onClick={goBackToHeadlines}
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
    <div className="p-4 sm:p-6 lg:p-8 min-h-screen bg-[#FAF9F7] dark:bg-gray-900 max-w-7xl mx-auto space-y-6">
      {/* 1. 頂部區域：標題、多語切換、轉貼文章快捷鍵、喜歡/不喜歡 */}
      <header className="flex flex-col gap-4 pb-4 border-b border-gray-200 dark:border-gray-800">
        <button
          type="button"
          onClick={goBackToHeadlines}
          data-testid="btn-topic-detail-back"
          className="inline-flex items-center gap-1.5 self-start text-sm text-gray-600 dark:text-gray-300 hover:text-black dark:hover:text-white min-h-[44px]"
        >
          <ArrowLeft className="w-4 h-4" />
          {t('common.back')}
        </button>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              <span className="px-3 py-1 bg-primary/10 text-primary rounded-full text-xs font-medium font-sans uppercase tracking-wider">
                {topic.category}
              </span>
              <span className="px-2.5 py-0.5 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300 rounded-full text-xs font-sans">
                {topic.status}
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold font-display text-gray-900 dark:text-white break-words tracking-tight leading-tight">
              {displayCopy?.localePending ? (
                <span className="text-gray-500 dark:text-gray-400">{t('topics.translating')}</span>
              ) : (
                displayCopy?.title ?? topic.title
              )}
            </h1>
            {displayCopy && !displayCopy.localePending && getOriginalTitleLine(topic, displayCopy.title) && (
              <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 font-sans italic mt-1.5 break-words">
                {t('topics.originalTitlePrefix')}{' '}
                {getOriginalTitleLine(topic, displayCopy.title)}
              </p>
            )}
          </div>

          {/* 右側操作按鈕群：轉貼文章 + 點讚/倒讚 */}
          <div className="flex flex-wrap items-center gap-3 shrink-0">
            <button
              type="button"
              onClick={handleJumpToPostKit}
              data-testid="btn-topic-detail-jump-post"
              className="inline-flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-white bg-primary hover:bg-primary-dark rounded-xl shadow-sm transition-all duration-200 touch-manipulation min-h-[44px]"
            >
              <ArrowDownCircle className="w-4 h-4" />
              <span>{t('topics.jumpToPost')}</span>
            </button>

            {/* 喜歡 / 不喜歡互動按鈕 */}
            <div className="bg-white dark:bg-gray-800 p-1 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
              <InteractionButtons
                topicId={id!}
                articleId={content?.id}
                scriptId={content?.id}
                userId={user?.id}
              />
            </div>
          </div>
        </div>

        {/* 語系切換輔助條 */}
        {(needsTranslateToCurrentLanguage(topic, language) || displayCopy?.fromCache) && (
          <div className="flex flex-wrap items-center gap-2 pt-1">
            {needsTranslateToCurrentLanguage(topic, language) && !showCollectionTitle && (
              <>
                <TopicTranslateDisplayButton
                  topic={topic}
                  translationType="standard_translation"
                  testId="btn-topic-detail-translate-display"
                  className="inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-medium text-white bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50 min-h-[38px] touch-manipulation"
                  onTranslated={(next) => {
                    setDisplayOverride(next)
                    setShowCollectionTitle(false)
                  }}
                />
                <TopicTranslateDisplayButton
                  topic={topic}
                  translationType="kol_style"
                  testId="btn-topic-detail-kol-style"
                  className="inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-medium text-amber-900 dark:text-amber-100 bg-amber-100 dark:bg-amber-900/30 border border-amber-300 dark:border-amber-700 rounded-lg hover:bg-amber-200 dark:hover:bg-amber-900/50 disabled:opacity-50 min-h-[38px] touch-manipulation"
                  onTranslated={(next) => {
                    setDisplayOverride(next)
                    setShowCollectionTitle(false)
                  }}
                />
              </>
            )}
            {(displayOverride || showCollectionTitle || displayCopy?.fromCache) && (
              <button
                type="button"
                onClick={() => setShowCollectionTitle((v) => !v)}
                data-testid="btn-topic-detail-show-collected"
                className="px-3.5 py-1.5 text-xs font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 min-h-[38px] touch-manipulation"
              >
                {showCollectionTitle
                  ? t('topics.showTranslatedTitle')
                  : t('topics.showCollectionTitle')}
              </button>
            )}
            {displayCopy?.fromCache && !showCollectionTitle && (
              <span className="text-xs text-green-700 dark:text-green-400 px-2 py-1 bg-green-50 dark:bg-green-900/20 rounded font-sans">
                {t('topics.translatedCached')}
              </span>
            )}
          </div>
        )}
      </header>

      {/* 2. 上半部：主視覺大圖 ＋ 源文章翻譯內容摘要 */}
      <section className="space-y-4">
        {/* 主視覺大圖 (轉版/封面) */}
        <div className="w-full bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-800 overflow-hidden">
          {heroImageUrl ? (
            <div className="relative w-full aspect-[16/9] max-h-[380px] bg-gray-100 dark:bg-gray-950 overflow-hidden flex items-center justify-center">
              <img
                src={heroImageUrl}
                alt={displayCopy?.title || topic.title}
                className="w-full h-full object-cover"
                loading="eager"
              />
              <div className="absolute top-3 left-3 px-3 py-1 bg-black/60 backdrop-blur-sm text-white text-xs font-medium rounded-full flex items-center gap-1.5">
                <ImageIcon className="w-3.5 h-3.5" />
                <span>{t('topics.heroImage')}</span>
              </div>
            </div>
          ) : (
            <div className="w-full py-12 flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-800/60 text-gray-400">
              <ImageIcon className="w-12 h-12 mb-2 stroke-1" />
              <p className="text-sm font-sans">{t('images.noImages')}</p>
            </div>
          )}
        </div>

        {/* 源文章新聞報道與翻譯內容 */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-800 p-5 sm:p-6 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-gray-100 dark:border-gray-700/60 pb-3">
            <div className="flex items-center gap-3">
              <h3 className="font-display text-base sm:text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                <span className="text-primary">📖</span>
                <span>{t('topics.sourceNewsContent')}</span>
              </h3>
              {/* 原文 / 譯文切換按鈕組 */}
              {hasOriginalContent && (
                <div className="inline-flex rounded-lg p-0.5 bg-gray-100 dark:bg-gray-700/60 text-xs">
                  <button
                    type="button"
                    onClick={() => setSourceViewMode('translated')}
                    className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                      sourceViewMode === 'translated'
                        ? 'bg-white dark:bg-gray-800 text-primary shadow-xs font-semibold'
                        : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                    }`}
                    data-testid="btn-topic-detail-view-translated"
                  >
                    {t('topics.viewTranslatedContent')}
                  </button>
                  <button
                    type="button"
                    onClick={() => setSourceViewMode('original')}
                    className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                      sourceViewMode === 'original'
                        ? 'bg-white dark:bg-gray-800 text-primary shadow-xs font-semibold'
                        : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                    }`}
                    data-testid="btn-topic-detail-view-original"
                  >
                    {t('topics.viewOriginalContent')}
                  </button>
                </div>
              )}
            </div>
            {topic.source && (
              <span className="text-xs px-2.5 py-1 rounded-full bg-gray-50 dark:bg-gray-700/50 text-gray-500 dark:text-gray-400 font-sans border border-gray-100 dark:border-gray-700">
                {t('topics.source')}: <strong className="text-gray-700 dark:text-gray-300">{topic.source}</strong>
              </span>
            )}
          </div>

          <div className="text-gray-700 dark:text-gray-300 text-sm sm:text-base leading-relaxed font-sans max-h-[460px] overflow-y-auto pr-2">
            {sourceDisplayContent ? (
              <p className="whitespace-pre-line leading-relaxed">{sourceDisplayContent}</p>
            ) : (
              <p className="text-gray-400 dark:text-gray-500 italic">{t('topics.noContent')}</p>
            )}
          </div>

          {/* 原始出處連結 */}
          {topic.sources && topic.sources.length > 0 && topic.sources[0]?.url && (
            <div className="pt-2 border-t border-gray-50 dark:border-gray-700/40 flex items-center justify-between">
              <a
                href={topic.sources[0].url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 text-xs sm:text-sm text-primary hover:text-primary-dark font-sans underline"
                data-testid="link-topic-detail-original-article"
              >
                <ExternalLink className="w-3.5 h-3.5" />
                <span>{t('topics.viewOriginalArticle')}</span>
              </a>
            </div>
          )}
        </div>
      </section>

      {/* 3. 中段雙欄佈局：左欄【圖片 (X張)】 vs 右欄【生成設定與短文成果】 */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* 左欄 (5 欄)：圖片庫與管理 */}
        <div className="col-span-12 lg:col-span-5 bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-800 p-5 sm:p-6 space-y-4">
          <div className="flex justify-between items-center pb-3 border-b border-gray-100 dark:border-gray-700/60">
            <h3 className="font-display text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
              <span>🖼️</span>
              <span>{t('images.title')}（{images.length} {t('common.count')}）</span>
            </h3>
            <button
              onClick={() => requireAuth(() => setShowImageSearch(true))}
              data-testid="btn-topic-detail-add-image"
              className="px-3 py-1.5 text-xs font-medium text-primary bg-primary/10 rounded-lg hover:bg-primary/20 transition-colors touch-manipulation min-h-[38px]"
            >
              {t('images.upload')}
            </button>
          </div>

          {imagesLoading ? (
            <div className="py-8 flex justify-center">
              <LoadingSpinner size="sm" text={t('images.loading')} />
            </div>
          ) : imagesError ? (
            <ErrorDisplay error={imagesError} />
          ) : images.length === 0 ? (
            <div className="space-y-4 py-4">
              <EmptyState message={t('images.noImages')} size="sm" />
              <div className="flex flex-col sm:flex-row gap-2">
                <button
                  onClick={() => requireAuth(() => matchPhotosMutation.mutate(8))}
                  disabled={matchPhotosMutation.isPending || !content || !content?.article}
                  data-testid="btn-topic-detail-match-photos"
                  className="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2.5 text-xs font-medium text-white bg-primary rounded-xl hover:bg-primary-dark disabled:opacity-50 disabled:cursor-not-allowed min-h-[44px] touch-manipulation shadow-sm"
                  title={!content || !content?.article ? t('images.generateContentFirst') : t('images.matchPhotosTitle')}
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>{matchPhotosMutation.isPending ? t('common.matching') : t('images.smartMatchPhotos')}</span>
                </button>
                <button
                  onClick={() => requireAuth(() => setShowImageSearch(true))}
                  data-testid="btn-topic-detail-search-images"
                  className="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2.5 text-xs font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 min-h-[44px] touch-manipulation"
                >
                  <Search className="w-3.5 h-3.5" />
                  <span>{t('images.search')}</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <ImageGallery
                images={images}
                topicId={id!}
                onImageUpdate={() => {
                  queryClient.invalidateQueries({ queryKey: ['images', id] })
                }}
              />
              <div className="flex gap-2 pt-2 border-t border-gray-100 dark:border-gray-700/60">
                <button
                  onClick={() => requireAuth(() => matchPhotosMutation.mutate(8))}
                  disabled={matchPhotosMutation.isPending}
                  data-testid="btn-topic-detail-match-photos"
                  className="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-medium text-primary bg-primary/10 hover:bg-primary/20 rounded-lg min-h-[40px] touch-manipulation"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>{t('images.smartMatchPhotos')}</span>
                </button>
                <button
                  onClick={() => requireAuth(() => setShowImageSearch(true))}
                  data-testid="btn-topic-detail-search-images"
                  className="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-medium text-gray-700 dark:text-gray-200 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 rounded-lg min-h-[40px] touch-manipulation"
                >
                  <Search className="w-3.5 h-3.5" />
                  <span>{t('images.search')}</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* 右欄 (7 欄)：社群發文組裝器（舊生成面板／短文卡改為不掛載） */}
        <div ref={postKitRef} className="col-span-12 lg:col-span-7 space-y-4">
          <PostComposerPanel
            topicId={topic.id}
            topicTitle={
              displayCopy?.localePending ? topic.title : displayCopy?.title || topic.title
            }
            contextSummary={
              topic.summaryFlash || topic.summary_flash || topic.description || ''
            }
            language={language}
            requireAuth={requireAuth}
          />
          {false && (
          <ContentGenerationPanel
            onGenerate={(settings) =>
              requireAuth(() =>
                content
                  ? regenerateContentMutation.mutate(settings)
                  : generateContentMutation.mutate(settings)
              )
            }
            isGenerating={generateContentMutation.isPending || regenerateContentMutation.isPending}
            hasExistingContent={Boolean(content?.article)}
          />
          )}

          {false && (
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-800 p-5 sm:p-6 space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-gray-100 dark:border-gray-700/60">
              <h3 className="font-display text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                <span>📝</span>
                <span>{t('content.generatedArticle')}</span>
              </h3>
              {content?.article && (
                <button
                  type="button"
                  onClick={() => handleCopyArticle(content.article!)}
                  data-testid="btn-copy-generated-article"
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-700 dark:text-gray-200 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg min-h-[38px] touch-manipulation transition-colors"
                >
                  <Copy className="w-3.5 h-3.5" />
                  <span>{t('content.copy')}</span>
                </button>
              )}
            </div>

            {contentLoading ? (
              <div className="py-12 flex justify-center">
                <LoadingSpinner size="sm" text={t('common.loadingContent')} />
              </div>
            ) : contentTranslating ? (
              <div className="py-8 text-center space-y-2">
                <LoadingSpinner size="sm" text={t('topics.translating')} />
                <p className="text-xs text-amber-600 dark:text-amber-400 font-sans">
                  {t('topics.translating')}
                </p>
              </div>
            ) : content?.article ? (
              <div className="space-y-3">
                <div className="bg-gray-50/70 dark:bg-gray-750 rounded-xl p-4 sm:p-5 border border-gray-100 dark:border-gray-700/60 max-h-96 overflow-y-auto">
                  <p className="text-gray-800 dark:text-gray-200 whitespace-pre-line text-sm sm:text-base leading-relaxed font-sans">
                    {content.article}
                  </p>
                </div>
                <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 font-sans px-1">
                  <span>
                    {t('content.wordCount')}: {content.wordCount} {t('common.words')}
                  </span>
                  {content.modelUsed && <span>AI: {content.modelUsed}</span>}
                </div>
              </div>
            ) : (
              <div className="py-6 text-center space-y-2">
                <EmptyState message={t('common.noContent')} size="sm" />
                <p className="text-xs text-gray-400 dark:text-gray-500 font-sans">
                  {t('content.styleSelectionDesc')}
                </p>
              </div>
            )}
          </div>
          )}
        </div>
      </section>

      {/* 舊 Post Kit 保留檔案與字串，主路改為組裝器（不掛載） */}
      <section className="hidden" aria-hidden="true">
        {false && (
        <PostKitPanel
          displayTitle={
            displayCopy?.localePending ? '' : displayCopy?.title || topic.title
          }
          category={topic.category}
          content={content ?? null}
          images={images}
          previewImages={topic.previewImages || []}
          topicId={topic.id}
          contentTranslating={contentTranslating}
          summaryFlash={translatedContentText || originalContentText}
        />
        )}
      </section>

      {/* 登入提示模態框 */}
      {showLoginPrompt && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 max-w-md w-full text-center space-y-4">
            <h3 className="text-lg font-semibold font-display text-gray-900 dark:text-white">
              {t('auth.loginRequired')}
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 font-sans">
              {t('auth.loginRequiredMessage')}
            </p>
            <div className="flex gap-3 justify-center pt-2">
              <button
                onClick={() => setShowLoginPrompt(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-xl hover:bg-gray-200 min-h-[44px] touch-manipulation"
              >
                {t('common.cancel')}
              </button>
              <button
                onClick={() => navigate('/login')}
                className="px-4 py-2 text-sm font-medium text-white bg-primary rounded-xl hover:bg-primary-dark min-h-[44px] touch-manipulation"
              >
                {t('auth.login.title')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 圖片搜尋模態框 */}
      {showImageSearch && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
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
    </div>
  )
}
