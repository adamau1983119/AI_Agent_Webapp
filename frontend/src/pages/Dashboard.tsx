import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { topicsAPI } from '@/api/client'
import TopicCard from '@/components/ui/TopicCard'
import ConnectionErrorDisplay from '@/components/ui/ConnectionErrorDisplay'
import { usePageTitle } from '@/hooks/usePageTitle'
import { useTranslation } from '@/i18n'
import {
  EXPECTED_DAILY_TOPICS,
  countTopicsForHktDay,
  dedupeTopicsByTitle,
  filterTopicsForHktDay,
} from '@/lib/topicDayHkt'

type DashTab = 'all' | 'fashion' | 'food' | 'trend'

/** 方案 C：收集語言固定 zh-TW（介面語系不影響產卡） */

/**
 * Dashboard：今日頭條牆（HKT）＋分類 Tab；「更多」進主題庫無限滾。
 */
export default function Dashboard() {
  usePageTitle()
  const { t, language } = useTranslation()
  const [tab, setTab] = useState<DashTab>('all')

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
  const displayTopics = dedupeTopicsByTitle(filterTopicsForHktDay(topics))
  const tabTopics =
    tab === 'all' ? displayTopics : displayTopics.filter((topic) => topic.category === tab)

  useEffect(() => {
    if (topicsError || todayTopicsCount >= EXPECTED_DAILY_TOPICS) return
    const id = window.setInterval(() => {
      refetchTopics()
    }, 120_000)
    return () => window.clearInterval(id)
  }, [todayTopicsCount, topicsError, refetchTopics])

  const handleRetry = () => {
    refetchTopics()
  }

  const tabs: Array<{ id: DashTab; label: string; testId: string }> = [
    { id: 'all', label: t('dashboard.tabAll'), testId: 'btn-dashboard-tab-all' },
    { id: 'fashion', label: t('dashboard.fashionTrends'), testId: 'btn-dashboard-tab-fashion' },
    { id: 'food', label: t('dashboard.foodDining'), testId: 'btn-dashboard-tab-food' },
    { id: 'trend', label: t('dashboard.socialTrends'), testId: 'btn-dashboard-tab-trend' },
  ]

  const moreHref = tab === 'all' ? '/topics' : `/topics?category=${tab}`
  const moreLabel =
    tab === 'fashion'
      ? t('dashboard.moreFashion')
      : tab === 'food'
        ? t('dashboard.moreFood')
        : tab === 'trend'
          ? t('dashboard.moreTrend')
          : t('dashboard.moreAll')

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

      <div className="mb-6 flex flex-col sm:flex-row sm:items-end sm:justify-between gap-3">
        <div>
          <h3 className="text-[11px] tracking-[0.15em] uppercase text-gray-500">
            {t('dashboard.headlines')}
          </h3>
          {!topicsLoading && displayTopics.length > 0 ? (
            <p className="text-sm text-gray-500 font-light mt-2">
              {t('dashboard.todayTopics')} — {tabTopics.length} {t('dashboard.items')}
            </p>
          ) : null}
        </div>
      </div>

      <div className="flex gap-1 overflow-x-auto border-b border-gray-200 mb-8" role="tablist">
        {tabs.map((item) => {
          const selected = tab === item.id
          return (
            <button
              key={item.id}
              type="button"
              role="tab"
              aria-selected={selected}
              data-testid={item.testId}
              onClick={() => setTab(item.id)}
              className={`shrink-0 min-h-[44px] px-4 py-3 text-[11px] tracking-[0.15em] uppercase transition-colors ${
                selected
                  ? 'text-black border-b-2 border-black'
                  : 'text-gray-400 hover:text-gray-700'
              }`}
            >
              {item.label}
            </button>
          )
        })}
      </div>

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
                {t('dashboard.todayTopicsPreparing')}
              </h4>
              <div className="w-12 h-px bg-gray-300 mx-auto mb-4" />
              <p className="text-gray-500 font-light text-sm mb-2">{t('dashboard.systemUpdatesEvery6h')}</p>
              <p className="text-[10px] tracking-[0.1em] uppercase text-gray-400">{t('dashboard.categoryList')}</p>
              <Link
                to="/topics"
                data-testid="link-dashboard-topics"
                className="inline-block mt-6 text-sm text-primary hover:text-primary-dark font-medium"
              >
                {t('dashboard.browseTopics')}
              </Link>
            </div>
          ) : (
            <>
              {tabTopics.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {tabTopics.map((topic) => (
                    <div key={topic.id} className="h-full">
                      <TopicCard topic={topic} enableAutoTranslate={false} hideCacheBadge />
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-[10px] tracking-[0.1em] uppercase text-gray-400 bg-white border border-gray-100">
                  {t('dashboard.collecting').replace(
                    '{category}',
                    tabs.find((item) => item.id === tab)?.label || ''
                  )}
                </div>
              )}
              <div className="mt-10 text-center">
                <Link
                  to={moreHref}
                  data-testid="link-dashboard-topics"
                  className="inline-block min-h-[44px] px-6 py-3 text-[11px] tracking-[0.15em] uppercase text-black border border-gray-200 hover:border-black transition-all duration-300"
                >
                  {moreLabel}
                </Link>
              </div>
            </>
          )}
        </>
      )}
    </div>
  )
}
