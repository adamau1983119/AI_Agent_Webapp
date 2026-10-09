import { useTranslation } from '@/i18n'

type Props = {
  onChannel: () => void
  onCompose: () => void
}

export default function FirstRunChoice({ onChannel, onCompose }: Props) {
  const { t } = useTranslation()
  return (
    <section
      className="mb-8 bg-white border border-gray-200 p-6 sm:p-8"
      data-testid="section-dashboard-first-run"
    >
      <h2 className="font-display text-2xl font-light tracking-wide text-black">
        {t('dashboard.firstRunTitle')}
      </h2>
      <p className="mt-3 text-sm text-gray-600 leading-relaxed">{t('dashboard.firstRunBody')}</p>
      <div className="mt-6 flex flex-col sm:flex-row gap-3">
        <button
          type="button"
          data-testid="btn-dashboard-first-run-channel"
          onClick={onChannel}
          className="min-h-[44px] px-5 bg-black text-white text-[11px] tracking-[0.14em] uppercase"
        >
          {t('dashboard.firstRunChannel')}
        </button>
        <button
          type="button"
          data-testid="btn-dashboard-first-run-compose"
          onClick={onCompose}
          className="min-h-[44px] px-5 border border-black text-[11px] tracking-[0.14em] uppercase"
        >
          {t('dashboard.firstRunCompose')}
        </button>
      </div>
    </section>
  )
}
