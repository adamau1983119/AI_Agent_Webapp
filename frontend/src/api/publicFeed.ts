/**
 * Discover 公共主題牆 — 只讀 feed（零 LLM）
 */
import { fetchAPI } from './client'

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

export type PublicFeedLang = 'zh-TW' | 'ja'

export function resolvePublicFeedLang(uiLanguage: string): PublicFeedLang {
  return uiLanguage === 'ja' ? 'ja' : 'zh-TW'
}

export const publicFeedAPI = {
  getFeed(lang: PublicFeedLang): Promise<PublicFeedResponse> {
    const params = new URLSearchParams({ lang })
    return fetchAPI<PublicFeedResponse>(`/public/topics/feed?${params.toString()}`)
  },
}
