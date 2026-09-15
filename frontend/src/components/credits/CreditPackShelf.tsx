/**
 * Black credit-pack cards + display-currency toggle (charge remains USD).
 */
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import type { CreditPack } from '@/api/billing'
import { useTranslation } from '@/i18n'
import {
  DISPLAY_CURRENCIES,
  FX_AS_OF,
  formatLocalFromCents,
  formatUsdFromCents,
  loadDisplayCurrency,
  saveDisplayCurrency,
  type DisplayCurrency,
} from '@/lib/creditDisplay'

type Props = {
  packs: CreditPack[]
  mode: 'guest' | 'buy'
  testPrefix: 'landing' | 'settings'
  buying?: string | null
  onBuy?: (packId: string) => void
}

export default function CreditPackShelf({
  packs,
  mode,
  testPrefix,
  buying = null,
  onBuy,
}: Props) {
  const { t } = useTranslation()
  const [currency, setCurrency] = useState<DisplayCurrency>('USD')

  useEffect(() => {
    setCurrency(loadDisplayCurrency())
  }, [])

  const choose = (code: DisplayCurrency) => {
    setCurrency(code)
    saveDisplayCurrency(code)
  }

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
        <div>
          <h2 className="font-display text-2xl tracking-[0.12em] uppercase">
            {t('credits.shelfTitle')}
          </h2>
          <p className="mt-2 text-[11px] tracking-[0.14em] uppercase text-white/70">
            {t('credits.shelfOnce')}
          </p>
        </div>
        <div>
          <p className="text-[10px] tracking-[0.16em] uppercase text-white/50 mb-2">
            {t('credits.fxLabel')}
          </p>
          <div className="flex flex-wrap gap-1">
            {DISPLAY_CURRENCIES.map((code) => (
              <button
                key={code}
                type="button"
                data-testid={`btn-${testPrefix}-fx-${code.toLowerCase()}`}
                onClick={() => choose(code)}
                className={`min-h-[44px] px-2.5 text-[10px] tracking-[0.12em] uppercase rounded-full border ${
                  currency === code
                    ? 'bg-white text-[#0d0d0d] border-white'
                    : 'border-white/30 text-white/80 hover:border-white'
                }`}
              >
                {code}
              </button>
            ))}
          </div>
          <p className="mt-2 text-[10px] text-white/45">
            {t('credits.fxPaidUsd')} · {t('credits.fxAsOf', { date: FX_AS_OF })}
          </p>
        </div>
      </div>

      <div className="mt-8 grid gap-3 sm:grid-cols-3">
        {packs.map((pack) => {
          const recommended = pack.id === 'usd5'
          const local = formatLocalFromCents(pack.amount_cents, currency)
          const usd = formatUsdFromCents(pack.amount_cents)
          const headline =
            currency === 'USD' ? usd : t('credits.fxApprox', { amount: local })
          return (
            <article
              key={pack.id}
              data-testid={`card-${testPrefix}-pack-${pack.id}`}
              className={`rounded-2xl px-5 py-6 text-center border ${
                recommended ? 'border-white' : 'border-white/15'
              }`}
            >
              {recommended && (
                <p className="text-[9px] tracking-[0.2em] uppercase text-white/80 mb-3">
                  {t('credits.recommended')}
                </p>
              )}
              <p className="font-display text-3xl">{headline}</p>
              <p className="mt-2 text-sm tracking-[0.08em]">
                {t('credits.packCredits', { n: String(pack.credits) })}
              </p>
              {currency !== 'USD' && (
                <p className="mt-1 text-[11px] text-white/50">{usd}</p>
              )}
              {mode === 'guest' ? (
                <Link
                  to="/login"
                  data-testid={`btn-${testPrefix}-pack-${pack.id}`}
                  className="mt-5 inline-flex items-center justify-center min-h-[44px] w-full rounded-full border border-white text-[11px] tracking-[0.16em] uppercase hover:bg-white hover:text-[#0d0d0d] transition-colors"
                >
                  {t('credits.select')}
                </Link>
              ) : (
                <button
                  type="button"
                  data-testid={`btn-${testPrefix}-buy-${pack.id}`}
                  disabled={buying !== null}
                  onClick={() => onBuy?.(pack.id)}
                  className="mt-5 min-h-[44px] w-full rounded-full border border-white text-[11px] tracking-[0.16em] uppercase hover:bg-white hover:text-[#0d0d0d] disabled:opacity-50 transition-colors"
                >
                  {t('credits.buy')}
                </button>
              )}
            </article>
          )
        })}
      </div>
    </div>
  )
}
