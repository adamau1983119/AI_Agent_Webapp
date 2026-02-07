/**
 * 內容生成設定面板
 * 4.2: 風格選擇 UI
 * 4.3: 輸出格式選擇 UI
 */
import { useState } from 'react'
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

const ARTICLE_LENGTHS = [300, 500, 800, 1200]
const SCRIPT_DURATIONS = [15, 30, 60, 90]

export default function ContentGenerationPanel({
  onGenerate,
  isGenerating,
  hasExistingContent = false,
}: ContentGenerationPanelProps) {
  const { t } = useTranslation()
  const [style, setStyle] = useState<ContentStyle>('professional')
  const [outputFormat, setOutputFormat] = useState<OutputFormat>('both')
  const [articleLength, setArticleLength] = useState(500)
  const [scriptDuration, setScriptDuration] = useState(30)
  const [isExpanded, setIsExpanded] = useState(!hasExistingContent)

  const handleGenerate = () => {
    onGenerate({
      style,
      outputFormat,
      articleLength,
      scriptDuration,
    })
  }

  return (
    <div
      className="bg-gradient-to-br from-purple-50 to-indigo-50 dark:from-gray-800 dark:to-gray-750 rounded-xl border border-purple-200 dark:border-purple-800/50 overflow-hidden"
      data-testid="content-generation-panel"
    >
      {/* 標題區域 */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        data-testid="btn-content-gen-toggle"
        className="w-full flex items-center justify-between p-4 sm:p-5 hover:bg-purple-100/50 dark:hover:bg-gray-700/50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div className="text-left">
            <h3 className="font-semibold text-gray-900 dark:text-white text-sm sm:text-base">
              {t('content.generateSettings')}
            </h3>
            <p className="text-xs text-gray-500 dark:text-gray-400 hidden sm:block">
              {t('content.generateSettingsDesc')}
            </p>
          </div>
        </div>
        <svg
          className={`w-5 h-5 text-gray-400 transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* 展開的設定面板 */}
      {isExpanded && (
        <div className="px-4 pb-4 sm:px-5 sm:pb-5 space-y-5">
          {/* 4.2: 風格選擇 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('content.styleSelection')}
            </label>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">
              {t('content.styleSelectionDesc')}
            </p>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
              {STYLE_OPTIONS.map((option) => (
                <button
                  key={option.value}
                  onClick={() => setStyle(option.value)}
                  data-testid={`btn-content-style-${option.value}`}
                  className={`relative flex flex-col items-center gap-1.5 p-3 sm:p-4 rounded-xl border-2 transition-all duration-200 min-h-[44px] ${
                    style === option.value
                      ? 'border-purple-500 dark:border-purple-400 bg-purple-100 dark:bg-purple-900/40 ring-1 ring-purple-300 dark:ring-purple-700 shadow-sm'
                      : 'border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 hover:border-purple-300 dark:hover:border-purple-600 hover:shadow-sm'
                  }`}
                >
                  {style === option.value && (
                    <div className="absolute top-1.5 right-1.5">
                      <svg className="w-4 h-4 text-purple-500 dark:text-purple-400" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                    </div>
                  )}
                  <span className="text-xl sm:text-2xl">{option.icon}</span>
                  <span className={`text-xs sm:text-sm font-medium ${
                    style === option.value
                      ? 'text-purple-700 dark:text-purple-300'
                      : 'text-gray-700 dark:text-gray-300'
                  }`}>
                    {t(`content.style.${option.value}` as any)}
                  </span>
                  <span className="text-[10px] sm:text-xs text-gray-500 dark:text-gray-400 text-center line-clamp-2 hidden sm:block">
                    {t(`content.style.${option.value}.desc` as any)}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* 4.3: 輸出格式選擇 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('content.outputFormat')}
            </label>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">
              {t('content.outputFormatDesc')}
            </p>
            <div className="grid grid-cols-3 gap-2 sm:gap-3">
              {FORMAT_OPTIONS.map((option) => (
                <button
                  key={option.value}
                  onClick={() => setOutputFormat(option.value)}
                  data-testid={`btn-content-format-${option.value}`}
                  className={`relative flex flex-col items-center gap-2 p-3 sm:p-4 rounded-xl border-2 transition-all duration-200 min-h-[44px] ${
                    outputFormat === option.value
                      ? 'border-indigo-500 dark:border-indigo-400 bg-indigo-100 dark:bg-indigo-900/40 ring-1 ring-indigo-300 dark:ring-indigo-700 shadow-sm'
                      : 'border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 hover:border-indigo-300 dark:hover:border-indigo-600 hover:shadow-sm'
                  }`}
                >
                  {outputFormat === option.value && (
                    <div className="absolute top-1.5 right-1.5">
                      <svg className="w-4 h-4 text-indigo-500 dark:text-indigo-400" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                    </div>
                  )}
                  <span className="text-xl sm:text-2xl">{option.icon}</span>
                  <span className={`text-xs sm:text-sm font-medium ${
                    outputFormat === option.value
                      ? 'text-indigo-700 dark:text-indigo-300'
                      : 'text-gray-700 dark:text-gray-300'
                  }`}>
                    {t(`content.format.${option.value}` as any)}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* 文章長度設定（當輸出格式包含文章時顯示） */}
          {(outputFormat === 'article' || outputFormat === 'both') && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('content.articleLength')}
              </label>
              <div className="flex flex-wrap gap-2">
                {ARTICLE_LENGTHS.map((len) => (
                  <button
                    key={len}
                    onClick={() => setArticleLength(len)}
                    data-testid={`btn-content-article-length-${len}`}
                    className={`px-3 py-2 text-xs sm:text-sm rounded-lg border transition-all min-h-[44px] ${
                      articleLength === len
                        ? 'border-purple-500 dark:border-purple-400 bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300 font-medium'
                        : 'border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:border-purple-300'
                    }`}
                  >
                    {t('content.articleLengthWords', { count: String(len) })}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* 腳本時長設定（當輸出格式包含腳本時顯示） */}
          {(outputFormat === 'script' || outputFormat === 'both') && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('content.scriptDuration')}
              </label>
              <div className="flex flex-wrap gap-2">
                {SCRIPT_DURATIONS.map((dur) => (
                  <button
                    key={dur}
                    onClick={() => setScriptDuration(dur)}
                    data-testid={`btn-content-script-duration-${dur}`}
                    className={`px-3 py-2 text-xs sm:text-sm rounded-lg border transition-all min-h-[44px] ${
                      scriptDuration === dur
                        ? 'border-purple-500 dark:border-purple-400 bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300 font-medium'
                        : 'border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:border-purple-300'
                    }`}
                  >
                    {t('content.scriptDurationSeconds', { count: String(dur) })}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* 目前選擇摘要 */}
          <div className="bg-white/70 dark:bg-gray-700/50 rounded-lg p-3 sm:p-4 border border-gray-200/50 dark:border-gray-600/50">
            <div className="flex flex-wrap gap-2 text-xs sm:text-sm text-gray-600 dark:text-gray-400">
              <span className="flex items-center gap-1">
                🎨 {t(`content.style.${style}` as any)}
              </span>
              <span className="text-gray-300 dark:text-gray-600">|</span>
              <span className="flex items-center gap-1">
                📋 {t(`content.format.${outputFormat}` as any)}
              </span>
              {(outputFormat === 'article' || outputFormat === 'both') && (
                <>
                  <span className="text-gray-300 dark:text-gray-600">|</span>
                  <span className="flex items-center gap-1">
                    📏 {t('content.articleLengthWords', { count: String(articleLength) })}
                  </span>
                </>
              )}
              {(outputFormat === 'script' || outputFormat === 'both') && (
                <>
                  <span className="text-gray-300 dark:text-gray-600">|</span>
                  <span className="flex items-center gap-1">
                    ⏱️ {t('content.scriptDurationSeconds', { count: String(scriptDuration) })}
                  </span>
                </>
              )}
            </div>
          </div>

          {/* 生成按鈕 */}
          <button
            onClick={handleGenerate}
            disabled={isGenerating}
            data-testid="btn-content-gen-start"
            className="w-full flex items-center justify-center gap-2 px-6 py-3 sm:py-4 text-sm sm:text-base font-semibold text-white bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-lg min-h-[48px]"
          >
            {isGenerating ? (
              <>
                <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                <span>{hasExistingContent ? t('common.regenerating') : t('common.generating')}</span>
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <span>{hasExistingContent ? t('common.regenerate') : t('content.startGenerate')}</span>
              </>
            )}
          </button>
        </div>
      )}
    </div>
  )
}

