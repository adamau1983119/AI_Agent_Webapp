/**
 * Shared title-image editor: live preview + confirm download (client canvas, 0 LLM).
 */
import { useEffect, useMemo, useState } from 'react'
import { useTranslation } from '@/i18n'
import {
  renderAndDownloadEdit,
  renderEditPreviewDataUrl,
  TITLE_BG_OPTS,
  TITLE_BG_PALETTE,
  type FontFace,
  type FontScale,
  type HAlign,
  type TitleBg,
  type VAlign,
  type WritingMode,
} from '@/lib/renderTitleImageEdit'
import { showError, showSuccess } from '@/utils/toast'

export type TitleEditPhoto = { id: string; url: string }

const V_OPTS: VAlign[] = ['top', 'middle', 'bottom']
const H_OPTS: HAlign[] = ['left', 'center', 'right']
const F_OPTS: FontScale[] = ['sm', 'md', 'lg']
const W_OPTS: WritingMode[] = ['h', 'v']
const FACE_OPTS: FontFace[] = ['hei', 'song', 'kai']

type Props = {
  photos: TitleEditPhoto[]
  headings: string[]
  /** data-testid prefix: demo → btn-title-edit-demo-*; live → btn-title-edit-live-* */
  testPrefix: 'demo' | 'live'
  titleKey: 'titleImage.editDemoTitle' | 'titleImage.editPanelTitle'
  hintKey: 'titleImage.editDemoHint' | 'titleImage.editPanelHint'
  filename: string
  emptyHintKey?: 'titleImage.needComposeOrTitle'
}

