/**
 * Compact one-tap post: teaser → generate ≤500 + title image → share → charge 20.
 * Restores latest pack from API; optional apply to advanced composer (no double debit).
 */
import { useEffect, useMemo, useRef, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { Download, Sparkles, Wand2 } from 'lucide-react'
import {
  alterEgoApi,
  type ComposeDomain,
  type OneTapApplyPack,
  type OneTapSurface,
} from '@/api/alterEgo'
import { APIError } from '@/api/errors'
import { trackOneTapEvent } from '@/lib/analytics'
import {
  renderAndDownloadTitleImage,
  renderTitleImagePreviewDataUrl,
} from '@/lib/renderTitleImageOverlay'
import { useTranslation } from '@/i18n'
import { useAuthStore } from '@/stores/authStore'
import { copyToClipboard } from '@/utils/copyToClipboard'
import { showError, showSuccess } from '@/utils/toast'
import LoadingSpinner from '@/components/ui/LoadingSpinner'

const ONE_TAP_COST = 20

function assemble(title: string, body: string, tags: string[]): string {
  return [title, body, tags.join(' ')].filter((p) => p.trim()).join('\n\n')
}

async function blobFromDataUrl(dataUrl: string): Promise<Blob | null> {
  try {
    const res = await fetch(dataUrl)
    return await res.blob()
  } catch {
    return null
  }
}

/** Desktop Chrome/Edge expose navigator.share → Windows share sheet (no download). Phone keeps Web Share. */
function preferNativeWebShare(): boolean {
  if (typeof window === 'undefined' || typeof navigator === 'undefined') return false
  if (typeof navigator.share !== 'function') return false
  try {
    const coarse = window.matchMedia('(pointer: coarse)').matches
    const narrow = window.matchMedia('(max-width: 768px)').matches
    return coarse || narrow
  } catch {
    return false
  }
}

function triggerBlobDownload(blob: Blob, filename: string) {
  const href = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = href
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(href)
}

export default function OneTapPostPanel({
  topicId,
  topicTitle,
  contextSummary,
  language,
  photoUrl,
  domain,
  surface = 'public',
  requireAuth,
  testIdPrefix = 'topic-detail',
  onApplyToAdvanced,
  onChargedChange,
}: {
  topicId: string
  topicTitle: string
  contextSummary: string
  language: string
  photoUrl: string
  domain?: string
  surface?: OneTapSurface
  requireAuth: (action: () => void, cost?: number) => void
  testIdPrefix?: string
  onApplyToAdvanced?: (pack: OneTapApplyPack) => void
  onChargedChange?: (charged: boolean) => void
}) {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const { isAuthenticated } = useAuthStore()
  const rootRef = useRef<HTMLDivElement>(null)
  const impressed = useRef(false)
  const restoredFor = useRef('')

  const [busy, setBusy] = useState(false)
  const [sharing, setSharing] = useState(false)
  const [restoring, setRestoring] = useState(false)
  const [packToken, setPackToken] = useState('')
  const [packTitles, setPackTitles] = useState<string[]>([])
  const [packBody, setPackBody] = useState('')
  const [packTags, setPackTags] = useState<string[]>([])
  const [postText, setPostText] = useState('')
  const [titlePreview, setTitlePreview] = useState('')
  const [heading, setHeading] = useState('')
  const [charged, setCharged] = useState(false)

  const teaser = useMemo(() => {
    const raw = (contextSummary || topicTitle || '').trim()
    if (!raw) return ''
    return raw.length > 120 ? `${raw.slice(0, 120)}…` : raw
  }, [contextSummary, topicTitle])

  const composeDomain: ComposeDomain | undefined =
    domain === 'fashion' || domain === 'food' || domain === 'trend' ? domain : undefined

  const tid = (suffix: string) => `btn-${testIdPrefix}-${suffix}`
  const sid = (suffix: string) => `section-${testIdPrefix}-${suffix}`
  const costN = String(ONE_TAP_COST)

  const hydrateFromPack = async (opts: {
    pack_token: string
    titles: string[]
    body: string
    hashtag_sets: string[][]
    charged?: boolean
    silent?: boolean
  }) => {
    const title = (opts.titles.find((x) => x.trim()) || topicTitle || '').trim()
    const tags = opts.hashtag_sets.find((s) => s.length > 0) || []
    const whole = assemble(title, opts.body || '', tags)
    setPackToken(opts.pack_token)
    setPackTitles(opts.titles)
    setPackBody(opts.body || '')
    setPackTags(tags)
    setPostText(whole)
    setHeading(title)
    const nextCharged = Boolean(opts.charged)
    setCharged(nextCharged)
    onChargedChange?.(nextCharged)
    if (photoUrl && title) {
      try {
        const preview = await renderTitleImagePreviewDataUrl({
          photoUrl,
          heading: title,
          style: 'a',
        })
        setTitlePreview(preview)
      } catch {
        setTitlePreview('')
      }
    } else {
      setTitlePreview('')
    }
    if (!opts.silent) {
      showSuccess(t('topics.oneTapRestored'))
    }
  }

  useEffect(() => {
    if (impressed.current) return
    const el = rootRef.current
    if (!el || typeof IntersectionObserver === 'undefined') {
      impressed.current = true
      trackOneTapEvent('one_tap_impression', { surface, topic_id: topicId })
      return
    }
    const obs = new IntersectionObserver(
      (entries) => {
        if (impressed.current) return
        if (entries.some((e) => e.isIntersecting && e.intersectionRatio > 0.35)) {
          impressed.current = true
          trackOneTapEvent('one_tap_impression', { surface, topic_id: topicId })
          obs.disconnect()
        }
      },
      { threshold: [0.35] },
    )
    obs.observe(el)
    return () => obs.disconnect()
  }, [surface, topicId])

  useEffect(() => {
    if (!isAuthenticated || !topicId) return
    if (restoredFor.current === topicId) return
    restoredFor.current = topicId
    setRestoring(true)
    void (async () => {
      try {
        const latest = await alterEgoApi.getLatestOneTapPack(topicId)
        if (!latest?.pack_token) return
        await hydrateFromPack({
          pack_token: latest.pack_token,
          titles: latest.titles,
          body: latest.body,
          hashtag_sets: latest.hashtag_sets,
          charged: latest.charged,
          silent: false,
        })
      } catch {
        // leave empty; user can regenerate
      } finally {
        setRestoring(false)
      }
    })()
    // eslint-disable-next-line react-hooks/exhaustive-deps -- restore once per topic when auth
  }, [isAuthenticated, topicId])

  const chargeAfterSuccess = async (token: string) => {
    try {
      const res = await alterEgoApi.chargeOneTapPack(token)
      await queryClient.invalidateQueries({ queryKey: ['creditsBalance'] })
      setCharged(true)
      onChargedChange?.(true)
      if (!res.already_charged) {
        showSuccess(t('topics.oneTapShareSuccess', { n: costN }))
      } else {
        showSuccess(t('topics.oneTapAlreadyPaid'))
      }
      trackOneTapEvent('one_tap_share_success', { surface, topic_id: topicId })
    } catch (error: unknown) {
      const status = error instanceof APIError ? error.status : 0
      if (status === 402) showError(t('topics.oneTapNeedCredits', { n: costN }))
      else showError(t('common.failed'))
    }
  }

  const runGenerate = () => {
    requireAuth(() => {
      void (async () => {
        trackOneTapEvent('one_tap_click', { surface, topic_id: topicId })
        setBusy(true)
        try {
          const res = await alterEgoApi.generateOneTapPack({
            language,
            topic_id: topicId,
            topic_title: topicTitle,
            context_summary: (contextSummary || topicTitle || '').slice(0, 1500),
            domain: composeDomain,
            surface,
          })
          await hydrateFromPack({
            pack_token: res.pack_token,
            titles: res.titles,
            body: res.body || '',
            hashtag_sets: res.hashtag_sets,
            charged: false,
            silent: true,
          })
          trackOneTapEvent('one_tap_generate_success', { surface, topic_id: topicId })
          showSuccess(t('topics.oneTapGenerated', { n: costN }))
        } catch (error: unknown) {
          const status = error instanceof APIError ? error.status : 0
          if (status === 401) {
            showError(t('auth.loginRequired'))
            return
          }
          if (status === 402) {
            showError(t('topics.oneTapNeedCredits', { n: costN }))
            return
          }
          const detail =
            error instanceof APIError ? String(error.details?.detail ?? error.message ?? '') : ''
          if (
            status === 503 &&
            (detail.includes('model_busy') ||
              detail.includes('too busy') ||
              detail.includes('service_unavailable'))
          ) {
            showError(t('composer.modelBusy'))
            return
          }
          showError(t('common.failed'))
        } finally {
          setBusy(false)
        }
      })()
    }, ONE_TAP_COST)
  }

  const runShare = () => {
    if (!packToken || !postText.trim()) {
      showError(t('composer.emptyPack'))
      return
    }
    requireAuth(() => {
      void (async () => {
        setSharing(true)
        try {
          let shared = false
          const files: File[] = []
          if (titlePreview) {
            const blob = await blobFromDataUrl(titlePreview)
            if (blob) {
              files.push(new File([blob], 'title-image.jpg', { type: 'image/jpeg' }))
            }
          }

          // Phone only: system share. Desktop skips Web Share (Windows sheet ≠ download).
          if (preferNativeWebShare()) {
            try {
              const data: ShareData = { text: postText, title: heading || topicTitle }
              if (files.length > 0 && navigator.canShare?.({ files })) {
                data.files = files
              }
              await navigator.share(data)
              shared = true
            } catch (err: unknown) {
              const name =
                err && typeof err === 'object' && 'name' in err
                  ? String((err as { name: string }).name)
                  : ''
              if (name === 'AbortError') {
                trackOneTapEvent('one_tap_share_cancel', { surface, topic_id: topicId })
                showSuccess(t('topics.oneTapShareCancel'))
                return
              }
            }
          }

          if (!shared) {
            const ok = await copyToClipboard(postText)
            if (!ok) {
              showError(t('postKit.copyFailed'))
              return
            }
            try {
              if (titlePreview) {
                const blob = await blobFromDataUrl(titlePreview)
                if (blob) triggerBlobDownload(blob, 'title-image.jpg')
              } else if (photoUrl && heading) {
                await renderAndDownloadTitleImage({
                  photoUrl,
                  heading,
                  style: 'a',
                  filename: 'title-image.jpg',
                })
              }
            } catch {
              // text copy already succeeded
            }
            if (!charged) {
              showSuccess(t('topics.oneTapFallbackCopied', { n: costN }))
            }
          }

          await chargeAfterSuccess(packToken)
        } finally {
          setSharing(false)
        }
      })()
    }, charged ? undefined : ONE_TAP_COST)
  }

  const runApplyAdvanced = () => {
    if (!packToken || !packBody.trim()) {
      showError(t('composer.emptyPack'))
      return
    }
    onApplyToAdvanced?.({
      titles: packTitles.length ? packTitles : [heading || topicTitle],
      body: packBody,
      hashtag_sets: packTags.length ? [packTags] : [[]],
      pack_token: packToken,
      charged,
    })
    showSuccess(
      charged ? t('topics.oneTapAppliedAdvancedPaid') : t('topics.oneTapAppliedAdvanced'),
    )
  }

  const ready = Boolean(packToken && postText.trim())

  return (
    <div
      ref={rootRef}
      data-testid={sid('one-tap')}
      className="w-full max-w-xl mr-auto rounded-2xl bg-white dark:bg-gray-800 shadow-md border border-gray-100 dark:border-gray-700 p-3 sm:p-4 space-y-3"
    >
      {/* 手機版已驗證好看：紫底提示保留；桌面僅拉滿主欄寬度 */}
      <p
        className="text-sm sm:text-base font-semibold leading-snug text-purple-900 dark:text-purple-100 bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-950/50 dark:to-indigo-950/40 border border-purple-200/80 dark:border-purple-700/60 rounded-xl px-3 py-2.5 shadow-sm"
        data-testid={`text-${testIdPrefix}-one-tap-hint`}
      >
        {t('topics.oneTapPostHint', { n: costN })}
      </p>

      <div
        className={`grid gap-2 items-stretch ${photoUrl ? 'grid-cols-1 min-[360px]:grid-cols-[1fr_140px]' : 'grid-cols-1'}`}
        data-testid={sid('one-tap-preview')}
      >
        <div className="rounded-xl bg-gray-50 dark:bg-gray-900/60 border border-gray-100 dark:border-gray-700 p-2.5 min-h-[72px] flex flex-col">
          <p className="text-[10px] uppercase tracking-wide text-gray-400 mb-1">
            {ready ? t('topics.oneTapContentPreview') : t('topics.oneTapPreview')}
          </p>
          <p className="text-xs sm:text-sm text-gray-700 dark:text-gray-200 line-clamp-4 whitespace-pre-wrap flex-1 leading-relaxed">
            {restoring
              ? t('common.loading')
              : ready
                ? postText
                : teaser || t('topics.noContent')}
          </p>
        </div>
        {photoUrl ? (
          <div className="rounded-xl overflow-hidden border border-gray-100 dark:border-gray-700 bg-gray-100 dark:bg-gray-900 aspect-square max-h-[140px] w-full justify-self-end min-[360px]:max-w-[140px]">
            <p className="sr-only">{t('topics.oneTapTitleImage')}</p>
            {titlePreview ? (
              <img src={titlePreview} alt="" className="w-full h-full object-cover aspect-square" />
            ) : (
              <img src={photoUrl} alt="" className="w-full h-full object-cover aspect-square" />
            )}
          </div>
        ) : (
          <p className="text-xs text-gray-500 px-1">{t('topics.oneTapNoImage')}</p>
        )}
      </div>

      <button
        type="button"
        onClick={runGenerate}
        disabled={busy || restoring}
        data-testid={tid('one-tap-post')}
        className="w-full inline-flex items-center justify-center gap-2 min-h-[52px] sm:min-h-[56px] px-4 text-base sm:text-lg font-semibold text-white rounded-2xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 shadow-md hover:shadow-lg hover:scale-[1.01] transition-all duration-200 touch-manipulation disabled:opacity-60"
      >
        {busy ? (
          <>
            <LoadingSpinner size="sm" />
            <span>{t('topics.oneTapGenerating')}</span>
          </>
        ) : (
          <>
            <Sparkles className="w-5 h-5" />
            <span>{t('topics.oneTapPost')}</span>
          </>
        )}
      </button>

      <button
        type="button"
        onClick={runShare}
        disabled={!ready || sharing || busy}
        data-testid={tid('one-tap-share')}
        className="w-full inline-flex items-center justify-center gap-2 min-h-[44px] px-4 text-sm font-medium text-gray-800 dark:text-gray-100 rounded-xl bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-40 touch-manipulation"
      >
        <Download className="w-4 h-4" />
        <span>
          {charged
            ? t('topics.oneTapDownloadSharePaid')
            : t('topics.oneTapDownloadShare', { n: costN })}
        </span>
      </button>

      {ready && onApplyToAdvanced ? (
        <button
          type="button"
          onClick={runApplyAdvanced}
          disabled={busy || sharing}
          data-testid={tid('one-tap-apply-advanced')}
          className="w-full inline-flex items-center justify-center gap-2 min-h-[40px] px-4 text-sm font-medium text-purple-800 dark:text-purple-100 rounded-xl border border-purple-200 dark:border-purple-700 bg-purple-50/80 dark:bg-purple-950/40 hover:bg-purple-100 dark:hover:bg-purple-900/50 touch-manipulation disabled:opacity-40"
        >
          <Wand2 className="w-4 h-4" />
          <span>{t('topics.oneTapApplyAdvanced')}</span>
        </button>
      ) : null}
    </div>
  )
}
