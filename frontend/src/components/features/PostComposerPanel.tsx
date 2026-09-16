/**
 * Public topic post composer (JIT). Does not auto-call LLM in useEffect.
 */
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { AtSign, Copy, Facebook, Instagram, Lock, RefreshCw, Sparkles } from 'lucide-react'
import { alterEgoApi, type ComposePart, type ComposePlatform, type ComposeStyle } from '@/api/alterEgo'
import { APIError } from '@/api/errors'
import { getComposeDemoPack } from '@/data/composeDemoPack'
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
const LENGTHS = [100, 150, 500] as const
const LENGTH_KEYS = {
  100: 'composer.length100',
  150: 'composer.length150',
  500: 'composer.length500',
} as const
const CAPS: Record<ComposePlatform, number> = {
  facebook: 5000,
  instagram: 2200,
  threads: 150,
}
const INTENTS = [
  'composer.intentPunchier',
  'composer.intentShorter',
  'composer.intentLeadKeep',
  'composer.intentMorePoint',
  'composer.intentLikeMe',
] as const

type Draft = { titles: string[]; body: string; hashtag_sets: string[][] }

function assemble(title: string, body: string, tags: string[]): string {
  return [title, body, tags.join(' ')].filter((p) => p.trim()).join('\n\n')
}

