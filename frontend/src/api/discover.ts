/**
 * Discover API
 * 主題發掘相關 API
 * 只使用真實後端 API，不使用 Mock 數據
 */

import { fetchAPI } from './client'

/**
 * 主題發掘請求
 */
export interface DiscoverTopicsRequest {
  category: 'fashion' | 'food' | 'trend'
  region?: string
  count?: number
  time_slot?: string
}

/**
 * 主題發掘回應
 */
export interface DiscoverTopicsResponse {
  timestamp: string
  category: string
  time_slot?: string
  region: string
  topics: Array<{
    title: string
    keyword: string
    category: string
    source: string
    sources: Array<{
      type: string
      name: string
      url: string
      title: string
      fetched_at: string
      verified: boolean
      reliability: string
    }>
    fallback?: boolean
    validation?: {
      valid: boolean
      consistency_score?: number
    }
  }>
}

/**
 * 排行榜回應
 */
export interface RankingsResponse {
  date: string
  category: string
  region: string
  rankings: Array<{
    rank: number
    keyword: string
    search_volume: number
    trend: 'up' | 'down' | 'stable'
    source: string
  }>
}

/**
 * Discover API
 */
export const discoverAPI = {
  /**
   * 自動發掘主題
   */
  autoDiscoverTopics: async (data: DiscoverTopicsRequest): Promise<DiscoverTopicsResponse> => {
    return await fetchAPI<DiscoverTopicsResponse>('/discover/topics/auto', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  /**
   * 手動發掘主題
   */
  manualDiscoverTopics: async (data: DiscoverTopicsRequest): Promise<DiscoverTopicsResponse> => {
    return await fetchAPI<DiscoverTopicsResponse>('/discover/topics/manual', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  /**
   * 查詢排行榜
   */
  getRankings: async (
    category: 'fashion' | 'food' | 'trend',
    options?: {
      region?: string
      date?: string
    }
  ): Promise<RankingsResponse> => {
    const params = new URLSearchParams()
    params.append('category', category)
    if (options?.region) params.append('region', options.region)
    if (options?.date) params.append('date', options.date)

    return await fetchAPI<RankingsResponse>(`/discover/topics/rankings?${params.toString()}`)
  },
}