export default function TitleImageEditPanel({
  photos,
  headings,
  testPrefix,
  titleKey,
  hintKey,
  filename,
  emptyHintKey,
}: Props) {
  const { t } = useTranslation()
  const cleanHeadings = useMemo(
    () => headings.map((h) => h.trim()).filter(Boolean).slice(0, 5),
    [headings]
  )
  const [photoId, setPhotoId] = useState<string | null>(photos[0]?.id ?? null)
  const [headingIdx, setHeadingIdx] = useState(0)
  const [writing, setWriting] = useState<WritingMode>('h')
  const [vAlign, setVAlign] = useState<VAlign>('middle')
  const [hAlign, setHAlign] = useState<HAlign>('center')
  const [fontScale, setFontScale] = useState<FontScale>('md')
  const [fontFace, setFontFace] = useState<FontFace>('hei')
  const [titleBg, setTitleBg] = useState<TitleBg>('black')
  const [preview, setPreview] = useState<string | null>(null)
  const [previewing, setPreviewing] = useState(false)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    if (!photos.length) {
      setPhotoId(null)
      return
    }
    if (!photoId || !photos.some((p) => p.id === photoId)) {
      setPhotoId(photos[0].id)
    }
  }, [photos, photoId])

  useEffect(() => {
    if (headingIdx >= cleanHeadings.length) setHeadingIdx(0)
  }, [cleanHeadings.length, headingIdx])

  const photo = photos.find((p) => p.id === photoId) || photos[0] || null
  const heading = cleanHeadings[headingIdx] || ''
  const tid = (suffix: string) => `btn-title-edit-${testPrefix}-${suffix}`
  const sid = (suffix: string) => `section-title-edit-${testPrefix}-${suffix}`

  const editOpts = useMemo(() => {
    if (!photo || !heading) return null
    return {
      photoUrl: photo.url,
      heading,
      vAlign,
      hAlign,
      fontScale,
      writing,
      fontFace,
      titleBg,
    }
  }, [photo, heading, vAlign, hAlign, fontScale, writing, fontFace, titleBg])

  useEffect(() => {
    if (!editOpts) {
      setPreview(null)
      return
    }
    let cancelled = false
    const timer = window.setTimeout(() => {
      setPreviewing(true)
      void renderEditPreviewDataUrl(editOpts)
        .then((url) => {
          if (!cancelled) setPreview(url)
        })
        .catch(() => {
          if (!cancelled) setPreview(null)
        })
        .finally(() => {
          if (!cancelled) setPreviewing(false)
        })
    }, 80)
    return () => {
      cancelled = true
      window.clearTimeout(timer)
    }
  }, [editOpts])

  const confirmDownload = async () => {
    if (!editOpts) return
    setBusy(true)
    try {
      await renderAndDownloadEdit({ ...editOpts, filename })
      showSuccess(t('titleImage.demoDownloadDone'))
    } catch {
      showError(t('common.failed'))
    } finally {
      setBusy(false)
    }
  }

  const chip = (on: boolean) =>
    `min-h-[40px] px-3 rounded-xl border-2 text-xs font-medium touch-manipulation ${
      on ? 'border-primary bg-primary/10 text-primary' : 'border-gray-200 text-gray-700'
    }`

  const sectionTestId =
    testPrefix === 'demo' ? 'section-title-image-edit-demo' : 'section-title-image-edit-live'

  if (!photos.length) {
    return (
      <section
        className="bg-white rounded-2xl border border-gray-100 p-5 sm:p-6 space-y-2"
        data-testid={sectionTestId}
      >
        <h2 className="font-display text-lg font-semibold">{t(titleKey)}</h2>
        <p className="text-sm text-amber-800" data-testid={`text-title-edit-${testPrefix}-no-photo`}>
          {t('titleImage.missingPhoto')}
        </p>
      </section>
    )
  }

  return (
    <section
      className="bg-white rounded-2xl border border-gray-100 p-5 sm:p-6 space-y-4"
      data-testid={sectionTestId}
    >
      <div className="space-y-1">
        <h2 className="font-display text-lg font-semibold">{t(titleKey)}</h2>
        <p className="text-xs text-gray-500">{t(hintKey)}</p>
      </div>

      <div className="space-y-2" data-testid={sid('result')}>
        <p className="text-xs font-medium text-gray-500">{t('titleImage.editLivePreview')}</p>
        <div className="relative aspect-square overflow-hidden rounded-xl border border-gray-100 bg-slate-900">
          {preview && heading ? (
            <img
              src={preview}
              alt=""
              className={`h-full w-full object-cover transition-opacity ${previewing ? 'opacity-70' : 'opacity-100'}`}
              data-testid={`img-title-edit-${testPrefix}-preview`}
            />
          ) : (
            <div
              className="flex h-full items-center justify-center text-sm text-slate-400 px-4 text-center"
              data-testid={`text-title-edit-${testPrefix}-preview-empty`}
            >
              {cleanHeadings.length
                ? t('common.loading')
                : t(emptyHintKey || 'titleImage.needComposeOrTitle')}
            </div>
          )}
        </div>
      </div>

      <p className="text-xs font-medium text-gray-500">{t('titleImage.stepPhoto')}</p>
      <div
        className={`grid gap-2 ${photos.length >= 3 ? 'grid-cols-3' : 'grid-cols-2'}`}
        data-testid={`grid-title-edit-${testPrefix}-photos`}
      >
        {photos.map((p) => (
          <button
            key={p.id}
            type="button"
            data-testid={tid(`photo-${p.id}`)}
            onClick={() => setPhotoId(p.id)}
            className={`aspect-square overflow-hidden rounded-xl border-2 ${
              photoId === p.id ? 'border-primary' : 'border-transparent'
            }`}
          >
            <img src={p.url} alt="" className="w-full h-full object-cover" />
          </button>
        ))}
      </div>

      <p className="text-xs font-medium text-gray-500">{t('titleImage.stepHeading')}</p>
      {cleanHeadings.length === 0 ? (
        <p className="text-sm text-amber-800" data-testid={`text-title-edit-${testPrefix}-need-heading`}>
          {t(emptyHintKey || 'titleImage.needComposeOrTitle')}
        </p>
      ) : (
        <div className="space-y-2" data-testid={sid('headings')}>
          {cleanHeadings.map((h, i) => (
            <button
              key={`${i}-${h.slice(0, 12)}`}
              type="button"
              data-testid={tid(`heading-${i + 1}`)}
              onClick={() => setHeadingIdx(i)}
              className={`w-full text-left px-3 py-2 rounded-xl border-2 text-sm min-h-[44px] ${
                headingIdx === i ? 'border-primary bg-primary/10' : 'border-gray-200'
              }`}
            >
              {h}
            </button>
          ))}
        </div>
      )}

      <p className="text-xs font-medium text-gray-500">{t('titleImage.editWriting')}</p>
      <div className="flex flex-wrap gap-2" data-testid={sid('writing')}>
        {W_OPTS.map((w) => (
          <button
            key={w}
            type="button"
            data-testid={tid(`writing-${w}`)}
            className={chip(writing === w)}
            onClick={() => setWriting(w)}
          >
            {t(`titleImage.writing.${w}` as 'titleImage.writing.h')}
          </button>
        ))}
      </div>

      <p className="text-xs font-medium text-gray-500">{t('titleImage.editFace')}</p>
      <div className="flex flex-wrap gap-2" data-testid={sid('face')}>
        {FACE_OPTS.map((f) => (
          <button
            key={f}
            type="button"
            data-testid={tid(`face-${f}`)}
            className={chip(fontFace === f)}
            onClick={() => setFontFace(f)}
          >
            {t(`titleImage.face.${f}` as 'titleImage.face.hei')}
          </button>
        ))}
      </div>

      <p className="text-xs font-medium text-gray-500">{t('titleImage.editTitleBg')}</p>
      <div className="grid grid-cols-5 gap-2" data-testid={sid('bg')}>
        {TITLE_BG_OPTS.map((bg) => {
          const on = titleBg === bg
          return (
            <button
              key={bg}
              type="button"
              title={t(`titleImage.bg.${bg}` as 'titleImage.bg.black')}
              data-testid={tid(`bg-${bg}`)}
              aria-label={t(`titleImage.bg.${bg}` as 'titleImage.bg.black')}
              onClick={() => setTitleBg(bg)}
              className={`aspect-square rounded-xl border-2 touch-manipulation ${
                on ? 'border-primary ring-2 ring-primary/30' : 'border-gray-200'
              }`}
              style={{ background: TITLE_BG_PALETTE[bg].swatch }}
            />
          )
        })}
      </div>

      <p className="text-xs font-medium text-gray-500">{t('titleImage.editVAlign')}</p>
      <div className="flex flex-wrap gap-2">
        {V_OPTS.map((v) => (
          <button
            key={v}
            type="button"
            data-testid={tid(`v-${v}`)}
            className={chip(vAlign === v)}
            onClick={() => setVAlign(v)}
          >
            {t(`titleImage.v.${v}` as 'titleImage.v.top')}
          </button>
        ))}
      </div>

      <p className="text-xs font-medium text-gray-500">{t('titleImage.editHAlign')}</p>
      <div className="flex flex-wrap gap-2">
        {H_OPTS.map((h) => (
          <button
            key={h}
            type="button"
            data-testid={tid(`h-${h}`)}
            className={chip(hAlign === h)}
            onClick={() => setHAlign(h)}
          >
            {t(`titleImage.h.${h}` as 'titleImage.h.left')}
          </button>
        ))}
      </div>

      <p className="text-xs font-medium text-gray-500">{t('titleImage.editFont')}</p>
      <div className="flex flex-wrap gap-2">
        {F_OPTS.map((f) => (
          <button
            key={f}
            type="button"
            data-testid={tid(`font-${f}`)}
            className={chip(fontScale === f)}
            onClick={() => setFontScale(f)}
          >
            {t(`titleImage.font.${f}` as 'titleImage.font.sm')}
          </button>
        ))}
      </div>

      <button
        type="button"
        data-testid={tid('confirm')}
        disabled={busy || !preview || !heading}
        onClick={() => void confirmDownload()}
        className="w-full min-h-[44px] rounded-xl bg-primary text-white text-sm font-medium disabled:opacity-50"
      >
        {busy ? t('common.loading') : t('titleImage.editConfirm')}
      </button>
    </section>
  )
}
