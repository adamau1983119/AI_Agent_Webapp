/**
 * Live title-image: featured photo + DeepSeek Post Kit heading + style → backend JPEG.
 * Overlay is Pillow (0 credits); headings come from compose (−1).
 */
import { useEffect, useMemo, useState } from 'react'
import { API_BASE_URL } from '@/api/client'
import { useTranslation } from '@/i18n'
import type { Image } from '@/types'
import { showError, showSuccess } from '@/utils/toast'

type OverlayStyleId = 'a' | 'b' | 'c'
const STYLES: OverlayStyleId[] = ['a', 'b', 'c']
const STYLE_KEYS: Record<OverlayStyleId, 'titleImage.styleA' | 'titleImage.styleB' | 'titleImage.styleC'> = {
  a: 'titleImage.styleA',
  b: 'titleImage.styleB',
  c: 'titleImage.styleC',
}

function getProxyImageUrl(imageUrl: string): string {
  if (!imageUrl) return ''
  if (imageUrl.includes('/images/proxy')) return imageUrl
  return `${API_BASE_URL}/images/proxy?url=${encodeURIComponent(imageUrl)}`
}

function triggerDownload(blob: Blob, filename: string): void {
  const href = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = href
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(href)
}

export default function TitleImageLivePanel({
  images,
  headings,
}: {
  images: Image[]
  headings: string[]
}) {
  const { t } = useTranslation()
  const cleanHeadings = useMemo(
    () => headings.map((h) => h.trim()).filter(Boolean).slice(0, 3),
    [headings]
  )
  const [photoId, setPhotoId] = useState<string | null>(null)
  const [headingIdx, setHeadingIdx] = useState(0)
  const [styleId, setStyleId] = useState<OverlayStyleId | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [dirty, setDirty] = useState(false)

  const photo = images.find((i) => i.id === photoId) || null
  const heading = cleanHeadings[headingIdx] || ''
  const ready = Boolean(photo && heading && styleId)
  const missing: string[] = []
  if (!photo) missing.push(t('titleImage.missingPhoto'))
  if (!heading) missing.push(t('titleImage.missingHeading'))
  if (!styleId) missing.push(t('titleImage.missingStyle'))

  useEffect(() => {
    if (!dirty) return
    const onBeforeUnload = (e: BeforeUnloadEvent) => {
      e.preventDefault()
      e.returnValue = ''
    }
    window.addEventListener('beforeunload', onBeforeUnload)
    return () => window.removeEventListener('beforeunload', onBeforeUnload)
  }, [dirty])

  useEffect(() => {
    let cancelled = false
    let objectUrl: string | null = null
    if (!ready || !photo || !styleId) {
      setPreviewUrl(null)
      return
    }
    setBusy(true)
    fetch(`${API_BASE_URL}/images/title-image`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image_id: photo.id, heading, style: styleId }),
    })
      .then(async (res) => {
        if (!res.ok) throw new Error(`status_${res.status}`)
        const blob = await res.blob()
        objectUrl = URL.createObjectURL(blob)
        if (!cancelled) setPreviewUrl(objectUrl)
      })
      .catch(() => {
        if (!cancelled) setPreviewUrl(null)
      })
      .finally(() => {
        if (!cancelled) setBusy(false)
      })
    return () => {
      cancelled = true
      if (objectUrl) URL.revokeObjectURL(objectUrl)
    }
  }, [ready, photo, heading, styleId])

  const handleDownload = async () => {
    if (!ready || !photo || !styleId) return
    setBusy(true)
    try {
      const res = await fetch(`${API_BASE_URL}/images/title-image`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_id: photo.id, heading, style: styleId }),
      })
      if (!res.ok) throw new Error(`status_${res.status}`)
      const blob = await res.blob()
      triggerDownload(blob, `title-${photo.id.slice(-8)}.jpg`)
      showSuccess(t('titleImage.liveRendered'))
    } catch {
      showError(t('common.failed'))
    } finally {
      setBusy(false)
    }
  }

  if (images.length === 0) return null

  return (
    <section
      id="title-image-live"
      className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-800 p-5 sm:p-6 space-y-4"
      data-testid="section-title-image-live"
    >
      <h3 className="font-display text-lg font-semibold text-gray-900 dark:text-white">
        {t('titleImage.panelTitle')}
      </h3>
      <p className="text-xs text-gray-500" data-testid="text-title-image-live-hint">
        {t('titleImage.liveHint')}
      </p>

      <p className="text-xs font-medium text-gray-500">{t('titleImage.stepPhoto')}</p>
      <div className="grid grid-cols-2 gap-2" data-testid="grid-title-image-live-photos">
        {images.slice(0, 4).map((img) => {
          const selected = photoId === img.id
          return (
            <button
              key={img.id}
              type="button"
              data-testid={`btn-title-image-live-photo-${img.id}`}
              onClick={() => {
                setPhotoId(img.id)
                setDirty(true)
              }}
              className={`relative aspect-square overflow-hidden rounded-xl border-2 touch-manipulation ${
                selected ? 'border-primary' : 'border-transparent'
              }`}
            >
              <img
                src={getProxyImageUrl(img.url)}
                alt=""
                className="w-full h-full object-cover"
              />
            </button>
          )
        })}
      </div>

      <p className="text-xs font-medium text-gray-500">{t('titleImage.stepHeading')}</p>
      {cleanHeadings.length === 0 ? (
        <p className="text-sm text-amber-800" data-testid="text-title-image-need-compose">
          {t('titleImage.needCompose')}
        </p>
      ) : (
        <div className="space-y-2" data-testid="section-title-image-live-kit">
          {cleanHeadings.map((h, i) => (
            <button
              key={`${i}-${h.slice(0, 12)}`}
              type="button"
              data-testid={`btn-title-image-live-heading-${i + 1}`}
              onClick={() => {
                setHeadingIdx(i)
                setDirty(true)
              }}
              className={`w-full text-left px-3 py-2 rounded-xl border-2 text-sm touch-manipulation min-h-[44px] ${
                headingIdx === i
                  ? 'border-primary bg-primary/10'
                  : 'border-gray-200 dark:border-gray-600'
              }`}
            >
              {h}
            </button>
          ))}
        </div>
      )}

      <p className="text-xs font-medium text-gray-500">{t('titleImage.stepStyle')}</p>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
        {STYLES.map((s) => (
          <button
            key={s}
            type="button"
            data-testid={`btn-title-image-live-style-${s}`}
            onClick={() => {
              setStyleId(s)
              setDirty(true)
            }}
            className={`min-h-[44px] rounded-xl border-2 text-xs font-medium touch-manipulation ${
              styleId === s
                ? 'border-primary bg-primary/10 text-primary'
                : 'border-gray-200 dark:border-gray-600'
            }`}
          >
            {t(STYLE_KEYS[s])}
          </button>
        ))}
      </div>

      {previewUrl ? (
        <img
          src={previewUrl}
          alt=""
          className="w-full h-auto rounded-xl border border-gray-100"
          data-testid="img-title-image-live-preview"
        />
      ) : !ready ? (
        <p className="text-sm text-amber-800" data-testid="text-title-image-live-missing">
          {t('titleImage.missingPrefix')}
          {missing.join('、')}
        </p>
      ) : null}

      <button
        type="button"
        data-testid="btn-title-image-live-download"
        disabled={!ready || busy}
        onClick={() => void handleDownload()}
        className="w-full inline-flex items-center justify-center min-h-[44px] rounded-xl bg-primary text-white text-sm font-medium hover:bg-primary-dark disabled:opacity-50 touch-manipulation"
      >
        {busy ? t('common.loading') : t('titleImage.downloadJpg')}
      </button>
    </section>
  )
}
