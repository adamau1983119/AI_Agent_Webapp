/**
 * Discover 公共主題牆 — 只讀 feed（零 LLM）
 */
import { fetchAPIEnvelope } from './client'

export interface PublicFeedCard {
  id: string
  title: string
  description: string
  summary_flash?: string | null
  category?: string | null
  image_url?: string | null
  source?: string | null
  source_lang: string
  created_at?: string | null
}

export interface PublicFeedResponse {
  data: PublicFeedCard[]
  lang: string
  cached: boolean
  count: number
}

export type PublicFeedLang = 'zh-TW' | 'ja' | 'en'

export function resolvePublicFeedLang(uiLanguage: string): PublicFeedLang {
  if (uiLanguage === 'ja') return 'ja'
  if (uiLanguage === 'en') return 'en'
  return 'zh-TW'
}

export const publicFeedAPI = {
  /** 勿用 fetchAPI unwrap，否則 data[] 被拆掉後 Discover 讀 data.data → 永遠空牆 */
  getFeed(lang: PublicFeedLang): Promise<PublicFeedResponse> {
    const params = new URLSearchParams({ lang })
    return fetchAPIEnvelope<PublicFeedResponse>(`/public/topics/feed?${params.toString()}`)
  },
}
