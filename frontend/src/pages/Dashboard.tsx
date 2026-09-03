import { useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { topicsAPI } from '@/api/client'
import TopicCard from '@/components/ui/TopicCard'
import ConnectionErrorDisplay from '@/components/ui/ConnectionErrorDisplay'
import InfiniteTopicsList from '@/components/features/InfiniteTopicsList'
import { usePageTitle } from '@/hooks/usePageTitle'
import { useTranslation } from '@/i18n'
import {
  EXPECTED_DAILY_TOPICS,
  countTopicsForHktDay,
  dedupeTopicsByTitle,
  filterTopicsForHktDay,
} from '@/lib/topicDayHkt'

type DashTab = 'all' | 'fashion' | 'food' | 'trend'
type DashCategory = 'fashion' | 'food' | 'trend'

/** 方案 C：收集語言固定 zh-TW（介面語系不影響產卡） */

function parseDashTab(raw: string | null): DashTab {
  if (raw === 'fashion' || raw === 'food' || raw === 'trend') return raw
  return 'all'
}

/**
 * Dashboard：全部＝三類今日各 5；分類 Tab 直接今日＋歷史，不跳 /topics。
 */
export default function Dashboard() {
  usePageTitle()
  const { t, language } = useTranslation()
  const [searchParams, setSearchParams] = useSearchParams()
  const tab = parseDashTab(searchParams.get('tab'))

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

  const selectTab = (next: DashTab) => {
    const nextParams = new URLSearchParams(searchParams)
    if (next === 'all') nextParams.delete('tab')
    else nextParams.set('tab', next)
    setSearchParams(nextParams, { replace: true })
  }

  const moreLabel = (category: DashCategory) =>
    category === 'fashion'
      ? t('dashboard.moreFashion')
      : category === 'food'
        ? t('dashboard.moreFood')
        : t('dashboard.moreTrend')

  const tabs: Array<{ id: DashTab; label: string; testId: string }> = [
    { id: 'all', label: t('dashboard.tabAll'), testId: 'btn-dashboard-tab-all' },
    { id: 'fashion', label: t('dashboard.fashionTrends'), testId: 'btn-dashboard-tab-fashion' },
    { id: 'food', label: t('dashboard.foodDining'), testId: 'btn-dashboard-tab-food' },
    { id: 'trend', label: t('dashboard.socialTrends'), testId: 'btn-dashboard-tab-trend' },
  ]

  const sections: Array<{
    key: DashCategory
    label: string
    moreTestId: string
    topics: typeof displayTopics
  }> = [
    {
      key: 'fashion',
      label: t('dashboard.fashionTrends'),
      moreTestId: 'btn-dashboard-more-fashion',
      topics: displayTopics.filter((topic) => topic.category === 'fashion'),
    },
    {
      key: 'food',
      label: t('dashboard.foodDining'),
      moreTestId: 'btn-dashboard-more-food',
      topics: displayTopics.filter((topic) => topic.category === 'food'),
    },
    {
      key: 'trend',
      label: t('dashboard.socialTrends'),
      moreTestId: 'btn-dashboard-more-trend',
      topics: displayTopics.filter((topic) => topic.category === 'trend'),
    },
  ]

  const archiveCategory: DashCategory | null = tab === 'all' ? null : tab

  const moreBtnClass =
    'inline-block min-h-[44px] px-6 py-3 text-[11px] tracking-[0.15em] uppercase text-black border border-gray-200 hover:border-black transition-all duration-300'

  const renderTopicGrid = (list: typeof displayTopics) => (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {list.map((topic) => (
        <div key={topic.id} className="h-full">
          <TopicCard topic={topic} enableAutoTranslate={false} hideCacheBadge />
        </div>
      ))}
    </div>
  )

  const showAllLoading = tab === 'all' && topicsLoading && !topicsError
  const showAllEmpty = tab === 'all' && !topicsLoading && displayTopics.length === 0

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

      <div className="mb-6">
        <h3 className="text-[11px] tracking-[0.15em] uppercase text-gray-500">
          {t('dashboard.headlines')}
        </h3>
        {tab === 'all' && !topicsLoading && displayTopics.length > 0 ? (
          <p className="text-sm text-gray-500 font-light mt-2">
            {t('dashboard.todayTopics')} — {displayTopics.length} {t('dashboard.items')}
          </p>
        ) : null}
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
              onClick={() => selectTab(item.id)}
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

      {showAllLoading ? (
        <div className="text-center py-16">
          <div className="inline-block animate-spin rounded-full h-6 w-6 border-b border-black" />
          <p className="mt-4 text-[11px] tracking-[0.1em] uppercase text-gray-500">{t('dashboard.loading')}</p>
        </div>
      ) : showAllEmpty ? (
        <div className="text-center py-20 bg-white border border-gray-100">
          <h4 className="text-sm tracking-[0.15em] uppercase text-black mb-4">
            {t('dashboard.todayTopicsPreparing')}
          </h4>
          <div className="w-12 h-px bg-gray-300 mx-auto mb-4" />
          <p className="text-sm text-gray-500 font-light mb-2">{t('dashboard.systemUpdatesEvery6h')}</p>
          <p className="text-[10px] tracking-[0.1em] uppercase text-gray-400">{t('dashboard.categoryList')}</p>
          <Link
            to="/topics"
            data-testid="link-dashboard-topics"
            className="inline-block mt-6 text-sm text-primary hover:text-primary-dark font-medium"
          >
            {t('dashboard.browseTopics')}
          </Link>
        </div>
      ) : tab === 'all' ? (
        <div className="space-y-10">
          {sections.map((section) => (
            <section key={section.key}>
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-[11px] tracking-[0.15em] uppercase text-black">{section.label}</h4>
                <span className="text-[10px] text-gray-400 font-light">
                  {section.topics.length} {t('dashboard.topics')}
                </span>
              </div>
              {section.topics.length > 0 ? (
                renderTopicGrid(section.topics)
              ) : (
                <div className="text-center py-8 text-[10px] tracking-[0.1em] uppercase text-gray-400 bg-white border border-gray-100">
                  {t('dashboard.collecting').replace('{category}', section.label)}
                </div>
              )}
              <div className="mt-6 text-center">
                <button
                  type="button"
                  data-testid={section.moreTestId}
                  onClick={() => selectTab(section.key)}
                  className={moreBtnClass}
                >
                  {moreLabel(section.key)}
                </button>
              </div>
            </section>
          ))}
        </div>
      ) : archiveCategory ? (
        <InfiniteTopicsList
          filters={{ category: archiveCategory }}
          showTimeGroups
          pageSize={20}
          emptyMessage={t('topics.noTopics')}
        />
      ) : null}
    </div>
  )
}
