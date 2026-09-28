/**
 * Sample title-image flow: matched photo + Post Kit heading + style → demo JPG.
 * Same-page; no credits; no live match API.
 */
import { useEffect, useMemo, useState } from 'react'
import { useTranslation } from '@/i18n'
import { getWwwTitleImageSample } from '@/data/wwwTitleImageSample'
import {
  renderAndDownloadTitleImage,
  renderTitleImagePreviewDataUrl,
  type OverlayStyleId,
} from '@/lib/renderTitleImageOverlay'
import { showError, showSuccess } from '@/utils/toast'

function logSample(tag: string, fields: Record<string, string | number | boolean | undefined>) {
  // eslint-disable-next-line no-console
  console.info(`[${tag}]`, fields)
}

export default function TitleImageSamplePanel({ language }: { language: string }) {
  const { t } = useTranslation()
  const sample = useMemo(() => getWwwTitleImageSample(language), [language])
  const [headingIdx, setHeadingIdx] = useState(0)
  const [photoId, setPhotoId] = useState<string | null>(null)
  const [styleId, setStyleId] = useState<OverlayStyleId | null>(null)
  const [panelOpen, setPanelOpen] = useState(false)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [dirty, setDirty] = useState(false)

  const heading = sample.headings[headingIdx] || sample.title
  const photo = sample.photos.find((p) => p.id === photoId) || null
  const ready = Boolean(photo && heading.trim() && styleId)
  const missing: string[] = []
  if (!photo) missing.push(t('titleImage.missingPhoto'))
  if (!heading.trim()) missing.push(t('titleImage.missingHeading'))
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
    if (!ready || !photo || !styleId) {
      setPreviewUrl(null)
      return
    }
    setBusy(true)
    renderTitleImagePreviewDataUrl({
      photoUrl: photo.url,
      heading,
      style: styleId,
    })
      .then((url) => {
        if (!cancelled) {
          setPreviewUrl(url)
          logSample('TITLE_IMAGE_SAMPLE_PREVIEW', {
            photo_id: photo.id,
            style: styleId,
            heading: heading.slice(0, 40),
          })
        }
      })
      .catch(() => {
        if (!cancelled) setPreviewUrl(null)
      })
      .finally(() => {
        if (!cancelled) setBusy(false)
      })
    return () => {
      cancelled = true
    }
  }, [ready, photo, heading, styleId])

  const markDirty = () => setDirty(true)

  const handleRenderDownload = async () => {
    if (!ready || !photo || !styleId) return
    setBusy(true)
    try {
      await renderAndDownloadTitleImage({
        photoUrl: photo.url,
        heading,
        style: styleId,
        filename: 'title-image-sample.jpg',
      })
      logSample('TITLE_IMAGE_SAMPLE_RENDER', {
        photo_id: photo.id,
        style: styleId,
        heading: heading.slice(0, 40),
        demo: true,
      })
      showSuccess(t('titleImage.demoRendered'))
      markDirty()
    } catch {
      showError(t('common.failed'))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="space-y-4" data-testid="section-title-image-sample">
      {dirty && (
        <div
          role="status"
          data-testid="banner-compose-unsaved"
          className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950"
        >
          {t('composer.unsavedBanner')}
        </div>
      )}

      <section
        className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-800 p-5 sm:p-6 space-y-4"
        data-testid="section-www-topic-card"
      >
        <p className="text-xs tracking-[0.2em] uppercase text-gray-500">{t('composer.demoBadge')}</p>
        <h2 className="font-display text-xl font-semibold text-gray-900 dark:text-white">
          {sample.title}
        </h2>
        <p className="text-sm text-gray-600 dark:text-gray-300">{sample.summary}</p>
        <a
          href={sample.sourceUrl}
          target="_blank"
          rel="noopener noreferrer"
          data-testid="link-title-image-sample-source"
          className="text-sm text-primary underline break-all"
        >
          {t('titleImage.sourceLink')}
        </a>

        <div>
          <h3 className="font-sans text-sm font-semibold text-gray-800 dark:text-gray-200 mb-2">
            {t('titleImage.featuredPhotos')}
          </h3>
          <div className="grid grid-cols-2 gap-2" data-testid="grid-title-image-sample-photos">
            {sample.photos.map((p) => {
              const selected = photoId === p.id
              return (
                <button
                  key={p.id}
                  type="button"
                  data-testid={`btn-title-image-pick-photo-${p.id}`}
                  onClick={() => {
                    setPhotoId(p.id)
                    markDirty()
                    logSample('TITLE_IMAGE_SAMPLE_PHOTO', { photo_id: p.id })
                  }}
                  className={`relative aspect-square overflow-hidden rounded-xl border-2 touch-manipulation ${
                    selected ? 'border-primary ring-2 ring-primary/30' : 'border-gray-200'
                  }`}
                >
                  <img
                    src={p.url}
                    alt=""
                    className="h-full w-full object-cover"
                    loading="lazy"
                  />
                  <span className="sr-only">{p.credit}</span>
                </button>
              )
            })}
          </div>
          <p className="text-xs text-gray-500 mt-2">{t('titleImage.photoCreditHint')}</p>
        </div>
      </section>

      <section
        className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 p-5 sm:p-6 space-y-4"
        data-testid="section-title-image-sample-kit"
      >
        <h3 className="font-display text-lg font-semibold">{t('titleImage.postKitHeading')}</h3>
        <div className="space-y-2">
          {sample.headings.map((h, i) => (
            <button
              key={h}
              type="button"
              data-testid={`btn-title-image-heading-${i + 1}`}
              onClick={() => {
                setHeadingIdx(i)
                markDirty()
              }}
              className={`w-full text-left min-h-[44px] px-3 py-2 rounded-xl border text-sm touch-manipulation ${
                headingIdx === i
                  ? 'border-primary bg-primary/5 text-gray-900'
                  : 'border-gray-200 text-gray-700'
              }`}
            >
              {h}
            </button>
          ))}
        </div>
        <p className="text-sm text-gray-600 whitespace-pre-line max-h-32 overflow-y-auto">{sample.body}</p>
        <p className="text-xs text-primary">{sample.hashtags.join(' ')}</p>
        <button
          type="button"
          data-testid="btn-postkit-open-title-image"
          onClick={() => {
            setPanelOpen(true)
            markDirty()
            document.getElementById('title-image-stage')?.scrollIntoView({ behavior: 'smooth' })
          }}
          className="w-full inline-flex items-center justify-center min-h-[44px] rounded-xl bg-primary text-white text-sm font-medium hover:bg-primary-dark touch-manipulation"
        >
          {t('titleImage.openPanel')}
        </button>
      </section>

      {(panelOpen || ready) && (
        <section
          id="title-image-stage"
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 p-5 sm:p-6 space-y-4"
          data-testid="section-title-image"
        >
          <h3 className="font-display text-lg font-semibold">{t('titleImage.panelTitle')}</h3>
          <p className="text-sm text-gray-600">{t('titleImage.panelHint')}</p>

          <div className="space-y-2">
            <p className="text-sm font-semibold">{t('titleImage.stepPhoto')}</p>
            <p className="text-xs text-gray-500">
              {photo ? t('titleImage.photoSelected') : t('titleImage.pickPhotoAbove')}
            </p>
          </div>

          <div className="space-y-2">
            <p className="text-sm font-semibold">{t('titleImage.stepHeading')}</p>
            <p className="text-sm text-gray-800 dark:text-gray-200">「{heading}」</p>
          </div>

          <div className="space-y-2">
            <p className="text-sm font-semibold">{t('titleImage.stepStyle')}</p>
            <div className="grid grid-cols-3 gap-2">
              {sample.styles.map((s) => (
                <button
                  key={s.id}
                  type="button"
                  data-testid={`btn-title-image-style-${s.id}`}
                  onClick={() => {
                    setStyleId(s.id)
                    markDirty()
                    logSample('TITLE_IMAGE_SAMPLE_STYLE', { style: s.id })
                  }}
                  className={`min-h-[44px] rounded-xl border text-xs sm:text-sm px-2 touch-manipulation ${
                    styleId === s.id
                      ? 'border-primary bg-primary/10 text-primary'
                      : 'border-gray-200 text-gray-700'
                  }`}
                >
                  {t(s.labelKey as 'titleImage.styleA')}
                </button>
              ))}
            </div>
          </div>

          {previewUrl && (
            <div className="rounded-xl overflow-hidden border border-gray-200">
              <img src={previewUrl} alt="" className="w-full h-auto" data-testid="img-title-image-preview" />
            </div>
          )}

          {!ready && (
            <p className="text-sm text-amber-800" data-testid="text-title-image-missing">
              {t('titleImage.missingPrefix')}
              {missing.join('、')}
            </p>
          )}

          <button
            type="button"
            data-testid="btn-title-image-render"
            disabled={!ready || busy}
            onClick={handleRenderDownload}
            className="w-full inline-flex items-center justify-center min-h-[44px] rounded-xl bg-primary text-white text-sm font-medium disabled:opacity-50 touch-manipulation"
          >
            {busy ? t('common.loading') : t('titleImage.renderDemo')}
          </button>
          <button
            type="button"
            data-testid="btn-title-image-download"
            disabled={!ready || busy}
            onClick={handleRenderDownload}
            className="w-full inline-flex items-center justify-center min-h-[44px] rounded-xl border border-gray-200 text-sm font-medium disabled:opacity-50 touch-manipulation"
          >
            {t('titleImage.downloadJpg')}
          </button>
        </section>
      )}
    </div>
  )
}
