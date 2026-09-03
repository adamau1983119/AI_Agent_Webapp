/**
 * Public topic post composer (JIT). Does not auto-call LLM in useEffect.
 */
import { useMemo, useState } from 'react'
import { AtSign, Copy, Facebook, Instagram, RefreshCw, Sparkles } from 'lucide-react'
import { alterEgoApi, type ComposePart, type ComposePlatform, type ComposeStyle } from '@/api/alterEgo'
import { APIError } from '@/api/errors'
import { useTranslation } from '@/i18n'
import { copyToClipboard } from '@/utils/copyToClipboard'
import { showError, showSuccess } from '@/utils/toast'
import LoadingSpinner from '@/components/ui/LoadingSpinner'

const PLATFORMS: { id: ComposePlatform; Icon: typeof Facebook }[] = [
  { id: 'facebook', Icon: Facebook },
  { id: 'instagram', Icon: Instagram },
  { id: 'threads', Icon: AtSign },
]
const STYLES: ComposeStyle[] = [
  'professional',
  'casual',
  'humorous',
  'storytelling',
  'educational',
]
const LENGTHS = [50, 100, 150] as const
const LENGTH_KEYS = {
  50: 'composer.length50',
  100: 'composer.length100',
  150: 'composer.length150',
} as const
const CAPS: Record<ComposePlatform, number> = {
  facebook: 5000,
  instagram: 2200,
  threads: 150,
}

function assemble(title: string, body: string, tags: string[]): string {
  return [title, body, tags.join(' ')].filter((p) => p.trim()).join('\n\n')
}

