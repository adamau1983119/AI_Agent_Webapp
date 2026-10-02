/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_USE_MOCK?: string
  readonly VITE_POST_LOGIN_PATH?: string
  /** GA4 Measurement ID (public); production builds fall back to G-F38Q4L6CPV */
  readonly VITE_GA_MEASUREMENT_ID?: string
  /** Google Ads conversion ID (public); production builds fall back to AW-18489161677 */
  readonly VITE_AW_CONVERSION_ID?: string
  readonly DEV: boolean
  readonly PROD: boolean
  readonly MODE: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

