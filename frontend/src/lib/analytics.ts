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
export function trackProductEvent(name: 'sign_up' | 'generate_post' | 'purchase'): void {
  if (!import.meta.env.PROD) return
  if (typeof window.gtag !== 'function') return
  window.gtag('event', name)
  if (name === 'sign_up') {
    window.gtag('event', 'conversion', { send_to: SIGN_UP_CONVERSION_SEND_TO })
  }
}
