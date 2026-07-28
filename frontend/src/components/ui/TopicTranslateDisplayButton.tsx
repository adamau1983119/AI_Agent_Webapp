import { useState } from 'react'
import { Languages, Sparkles } from 'lucide-react'
import { useTranslation } from '@/i18n'
import { topicsAPI } from '@/api/topics'
import type { Topic } from '@/types'
import toast from 'react-hot-toast'

export type TopicTranslationType = 'standard_translation' | 'kol_style'

export interface TopicDisplayOverride {
  title: string
  description?: string | null
  cached?: boolean
  translationType?: TopicTranslationType
}

interface TopicTranslateDisplayButtonProps {
  topic: Topic
  className?: string
  testId?: string
  translationType?: TopicTranslationType
  onTranslated?: (override: TopicDisplayOverride) => void
}

export default function TopicTranslateDisplayButton({
  topic,
  className = '',
  testId,
  translationType = 'standard_translation',
  onTranslated,
}: TopicTranslateDisplayButtonProps) {
  const { t, language } = useTranslation()
  const [loading, setLoading] = useState(false)
  const isKol = translationType === 'kol_style'
  const defaultTestId = isKol ? 'btn-topic-card-kol-style' : 'btn-topic-card-translate'

  const handleClick = async (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (loading) return

    setLoading(true)
    try {
      const res = await topicsAPI.translateDisplay(topic.id, language, translationType)
      onTranslated?.({
        title: res.title,
        description: res.description,
        cached: res.cached,
        translationType,
      })
      if (!res.cached) {
        toast.success(isKol ? t('topics.kolStyleDone') : t('topics.translateDisplayDone'))
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : t('topics.translateDisplayFailed')
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  const defaultClassName = isKol
    ? 'inline-flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium text-amber-800 dark:text-amber-200 bg-amber-50 dark:bg-amber-900/25 border border-amber-200 dark:border-amber-700 rounded-lg hover:bg-amber-100 dark:hover:bg-amber-900/40 disabled:opacity-50 min-h-[36px]'
    : 'inline-flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium text-purple-700 dark:text-purple-300 bg-purple-50 dark:bg-purple-900/25 border border-purple-200 dark:border-purple-800 rounded-lg hover:bg-purple-100 dark:hover:bg-purple-900/40 disabled:opacity-50 min-h-[36px]'

  const Icon = isKol ? Sparkles : Languages
  const label = loading
    ? t('topics.translating')
    : isKol
      ? t('topics.translateKolStyle')
      : t('topics.translateToCurrentLanguage')

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={loading}
      data-testid={testId || defaultTestId}
      className={className || defaultClassName}
    >
      <Icon className="w-3.5 h-3.5 shrink-0" aria-hidden />
      {label}
    </button>
  )
}
