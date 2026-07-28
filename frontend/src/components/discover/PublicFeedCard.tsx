import { API_BASE_URL } from '@/api/client'
import type { PublicFeedCard as PublicFeedCardType } from '@/api/publicFeed'
import { useTranslation } from '@/i18n'

const gradientClasses: Record<string, string> = {
  fashion: 'from-purple-400 to-blue-400',
  food: 'from-orange-400 to-pink-400',
  trend: 'from-green-400 to-blue-400',
}

function getProxyImageUrl(imageUrl: string): string {
  if (!imageUrl) return ''
  if (imageUrl.includes('/images/proxy') || imageUrl.startsWith('/')) return imageUrl
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
    return `${API_BASE_URL}/images/proxy?url=${encodeURIComponent(imageUrl)}`
  }
  return imageUrl
}

function categoryLabelKey(category: string | null | undefined): string {
  if (category === 'fashion') return 'channels.category.fashion'
  if (category === 'food') return 'channels.category.food'
  if (category === 'trend') return 'channels.category.trend'
  return 'topics.category'
}

interface PublicFeedCardProps {
  card: PublicFeedCardType
  testId: string
}

export default function PublicFeedCard({ card, testId }: PublicFeedCardProps) {
  const { t } = useTranslation()
  const gradient = gradientClasses[card.category || ''] || 'from-gray-400 to-gray-500'
  const imageSrc = card.image_url ? getProxyImageUrl(card.image_url) : ''

  return (
    <article
      className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm hover:shadow-md transition-shadow"
      data-testid={testId}
    >
      <div className={`relative h-40 bg-gradient-to-br ${gradient}`}>
        {imageSrc ? (
          <img
            src={imageSrc}
            alt=""
            className="absolute inset-0 w-full h-full object-cover"
            loading="lazy"
          />
        ) : null}
        {card.category ? (
          <span
            className="absolute top-3 left-3 text-xs font-medium text-white bg-black/40 px-2 py-0.5 rounded"
            data-testid={`${testId}-category`}
          >
            {t(categoryLabelKey(card.category) as 'channels.category.fashion')}
          </span>
        ) : null}
      </div>
      <div className="p-4">
        <h2
          className="text-base font-semibold text-gray-900 line-clamp-2 leading-snug"
          data-testid={`${testId}-title`}
        >
          {card.title}
        </h2>
        {card.description ? (
          <p
            className="mt-2 text-sm text-gray-600 line-clamp-3"
            data-testid={`${testId}-description`}
          >
            {card.description}
          </p>
        ) : null}
        {card.source ? (
          <p className="mt-3 text-xs text-gray-400 truncate" data-testid={`${testId}-source`}>
            {card.source}
          </p>
        ) : null}
      </div>
    </article>
  )
}
