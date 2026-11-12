import { Link } from 'react-router-dom'
import { useQueries } from '@tanstack/react-query'
import { topicsAPI } from '@/api/topics'
import { API_BASE_URL } from '@/api/client'
import { useTranslation } from '@/i18n'
import { todayHktDateString } from '@/lib/topicDayHkt'
import type { Topic } from '@/types'

function previewUrl(topic: Topic): string {
  const images = topic.previewImages || topic.preview_images || []
  const raw = images[0] || ''
  if (!raw) return ''
  if (raw.includes('/images/proxy') || raw.startsWith('/')) return raw
  if (raw.startsWith('http://') || raw.startsWith('https://')) {
    return `${API_BASE_URL}/images/proxy?url=${encodeURIComponent(raw)}`
  }
  return raw
}

export function MobileTopicList({
  topics,
  testId,
  onOpen,
  compact = false,
}: {
  topics: Topic[]
  testId: string
  onOpen?: (topic: Topic) => void
  compact?: boolean
}) {
  if (topics.length === 0) return null
  const lead = compact ? null : topics[0]
  const rows = compact ? topics : topics.slice(1)
  return (
    <div data-testid={testId} className="space-y-3">
      {!compact && lead ? (
        <Link
          to={`/topics/${lead.id}`}
          data-testid="link-mobile-topic"
          onClick={() => onOpen?.(lead)}
          className="block overflow-hidden rounded-2xl border border-black/5 bg-white"
        >
          {previewUrl(lead) ? (
            <img src={previewUrl(lead)} alt="" className="h-48 w-full object-cover" />
          ) : (
            <div className="h-24 bg-[#ebe8e3]" />
          )}
          <p className="p-4 font-display text-xl leading-snug text-[#1a1a1a]">{lead.title}</p>
        </Link>
      ) : null}
      {rows.map((topic) => (
        <Link
          key={topic.id}
          to={`/topics/${topic.id}`}
          data-testid="link-mobile-topic"
          onClick={() => onOpen?.(topic)}
          className="flex items-center gap-3 rounded-2xl border border-black/5 bg-white p-3"
        >
          {previewUrl(topic) ? (
            <img src={previewUrl(topic)} alt="" className="h-16 w-16 rounded-lg object-cover" />
          ) : (
            <div className="h-16 w-16 rounded-lg bg-[#ebe8e3]" />
          )}
          <span className="min-w-0 flex-1 text-sm leading-snug text-[#1a1a1a]">{topic.title}</span>
        </Link>
      ))}
    </div>
  )
}

const WELCOME_CATEGORIES = ['fashion', 'food', 'trend'] as const
const WELCOME_CATEGORY_LABEL = {
  fashion: 'dashboard.fashionTrends',
  food: 'dashboard.foodDining',
  trend: 'dashboard.socialTrends',
} as const

export function TodayMobileTopics({
  testId,
  onOpen,
}: {
  testId: string
  onOpen?: (topic: Topic) => void
}) {
  const { t, language } = useTranslation()
  const today = todayHktDateString()
  const categoryQueries = useQueries({
    queries: WELCOME_CATEGORIES.map((category) => ({
      queryKey: ['mobile-topics', language, today, category],
      queryFn: () => topicsAPI.getTopics({
        limit: 3,
        lang: language,
        date: today,
        category,
      }),
      retry: false,
    })),
  })

  return (
    <div className="space-y-8">
      <p className="text-sm leading-relaxed text-[#6b6b6b]">
        {t('welcomeSample.themesIntro')}
      </p>
      {WELCOME_CATEGORIES.map((category, index) => {
        const query = categoryQueries[index]
        const topics = (query?.data?.data || []).slice(0, 3)
        return (
          <section key={category} className="space-y-3">
            <h2 className="font-display text-lg tracking-wide text-[#1a1a1a]">
              {t(WELCOME_CATEGORY_LABEL[category])}
            </h2>
            {query?.isLoading ? (
              <p className="text-sm text-[#6b6b6b]">{t('welcomeSample.loading')}</p>
            ) : null}
            {!query?.isLoading && topics.length === 0 ? (
              <p className="text-sm text-[#6b6b6b]">{t('welcomeSample.empty')}</p>
            ) : (
              <MobileTopicList
                topics={topics}
                testId={`${testId}-${category}`}
                onOpen={onOpen}
              />
            )}
          </section>
        )
      })}
    </div>
  )
}
