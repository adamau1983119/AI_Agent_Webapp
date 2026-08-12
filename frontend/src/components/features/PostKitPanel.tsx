import { useCallback, useEffect, useMemo, useState } from 'react'
import { Copy } from 'lucide-react'
import { useTranslation } from '@/i18n'
import { alterEgoApi, type AlterEgoPlatform } from '@/api/alterEgo'
import { copyToClipboard } from '@/utils/copyToClipboard'
import { showError, showSuccess } from '@/utils/toast'
import type { Content, Image, Topic } from '@/types'

type Props = {
  displayTitle: string
  category: Topic['category']
  content: Content | null
  images: Image[]
  previewImages?: string[]
  topicId?: string
}

const PLATFORMS: AlterEgoPlatform[] = ['facebook', 'threads', 'x']

const CATEGORY_TAGS: Record<Topic['category'], string[]> = {
  fashion: ['fashion', 'style', 'ootd'],
  food: ['food', 'foodie', 'recipe'],
  trend: ['trend', 'viral', 'news'],
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
    const tags = [...(CATEGORY_TAGS[category] || [])]
    return tags.map((tag) => (tag.startsWith('#') ? tag : `#${tag}`))
  }, [category])

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

  const loadPlatformPreview = useCallback(async () => {
    if (!hasDna) return
    setPreviewLoading(true)
    try {
      const hint = displayTitle.trim().slice(0, 200)
      const preview = await alterEgoApi.preview(platform, hint, language)
      setPlatformCopy(preview.preview_text)
    } catch {
      setPlatformCopy('')
    } finally {
      setPreviewLoading(false)
    }
  }, [hasDna, platform, displayTitle, language])

  useEffect(() => {
    alterEgoApi
      .getStatus()
      .then((s) => setHasDna(s.has_dna && s.dna_status === 'active'))
      .catch(() => setHasDna(false))
  }, [])

  useEffect(() => {
    if (hasDna) {
      setPlatformCopy('')
      loadPlatformPreview()
    }
  }, [hasDna, platform, language, loadPlatformPreview])

  const handleCopy = async (text: string) => {
    const ok = await copyToClipboard(text)
    if (ok) {
      showSuccess(t('postKit.copied'))
    } else {
      showError(t('postKit.copyFailed'))
    }
  }

  const handleAdoptCopy = async () => {
    const text = platformCopy || bodyText
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
  const bodyText = content?.article?.trim() || ''
  const scriptText = content?.script?.trim() || ''
  const displayBody = hasDna && platformCopy.trim() ? platformCopy : bodyText

  const copyAllText = [selectedTitle, displayBody, hashtagLine].filter(Boolean).join('\n\n')

  return (
    <section
      className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 sm:p-6"
      data-testid="section-postkit"
      aria-label={t('postKit.sectionTitle')}
    >
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-6">
        <div>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            {t('postKit.sectionTitle')}
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            {t('postKit.hint.pasteOnPlatform')}
          </p>
        </div>
        <button
          type="button"
          data-testid="btn-postkit-copy-all"
          disabled={!copyAllText}
          onClick={() => handleCopy(copyAllText)}
          className="min-h-[44px] px-4 py-2 text-sm font-medium text-primary border border-primary/30 rounded-md hover:bg-primary/10 disabled:opacity-50"
        >
          {t('postKit.copyAll')}
        </button>
      </div>

      <div className="mb-6 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
        <h3 className="font-medium text-gray-800 dark:text-gray-200 mb-3">
          {t('postKit.platformSwitch')}
        </h3>
        <div className="flex gap-2 flex-wrap mb-4">
          {PLATFORMS.map((p) => (
            <button
              key={p}
              type="button"
              data-testid={`btn-postkit-platform-${p}`}
              onClick={() => setPlatform(p)}
              className={`px-3 py-2 text-xs uppercase min-h-[44px] border rounded-md ${
                platform === p
                  ? 'bg-primary text-white border-primary'
                  : 'border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300'
              }`}
            >
              {t(`alterEgo.platform.${p}`)}
            </button>
          ))}
        </div>
        {hasDna && (
          <div className="mb-4">
            <div className="flex justify-between items-start gap-2 mb-2">
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                {t('postKit.platformCopy', { platform: t(`alterEgo.platform.${platform}`) })}
              </h4>
              <button
                type="button"
                data-testid="btn-postkit-adopt-copy"
                disabled={!displayBody || previewLoading}
                onClick={handleAdoptCopy}
                className="min-h-[44px] px-3 py-1 text-xs font-medium border border-primary/30 rounded-md hover:bg-primary/10 disabled:opacity-50"
              >
                {t('postKit.adoptCopy')}
              </button>
            </div>
            <p
              data-testid="section-postkit-platform-copy"
              className="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-line max-h-48 overflow-y-auto"
            >
              {previewLoading ? t('common.loading') : displayBody || t('common.noContent')}
            </p>
          </div>
        )}
        <div>
          <div className="flex justify-between items-start gap-2 mb-2">
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
              {t('postKit.visualPrompt')}
            </h4>
            <button
              type="button"
              data-testid="btn-postkit-copy-visual-prompt"
              disabled={!visualPrompt}
              aria-label={t('postKit.visualPrompt')}
              onClick={() => handleCopy(visualPrompt)}
              className="min-h-[44px] min-w-[44px] inline-flex items-center justify-center rounded-md bg-gray-100 dark:bg-gray-700 hover:bg-gray-200"
            >
              <Copy className="w-4 h-4" />
            </button>
          </div>
          <p
            data-testid="section-postkit-visual-prompt"
            className="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-line"
          >
            {visualPrompt}
          </p>
        </div>
      </div>

      <div className="space-y-6">
        <div>
          <h3 className="font-medium text-gray-800 dark:text-gray-200 mb-3">{t('postKit.titleOptions')}</h3>
          <div className="space-y-2">
            {titleOptions.map((opt, idx) => (
              <div
                key={idx}
                className="flex flex-col sm:flex-row sm:items-center gap-2 p-3 rounded-lg border border-gray-200 dark:border-gray-700"
              >
                <label className="flex items-start gap-2 flex-1 cursor-pointer min-h-[44px]">
                  <input
                    type="radio"
                    name="postkit-title"
                    checked={selectedTitleIdx === idx}
                    onChange={() => setSelectedTitleIdx(idx)}
                    className="mt-1"
                    data-testid={`input-postkit-title-${idx + 1}`}
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300 break-words">
                    <span className="text-xs text-gray-400 block mb-1">
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
                  className="min-h-[44px] min-w-[44px] inline-flex items-center justify-center rounded-md bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600"
                >
                  <Copy className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="flex justify-between items-start gap-2 mb-2">
              <h3 className="font-medium text-gray-800 dark:text-gray-200">{t('postKit.body')}</h3>
              <button
                type="button"
                data-testid="btn-postkit-copy-body"
                disabled={!displayBody}
                aria-label={t('postKit.body')}
                onClick={() => handleCopy(displayBody)}
                className="min-h-[44px] min-w-[44px] inline-flex items-center justify-center rounded-md bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 disabled:opacity-50"
              >
                <Copy className="w-4 h-4" />
              </button>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-line max-h-40 overflow-y-auto">
              {displayBody || t('common.noContent')}
            </p>
          </div>

          <div className="p-4 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="flex justify-between items-start gap-2 mb-2">
              <h3 className="font-medium text-gray-800 dark:text-gray-200">{t('postKit.script')}</h3>
              <button
                type="button"
                data-testid="btn-postkit-copy-script"
                disabled={!scriptText}
                aria-label={t('postKit.script')}
                onClick={() => handleCopy(scriptText)}
                className="min-h-[44px] min-w-[44px] inline-flex items-center justify-center rounded-md bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 disabled:opacity-50"
              >
                <Copy className="w-4 h-4" />
              </button>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-line max-h-40 overflow-y-auto">
              {scriptText || t('common.noContent')}
            </p>
          </div>
        </div>

        <div className="p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex justify-between items-start gap-2 mb-2">
            <h3 className="font-medium text-gray-800 dark:text-gray-200">{t('postKit.hashtags')}</h3>
            <button
              type="button"
              data-testid="btn-postkit-copy-hashtags"
              disabled={!hashtagLine}
              aria-label={t('postKit.hashtags')}
              onClick={() => handleCopy(hashtagLine)}
              className="min-h-[44px] min-w-[44px] inline-flex items-center justify-center rounded-md bg-gray-100 dark:bg-gray-700 hover:bg-gray-200"
            >
              <Copy className="w-4 h-4" />
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {hashtags.map((tag) => (
              <span
                key={tag}
                className="px-2 py-1 text-xs rounded-full bg-primary/10 text-primary"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>

        <div>
          <h3 className="font-medium text-gray-800 dark:text-gray-200 mb-3">{t('postKit.photos')}</h3>
          {imageUrls.length === 0 ? (
            <p className="text-sm text-gray-500 dark:text-gray-400">{t('postKit.noPhotos')}</p>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {imageUrls.map((url, idx) => (
                <div key={url} className="rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
                  <img src={url} alt="" className="w-full h-24 object-cover" loading="lazy" />
                  <button
                    type="button"
                    data-testid={`btn-postkit-copy-image-${idx + 1}`}
                    aria-label={`${t('postKit.copy')} ${t('postKit.photos')} ${idx + 1}`}
                    onClick={() => handleCopy(url)}
                    className="w-full min-h-[44px] flex items-center justify-center gap-2 text-sm text-primary hover:bg-primary/5"
                  >
                    <Copy className="w-4 h-4" />
                    {t('postKit.copyLink')}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  )
}
