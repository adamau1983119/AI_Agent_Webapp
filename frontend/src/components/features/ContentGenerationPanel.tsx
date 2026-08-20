/**
 * 內容生成設定面板
 * 4.2: 風格選擇 UI
 * 4.3: 輸出格式選擇 UI
 */
import { useState, type ReactNode } from 'react'
import { useTranslation } from '@/i18n'

export type ContentStyle = 'professional' | 'casual' | 'humorous' | 'storytelling' | 'educational'
export type OutputFormat = 'article' | 'script' | 'both'

export interface GenerationSettings {
  style: ContentStyle
  outputFormat: OutputFormat
  articleLength: number
  scriptDuration: number
}

interface ContentGenerationPanelProps {
  onGenerate: (settings: GenerationSettings) => void
  isGenerating: boolean
  hasExistingContent?: boolean
}

const STYLE_OPTIONS: { value: ContentStyle; icon: string }[] = [
  { value: 'professional', icon: '💼' },
  { value: 'casual', icon: '😊' },
  { value: 'humorous', icon: '😂' },
  { value: 'storytelling', icon: '📖' },
  { value: 'educational', icon: '🎓' },
]

const FORMAT_OPTIONS: { value: OutputFormat; icon: string }[] = [
  { value: 'article', icon: '📝' },
  { value: 'script', icon: '🎬' },
  { value: 'both', icon: '📦' },
]

const ARTICLE_LENGTH_OPTIONS = [
  { value: 150, key: 'content.wordCount150' },
  { value: 300, key: 'content.wordCount300', isDefault: true },
  { value: 500, key: 'content.wordCount500' },
] as const

/** 選項卡共用：防止 flex 子項撐破邊框、多語長文案溢出 */
const CARD_BASE =
  'relative flex w-full min-w-0 flex-col items-stretch gap-1 overflow-hidden rounded-xl border-2 p-2.5 sm:p-3 transition-all duration-200 min-h-[44px]'
const CARD_LABEL =
  'block w-full min-w-0 overflow-hidden text-center text-xs sm:text-sm font-medium leading-tight line-clamp-2 break-words'
const CARD_DESC =
  'block w-full min-w-0 overflow-hidden text-center text-[10px] sm:text-xs leading-snug text-gray-500 dark:text-gray-400 line-clamp-3 break-words min-h-[2.75rem] sm:min-h-[3rem]'
const PILL_LABEL =
  'block w-full min-w-0 overflow-hidden text-center text-xs sm:text-sm leading-tight line-clamp-2 break-words'

type CardTone = 'purple' | 'indigo'

function SelectionOptionCard({
  selected,
  onClick,
  testId,
  title,
  icon,
  label,
  description,
  tone,
}: {
  selected: boolean
  onClick: () => void
  testId: string
  title: string
  icon: ReactNode
  label: string
  description?: string
  tone: CardTone
}) {
  const selectedRing =
    tone === 'purple'
      ? 'border-purple-500 dark:border-purple-400 bg-purple-100 dark:bg-purple-900/40 ring-1 ring-purple-300 dark:ring-purple-700'
      : 'border-indigo-500 dark:border-indigo-400 bg-indigo-100 dark:bg-indigo-900/40 ring-1 ring-indigo-300 dark:ring-indigo-700'
  const selectedText =
    tone === 'purple'
      ? 'text-purple-700 dark:text-purple-300'
      : 'text-indigo-700 dark:text-indigo-300'
  const checkColor = tone === 'purple' ? 'text-purple-500 dark:text-purple-400' : 'text-indigo-500 dark:text-indigo-400'
  const idleBorder =
    tone === 'purple'
      ? 'border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 hover:border-purple-300 dark:hover:border-purple-600'
      : 'border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 hover:border-indigo-300 dark:hover:border-indigo-600'

  return (
    <button
      type="button"
      onClick={onClick}
      title={title}
      data-testid={testId}
      className={`${CARD_BASE} ${selected ? `pr-7 shadow-sm ${selectedRing}` : `${idleBorder} hover:shadow-sm`}`}
    >
      {selected && (
        <div className="pointer-events-none absolute top-1.5 right-1.5" aria-hidden>
          <svg className={`w-4 h-4 ${checkColor}`} fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clipRule="evenodd"
            />
          </svg>
        </div>
      )}
      <span className="text-center text-xl sm:text-2xl leading-none shrink-0">{icon}</span>
      <span className={`${CARD_LABEL} ${selected ? selectedText : 'text-gray-700 dark:text-gray-300'}`}>
        {label}
      </span>
      {description ? <span className={CARD_DESC}>{description}</span> : null}
    </button>
  )
}

