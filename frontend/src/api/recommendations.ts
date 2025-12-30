/**
 * Recommendations API
 * 推薦系統相關 API
 * 只使用真實後端 API，不使用 Mock 數據
 */

import { fetchAPI } from './client'

/**
 * 推薦回應
 */
export interface RecommendationResponse {
  id: string
  user_id: string
  category: 'fashion' | 'food' | 'trend'
  keyword: string
  confidence_score: number
  reason?: string
  generated_at: string
  interaction_result?: {
    action: string
    duration: number
  }
  effectiveness?: 'high' | 'medium' | 'low'
}

/**
 * 推薦列表回應
 */
export interface RecommendationListResponse {
  user_id: string
  recommendations: RecommendationResponse[]
}

/**
 * 推薦歷史回應
 */
export interface RecommendationHistoryResponse {
  user_id: string
  history: RecommendationResponse[]
}

/**
 * Recommendations API
 */
export const recommendationsAPI = {
  /**
   * 取得推薦列表
   */
  getRecommendations: async (
    userId: string,
    options?: {
      category?: 'fashion' | 'food' | 'trend'
      limit?: number
    }
  ): Promise<RecommendationListResponse> => {
    const params = new URLSearchParams()
    if (options?.category) params.append('category', options.category)
    if (options?.limit) params.append('limit', options.limit.toString())

    const query = params.toString()
    return await fetchAPI<RecommendationListResponse>(`/recommendations/${userId}${query ? `?${query}` : ''}`)
  },

  /**
   * 查詢推薦歷史
   */
  getRecommendationHistory: async (
    userId: string,
    options?: {
      start_date?: string
      end_date?: string
    }
  ): Promise<RecommendationHistoryResponse> => {
    const params = new URLSearchParams()
    if (options?.start_date) params.append('start_date', options.start_date)
    if (options?.end_date) params.append('end_date', options.end_date)

    const query = params.toString()
    return await fetchAPI<RecommendationHistoryResponse>(`/recommendations/${userId}/history${query ? `?${query}` : ''}`)
  },
}
