import { useQuery } from '@tanstack/react-query'
import { publicFeedAPI, resolvePublicFeedLang } from '@/api/publicFeed'
import PublicFeedCard from '@/components/discover/PublicFeedCard'
import PublicFeedSkeleton from '@/components/discover/PublicFeedSkeleton'
import EmptyState from '@/components/ui/EmptyState'
import ErrorDisplay from '@/components/ui/ErrorDisplay'
import { usePageTitle } from '@/hooks/usePageTitle'
import { useTranslation } from '@/i18n'

export default function Discover() {
  usePageTitle()
  const { t, language } = useTranslation()
  const feedLang = resolvePublicFeedLang(language)

  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['publicFeed', feedLang],
    queryFn: () => publicFeedAPI.getFeed(feedLang),
    staleTime: 5 * 60 * 1000,
    retry: 1,
  })

  const cards = data?.data ?? []

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6" data-testid="page-discover">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900" data-testid="discover-page-title">
          {t('discover.title')}
        </h1>
        <p className="mt-1 text-sm text-gray-500" data-testid="discover-page-subtitle">
          {t('discover.subtitle')}
        </p>
      </header>

      {isLoading ? <PublicFeedSkeleton /> : null}

      {isError && !isLoading ? (
        <ErrorDisplay error={error} onRetry={() => refetch()} />
      ) : null}

      {!isLoading && !isError && cards.length === 0 ? (
        <EmptyState message={t('discover.empty')} description={t('discover.emptyHint')} />
      ) : null}

      {!isLoading && !isError && cards.length > 0 ? (
        <div
          className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 ${
            isFetching ? 'opacity-90' : ''
          }`}
          data-testid="discover-feed-grid"
        >
          {cards.map((card, index) => (
            <PublicFeedCard
              key={card.id}
              card={card}
              testId={`card-discover-feed-${index}`}
            />
          ))}
        </div>
      ) : null}
    </div>
  )
}
