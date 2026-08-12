import { useEffect, useRef, useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { schedulesAPI, topicsAPI } from '@/api/client'
import TopicCard from '@/components/ui/TopicCard'
import ConnectionErrorDisplay from '@/components/ui/ConnectionErrorDisplay'
import { usePageTitle } from '@/hooks/usePageTitle'
import { useTranslation } from '@/i18n'
import {
  EXPECTED_DAILY_TOPICS,
  countTopicsForHktDay,
  filterTopicsForHktDay,
} from '@/lib/topicDayHkt'

/** 方案 C：收集語言固定 zh-TW（介面語系不影響產卡） */
const COLLECTION_LANGUAGE = 'zh-TW'

/**
 * Dashboard：只顯示今日主題卡；空列表時可強制各分類再產 5 張（測試／軟切換）。
 */
export default function Dashboard() {
  usePageTitle()
  const { t, language } = useTranslation()
  const autoTriggered = useRef(false)
  const [isGenerating, setIsGenerating] = useState(false)

  const {
    data: topicsResponse,
    isLoading: topicsLoading,
    error: topicsError,
    refetch: refetchTopics,
  } = useQuery({
    queryKey: ['topics', language],
    queryFn: () => topicsAPI.getTopics({ limit: 30, lang: language }),
    retry: false,
    staleTime: 30000,
    gcTime: 5 * 60 * 1000,
    refetchInterval: false,
    refetchOnWindowFocus: false,
    refetchOnMount: true,
  })

  const topics = topicsError ? [] : topicsResponse?.data || []
  const todayTopicsCount = countTopicsForHktDay(topics)
  const displayTopics = filterTopicsForHktDay(topics)

  const generateMutation = useMutation({
    mutationFn: () => schedulesAPI.generateTodayAllTopics(true, COLLECTION_LANGUAGE),
    onMutate: () => {
      setIsGenerating(true)
      toast.loading(t('dashboard.generating'), { id: 'generate-today' })
    },
    onSuccess: (data) => {
      toast.success(data.message || t('dashboard.generateStarted'), { id: 'generate-today' })
      refetchTopics()
    },
    onError: (error: unknown) => {
      setIsGenerating(false)
      const err = error as { message?: string; status?: number; details?: { suggestion?: string } }
      let msg = err?.message || t('dashboard.generateFailed')
      if (err?.details?.suggestion) {
        msg = `${msg}\n${err.details.suggestion}`
      }
      toast.error(msg, { id: 'generate-today', duration: 5000 })
    },
  })
  const { mutate: triggerGenerate, isPending: generatePending } = generateMutation

  // 產卡中：每 15s 刷新，直到滿額或逾時
  useEffect(() => {
    if (!isGenerating) return
    const started = Date.now()
    const id = window.setInterval(() => {
      refetchTopics()
      if (Date.now() - started > 180_000) {
        setIsGenerating(false)
      }
    }, 15_000)
    return () => window.clearInterval(id)
  }, [isGenerating, refetchTopics])

  useEffect(() => {
    if (!isGenerating) return
    if (todayTopicsCount >= EXPECTED_DAILY_TOPICS) {
      setIsGenerating(false)
      toast.success(t('dashboard.generateSuccess'), { id: 'generate-today-complete' })
    }
  }, [todayTopicsCount, isGenerating, t])

  // 未滿日配額：每 2 分鐘輕量刷新
  useEffect(() => {
    if (topicsError || todayTopicsCount >= EXPECTED_DAILY_TOPICS) return
    const id = window.setInterval(() => {
      refetchTopics()
    }, 120_000)
    return () => window.clearInterval(id)
  }, [todayTopicsCount, topicsError, refetchTopics])

  // 列表為空：自動強制各系列再產 5 張（方便測試／軟切換）
  useEffect(() => {
    if (autoTriggered.current || topicsLoading || topicsError) return
    if (displayTopics.length > 0) return
    if (generatePending || isGenerating) return
    autoTriggered.current = true
    triggerGenerate()
  }, [
    topicsLoading,
    topicsError,
    displayTopics.length,
    generatePending,
    isGenerating,
    triggerGenerate,
  ])

  const handleRetry = () => {
    refetchTopics()
  }

  const handleGenerateToday = () => {
    if (generatePending || isGenerating) return
    triggerGenerate()
  }

  const categories = [
    { key: 'fashion', label: t('dashboard.fashionTrends') },
    { key: 'food', label: t('dashboard.foodDining') },
    { key: 'trend', label: t('dashboard.socialTrends') },
  ]

  const topicsByCategory = categories.map((cat) => ({
    ...cat,
    topics: displayTopics.filter((topic) => topic.category === cat.key),
  }))

  return (
    <div className="min-h-screen bg-[#FAF9F7] p-6 sm:p-8 font-sans" data-testid="dashboard-topic-cards-only">
      {topicsError && (
        <div className="mb-6">
          <ConnectionErrorDisplay
            error={topicsError || new Error(t('dashboard.cannotConnect'))}
            onRetry={handleRetry}
          />
        </div>
      )}

      {(topicsError as { status?: number } | null)?.status === 429 ? (
        <div className="mb-6 bg-white border border-gray-200 p-6">
          <h3 className="text-[11px] tracking-[0.15em] uppercase text-gray-800 mb-2">
            {t('dashboard.requestLimitReached')}
          </h3>
          <p className="text-sm text-gray-500 font-light mb-4">{t('dashboard.rateLimitMessage')}</p>
          <button
            type="button"
            onClick={handleRetry}
            className="px-6 py-3 bg-black text-white text-[11px] tracking-[0.2em] uppercase hover:bg-gray-900 transition-colors"
          >
            {t('dashboard.retry')}
          </button>
        </div>
      ) : null}

      <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
        <h3 className="text-[11px] tracking-[0.15em] uppercase text-gray-500">
          {t('dashboard.topicCards')}
        </h3>
        <button
          type="button"
          data-testid="btn-dashboard-generate"
          onClick={handleGenerateToday}
          disabled={generatePending || isGenerating}
          className="px-5 py-2.5 bg-black text-white text-[10px] tracking-[0.15em] uppercase hover:bg-gray-900 disabled:opacity-50 transition-colors"
        >
          {generatePending || isGenerating
            ? t('dashboard.generatingTopics')
            : t('dashboard.generateTodayForce')}
        </button>
      </div>

      {(generatePending || isGenerating) && (
        <div className="mb-6 bg-white border border-black p-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b border-black" />
            <h3 className="text-[11px] tracking-[0.15em] uppercase text-black">
              {t('dashboard.generatingTopics')}
            </h3>
          </div>
          <p className="text-[10px] text-gray-500 font-light tracking-wide">
            {t('dashboard.generateTodayForceHint')}
          </p>
        </div>
      )}

      {topicsLoading && !topicsError ? (
        <div className="text-center py-16">
          <div className="inline-block animate-spin rounded-full h-6 w-6 border-b border-black" />
          <p className="mt-4 text-[11px] tracking-[0.1em] uppercase text-gray-500">{t('dashboard.loading')}</p>
        </div>
      ) : (
        <>
          {displayTopics.length === 0 ? (
            <div className="text-center py-20 bg-white border border-gray-100">
              <div className="inline-flex items-center justify-center w-16 h-16 border border-gray-200 mb-8">
                <svg className="w-8 h-8 text-gray-400 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1}
                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                  />
                </svg>
              </div>
              <h4 className="text-sm tracking-[0.15em] uppercase text-black mb-4">
                {isGenerating ? t('dashboard.generatingTopics') : t('dashboard.aiAgentCollecting')}
              </h4>
              <div className="w-12 h-px bg-gray-300 mx-auto mb-4" />
              <p className="text-gray-500 font-light text-sm mb-2">{t('dashboard.generateTodayForceHint')}</p>
              <p className="text-[10px] tracking-[0.1em] uppercase text-gray-400">{t('dashboard.categoryList')}</p>
            </div>
          ) : (
            <>
              <p className="text-sm text-gray-500 font-light mb-6">
                {t('dashboard.todayTopics')} — {displayTopics.length} {t('dashboard.items')}
              </p>
              <div className="space-y-8">
                {topicsByCategory.map((category) => (
                  <div key={category.key}>
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="text-[11px] tracking-[0.15em] uppercase text-black">
                        {category.label}
                      </h4>
                      <span className="text-[10px] text-gray-400 font-light">
                        {category.topics.length} {t('dashboard.topics')}
                      </span>
                    </div>
                    {category.topics.length > 0 ? (
                      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                        {category.topics.map((topic) => (
                          <div key={topic.id} className="h-full">
                            <TopicCard topic={topic} enableAutoTranslate={false} />
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8 text-[10px] tracking-[0.1em] uppercase text-gray-400 bg-white border border-gray-100">
                        {t('dashboard.collecting').replace('{category}', category.label)}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </>
          )}
        </>
      )}
    </div>
  )
}
