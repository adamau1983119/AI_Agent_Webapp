/**
 * Discover API
 * 主題發掘相關 API
 */

import { fetchAPI, USE_MOCK, delay } from './client'

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
    if (USE_MOCK) {
      await delay(2000)
      return {
        timestamp: new Date().toISOString(),
        category: data.category,
        time_slot: data.time_slot || 'morning',
        region: data.region || 'global',
        topics: [
          {
            title: `Mock ${data.category} topic 1`,
            keyword: `Mock ${data.category} keyword 1`,
            category: data.category,
            source: 'Mock Source',
            sources: [],
            validation: { valid: true },
          },
        ],
      }
    }

    return await fetchAPI<DiscoverTopicsResponse>('/discover/topics/auto', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  /**
   * 手動發掘主題
   */
  manualDiscoverTopics: async (data: DiscoverTopicsRequest): Promise<DiscoverTopicsResponse> => {
    if (USE_MOCK) {
      await delay(2000)
      return {
        timestamp: new Date().toISOString(),
        category: data.category,
        region: data.region || 'global',
        topics: [],
      }
    }

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
    if (USE_MOCK) {
      await delay(300)
      return {
        date: options?.date || new Date().toISOString().split('T')[0],
        category,
        region: options?.region || 'global',
        rankings: [
          {
            rank: 1,
            keyword: `Mock ${category} keyword 1`,
            search_volume: 50000,
            trend: 'up',
            source: 'Mock Source',
          },
        ],
      }
    }

    const params = new URLSearchParams()
    params.append('category', category)
    if (options?.region) params.append('region', options.region)
    if (options?.date) params.append('date', options.date)

    return await fetchAPI<RankingsResponse>(`/discover/topics/rankings?${params.toString()}`)
  },
}

