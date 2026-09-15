/**
 * Locked display FX for credit packs. Checkout always charges USD.
 * Rates as of 2026-09-15; not a live ticker.
 */
export const DISPLAY_CURRENCIES = ['USD', 'TWD', 'CNY', 'HKD', 'JPY'] as const
export type DisplayCurrency = (typeof DISPLAY_CURRENCIES)[number]

export const FX_AS_OF = '2026-09-15'
const LS_KEY = 'credits-display-currency'

const USD_PER: Record<DisplayCurrency, number> = {
  USD: 1,
  TWD: 32,
  CNY: 7.2,
  HKD: 7.84,
  JPY: 150,
}

const PREFIX: Record<DisplayCurrency, string> = {
  USD: 'US$',
  TWD: 'NT$',
  CNY: 'CN¥',
  HKD: 'HK$',
  JPY: '¥',
}

export function loadDisplayCurrency(): DisplayCurrency {
  try {
    const raw = localStorage.getItem(LS_KEY) || ''
    if ((DISPLAY_CURRENCIES as readonly string[]).includes(raw)) {
      return raw as DisplayCurrency
    }
  } catch {
    /* ignore */
  }
  return 'USD'
}

export function saveDisplayCurrency(code: DisplayCurrency): void {
  try {
    localStorage.setItem(LS_KEY, code)
  } catch {
    /* ignore */
  }
}

export function formatUsdFromCents(cents: number): string {
  return `US$${Math.round(cents / 100)}`
}

export function formatLocalFromCents(cents: number, currency: DisplayCurrency): string {
  const usd = cents / 100
  const local = Math.round(usd * USD_PER[currency])
  return `${PREFIX[currency]}${local}`
}
