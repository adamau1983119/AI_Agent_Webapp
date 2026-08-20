import { useCallback, useEffect, useMemo, useState } from 'react'
import { Copy, Sparkles, RefreshCw } from 'lucide-react'
import { useTranslation } from '@/i18n'
import { alterEgoApi, type AlterEgoPlatform } from '@/api/alterEgo'
import { copyToClipboard } from '@/utils/copyToClipboard'
import { showError, showSuccess } from '@/utils/toast'
import { normalizeUiLanguage, titleScriptMismatch } from '@/lib/topicLanguages'
import type { Content, Image, Topic } from '@/types'

type Props = {
  displayTitle: string
  category: Topic['category']
  content: Content | null
  images: Image[]
  previewImages?: string[]
  topicId?: string
  contentTranslating?: boolean
  summaryFlash?: string
}

const PLATFORMS: AlterEgoPlatform[] = ['facebook', 'threads', 'x']

function parseHashtagLine(raw: string): string[] {
  return raw
    .split(',')
    .map((tag) => tag.trim())
    .filter(Boolean)
    .map((tag) => (tag.startsWith('#') ? tag : `#${tag}`))
}

function buildTitleOptions(base: string, t: (k: string, p?: Record<string, string>) => string): string[] {
  if (!base.trim()) return []
  return [
    base,
    t('postKit.titleHook.curiosity', { title: base }),
    t('postKit.titleHook.benefit', { title: base }),
  ]
}

