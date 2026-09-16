/**
 * Black credit-pack cards + display-currency toggle (charge remains USD).
 * Pack rights lists: honest qty / unit-price diffs (✓／✗), ChatGPT-style columns.
 */
import { useEffect, useState } from 'react'
import { Check, X } from 'lucide-react'
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

type RightItem = { ok: boolean; key: string }

const PACK_META: Record<
  string,
  { taglineKey: string; stackKey?: string; rights: RightItem[] }
> = {
  usd3: {
    taglineKey: 'credits.pack.usd3.tagline',
    rights: [
      { ok: true, key: 'credits.pack.usd3.r1' },
      { ok: true, key: 'credits.pack.usd3.r2' },
      { ok: true, key: 'credits.pack.usd3.r3' },
      { ok: false, key: 'credits.pack.usd3.x1' },
    ],
  },
  usd5: {
    taglineKey: 'credits.pack.usd5.tagline',
    stackKey: 'credits.pack.usd5.stack',
    rights: [
      { ok: true, key: 'credits.pack.usd5.r1' },
      { ok: true, key: 'credits.pack.usd5.r2' },
      { ok: true, key: 'credits.pack.usd5.r3' },
      { ok: false, key: 'credits.pack.usd5.x1' },
    ],
  },
  usd10: {
    taglineKey: 'credits.pack.usd10.tagline',
    stackKey: 'credits.pack.usd10.stack',
    rights: [
      { ok: true, key: 'credits.pack.usd10.r1' },
      { ok: true, key: 'credits.pack.usd10.r2' },
      { ok: true, key: 'credits.pack.usd10.r3' },
    ],
  },
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
          <p className="mt-3 text-[12px] leading-relaxed text-white/55 max-w-xl text-left">
            {t('credits.shelfBlurb')}
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

      <div className="mt-8 grid gap-3 sm:grid-cols-3 items-stretch">
        {packs.map((pack) => {
          const recommended = pack.id === 'usd5'
          const local = formatLocalFromCents(pack.amount_cents, currency)
          const usd = formatUsdFromCents(pack.amount_cents)
          const headline =
            currency === 'USD' ? usd : t('credits.fxApprox', { amount: local })
          const meta = PACK_META[pack.id] ?? PACK_META.usd3
          const ctaClass =
            'mt-5 inline-flex items-center justify-center min-h-[44px] w-full rounded-full border border-white text-[11px] tracking-[0.16em] uppercase hover:bg-white hover:text-[#0d0d0d] transition-colors disabled:opacity-50'

          return (
            <article
              key={pack.id}
              data-testid={`card-${testPrefix}-pack-${pack.id}`}
              className={`rounded-2xl px-5 py-6 flex flex-col border ${
                recommended ? 'border-white' : 'border-white/15'
              }`}
            >
              {recommended && (
                <p className="text-[9px] tracking-[0.2em] uppercase text-white/80 mb-2 text-center">
                  {t('credits.recommended')}
                </p>
              )}
              <p className="text-[11px] text-white/65 text-center leading-snug min-h-[2.5em]">
                {t(meta.taglineKey)}
              </p>
              <p
                className={
                  testPrefix === 'landing'
                    ? 'mt-3 font-price text-4xl font-medium tracking-tight tabular-nums text-center'
                    : 'mt-3 font-display text-3xl text-center'
                }
              >
                {headline}
              </p>
              <p className="mt-2 text-sm tracking-[0.08em] text-center">
                {t('credits.packCredits', { n: String(pack.credits) })}
              </p>
              {currency !== 'USD' && (
                <p className="mt-1 text-[11px] text-white/50 text-center">{usd}</p>
              )}

              {mode === 'guest' ? (
                <Link
                  to="/login"
                  data-testid={`btn-${testPrefix}-pack-${pack.id}`}
                  className={ctaClass}
                >
                  {t('credits.select')}
                </Link>
              ) : (
                <button
                  type="button"
                  data-testid={`btn-${testPrefix}-buy-${pack.id}`}
                  disabled={buying !== null}
                  onClick={() => onBuy?.(pack.id)}
                  className={ctaClass}
                >
                  {t('credits.buy')}
                </button>
              )}

              {meta.stackKey && (
                <p className="mt-5 text-[11px] text-white/70 text-left font-medium">
                  {t(meta.stackKey)}
                </p>
              )}

              <ul
                data-testid={`list-${testPrefix}-pack-rights-${pack.id}`}
                className={`space-y-2.5 text-left ${meta.stackKey ? 'mt-3' : 'mt-5'} flex-1`}
              >
                {meta.rights.map((item) => (
                  <li key={item.key} className="flex gap-2 items-start text-[12px] leading-snug">
                    {item.ok ? (
                      <Check
                        className="w-4 h-4 shrink-0 mt-0.5 text-white"
                        strokeWidth={2.5}
                        aria-hidden
                      />
                    ) : (
                      <X
                        className="w-4 h-4 shrink-0 mt-0.5 text-white/45"
                        strokeWidth={2.5}
                        aria-hidden
                      />
                    )}
                    <span className={item.ok ? 'text-white/85' : 'text-white/45'}>
                      {t(item.key)}
                    </span>
                  </li>
                ))}
              </ul>
            </article>
          )
        })}
      </div>
    </div>
  )
}
