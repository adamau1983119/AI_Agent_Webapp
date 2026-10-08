import { useEffect, useState, type CSSProperties } from 'react'
import { useTranslation, type TranslationKey } from '@/i18n'
import { TOUR_STEPS, tourAnchorTestId } from '@/lib/publicTour'

const TITLE: Record<number, TranslationKey> = {
  1: 'tour.public.step1Title',
  2: 'tour.public.lengthTitle',
  3: 'tour.public.styleTitle',
  4: 'tour.public.generateTitle',
  5: 'tour.public.photosTitle',
  6: 'tour.public.copyTitle',
}
const BODY: Record<number, TranslationKey> = {
  1: 'tour.public.step1Body',
  2: 'tour.public.lengthBody',
  3: 'tour.public.styleBody',
  4: 'tour.public.generateBody',
  5: 'tour.public.photosBody',
  6: 'tour.public.copyBody',
}
const CTA: Record<number, TranslationKey> = {
  1: 'tour.public.step1Cta',
  2: 'tour.public.step2Cta',
  3: 'tour.public.step3Cta',
  4: 'tour.public.step4Cta',
  5: 'tour.public.step2Cta',
}

type Box = {
  top: number
  left: number
  width: number
  height: number
  panelLeft: number
  placeBelow: boolean
}

type Props = {
  step: number
  onNext: () => void
  onSkipStep: () => void
  onSkipAll: () => void
  onCopyIg?: () => void
}

function measureAnchor(testId: string): Box | null {
  const el = document.querySelector(`[data-testid="${testId}"]`)
  if (!(el instanceof HTMLElement)) return null
  const r = el.getBoundingClientRect()
  if (r.width < 2 || r.height < 2) return null
  const panelW = Math.min(448, window.innerWidth - 32)
  let panelLeft = r.left
  if (panelLeft + panelW > window.innerWidth - 16) panelLeft = window.innerWidth - 16 - panelW
  if (panelLeft < 16) panelLeft = 16
  const placeBelow = r.bottom + 200 < window.innerHeight || r.top < 180
  return {
    top: r.top,
    left: r.left,
    width: r.width,
    height: r.height,
    panelLeft,
    placeBelow,
  }
}

export default function PublicTourCoach({
  step,
  onNext,
  onSkipStep,
  onSkipAll,
  onCopyIg,
}: Props) {
  const { t } = useTranslation()
  const isLast = step === TOUR_STEPS
  const anchorId = tourAnchorTestId(step)
  const [box, setBox] = useState<Box | null>(null)

  useEffect(() => {
    if (!anchorId) {
      setBox(null)
      return
    }
    const update = () => setBox(measureAnchor(anchorId))
    update()
    const timer = window.setTimeout(update, 350)
    window.addEventListener('scroll', update, true)
    window.addEventListener('resize', update)
    return () => {
      window.clearTimeout(timer)
      window.removeEventListener('scroll', update, true)
      window.removeEventListener('resize', update)
    }
  }, [anchorId, step])

  const panelClass =
    'z-40 max-w-lg rounded-2xl border border-gray-200 bg-white p-4 shadow-lg'
  const panelStyle: CSSProperties = box
    ? {
        position: 'fixed',
        left: box.panelLeft,
        width: 'min(28rem, calc(100vw - 2rem))',
        top: box.placeBelow ? box.top + box.height + 12 : undefined,
        bottom: box.placeBelow ? undefined : window.innerHeight - box.top + 12,
      }
    : {}

  return (
    <>
      {box ? (
        <div
          className="fixed z-30 pointer-events-none rounded-xl ring-2 ring-black"
          data-testid="frame-tour-public-anchor"
          style={{
            top: box.top - 4,
            left: box.left - 4,
            width: box.width + 8,
            height: box.height + 8,
          }}
        />
      ) : null}
      <aside
        className={box ? panelClass : `fixed bottom-4 left-4 right-4 mx-auto ${panelClass}`}
        style={box ? panelStyle : undefined}
        data-testid="panel-tour-public"
        aria-label={t('tour.public.aria')}
      >
        <p className="text-[11px] uppercase tracking-[0.14em] text-gray-500" data-testid="text-tour-public-progress">
          {t('tour.public.progress', { n: String(step), total: String(TOUR_STEPS) })}
        </p>
        <h2 className="mt-2 text-sm font-medium text-gray-900">{t(TITLE[step] || TITLE[1])}</h2>
        <p className="mt-1 text-sm text-gray-600 leading-relaxed">{t(BODY[step] || BODY[1])}</p>
        <div className="mt-4 flex flex-wrap gap-2">
          {isLast ? (
            <>
              <button
                type="button"
                data-testid="btn-tour-public-copy-ig"
                onClick={onCopyIg}
                className="min-h-[44px] px-4 rounded-full bg-black text-white text-[11px] tracking-[0.14em] uppercase"
              >
                {t('tour.public.step5Cta')}
              </button>
              <button
                type="button"
                data-testid="btn-tour-public-finish"
                onClick={onNext}
                className="min-h-[44px] px-4 rounded-full border border-black text-[11px] tracking-[0.14em] uppercase"
              >
                {t('tour.public.finish')}
              </button>
            </>
          ) : (
            <button
              type="button"
              data-testid="btn-tour-public-next"
              onClick={onNext}
              className="min-h-[44px] px-4 rounded-full bg-black text-white text-[11px] tracking-[0.14em] uppercase"
            >
              {t(CTA[step] || CTA[1])}
            </button>
          )}
          <button
            type="button"
            data-testid="btn-tour-public-skip-step"
            onClick={onSkipStep}
            className="min-h-[44px] px-4 rounded-full border border-gray-300 text-[11px] tracking-[0.14em] uppercase"
          >
            {t('tour.public.skipStep')}
          </button>
          <button
            type="button"
            data-testid="btn-tour-public-skip-all"
            onClick={onSkipAll}
            className="min-h-[44px] px-3 text-[11px] text-gray-500 underline"
          >
            {t('tour.public.skipAll')}
          </button>
        </div>
      </aside>
    </>
  )
}
