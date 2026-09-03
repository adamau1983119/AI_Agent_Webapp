import { useState, useMemo, useEffect } from 'react'
import { Link } from 'react-router-dom'
import type { Topic } from '@/types'
import { API_BASE_URL } from '@/api/client'
import { topicsAPI } from '@/api/topics'
import { useTranslation } from '@/i18n'
import { formatDistanceToNow } from 'date-fns'
import { zhTW, enUS, ja } from 'date-fns/locale'
import {
  isTopicOnHktDay,
  topicHktDateString,
  yesterdayHktDateString,
} from '@/lib/topicDayHkt'
import TopicTranslateDisplayButton, {
  type TopicDisplayOverride,
} from '@/components/ui/TopicTranslateDisplayButton'
import {
  getOriginalTitleLine,
  hasCompleteDisplayPack,
  isServerLocaleResolved,
  needsTranslateToCurrentLanguage,
  resolveTopicDisplayCopy,
} from '@/lib/topicDisplay'
import {
  enqueueTranslateDisplay,
  isTranslateHardBlocked,
  isTranslateRateLimited,
  markTranslateRateLimited,
} from '@/lib/translateDisplayQueue'
import { isTopicRead, subscribeTopicRead } from '@/lib/topicReadState'

function getProxyImageUrl(imageUrl: string): string {
  if (!imageUrl) return ''
  if (imageUrl.includes('/images/proxy') || imageUrl.startsWith('/')) return imageUrl
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
    return `${API_BASE_URL}/images/proxy?url=${encodeURIComponent(imageUrl)}`
  }
  return imageUrl
}

function TopicTextSkeleton() {
  return (
    <div className="animate-pulse space-y-2" data-testid="topic-card-text-skeleton" aria-hidden>
      <div className="h-4 bg-gray-200 dark:bg-gray-600 rounded w-4/5" />
      <div className="h-3 bg-gray-200 dark:bg-gray-600 rounded w-full" />
      <div className="h-3 bg-gray-200 dark:bg-gray-600 rounded w-3/4" />
    </div>
  )
}

interface TopicCardProps {
  topic: Topic
  /** 頻道列表等場景可覆寫 kol 按鈕 testid */
  kolStyleTestId?: string
  /** Dashboard 列表關閉自動翻譯，避免一次 N 張卡打爆 API／Console */
  enableAutoTranslate?: boolean
  /** 列表預設可藏「已譯（快取）」；不改 fromCache 計算與翻譯管線 */
  hideCacheBadge?: boolean
}

const gradientClasses = {
  fashion: 'from-purple-400 to-blue-400',
  food: 'from-orange-400 to-pink-400',
  trend: 'from-green-400 to-blue-400',
}

