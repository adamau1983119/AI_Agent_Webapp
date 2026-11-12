/**
 * Credit offer card (MTR-style two-col numerals). Used on Welcome + samples.
 */
import { Link } from 'react-router-dom'
import {
  translateFor,
  useTranslation,
  type Language,
  type TranslationKey,
} from '@/i18n'

const WELCOME = '100'
const DAILY = '+20'
const DEFAULT_COST = '10'

const numClass =
  'font-price font-medium tracking-tight tabular-nums text-[#1a1a1a] leading-none'

function label(lang: Language | undefined, key: TranslationKey, t: (k: TranslationKey) => string) {
  return lang ? translateFor(lang, key) : t(key)
}

export type GuestCreditOfferCardProps = {
  /** When set, copy is read for that locale (sample dual cards). */
  lang?: Language
  registerTestId: string
  loginTestId: string
  cancelTestId?: string
  showCancel?: boolean
  /** Close modal without leaving the page (TopicDetail). */
  onCancel?: () => void
  /** This-generate cost; omit / null hides the cost row. */
  costValue?: string | null
  kicker?: string
  cardTestId?: string
  className?: string
}

export default function GuestCreditOfferCard({
  lang,
  registerTestId,
  loginTestId,
  cancelTestId,
  showCancel = false,
  onCancel,
  costValue = DEFAULT_COST,
  kicker,
  cardTestId,
  className = '',
}: GuestCreditOfferCardProps) {
  const { t } = useTranslation()
  const L = (key: TranslationKey) => label(lang, key, t)
  const showCost = costValue !== null && costValue !== undefined

  return (
    <div
      data-testid={cardTestId}
      className={`bg-white rounded-2xl shadow-xl p-6 w-full text-center space-y-5 border border-[#e8e4de] ${className}`}
    >
      {kicker ? (
        <p className="text-[10px] tracking-[0.16em] uppercase text-[#8a8a8a]">{kicker}</p>
      ) : null}

      <h2 className="text-lg font-semibold font-display text-[#1a1a1a]">
        {L('welcomeOffer.title')}
      </h2>

      <p className="text-sm text-[#6b6b6b] font-sans leading-relaxed">
        {L('guestChargeSample.lead')}
      </p>

      <div className="flex items-center gap-3">
        <div className="h-px flex-1 bg-[#e0dcd6]" />
        <p className="text-xs tracking-[0.12em] text-[#1a1a1a] shrink-0">
          {L('guestChargeSample.sectionEarn')}
        </p>
        <div className="h-px flex-1 bg-[#e0dcd6]" />
      </div>

      <div className="grid grid-cols-2 rounded-xl bg-[#f3f1ed] overflow-hidden border border-[#e8e4de]">
        <div className="px-3 py-5 border-r border-[#e0dcd6]">
          <p className={`${numClass} text-4xl`}>{WELCOME}</p>
          <p className="mt-2 text-xs text-[#6b6b6b] font-sans leading-snug">
            {L('guestChargeSample.welcomeLabel')}
          </p>
        </div>
        <div className="px-3 py-5">
          <p className={`${numClass} text-4xl`}>{DAILY}</p>
          <p className="mt-2 text-xs text-[#6b6b6b] font-sans leading-snug">
            {L('guestChargeSample.dailyLabel')}
          </p>
        </div>
      </div>

      <p className="text-xs text-[#8a8a8a] font-sans leading-relaxed">
        {L('guestChargeSample.useLine')}
      </p>

      {showCost ? (
        <div className="flex items-center justify-center gap-2 rounded-xl border border-[#e0dcd6] bg-[#faf9f7] px-4 py-3">
          <span className="text-xs text-[#6b6b6b] font-sans">
            {L('guestChargeSample.costLabel')}
          </span>
          <span className={`${numClass} text-2xl`}>{costValue}</span>
          <span className="text-xs text-[#6b6b6b] font-sans">
            {L('guestChargeSample.costUnit')}
          </span>
        </div>
      ) : null}

      <div className="flex flex-col gap-3 pt-1">
        <Link
          to="/register"
          data-testid={registerTestId}
          className="px-4 py-2 text-sm font-medium text-white bg-primary rounded-xl min-h-[44px] flex items-center justify-center hover:bg-primary-dark touch-manipulation"
        >
          {L('welcomeOffer.cta')}
        </Link>
        <Link
          to="/login"
          data-testid={loginTestId}
          className="px-4 py-2 text-sm font-medium text-[#1a1a1a] border border-[#1a1a1a] rounded-xl min-h-[44px] flex items-center justify-center touch-manipulation"
        >
          {L('landing.cta.login')}
        </Link>
        {showCancel && cancelTestId ? (
          onCancel ? (
            <button
              type="button"
              data-testid={cancelTestId}
              onClick={onCancel}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-xl min-h-[44px] touch-manipulation"
            >
              {L('common.cancel')}
            </button>
          ) : (
            <Link
              to="/dashboard"
              data-testid={cancelTestId}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-xl min-h-[44px] flex items-center justify-center"
            >
              {L('common.cancel')}
            </Link>
          )
        ) : null}
      </div>
    </div>
  )
}
