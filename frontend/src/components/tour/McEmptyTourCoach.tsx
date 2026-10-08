import { useTranslation } from '@/i18n'

type Props = {
  onCreate: () => void
  onSkip: () => void
}

export default function McEmptyTourCoach({ onCreate, onSkip }: Props) {
  const { t } = useTranslation()
  return (
    <aside
      className="fixed bottom-4 left-4 right-4 z-40 mx-auto max-w-lg rounded-2xl border border-gray-200 bg-white p-4 shadow-lg"
      data-testid="panel-tour-mc"
      aria-label={t('tour.mc.aria')}
    >
      <p className="text-[11px] uppercase tracking-[0.14em] text-gray-500">{t('tour.mc.kicker')}</p>
      <h2 className="mt-2 text-sm font-medium text-gray-900">{t('tour.mc.title')}</h2>
      <p className="mt-1 text-sm text-gray-600 leading-relaxed">{t('tour.mc.body')}</p>
      <div className="mt-4 flex flex-wrap gap-2">
        <button
          type="button"
          data-testid="btn-tour-mc-create"
          onClick={onCreate}
          className="min-h-[44px] px-4 rounded-full bg-black text-white text-[11px] tracking-[0.14em] uppercase"
        >
          {t('tour.mc.cta')}
        </button>
        <button
          type="button"
          data-testid="btn-tour-mc-skip"
          onClick={onSkip}
          className="min-h-[44px] px-3 text-[11px] text-gray-500 underline"
        >
          {t('tour.mc.skip')}
        </button>
      </div>
    </aside>
  )
}
