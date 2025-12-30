/**
 * Recommendations API
 * 推薦系統相關 API
 */

import { fetchAPI, USE_MOCK, delay } from './client'

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
    if (USE_MOCK) {
      await delay(500)
      return {
        user_id: userId,
        recommendations: [
          {
            id: 'rec_001',
            user_id: userId,
            category: 'fashion',
            keyword: 'Dior 2026 春夏秀',
            confidence_score: 0.85,
            reason: '顧客偏好fashion主題，推薦分數：0.85',
            generated_at: new Date().toISOString(),
          },
        ],
      }
    }

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
    if (USE_MOCK) {
      await delay(300)
      return {
        user_id: userId,
        history: [],
      }
    }

    const params = new URLSearchParams()
    if (options?.start_date) params.append('start_date', options.start_date)
    if (options?.end_date) params.append('end_date', options.end_date)

    const query = params.toString()
    return await fetchAPI<RecommendationHistoryResponse>(`/recommendations/${userId}/history${query ? `?${query}` : ''}`)
  },
}

