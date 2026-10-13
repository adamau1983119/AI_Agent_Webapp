import { useEffect, useRef, useState, type CSSProperties } from 'react'
import { createPortal } from 'react-dom'
import { useTranslation, type TranslationKey } from '@/i18n'
import { TOUR_STEPS, findTourAnchor } from '@/lib/publicTour'

const PURPLE = '#581c87'
const TITLE: Record<number, TranslationKey> = {
  1: 'tour.public.step1Title',
  2: 'tour.public.platformTitle',
  3: 'tour.public.lengthTitle',
  4: 'tour.public.styleTitle',
  5: 'tour.public.generateTitle',
  6: 'tour.public.titleImageTitle',
  7: 'tour.public.copyTitle',
}
const BODY: Record<number, TranslationKey> = {
  1: 'tour.public.step1Body',
  2: 'tour.public.platformBody',
  3: 'tour.public.lengthBody',
  4: 'tour.public.styleBody',
  5: 'tour.public.generateBody',
  6: 'tour.public.titleImageBody',
  7: 'tour.public.copyBody',
}

type Box = {
  top: number
  left: number
  width: number
  height: number
  panelLeft: number
  panelTop: number
}

type Props = {
  step: number
  onNext: () => void
  onSkipStep: () => void
  onSkipAll: () => void
  onCopyIg?: () => void
}

function measureAnchor(el: HTMLElement, panel: HTMLElement | null): Box {
  const r = el.getBoundingClientRect()
  const panelW = Math.min(448, window.innerWidth - 32)
  let panelLeft = r.left
  if (panelLeft + panelW > window.innerWidth - 16) panelLeft = window.innerWidth - 16 - panelW
  if (panelLeft < 16) panelLeft = 16
  const panelH = panel?.offsetHeight || 200
  const gap = 12
  let panelTop = r.bottom + gap
  if (panelTop + panelH > window.innerHeight - 16) panelTop = r.top - gap - panelH
  if (panelTop < 16) panelTop = 16
  const overlaps = panelTop < r.bottom + 4 && panelTop + panelH > r.top - 4
  if (overlaps) {
    const above = r.top - gap - panelH
    panelTop = above >= 16 ? above : Math.max(16, r.bottom + gap)
  }
  return {
    top: r.top,
    left: r.left,
    width: r.width,
    height: r.height,
    panelLeft,
    panelTop,
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
  const panelRef = useRef<HTMLElement | null>(null)
  const [box, setBox] = useState<Box | null>(null)

  useEffect(() => {
    let stopped = false
    let frames = 0
    let stable = 0
    let last = ''
    let raf = 0
    const tick = () => {
      if (stopped) return
      const el = findTourAnchor(step)
      const next = el ? measureAnchor(el, panelRef.current) : null
      const key = next
        ? [next.top, next.left, next.width, next.height, next.panelTop].map((n) => Math.round(n)).join(':')
        : 'none'
      stable = key === last ? stable + 1 : 0
      last = key
      setBox(next)
      frames += 1
      if (stable < 4 && frames < 45) raf = window.requestAnimationFrame(tick)
    }
    const kick = () => {
      frames = 0
      stable = 0
      window.cancelAnimationFrame(raf)
      raf = window.requestAnimationFrame(tick)
    }
    kick()
    window.addEventListener('scroll', kick, true)
    window.addEventListener('resize', kick)
    return () => {
      stopped = true
      window.cancelAnimationFrame(raf)
      window.removeEventListener('scroll', kick, true)
      window.removeEventListener('resize', kick)
    }
  }, [step])

  const panelStyle: CSSProperties = box
    ? {
        position: 'fixed',
        left: box.panelLeft,
        width: 'min(28rem, calc(100vw - 2rem))',
        top: box.panelTop,
        maxHeight: 'calc(100vh - 2rem)',
        overflow: 'auto',
        backgroundColor: PURPLE,
        color: '#ffffff',
      }
    : { backgroundColor: PURPLE, color: '#ffffff' }

  const primaryBtn =
    'min-h-[44px] px-4 rounded-full bg-white text-[11px] tracking-[0.14em] uppercase'
  const ghostBtn =
    'min-h-[44px] px-4 rounded-full border border-white text-white text-[11px] tracking-[0.14em] uppercase'

  const card = (
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
        ref={panelRef}
        className={
          box
            ? 'z-40 max-w-lg rounded-2xl border border-[#581c87] p-4 shadow-lg'
            : 'fixed bottom-4 left-4 right-4 z-40 mx-auto max-w-lg rounded-2xl border border-[#581c87] p-4 shadow-lg'
        }
        style={panelStyle}
        data-testid="panel-tour-public"
        aria-label={t('tour.public.aria')}
      >
        <p className="text-[11px] uppercase tracking-[0.14em] text-white" data-testid="text-tour-public-progress">
          {t('tour.public.progress', { n: String(step), total: String(TOUR_STEPS) })}
        </p>
        <h2 className="mt-2 text-sm font-medium text-white">{t(TITLE[step] || TITLE[1])}</h2>
        <p className="mt-1 text-sm text-white leading-relaxed">{t(BODY[step] || BODY[1])}</p>
        <div className="mt-4 flex flex-wrap gap-2">
          {isLast ? (
            <>
              <button
                type="button"
                data-testid="btn-tour-public-copy-ig"
                onClick={onCopyIg}
                className={primaryBtn}
                style={{ color: PURPLE }}
              >
                {t('tour.public.step5Cta')}
              </button>
              <button
                type="button"
                data-testid="btn-tour-public-finish"
                onClick={onNext}
                className={ghostBtn}
              >
                {t('tour.public.finish')}
              </button>
            </>
          ) : (
            <button
              type="button"
              data-testid="btn-tour-public-next"
              onClick={onNext}
              className={primaryBtn}
              style={{ color: PURPLE }}
            >
              {t(step === 1 ? 'tour.public.step1Cta' : 'tour.public.step2Cta')}
            </button>
          )}
          <button
            type="button"
            data-testid="btn-tour-public-skip-step"
            onClick={onSkipStep}
            className={ghostBtn}
          >
            {t('tour.public.skipStep')}
          </button>
          <button
            type="button"
            data-testid="btn-tour-public-skip-all"
            onClick={onSkipAll}
            className="min-h-[44px] px-3 text-[11px] text-white underline"
          >
            {t('tour.public.skipAll')}
          </button>
        </div>
      </aside>
    </>
  )

  return createPortal(card, document.body)
}