export default function PostKitPanel({
  displayTitle,
  category,
  content,
  images,
  previewImages = [],
  topicId,
  contentTranslating = false,
  summaryFlash = '',
}: Props) {
  const { t, language } = useTranslation()
  const [selectedTitleIdx, setSelectedTitleIdx] = useState(0)
  const [platform, setPlatform] = useState<AlterEgoPlatform>('facebook')
  const [hasDna, setHasDna] = useState(false)
  const [platformCopy, setPlatformCopy] = useState('')
  const [previewLoading, setPreviewLoading] = useState(false)

  const titleOptions = useMemo(
    () => buildTitleOptions(displayTitle, t),
    [displayTitle, t]
  )

  const hashtags = useMemo(() => {
    const key = `postKit.hashtagTags.${category}` as 'postKit.hashtagTags.fashion'
    return parseHashtagLine(t(key))
  }, [category, t, language])

  const imageUrls = useMemo(() => {
    const fromGallery = images.map((img) => img.url).filter(Boolean)
    const merged = [...fromGallery, ...previewImages.filter(Boolean)]
    return [...new Set(merged)]
  }, [images, previewImages])

  const visualPrompt = useMemo(
    () =>
      t('postKit.visualPromptTemplate', {
        title: displayTitle,
        category: t(`channels.category.${category}` as 'channels.category.fashion'),
        platform: t(`alterEgo.platform.${platform}`),
      }),
    [t, displayTitle, category, platform]
  )

  const uiLang = normalizeUiLanguage(language)

  const textMatchesUi = useCallback(
    (text: string) => !titleScriptMismatch(text.slice(0, 800), uiLang),
    [uiLang]
  )

  const bodyText = content?.article?.trim() || ''
  const scriptText = content?.script?.trim() || ''

  const contentLocaleReady = useMemo(() => {
    if (contentTranslating) return false
    const articleOk = !bodyText || textMatchesUi(bodyText)
    const scriptOk = !scriptText || textMatchesUi(scriptText)
    return articleOk && scriptOk
  }, [bodyText, scriptText, contentTranslating, textMatchesUi])

  const previewMatchesUi = Boolean(platformCopy.trim() && textMatchesUi(platformCopy))

  const displayBody = useMemo(() => {
    if (hasDna && previewMatchesUi) {
      return platformCopy
    }
    if (contentLocaleReady && bodyText && textMatchesUi(bodyText)) {
      return bodyText
    }
    return ''
  }, [hasDna, previewMatchesUi, platformCopy, contentLocaleReady, bodyText, textMatchesUi])

  const displayScript = useMemo(() => {
    if (!contentLocaleReady || !scriptText || !textMatchesUi(scriptText)) return ''
    return scriptText
  }, [contentLocaleReady, scriptText, textMatchesUi])

  const preparingContent = Boolean(
    contentTranslating ||
      previewLoading ||
      ((bodyText || scriptText) && !displayBody && !displayScript)
  )

  // 嚴格按需生成：只有用戶主動點擊按鈕時才呼叫 API
  const handleGeneratePlatformPreview = useCallback(async () => {
    if (!hasDna) return
    setPreviewLoading(true)
    try {
      const hint = displayTitle.trim().slice(0, 200)
      const preview = await alterEgoApi.preview(
        platform,
        hint,
        uiLang,
        summaryFlash,
        bodyText
      )
      const text = preview.preview_text?.trim() || ''
      setPlatformCopy(text && textMatchesUi(text) ? text : '')
    } catch {
      setPlatformCopy('')
      showError(t('common.failed'))
    } finally {
      setPreviewLoading(false)
    }
  }, [hasDna, platform, displayTitle, uiLang, summaryFlash, bodyText, textMatchesUi, t])

  // 僅查詢用戶是否擁有 DNA 狀態，絕不自動偷跑生成 preview
  useEffect(() => {
    alterEgoApi
      .getStatus()
      .then((s) => setHasDna(s.has_dna && s.dna_status === 'active'))
      .catch(() => setHasDna(false))
  }, [])

  // 當切換平台時重置當前平台的快取文案
  useEffect(() => {
    setPlatformCopy('')
  }, [platform])

  const handleCopy = async (text: string) => {
    const ok = await copyToClipboard(text)
    if (ok) {
      showSuccess(t('postKit.copied'))
    } else {
      showError(t('postKit.copyFailed'))
    }
  }

  const handleAdoptCopy = async () => {
    const text = displayBody
    if (!text.trim()) return
    await handleCopy(text)
    try {
      await alterEgoApi.adoptCopy({
        platform,
        topic_id: topicId,
        preview_text: text,
      })
    } catch {
      /* audit best-effort */
    }
  }

  const selectedTitle = titleOptions[selectedTitleIdx] || displayTitle
  const hashtagLine = hashtags.join(' ')

  const copyAllText = [selectedTitle, displayBody, hashtagLine].filter(Boolean).join('\n\n')

  return (
    <section
      className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-800 p-5 sm:p-6 space-y-6"
      data-testid="section-postkit"
      aria-label={t('postKit.sectionTitle')}
    >
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-4 border-b border-gray-100 dark:border-gray-700/60">
        <div>
          <h2 className="font-display text-xl font-bold text-gray-900 dark:text-white">
            {t('postKit.sectionTitle')}
          </h2>
          <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mt-1 font-sans">
            {t('postKit.hint.pasteOnPlatform')}
          </p>
        </div>
        <button
          type="button"
          data-testid="btn-postkit-copy-all"
          disabled={!copyAllText}
          onClick={() => handleCopy(copyAllText)}
          className="min-h-[44px] px-4 py-2 text-sm font-medium text-primary bg-primary/10 hover:bg-primary/20 rounded-xl transition-colors disabled:opacity-50 touch-manipulation"
        >
          {t('postKit.copyAll')}
        </button>
      </div>

      <div className="p-4 sm:p-5 rounded-xl border border-gray-100 dark:border-gray-700/60 bg-gray-50/50 dark:bg-gray-750/30 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <h3 className="font-sans text-sm font-semibold text-gray-800 dark:text-gray-200">
            {t('postKit.platformSwitch')}
          </h3>
          <div className="flex gap-2 flex-wrap">
            {PLATFORMS.map((p) => (
              <button
                key={p}
                type="button"
                data-testid={`btn-postkit-platform-${p}`}
                onClick={() => setPlatform(p)}
                className={`px-3.5 py-1.5 text-xs font-medium uppercase min-h-[38px] rounded-lg transition-all touch-manipulation ${
                  platform === p
                    ? 'bg-primary text-white shadow-sm'
                    : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                {t(`alterEgo.platform.${p}`)}
              </button>
            ))}
          </div>
        </div>

        {hasDna && (
          <div className="p-3.5 bg-white dark:bg-gray-800 rounded-xl border border-purple-100 dark:border-purple-900/40 space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h4 className="text-xs sm:text-sm font-semibold text-purple-900 dark:text-purple-300 flex items-center gap-1.5">
                <Sparkles className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                <span>{t('postKit.platformCopy', { platform: t(`alterEgo.platform.${platform}`) })}</span>
              </h4>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  data-testid="btn-postkit-generate-platform-copy"
                  disabled={previewLoading || !bodyText}
                  onClick={handleGeneratePlatformPreview}
                  className="min-h-[38px] px-3 py-1.5 text-xs font-medium text-purple-700 dark:text-purple-300 bg-purple-50 dark:bg-purple-950/40 border border-purple-200 dark:border-purple-800 rounded-lg hover:bg-purple-100 disabled:opacity-50 inline-flex items-center gap-1.5 touch-manipulation"
                  title={!bodyText ? t('postKit.generateArticleFirst') : ''}
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${previewLoading ? 'animate-spin' : ''}`} />
                  <span>{t('postKit.generatePlatformCopy')}</span>
                </button>
                {displayBody && (
                  <button
                    type="button"
                    data-testid="btn-postkit-adopt-copy"
                    disabled={!displayBody || previewLoading || preparingContent}
                    onClick={handleAdoptCopy}
                    className="min-h-[38px] px-3 py-1.5 text-xs font-medium text-white bg-primary rounded-lg hover:bg-primary-dark disabled:opacity-50 touch-manipulation"
                  >
                    {t('postKit.adoptCopy')}
                  </button>
                )}
              </div>
            </div>

            <p
              data-testid="section-postkit-platform-copy"
              className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-line max-h-48 overflow-y-auto font-sans leading-relaxed"
            >
              {preparingContent ? (
                <span className="text-gray-400 italic">{t('postKit.preparingContent')}</span>
              ) : displayBody ? (
                displayBody
              ) : (
                <span className="text-gray-400 italic">
                  {bodyText ? t('postKit.generatePlatformCopy') : t('postKit.generateArticleFirst')}
                </span>
              )}
            </p>
          </div>
        )}

        <div>
          <div className="flex justify-between items-start gap-2 mb-1.5">
            <h4 className="text-xs sm:text-sm font-medium text-gray-700 dark:text-gray-300">
              {t('postKit.visualPrompt')}
            </h4>
            <button
              type="button"
              data-testid="btn-postkit-copy-visual-prompt"
              disabled={!visualPrompt}
              aria-label={t('postKit.visualPrompt')}
              onClick={() => handleCopy(visualPrompt)}
              className="min-h-[36px] px-2.5 py-1 inline-flex items-center gap-1 text-xs text-gray-600 dark:text-gray-300 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:bg-gray-100"
            >
              <Copy className="w-3.5 h-3.5" />
              <span>{t('postKit.copy')}</span>
            </button>
          </div>
          <p
            data-testid="section-postkit-visual-prompt"
            className="text-xs text-gray-500 dark:text-gray-400 whitespace-pre-line font-sans"
          >
            {visualPrompt}
          </p>
        </div>
      </div>

      <div className="space-y-6">
        <div>
          <h3 className="font-sans text-sm font-semibold text-gray-800 dark:text-gray-200 mb-3">
            {t('postKit.titleOptions')}
          </h3>
          <div className="space-y-2">
            {titleOptions.map((opt, idx) => (
              <div
                key={idx}
                className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-3 rounded-xl border border-gray-100 dark:border-gray-700/60 bg-white dark:bg-gray-800 hover:border-gray-200 transition-all"
              >
                <label className="flex items-start gap-2.5 flex-1 cursor-pointer min-h-[44px]">
                  <input
                    type="radio"
                    name="postkit-title"
                    checked={selectedTitleIdx === idx}
                    onChange={() => setSelectedTitleIdx(idx)}
                    className="mt-1"
                    data-testid={`input-postkit-title-${idx + 1}`}
                  />
                  <span className="text-sm text-gray-800 dark:text-gray-200 break-words font-sans">
                    <span className="text-xs text-gray-400 block mb-0.5">
                      {t('postKit.suggested', { n: String(idx + 1) })}
                    </span>
                    {opt}
                  </span>
                </label>
                <button
                  type="button"
                  data-testid={`btn-postkit-copy-title-${idx + 1}`}
                  aria-label={`${t('postKit.copy')} ${t('postKit.titleOptions')} ${idx + 1}`}
                  onClick={() => handleCopy(opt)}
                  className="min-h-[38px] px-2.5 py-1.5 inline-flex items-center gap-1 rounded-lg bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 text-xs font-medium text-gray-700 dark:text-gray-200 touch-manipulation shrink-0"
                >
                  <Copy className="w-3.5 h-3.5" />
                  <span>{t('postKit.copy')}</span>
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl border border-gray-100 dark:border-gray-700/60 bg-white dark:bg-gray-800 space-y-2">
            <div className="flex justify-between items-start gap-2">
              <h3 className="font-sans text-sm font-semibold text-gray-800 dark:text-gray-200">
                {t('postKit.body')}
              </h3>
              <button
                type="button"
                data-testid="btn-postkit-copy-body"
                disabled={!displayBody}
                onClick={() => handleCopy(displayBody)}
                className="min-h-[36px] px-2.5 py-1 inline-flex items-center gap-1 text-xs text-gray-600 dark:text-gray-300 rounded-lg bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 disabled:opacity-50"
              >
                <Copy className="w-3.5 h-3.5" />
                <span>{t('postKit.copy')}</span>
              </button>
            </div>
            <p
              data-testid="section-postkit-body"
              className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-line max-h-48 overflow-y-auto font-sans leading-relaxed"
            >
              {preparingContent ? (
                <span className="text-gray-400 italic">{t('postKit.preparingContent')}</span>
              ) : displayBody ? (
                displayBody
              ) : (
                <span className="text-gray-400 italic">{t('postKit.generateArticleFirst')}</span>
              )}
            </p>
          </div>

          <div className="p-4 rounded-xl border border-gray-100 dark:border-gray-700/60 bg-white dark:bg-gray-800 space-y-2">
            <div className="flex justify-between items-start gap-2">
              <h3 className="font-sans text-sm font-semibold text-gray-800 dark:text-gray-200">
                {t('postKit.hashtags')}
              </h3>
              <button
                type="button"
                data-testid="btn-postkit-copy-hashtags"
                disabled={!hashtagLine}
                onClick={() => handleCopy(hashtagLine)}
                className="min-h-[36px] px-2.5 py-1 inline-flex items-center gap-1 text-xs text-gray-600 dark:text-gray-300 rounded-lg bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 disabled:opacity-50"
              >
                <Copy className="w-3.5 h-3.5" />
                <span>{t('postKit.copy')}</span>
              </button>
            </div>
            <div className="flex flex-wrap gap-1.5 pt-1">
              {hashtags.map((tag, i) => (
                <span
                  key={i}
                  className="px-2.5 py-1 text-xs rounded-lg bg-primary/10 text-primary font-sans"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>

        <div>
          <div className="flex justify-between items-center mb-3">
            <h3 className="font-sans text-sm font-semibold text-gray-800 dark:text-gray-200">
              {t('postKit.photos')}（{imageUrls.length}）
            </h3>
          </div>
          {imageUrls.length === 0 ? (
            <p className="text-xs text-gray-500 font-sans">{t('postKit.noPhotos')}</p>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {imageUrls.map((url, i) => (
                <div key={i} className="relative group rounded-xl overflow-hidden border border-gray-100 dark:border-gray-700 aspect-video bg-gray-100 dark:bg-gray-900">
                  <img
                    src={url}
                    alt=""
                    className="w-full h-full object-cover"
                    loading="lazy"
                  />
                  <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <button
                      type="button"
                      data-testid={`btn-postkit-copy-photo-${i + 1}`}
                      onClick={() => handleCopy(url)}
                      className="px-2.5 py-1.5 bg-white/90 text-gray-800 text-xs rounded-lg font-medium shadow-sm hover:bg-white"
                    >
                      {t('postKit.copyLink')}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  )
}