export default function TopicCard({
  topic,
  kolStyleTestId,
  enableAutoTranslate = false,
  hideCacheBadge = false,
}: TopicCardProps) {
  const { t, language } = useTranslation()
  const [override, setOverride] = useState<TopicDisplayOverride | null>(null)
  const [standardLoading, setStandardLoading] = useState(false)
  const [fadeReady, setFadeReady] = useState(true)
  const [hasOpened, setHasOpened] = useState(() => isTopicRead(topic.id))

  useEffect(() => {
    setHasOpened(isTopicRead(topic.id))
    return subscribeTopicRead(() => setHasOpened(isTopicRead(topic.id)))
  }, [topic.id])

  const needsTranslate = needsTranslateToCurrentLanguage(topic, language)
  const serverResolved = isServerLocaleResolved(topic, language)
  const hasStandardCache = serverResolved || hasCompleteDisplayPack(topic, language)
  const translateBlocked = isTranslateHardBlocked() || isTranslateRateLimited()

  const display = useMemo(
    () => resolveTopicDisplayCopy(topic, language, override),
    [topic, language, override]
  )
  const localePending = display.localePending === true
  const shouldAutoTranslate = enableAutoTranslate || localePending
  const originalLine = useMemo(
    () => getOriginalTitleLine(topic, display.title),
    [topic, display.title]
  )

  useEffect(() => {
    setOverride(null)
  }, [topic.id, language])

  useEffect(() => {
    if (!needsTranslate || serverResolved) {
      setStandardLoading(false)
      setFadeReady(true)
      return
    }

    if (hasStandardCache) {
      setStandardLoading(false)
      setFadeReady(false)
      const timer = window.setTimeout(() => setFadeReady(true), 30)
      return () => window.clearTimeout(timer)
    }

    if (!shouldAutoTranslate || translateBlocked) {
      setStandardLoading(false)
      setFadeReady(true)
      return
    }

    let cancelled = false
    setStandardLoading(true)
    setFadeReady(false)

    const cancelQueue = enqueueTranslateDisplay(async () => {
      if (cancelled || isTranslateHardBlocked() || isTranslateRateLimited()) {
        if (!cancelled) {
          setStandardLoading(false)
          setFadeReady(true)
        }
        return
      }
      try {
        const res = await topicsAPI.translateDisplay(
          topic.id,
          language,
          'standard_translation'
        )
        if (cancelled) return
        setOverride({
          title: res.title,
          description: res.description,
          cached: res.cached,
          translationType: 'standard_translation',
        })
        window.setTimeout(() => setFadeReady(true), 30)
      } catch (err: unknown) {
        const apiErr = err as {
          status?: number
          code?: string
          message?: string
          details?: { code?: string }
        }
        const code = apiErr.code || apiErr.details?.code || ''
        const msg = String(apiErr.message || '')
        if (apiErr.status === 429 || code === 'RATE_LIMIT') {
          markTranslateRateLimited(60_000)
        } else if (
          apiErr.status === 503 ||
          code === 'deepseek_not_configured' ||
          code === 'translation_fallback' ||
          msg.includes('deepseek') ||
          msg.includes('translation_fallback')
        ) {
          try {
            sessionStorage.setItem('flash_translate_unavailable', '1')
          } catch {
            /* ignore */
          }
        }
        if (!cancelled) setFadeReady(true)
      } finally {
        if (!cancelled) setStandardLoading(false)
      }
    })

    return () => {
      cancelled = true
      cancelQueue()
    }
  }, [
    topic.id,
    language,
    needsTranslate,
    hasStandardCache,
    shouldAutoTranslate,
    translateBlocked,
    serverResolved,
  ])

  const formatTimeAgo = (dateValue: string | Date | undefined): string => {
    if (!dateValue) return ''
    try {
      const date = typeof dateValue === 'string' ? new Date(dateValue) : dateValue
      if (isNaN(date.getTime())) return ''
      const locales = { 'zh-TW': zhTW, en: enUS, ja }
      const locale = locales[language as keyof typeof locales] || enUS
      return formatDistanceToNow(date, { addSuffix: true, locale })
    } catch {
      return ''
    }
  }

  const generatedTime = topic.generatedAt || topic.generated_at || topic.createdAt || topic.created_at
  const timeAgo = formatTimeAgo(generatedTime)
  const rec = topic as unknown as Record<string, unknown>
  const topicDay = topicHktDateString(rec)
  const dateLabel = isTopicOnHktDay(rec)
    ? t('topics.badgeNew')
    : topicDay === yesterdayHktDateString()
      ? t('topics.yesterday')
      : topicDay
        ? `${topicDay.slice(5, 7)}/${topicDay.slice(8, 10)}`
        : timeAgo
  const previewImages = topic.previewImages || topic.preview_images || []
  const previewImage = Array.isArray(previewImages) && previewImages.length > 0 ? previewImages[0] : null

  const handleKolTranslated = (next: TopicDisplayOverride) => {
    setOverride(next)
    setFadeReady(false)
    window.setTimeout(() => setFadeReady(true), 30)
  }

  const showKolButton = needsTranslate && !standardLoading && !localePending
  const showCacheLabel =
    !hideCacheBadge &&
    (display.fromCache || override?.cached) &&
    override?.translationType !== 'kol_style'
  const showTranslateFooter = showKolButton || showCacheLabel
  const showTextPending = localePending && !standardLoading

  const textFadeClass = `transition-opacity duration-500 ease-out ${
    fadeReady && !standardLoading && !showTextPending ? 'opacity-100' : 'opacity-0'
  }`

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden hover:shadow-lg transition-shadow p-3 md:p-4 h-full min-h-[120px] flex flex-col">
      <div className="flex items-start gap-3 mb-2 md:mb-3">
        <Link to={`/topics/${topic.id}`} className="flex-shrink-0">
          {previewImage ? (
            <div className="relative w-12 h-12 md:w-16 md:h-16 rounded overflow-hidden bg-gray-100">
              <img
                src={getProxyImageUrl(previewImage)}
                alt={display.title}
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.currentTarget.style.display = 'none'
                  e.currentTarget.parentElement!.className = `relative w-12 h-12 md:w-16 md:h-16 rounded overflow-hidden bg-gradient-to-br ${gradientClasses[topic.category]}`
                }}
              />
            </div>
          ) : (
            <div className={`w-12 h-12 md:w-16 md:h-16 rounded bg-gradient-to-br ${gradientClasses[topic.category]}`} />
          )}
        </Link>

        <div className="flex-1 min-w-0">
          <Link to={`/topics/${topic.id}`} className="block">
            {standardLoading || showTextPending ? (
              <TopicTextSkeleton />
            ) : (
              <div className={textFadeClass}>
                <h3
                  data-topic-read={hasOpened ? 'true' : 'false'}
                  className={`font-bold text-sm md:text-base lg:text-lg line-clamp-2 leading-tight ${
                    hasOpened ? 'text-gray-400 dark:text-gray-500' : 'text-gray-900 dark:text-white'
                  }`}
                >
                  {display.title}
                </h3>
              </div>
            )}
          </Link>
          {showTextPending && (
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{t('topics.translating')}</p>
          )}
          {!standardLoading && !showTextPending && originalLine && (
            <p className={`text-[11px] text-gray-500 dark:text-gray-400 italic line-clamp-1 mt-0.5 ${textFadeClass}`}>
              {t('topics.originalTitlePrefix')} {originalLine}
            </p>
          )}
          {dateLabel && (
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{dateLabel}</p>
          )}
        </div>
      </div>

      <Link to={`/topics/${topic.id}`} className="flex-1 flex flex-col justify-between min-h-0">
        <div className="flex-1 min-h-0">
          <div>
            {standardLoading || showTextPending ? (
              <TopicTextSkeleton />
            ) : (
              <p className={`text-xs md:text-sm line-clamp-2 leading-snug ${textFadeClass} ${
                hasOpened ? 'text-gray-400 dark:text-gray-500' : 'text-gray-600 dark:text-gray-300'
              }`}>
                {display.description ? (
                  display.description
                ) : (
                  <span className="text-gray-400 italic">{t('topics.noContent')}</span>
                )}
              </p>
            )}
          </div>
        </div>

        <span className="text-primary hover:text-primary-dark font-medium text-xs md:text-sm mt-3 self-start">
          {t('common.viewDetails')} →
        </span>
      </Link>

      {showTranslateFooter && (
        <div className="flex items-center justify-end gap-2 mt-2 pt-2 border-t border-gray-100 dark:border-gray-700">
          {showCacheLabel && (
            <span className="text-[10px] text-green-700 dark:text-green-400 bg-green-50 dark:bg-green-900/20 px-2 py-0.5 rounded">
              {t('topics.translatedCached')}
            </span>
          )}
          {showKolButton && (
            <TopicTranslateDisplayButton
              topic={topic}
              translationType="kol_style"
              testId={kolStyleTestId || `btn-topic-card-kol-style-${topic.id}`}
              onTranslated={handleKolTranslated}
            />
          )}
        </div>
      )}
    </div>
  )
}