export default function PostComposerPanel({
  topicId,
  topicTitle,
  contextSummary,
  language,
  requireAuth,
}: {
  topicId: string
  topicTitle: string
  contextSummary: string
  language: string
  requireAuth: (action: () => void) => void
}) {
  const { t } = useTranslation()
  const [platform, setPlatform] = useState<ComposePlatform>('facebook')
  const [style, setStyle] = useState<ComposeStyle>('casual')
  const [maxChars, setMaxChars] = useState<number>(150)
  const [titles, setTitles] = useState<string[]>(['', '', ''])
  const [body, setBody] = useState('')
  const [hashtagSets, setHashtagSets] = useState<string[][]>([[], [], []])
  const [titleIdx, setTitleIdx] = useState(0)
  const [tagIdx, setTagIdx] = useState(0)
  const [busyPart, setBusyPart] = useState<ComposePart | null>(null)

  const cap = CAPS[platform]
  const limit = Math.min(maxChars, cap)
  const whole = assemble(titles[titleIdx] || '', body, hashtagSets[tagIdx] || [])
  const used = Array.from(whole).length
  const generating = busyPart !== null

  const fact = useMemo(
    () => (contextSummary || topicTitle || '').slice(0, 1500),
    [contextSummary, topicTitle]
  )

  const runCompose = async (part: ComposePart) => {
    setBusyPart(part)
    try {
      const res = await alterEgoApi.compose({
        platform,
        style,
        max_chars: limit,
        part,
        language,
        topic_id: topicId,
        topic_title: topicTitle,
        context_summary: fact,
      })
      if (part === 'all' || part === 'title') {
        if (res.titles.some((x) => x.trim())) {
          setTitles(res.titles)
          setTitleIdx(0)
        }
      }
      if (part === 'all' || part === 'body') {
        if (res.body.trim()) setBody(res.body)
      }
      if (part === 'all' || part === 'hashtags') {
        if (res.hashtag_sets.some((s) => s.length > 0)) {
          setHashtagSets(res.hashtag_sets)
          setTagIdx(0)
        }
      }
      showSuccess(t('common.success'))
    } catch (error: unknown) {
      const status = error instanceof APIError ? error.status : 0
      if (status === 401) {
        showError(t('auth.loginRequired'))
        return
      }
      showError(status === 402 ? t('composer.insufficientCredits') : t('common.failed'))
    } finally {
      setBusyPart(null)
    }
  }

  const copyAll = async () => {
    if (!whole.trim()) {
      showError(t('composer.emptyPack'))
      return
    }
    const ok = await copyToClipboard(whole)
    if (ok) showSuccess(t('postKit.copied'))
    else showError(t('postKit.copyFailed'))
  }

  return (
    <div data-testid="section-composer" className="space-y-4">
      <section className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-800 p-5 sm:p-6 space-y-4">
        <h3 className="font-display text-lg font-semibold text-gray-900 dark:text-white">
          {t('composer.settings')}
        </h3>
        <p className="text-xs font-medium text-gray-500 dark:text-gray-400">{t('composer.platform')}</p>
        <div className="grid grid-cols-3 gap-2">
          {PLATFORMS.map(({ id, Icon }) => (
            <button
              key={id}
              type="button"
              data-testid={`btn-composer-platform-${id}`}
              onClick={() => setPlatform(id)}
              className={`inline-flex items-center justify-center gap-1.5 min-h-[44px] rounded-xl border-2 text-xs font-medium touch-manipulation ${
                platform === id
                  ? 'border-primary bg-primary/10 text-primary'
                  : 'border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-200'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{t(`alterEgo.platform.${id}`)}</span>
            </button>
          ))}
        </div>
        <p className="text-xs font-medium text-gray-500 dark:text-gray-400">{t('composer.style')}</p>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
          {STYLES.map((id) => (
            <button
              key={id}
              type="button"
              data-testid={`btn-composer-style-${id}`}
              onClick={() => setStyle(id)}
              className={`min-h-[44px] px-2 rounded-xl border-2 text-xs font-medium touch-manipulation ${
                style === id
                  ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/30'
                  : 'border-gray-200 dark:border-gray-600'
              }`}
            >
              {t(`content.style.${id}`)}
            </button>
          ))}
        </div>
        <p className="text-xs font-medium text-gray-500 dark:text-gray-400">{t('composer.length')}</p>
        <div className="grid grid-cols-3 gap-2">
          {LENGTHS.map((n) => {
            const over = n > cap
            return (
              <button
                key={n}
                type="button"
                disabled={over}
                title={over ? t('composer.overCap') : undefined}
                data-testid={`btn-composer-length-${n}`}
                onClick={() => !over && setMaxChars(n)}
                className={`min-h-[44px] rounded-xl border-2 text-xs font-medium touch-manipulation disabled:opacity-40 ${
                  maxChars === n
                    ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/30'
                    : 'border-gray-200 dark:border-gray-600'
                }`}
              >
                {t(LENGTH_KEYS[n])}
              </button>
            )
          })}
        </div>
        <button
          type="button"
          data-testid="btn-composer-generate-pack"
          disabled={generating}
          onClick={() => requireAuth(() => void runCompose('all'))}
          className="w-full inline-flex items-center justify-center gap-2 min-h-[44px] rounded-xl bg-primary text-white text-sm font-medium hover:bg-primary-dark disabled:opacity-50 touch-manipulation"
        >
          <Sparkles className="w-4 h-4" />
          {generating && busyPart === 'all' ? t('common.generating') : t('composer.generatePack')}
        </button>
      </section>

      <section className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-800 p-5 sm:p-6 space-y-4">
        <div className="flex items-center justify-between gap-2">
          <h3 className="font-display text-lg font-semibold text-gray-900 dark:text-white">
            {t('composer.packTitle')}
          </h3>
          {generating ? <LoadingSpinner size="sm" /> : null}
        </div>
        <div className="flex items-center justify-between">
          <p className="text-xs font-medium text-gray-500">{t('composer.titles')}</p>
          <button
            type="button"
            data-testid="btn-composer-regen-title"
            disabled={generating}
            onClick={() => requireAuth(() => void runCompose('title'))}
            className="inline-flex items-center gap-1 text-xs text-primary min-h-[40px] touch-manipulation"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            {t('composer.regenTitle')}
          </button>
        </div>
        <div className="space-y-2">
          {titles.map((title, i) => (
            <button
              key={`title-${i}`}
              type="button"
              data-testid={`btn-composer-title-${i + 1}`}
              onClick={() => setTitleIdx(i)}
              className={`w-full text-left text-sm rounded-xl border px-3 py-2 min-h-[44px] touch-manipulation ${
                titleIdx === i
                  ? 'border-primary bg-primary/5'
                  : 'border-gray-200 dark:border-gray-600'
              }`}
            >
              {title || t('composer.emptyPack')}
            </button>
          ))}
        </div>
        <div className="flex items-center justify-between">
          <p className="text-xs font-medium text-gray-500">{t('postKit.body')}</p>
          <button
            type="button"
            data-testid="btn-composer-regen-body"
            disabled={generating}
            onClick={() => requireAuth(() => void runCompose('body'))}
            className="inline-flex items-center gap-1 text-xs text-primary min-h-[40px] touch-manipulation"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            {t('composer.regenBody')}
          </button>
        </div>
        <p className="text-sm whitespace-pre-line rounded-xl bg-gray-50 dark:bg-gray-750 p-3 min-h-[72px]">
          {body || t('composer.emptyPack')}
        </p>
        <div className="flex items-center justify-between">
          <p className="text-xs font-medium text-gray-500">{t('composer.hashtagSets')}</p>
          <button
            type="button"
            data-testid="btn-composer-regen-hashtags"
            disabled={generating}
            onClick={() => requireAuth(() => void runCompose('hashtags'))}
            className="inline-flex items-center gap-1 text-xs text-primary min-h-[40px] touch-manipulation"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            {t('composer.regenTags')}
          </button>
        </div>
        <div className="space-y-2">
          {hashtagSets.map((tags, i) => (
            <button
              key={`tags-${i}`}
              type="button"
              data-testid={`btn-composer-hashtag-set-${i + 1}`}
              onClick={() => setTagIdx(i)}
              className={`w-full text-left text-sm rounded-xl border px-3 py-2 min-h-[44px] touch-manipulation ${
                tagIdx === i
                  ? 'border-primary bg-primary/5'
                  : 'border-gray-200 dark:border-gray-600'
              }`}
            >
              {tags.join(' ') || t('composer.emptyPack')}
            </button>
          ))}
        </div>
      </section>

      <section
        data-testid="section-composer-whole"
        className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-800 p-5 sm:p-6 space-y-3"
      >
        <div className="flex items-center justify-between gap-2">
          <h3 className="font-display text-lg font-semibold text-gray-900 dark:text-white">
            {t('composer.wholePost')}
          </h3>
          <button
            type="button"
            data-testid="btn-composer-copy-all"
            onClick={() => void copyAll()}
            className="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-medium rounded-lg bg-gray-100 dark:bg-gray-700 min-h-[38px] touch-manipulation"
          >
            <Copy className="w-3.5 h-3.5" />
            {t('composer.copyAll')}
          </button>
        </div>
        <p className="text-xs text-gray-500">{t('composer.charCount', { used, max: limit })}</p>
        <pre className="text-sm whitespace-pre-wrap font-sans rounded-xl bg-gray-50 dark:bg-gray-750 p-4 min-h-[96px]">
          {whole || t('composer.emptyPack')}
        </pre>
      </section>
    </div>
  )
}
