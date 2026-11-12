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

function label(lang: Language | undefined, key: TranslationKey, t: (k: TranslationKey) => string) {
  return lang ? translateFor(lang, key) : t(key)
}

export type GuestCreditOfferCardProps = {
  /** When set, copy is read for that locale (sample dual cards). */
  lang?: Language
  registerTestId: string
  loginTestId?: string
  cancelTestId?: string
  showCancel?: boolean
  /** Welcome only: hide login (Hero already has it). */
  showLogin?: boolean
  /** Welcome only: black card + white type; modal keeps light brand card. */
  monoActions?: boolean
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
  showLogin = true,
  monoActions = false,
  onCancel,
  costValue = DEFAULT_COST,
  kicker,
  cardTestId,
  className = '',
}: GuestCreditOfferCardProps) {
  const { t } = useTranslation()
  const L = (key: TranslationKey) => label(lang, key, t)
  const showCost = costValue !== null && costValue !== undefined
  const dark = monoActions

  const cardShell = dark
    ? 'bg-black rounded-2xl shadow-xl p-6 w-full text-center space-y-5 border border-[#2a2a2a]'
    : 'bg-white rounded-2xl shadow-xl p-6 w-full text-center space-y-5 border border-[#e8e4de]'
  const titleClass = dark
    ? 'text-lg font-semibold font-display text-white'
    : 'text-lg font-semibold font-display text-[#1a1a1a]'
  const leadClass = dark
    ? 'text-sm text-[#b3b3b3] font-sans leading-relaxed'
    : 'text-sm text-[#6b6b6b] font-sans leading-relaxed'
  const kickerClass = dark
    ? 'text-[10px] tracking-[0.16em] uppercase text-[#8a8a8a]'
    : 'text-[10px] tracking-[0.16em] uppercase text-[#8a8a8a]'
  const ruleClass = dark ? 'h-px flex-1 bg-[#3a3a3a]' : 'h-px flex-1 bg-[#e0dcd6]'
  const sectionClass = dark
    ? 'text-xs tracking-[0.12em] text-white shrink-0'
    : 'text-xs tracking-[0.12em] text-[#1a1a1a] shrink-0'
  const gridClass = dark
    ? 'grid grid-cols-2 rounded-xl bg-white overflow-hidden border border-[#2a2a2a]'
    : 'grid grid-cols-2 rounded-xl bg-[#f3f1ed] overflow-hidden border border-[#e8e4de]'
  const cellBorder = dark
    ? 'px-3 py-5 border-r border-[#1a1a1a]'
    : 'px-3 py-5 border-r border-[#e0dcd6]'
  const numClass = 'font-price font-medium tracking-tight tabular-nums text-[#1a1a1a] leading-none'
  const labelMuted = 'mt-2 text-xs text-[#6b6b6b] font-sans leading-snug'
  const costNumClass = dark
    ? 'font-price font-medium tracking-tight tabular-nums text-white leading-none'
    : numClass
  const useLineClass = dark
    ? 'text-xs text-[#8a8a8a] font-sans leading-relaxed'
    : 'text-xs text-[#8a8a8a] font-sans leading-relaxed'
  const costRowClass = dark
    ? 'flex items-center justify-center gap-2 rounded-xl border border-[#3a3a3a] bg-[#141414] px-4 py-3'
    : 'flex items-center justify-center gap-2 rounded-xl border border-[#e0dcd6] bg-[#faf9f7] px-4 py-3'
  const costMuted = dark
    ? 'text-xs text-[#9a9a9a] font-sans'
    : 'text-xs text-[#6b6b6b] font-sans'
  const ctaClass = dark
    ? 'px-4 py-2 text-sm font-medium text-white rounded-xl min-h-[44px] flex items-center justify-center bg-[#3a3a3a] border border-[#555] hover:bg-[#4a4a4a] touch-manipulation'
    : 'px-4 py-2 text-sm font-medium text-white bg-primary rounded-xl min-h-[44px] flex items-center justify-center hover:bg-primary-dark touch-manipulation'

  return (
    <div data-testid={cardTestId} className={`${cardShell} ${className}`}>
      {kicker ? <p className={kickerClass}>{kicker}</p> : null}

      <h2 className={titleClass}>{L('welcomeOffer.title')}</h2>

      <p className={leadClass}>{L('guestChargeSample.lead')}</p>

      <div className="flex items-center gap-3">
        <div className={ruleClass} />
        <p className={sectionClass}>{L('guestChargeSample.sectionEarn')}</p>
        <div className={ruleClass} />
      </div>

      <div className={gridClass}>
        <div className={cellBorder}>
          <p className={`${numClass} text-4xl`}>{WELCOME}</p>
          <p className={labelMuted}>{L('guestChargeSample.welcomeLabel')}</p>
        </div>
        <div className="px-3 py-5">
          <p className={`${numClass} text-4xl`}>{DAILY}</p>
          <p className={labelMuted}>{L('guestChargeSample.dailyLabel')}</p>
        </div>
      </div>

      <p className={useLineClass}>{L('guestChargeSample.useLine')}</p>

      {showCost ? (
        <div className={costRowClass}>
          <span className={costMuted}>{L('guestChargeSample.costLabel')}</span>
          <span className={`${costNumClass} text-2xl`}>{costValue}</span>
          <span className={costMuted}>{L('guestChargeSample.costUnit')}</span>
        </div>
      ) : null}

      <div className="flex flex-col gap-3 pt-1">
        <Link to="/register" data-testid={registerTestId} className={ctaClass}>
          {L('welcomeOffer.cta')}
        </Link>
        {showLogin && loginTestId ? (
          <Link
            to="/login"
            data-testid={loginTestId}
            className="px-4 py-2 text-sm font-medium text-[#1a1a1a] border border-[#1a1a1a] rounded-xl min-h-[44px] flex items-center justify-center touch-manipulation"
          >
            {L('landing.cta.login')}
          </Link>
        ) : null}
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
