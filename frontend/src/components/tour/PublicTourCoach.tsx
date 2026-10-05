import { useTranslation, type TranslationKey } from '@/i18n'
import { TOUR_STEPS } from '@/lib/publicTour'

const TITLE: Record<number, TranslationKey> = {
  1: 'tour.public.step1Title',
  2: 'tour.public.step2Title',
  3: 'tour.public.step3Title',
  4: 'tour.public.step4Title',
  5: 'tour.public.step5Title',
}
const BODY: Record<number, TranslationKey> = {
  1: 'tour.public.step1Body',
  2: 'tour.public.step2Body',
  3: 'tour.public.step3Body',
  4: 'tour.public.step4Body',
  5: 'tour.public.step5Body',
}
const CTA: Record<number, TranslationKey> = {
  1: 'tour.public.step1Cta',
  2: 'tour.public.step2Cta',
  3: 'tour.public.step3Cta',
  4: 'tour.public.step4Cta',
}

type Props = {
  step: number
  onNext: () => void
  onSkipStep: () => void
  onSkipAll: () => void
  onCopyIg?: () => void
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

  return (
    <aside
      className="fixed bottom-4 left-4 right-4 z-40 mx-auto max-w-lg rounded-2xl border border-gray-200 bg-white p-4 shadow-lg"
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
  )
}