export default function ContentGenerationPanel({
  onGenerate,
  isGenerating,
  hasExistingContent = false,
}: ContentGenerationPanelProps) {
  const { t } = useTranslation()
  const [style, setStyle] = useState<ContentStyle>('professional')
  const [outputFormat] = useState<OutputFormat>('article')
  const [articleLength, setArticleLength] = useState(300)
  const [isExpanded, setIsExpanded] = useState(!hasExistingContent)

  const handleGenerate = () => {
    onGenerate({
      style,
      outputFormat,
      articleLength,
      scriptDuration: 30,
    })
  }

  return (
    <div
      className="bg-gradient-to-br from-purple-50 to-indigo-50 dark:from-gray-800 dark:to-gray-750 rounded-xl border border-purple-200 dark:border-purple-800/50 overflow-hidden"
      data-testid="content-generation-panel"
    >
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        data-testid="btn-content-gen-toggle"
        className="w-full flex items-center justify-between gap-2 p-4 sm:p-5 hover:bg-purple-100/50 dark:hover:bg-gray-700/50 transition-colors min-w-0"
      >
        <div className="flex min-w-0 flex-1 items-center gap-3">
          <div className="w-10 h-10 shrink-0 rounded-lg bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div className="min-w-0 flex-1 text-left">
            <h3 className="font-semibold text-gray-900 dark:text-white text-sm sm:text-base line-clamp-2 break-words">
              {t('content.generateSettings')}
            </h3>
            <p className="text-xs text-gray-500 dark:text-gray-400 hidden sm:block line-clamp-2 break-words">
              {t('content.generateSettingsDesc')}
            </p>
          </div>
        </div>
        <svg
          className={`w-5 h-5 shrink-0 text-gray-400 transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isExpanded && (
        <div className="px-4 pb-4 sm:px-5 sm:pb-5 space-y-5 min-w-0">
          <div className="min-w-0">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('content.styleSelection')}
            </label>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-3 line-clamp-2 break-words">
              {t('content.styleSelectionDesc')}
            </p>
            <div className="grid grid-cols-2 md:grid-cols-3 2xl:grid-cols-5 gap-2 sm:gap-3">
              {STYLE_OPTIONS.map((option) => {
                const styleLabel = t(`content.style.${option.value}` as any)
                const styleDesc = t(`content.style.${option.value}.desc` as any)
                return (
                  <SelectionOptionCard
                    key={option.value}
                    selected={style === option.value}
                    onClick={() => setStyle(option.value)}
                    testId={`btn-content-style-${option.value}`}
                    title={`${styleLabel} — ${styleDesc}`}
                    icon={option.icon}
                    label={styleLabel}
                    description={styleDesc}
                    tone="purple"
                  />
                )
              })}
            </div>
          </div>

          <div className="min-w-0">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('content.articleLength')}
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
              {ARTICLE_LENGTH_OPTIONS.map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => setArticleLength(opt.value)}
                  title={t(opt.key)}
                  data-testid={`btn-content-article-length-${opt.value}`}
                  className={`min-w-0 overflow-hidden px-3 py-2.5 rounded-lg border transition-all min-h-[44px] touch-manipulation ${
                    articleLength === opt.value
                      ? 'border-purple-500 dark:border-purple-400 bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300 font-medium ring-1 ring-purple-300 dark:ring-purple-700'
                      : 'border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:border-purple-300'
                  }`}
                >
                  <span className={PILL_LABEL}>
                    {t(opt.key)}
                  </span>
                </button>
              ))}
            </div>
          </div>

          <div className="bg-white/70 dark:bg-gray-700/50 rounded-lg p-3 sm:p-4 border border-gray-200/50 dark:border-gray-600/50 min-w-0 overflow-hidden">
            <div className="flex flex-wrap gap-x-2 gap-y-1 text-xs sm:text-sm text-gray-600 dark:text-gray-400 min-w-0">
              <span className="inline-flex min-w-0 max-w-full items-center gap-1 overflow-hidden">
                <span className="shrink-0" aria-hidden>🎨</span>
                <span className="line-clamp-1 break-words">{t(`content.style.${style}` as any)}</span>
              </span>
              <span className="text-gray-300 dark:text-gray-600 shrink-0" aria-hidden>|</span>
              <span className="inline-flex min-w-0 max-w-full items-center gap-1 overflow-hidden">
                <span className="shrink-0" aria-hidden>📏</span>
                <span className="line-clamp-1 break-words">
                  {t('content.articleLengthWords', { count: String(articleLength) })}
                </span>
              </span>
            </div>
          </div>

          <button
            type="button"
            onClick={handleGenerate}
            disabled={isGenerating}
            data-testid="btn-content-gen-start"
            className="w-full min-w-0 overflow-hidden flex items-center justify-center gap-2 px-4 py-3 sm:py-4 text-sm sm:text-base font-semibold text-white bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-lg min-h-[48px]"
          >
            {isGenerating ? (
              <>
                <svg className="animate-spin w-5 h-5 shrink-0" fill="none" viewBox="0 0 24 24" aria-hidden>
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                <span className="line-clamp-2 break-words text-center">
                  {hasExistingContent ? t('common.regenerating') : t('common.generating')}
                </span>
              </>
            ) : (
              <>
                <svg className="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <span className="line-clamp-2 break-words text-center">
                  {hasExistingContent ? t('content.regenerateArticle') : t('content.generateArticle')}
                </span>
              </>
            )}
          </button>
        </div>
      )}
    </div>
  )
}
