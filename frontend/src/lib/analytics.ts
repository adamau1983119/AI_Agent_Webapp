/**
 * Production-only Google Analytics 4 + Google Ads gtag loader.
 * Measurement / conversion IDs are public client-side values (not secrets).
 */

declare global {
  interface Window {
    dataLayer?: unknown[]
    gtag?: (...args: unknown[]) => void
  }
}

const DEFAULT_GA_ID = 'G-F38Q4L6CPV'
const DEFAULT_AW_ID = 'AW-18489161677'
/** Website conversion label for registration. Public snippet value. */
const SIGN_UP_CONVERSION_SEND_TO = 'AW-18489161677/QrRhCJ2z-6IdEM3vqPBE'

export type ProductEventName = 'sign_up' | 'generate_post' | 'purchase'

/** Welcome dual-funnel CTAs (not Key events until 7-day review). */
export type WelcomeCtaId = 'hero_start' | 'offer_register'

/** TopicDetail guest charge modal CTAs. */
export type GuestChargeCtaId = 'register' | 'login' | 'cancel'

function resolveId(envKey: string, fallback: string): string {
  const fromEnv = (import.meta.env[envKey] as string | undefined)?.trim()
  if (fromEnv) return fromEnv
  return import.meta.env.PROD ? fallback : ''
}

/** Load gtag only in production builds (skip localhost / vite dev). */
export function initAnalytics(): void {
  if (!import.meta.env.PROD) return

  const gaId = resolveId('VITE_GA_MEASUREMENT_ID', DEFAULT_GA_ID)
  if (!gaId) return

  const awId = resolveId('VITE_AW_CONVERSION_ID', DEFAULT_AW_ID)

  window.dataLayer = window.dataLayer || []
  // gtag expects Arguments object pushes (official snippet shape)
  window.gtag = function gtag() {
    // eslint-disable-next-line prefer-rest-params
    window.dataLayer!.push(arguments)
  } as (...args: unknown[]) => void
  window.gtag('js', new Date())
  window.gtag('config', gaId)
  if (awId) {
    window.gtag('config', awId)
  }

  const script = document.createElement('script')
  script.async = true
  script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(gaId)}`
  document.head.appendChild(script)
}

/** Product funnel events. No email or other personal fields. No-op outside production. */
export function trackProductEvent(name: ProductEventName): void {
  if (!import.meta.env.PROD) return
  if (typeof window.gtag !== 'function') return
  window.gtag('event', name)
  if (name === 'sign_up') {
    window.gtag('event', 'conversion', { send_to: SIGN_UP_CONVERSION_SEND_TO })
  }
}

/**
 * Welcome CTA clicks. Params: cta_id only (no PII).
 * Does not fire Ads conversion — observe 7 days before Key event.
 */
export function trackWelcomeCta(ctaId: WelcomeCtaId): void {
  if (!import.meta.env.PROD) return
  if (typeof window.gtag !== 'function') return
  window.gtag('event', 'welcome_cta_click', { cta_id: ctaId })
}

/**
 * Guest charge modal CTA clicks. Params: cta_id only (no PII).
 */
export function trackGuestChargeCta(ctaId: GuestChargeCtaId): void {
  if (!import.meta.env.PROD) return
  if (typeof window.gtag !== 'function') return
  window.gtag('event', 'guest_charge_cta_click', { cta_id: ctaId })
}

/** One-tap post funnel. No PII. Observe ≥7 days before Key event. Do not optimize Ads on these. */
export type OneTapEventName =
  | 'one_tap_impression'
  | 'one_tap_click'
  | 'one_tap_generate_success'
  | 'one_tap_share_success'
  | 'one_tap_share_cancel'

export type OneTapEventParams = {
  surface: 'public' | 'my_channel'
  topic_id?: string
}

/**
 * One-tap post events. Params: surface + optional topic_id only (no PII).
 * Production-only; no-op on localhost.
 */
export function trackOneTapEvent(name: OneTapEventName, params: OneTapEventParams): void {
  if (!import.meta.env.PROD) return
  if (typeof window.gtag !== 'function') return
  const payload: Record<string, string> = { surface: params.surface }
  const topicId = params.topic_id?.trim()
  if (topicId) payload.topic_id = topicId
  window.gtag('event', name, payload)
}

/** Topic Card attention (Tier A). No PII. Observe ≥7 days before Key event. */
export type TopicOpenParams = {
  topic_id: string
  topic_category?: string
  language?: string
}

const LAST_TOPIC_SESSION_KEY = 'ae_ga4_last_topic_id'

/**
 * Fires topic_open; if another topic was opened earlier in this tab session,
 * also fires topic_open_again (previous_topic / current_topic).
 */
export function trackTopicOpen(params: TopicOpenParams): void {
  if (!import.meta.env.PROD) return
  if (typeof window.gtag !== 'function') return
  const topicId = params.topic_id?.trim()
  if (!topicId) return

  const openPayload: Record<string, string> = { topic_id: topicId }
  const category = params.topic_category?.trim()
  if (category) openPayload.topic_category = category
  const lang = params.language?.trim()
  if (lang) openPayload.language = lang

  window.gtag('event', 'topic_open', openPayload)

  try {
    const previous = sessionStorage.getItem(LAST_TOPIC_SESSION_KEY)
    if (previous && previous !== topicId) {
      window.gtag('event', 'topic_open_again', {
        previous_topic: previous,
        current_topic: topicId,
      })
    }
    sessionStorage.setItem(LAST_TOPIC_SESSION_KEY, topicId)
  } catch {
    // sessionStorage may be blocked; open event already sent
  }
}