export default function PostComposerPanel({
  topicId,
  topicTitle,
  contextSummary,
  language,
  requireAuth,
  mode = 'live',
}: {
  topicId: string
  topicTitle: string
  contextSummary: string
  language: string
  requireAuth: (action: () => void) => void
  mode?: 'live' | 'demo'
}) {
  const { t } = useTranslation()
  const isDemo = mode === 'demo'
  const [platform, setPlatform] = useState<ComposePlatform>(isDemo ? 'instagram' : 'facebook')
  const [style, setStyle] = useState<ComposeStyle>(isDemo ? 'humorous' : 'casual')
  const [maxChars, setMaxChars] = useState<number>(isDemo ? 100 : 150)
  const [titles, setTitles] = useState<string[]>(['', '', ''])
  const [body, setBody] = useState('')
  const [hashtagSets, setHashtagSets] = useState<string[][]>([[], [], []])
  const [titleIdx, setTitleIdx] = useState(0)
  const [tagIdx, setTagIdx] = useState(0)
  const [busyPart, setBusyPart] = useState<ComposePart | null>(null)
  const [needCredits, setNeedCredits] = useState(false)
  const [drafts, setDrafts] = useState<Draft[]>([])
  const [keep, setKeep] = useState<string[]>([])
  const [keepInput, setKeepInput] = useState('')
  const [intentKey, setIntentKey] = useState<string>('')
  const [intentCustom, setIntentCustom] = useState('')
  const [genCount, setGenCount] = useState(0)
  const [bodyOk, setBodyOk] = useState(false)
  const [confirmRegen, setConfirmRegen] = useState(false)

  const cap = CAPS[platform]
  const limit = Math.min(maxChars, cap)
  const whole = assemble(titles[titleIdx] || '', body, hashtagSets[tagIdx] || [])
  const used = Array.from(whole).length
  const generating = busyPart !== null
  const softCap = genCount >= 5
  const fact = useMemo(
    () => (contextSummary || topicTitle || '').slice(0, 1500),
    [contextSummary, topicTitle]
  )

  const pushDraft = (d: Draft) => {
    setDrafts((prev) => [...prev, d].slice(-3))
  }

  const applyPack = (pack: Draft, countBump = true) => {
    if (pack.titles.some((x) => x.trim())) {
      setTitles(pack.titles)
      setTitleIdx(0)
    }
    if (pack.body.trim()) setBody(pack.body)
    if (pack.hashtag_sets.some((s) => s.length > 0)) {
      setHashtagSets(pack.hashtag_sets)
      setTagIdx(0)
    }
    pushDraft(pack)
    if (countBump) setGenCount((n) => n + 1)
  }

  const loadDemo = () => {
    const pack = getComposeDemoPack(language, limit >= 150 ? 150 : 100)
    applyPack(pack, false)
    setKeep([pack.keepHint])
    setBodyOk(false)
    showSuccess(t('composer.demoLoaded'))
  }

  const revisionIntent = () => {
    const chip = intentKey ? t(intentKey) : ''
    return [chip, intentCustom.trim()].filter(Boolean).join(' · ').slice(0, 400)
  }

  const runCompose = async (part: ComposePart) => {
    if (isDemo) {
      loadDemo()
      return
    }
    if (softCap && part !== 'title' && part !== 'hashtags' && part !== 'meta' && !confirmRegen) {
      setConfirmRegen(true)
      showError(t('composer.creditSoftCap'))
      return
    }
    setBusyPart(part)
    setConfirmRegen(false)
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
        preserve_snippets: keep,
        revision_intent: revisionIntent(),
        base_body: part === 'body' || part === 'all' ? '' : body,
      })
      applyPack({
        titles: res.titles,
        body: part === 'title' || part === 'hashtags' || part === 'meta' ? body : res.body || body,
        hashtag_sets: res.hashtag_sets,
      })
      if (res.short_body) showError(t('composer.shortBodyHint'))
      else showSuccess(t('common.success'))
      setNeedCredits(false)
    } catch (error: unknown) {
      const status = error instanceof APIError ? error.status : 0
      if (status === 401) {
        showError(t('auth.loginRequired'))
        return
      }
      if (status === 402) {
        setNeedCredits(true)
        showError(t('composer.insufficientCredits'))
        return
      }
      showError(t('common.failed'))
    } finally {
      setBusyPart(null)
    }
  }

  const addKeepFromSelection = () => {
    const sel = typeof window !== 'undefined' ? window.getSelection()?.toString().trim() : ''
    const text = (sel || keepInput).trim()
    if (!text) {
      showError(t('composer.keepEmpty'))
      return
    }
    setKeep((prev) => [...prev, text].slice(0, 8))
    setKeepInput('')
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

  const onPlatform = (id: ComposePlatform) => {
    setPlatform(id)
    if (id === 'threads' && maxChars > 150) setMaxChars(150)
  }

  return (
    <div data-testid="section-composer" className="space-y-4">
      {isDemo && (
        <p className="text-xs tracking-wide uppercase text-gray-500" data-testid="text-composer-demo-badge">
          {t('composer.demoBadge')}
        </p>
      )}
      <section className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-800 p-5 sm:p-6 space-y-4">
        <h3 className="font-display text-lg font-semibold text-gray-900 dark:text-white">
          {t('composer.settings')}
        </h3>
        <p className="text-xs text-gray-500">{t('composer.coachHint')}</p>
        <p className="text-xs font-medium text-gray-500">{t('composer.platform')}</p>
        <div className="grid grid-cols-3 gap-2">
          {PLATFORMS.map(({ id, Icon }) => (
            <button
              key={id}
              type="button"
              data-testid={`btn-composer-platform-${id}`}
              onClick={() => onPlatform(id)}
              className={`inline-flex items-center justify-center gap-1.5 min-h-[44px] rounded-xl border-2 text-xs font-medium touch-manipulation ${
                platform === id
                  ? 'border-primary bg-primary/10 text-primary'
                  : 'border-gray-200 dark:border-gray-600'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{t(`alterEgo.platform.${id}`)}</span>
            </button>
          ))}
        </div>
        <p className="text-xs font-medium text-gray-500">{t('composer.style')}</p>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
          {STYLES.map((id) => (
            <button
              key={id}
              type="button"
              data-testid={`btn-composer-style-${id}`}
              onClick={() => setStyle(id)}
              className={`min-h-[44px] px-2 rounded-xl border-2 text-xs font-medium touch-manipulation ${
                style === id
                  ? 'border-primary bg-primary/10 text-primary'
                  : 'border-gray-200 dark:border-gray-600'
              }`}
            >
              {t(`content.style.${id}`)}
            </button>
          ))}
        </div>
        <p className="text-xs font-medium text-gray-500">{t('composer.length')}</p>
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
                    ? 'border-primary bg-primary/10 text-primary'
                    : 'border-gray-200 dark:border-gray-600'
                }`}
              >
                {t(LENGTH_KEYS[n])}
              </button>
            )
          })}
        </div>
        {!isDemo && (
          <p className="text-xs text-gray-500" data-testid="text-composer-session-credits">
            {t('composer.sessionCredits', { n: String(genCount) })}
          </p>
        )}
        <button
          type="button"
          data-testid="btn-composer-generate-pack"
          disabled={generating}
          onClick={() => (isDemo ? loadDemo() : requireAuth(() => void runCompose('all')))}
          className="w-full inline-flex items-center justify-center gap-2 min-h-[44px] rounded-xl bg-primary text-white text-sm font-medium hover:bg-primary-dark disabled:opacity-50 touch-manipulation"
        >
          <Sparkles className="w-4 h-4" />
          {generating && busyPart === 'all'
            ? t('common.generating')
            : isDemo
              ? t('composer.generateDemo')
              : softCap
                ? t('composer.generateAnyway')
                : t('composer.generatePack')}
        </button>
        {isDemo && (
          <button
            type="button"
            data-testid="btn-composer-demo-reset"
            onClick={() => {
              setTitles(['', '', ''])
              setBody('')
              setHashtagSets([[], [], []])
              setKeep([])
              setDrafts([])
              setBodyOk(false)
            }}
            className="w-full min-h-[44px] rounded-xl border border-gray-300 text-sm"
          >
            {t('composer.resetDemo')}
          </button>
        )}
        {needCredits && (
          <p className="text-sm text-gray-600 flex flex-wrap items-center gap-3" data-testid="text-composer-need-credits">
            <span>{t('composer.insufficientCredits')}</span>
            <Link
              to="/settings?tab=billing"
              data-testid="btn-composer-buy-credits"
              className="inline-flex items-center min-h-[44px] px-4 rounded-full border border-[#1a1a1a] text-[11px] tracking-[0.16em] uppercase"
            >
              {t('credits.buy')}
            </Link>
          </p>
        )}
      </section>

      {(body || drafts.length > 0) && (
        <section className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 p-5 space-y-3" data-testid="section-composer-keep">
          <p className="text-xs font-medium text-gray-500">{t('composer.keepTitle')}</p>
          <p className="text-xs text-gray-500">{t('composer.keepHint')}</p>
          <div className="flex flex-wrap gap-2">
            {keep.map((s, i) => (
              <button
                key={`${i}-${s.slice(0, 12)}`}
                type="button"
                data-testid={`btn-composer-keep-chip-${i}`}
                onClick={() => setKeep((prev) => prev.filter((_, j) => j !== i))}
                className="inline-flex items-center gap-1 text-xs border rounded-lg px-2 py-1"
              >
                <Lock className="w-3 h-3" />
                {s.slice(0, 40)}
                {s.length > 40 ? '…' : ''}
              </button>
            ))}
          </div>
          <textarea
            data-testid="input-composer-keep"
            value={keepInput}
            onChange={(e) => setKeepInput(e.target.value)}
            rows={2}
            className="w-full text-sm rounded-xl border border-gray-200 p-3"
            placeholder={t('composer.keepPlaceholder')}
          />
          <button
            type="button"
            data-testid="btn-composer-keep-add"
            onClick={addKeepFromSelection}
            className="min-h-[40px] px-3 rounded-lg border text-xs"
          >
            {t('composer.keepAdd')}
          </button>
          {drafts.length > 0 && (
            <div className="flex flex-wrap gap-2" data-testid="section-composer-drafts">
              {drafts.map((_, i) => (
                <button
                  key={`d-${i}`}
                  type="button"
                  data-testid={`btn-composer-draft-${i + 1}`}
                  onClick={() => {
                    const d = drafts[i]
                    setTitles(d.titles)
                    setBody(d.body)
                    setHashtagSets(d.hashtag_sets)
                  }}
                  className="text-xs min-h-[36px] px-3 rounded-lg border"
                >
                  {t('composer.draftN', { n: String(i + 1) })}
                </button>
              ))}
            </div>
          )}
          <p className="text-xs font-medium text-gray-500">{t('composer.intentTitle')}</p>
          <div className="flex flex-wrap gap-2">
            {INTENTS.map((key) => (
              <button
                key={key}
                type="button"
                data-testid={`btn-composer-intent-${key.split('.').pop()}`}
                onClick={() => setIntentKey(key === intentKey ? '' : key)}
                className={`text-xs min-h-[36px] px-3 rounded-lg border ${
                  intentKey === key ? 'border-primary text-primary' : 'border-gray-200'
                }`}
              >
                {t(key)}
              </button>
            ))}
          </div>
          <input
            data-testid="input-composer-intent-custom"
            value={intentCustom}
            onChange={(e) => setIntentCustom(e.target.value)}
            className="w-full text-sm rounded-xl border border-gray-200 px-3 py-2"
            placeholder={t('composer.intentCustom')}
          />
        </section>
      )}

      <section className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 p-5 sm:p-6 space-y-4">
        <div className="flex items-center justify-between gap-2">
          <h3 className="font-display text-lg font-semibold">{t('composer.packTitle')}</h3>
          {generating ? <LoadingSpinner size="sm" /> : null}
        </div>
        <div className="flex items-center justify-between">
          <p className="text-xs font-medium text-gray-500">{t('postKit.body')}</p>
          <button
            type="button"
            data-testid="btn-composer-regen-body"
            disabled={generating || (softCap && !confirmRegen)}
            onClick={() => requireAuth(() => void runCompose('body'))}
            className="inline-flex items-center gap-1 text-xs text-primary min-h-[40px] touch-manipulation disabled:opacity-40"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            {t('composer.regenBody')}
          </button>
        </div>
        <textarea
          data-testid="input-composer-body"
          value={body}
          onChange={(e) => setBody(e.target.value)}
          rows={6}
          className="w-full text-sm whitespace-pre-line rounded-xl bg-gray-50 dark:bg-gray-750 p-3 border border-gray-100"
          placeholder={t('composer.emptyPack')}
        />
        <button
          type="button"
          data-testid="btn-composer-body-ok"
          disabled={!body.trim()}
          onClick={() => setBodyOk(true)}
          className="min-h-[40px] px-4 rounded-xl border text-xs disabled:opacity-40"
        >
          {t('composer.bodyOk')}
        </button>
        {(bodyOk || (titles.some((x) => x.trim()) && hashtagSets.some((s) => s.length > 0))) && (
          <>
            <div className="flex items-center justify-between">
              <p className="text-xs font-medium text-gray-500">{t('composer.titles')}</p>
              <button
                type="button"
                data-testid="btn-composer-regen-title"
                disabled={generating || !body.trim()}
                onClick={() => requireAuth(() => void runCompose('title'))}
                className="inline-flex items-center gap-1 text-xs text-primary min-h-[40px]"
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
                  className={`w-full text-left text-sm rounded-xl border px-3 py-2 min-h-[44px] ${
                    titleIdx === i ? 'border-primary bg-primary/5' : 'border-gray-200'
                  }`}
                >
                  {title || t('composer.emptyPack')}
                </button>
              ))}
            </div>
            <div className="flex items-center justify-between">
              <p className="text-xs font-medium text-gray-500">{t('composer.hashtagSets')}</p>
              <button
                type="button"
                data-testid="btn-composer-regen-hashtags"
                disabled={generating || !body.trim()}
                onClick={() => requireAuth(() => void runCompose('hashtags'))}
                className="inline-flex items-center gap-1 text-xs text-primary min-h-[40px]"
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
                  className={`w-full text-left text-sm rounded-xl border px-3 py-2 min-h-[44px] ${
                    tagIdx === i ? 'border-primary bg-primary/5' : 'border-gray-200'
                  }`}
                >
                  {tags.join(' ') || t('composer.emptyPack')}
                </button>
              ))}
            </div>
          </>
        )}
      </section>

      <section
        data-testid="section-composer-whole"
        className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 p-5 sm:p-6 space-y-3"
      >
        <div className="flex items-center justify-between gap-2">
          <h3 className="font-display text-lg font-semibold">{t('composer.wholePost')}</h3>
          <button
            type="button"
            data-testid="btn-composer-copy-all"
            onClick={() => void copyAll()}
            className="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-medium rounded-lg bg-gray-100 min-h-[38px]"
          >
            <Copy className="w-3.5 h-3.5" />
            {t('composer.copyAll')}
          </button>
        </div>
        <p className="text-xs text-gray-500">{t('composer.charCount', { used: String(used), max: String(limit) })}</p>
        <pre className="text-sm whitespace-pre-wrap font-sans rounded-xl bg-gray-50 p-4 min-h-[96px]">
          {whole || t('composer.emptyPack')}
        </pre>
      </section>
    </div>
  )
}
