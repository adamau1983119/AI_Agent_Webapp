/**
 * Interactions API
 * 互動追蹤相關 API
 * 只使用真實後端 API，不使用 Mock 數據
 */

import { fetchAPI } from './client'

/**
 * 互動類型
 */
export type InteractionAction = 'like' | 'dislike' | 'edit' | 'replace' | 'view'

/**
 * 建立互動請求
 */
export interface CreateInteractionRequest {
  user_id: string
  topic_id: string
  article_id?: string
  photo_id?: string
  script_id?: string
  action: InteractionAction
  duration?: number
}

/**
 * 互動回應
 */
export interface InteractionResponse {
  id: string
  user_id: string
  topic_id: string
  article_id?: string
  photo_id?: string
  script_id?: string
  action: InteractionAction
  duration?: number
  category?: string
  created_at: string
}

/**
 * 互動列表回應
 */
export interface InteractionListResponse {
  user_id: string
  interactions: InteractionResponse[]
  pagination: {
    page: number
    limit: number
    total: number
    totalPages: number
  }
}

/**
 * 互動統計回應
 */
export interface InteractionStatsResponse {
  user_id: string
  stats: {
    total_likes: number
    total_dislikes: number
    total_edits: number
    total_replaces: number
    total_views: number
    avg_view_time: number
    category_distribution: Record<string, {
      likes: number
      dislikes: number
    }>
  }
}

/**
 * Interactions API
 */
export const interactionsAPI = {
  /**
   * 記錄互動
   */
  createInteraction: async (data: CreateInteractionRequest): Promise<InteractionResponse> => {
    return await fetchAPI<InteractionResponse>('/interactions', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  /**
   * 查詢互動歷史
   */
  getInteractions: async (
    userId: string,
    options?: {
      action?: InteractionAction
      category?: string
      start_date?: string
      end_date?: string
      page?: number
      limit?: number
    }
  ): Promise<InteractionListResponse> => {
    const params = new URLSearchParams()
    if (options?.action) params.append('action', options.action)
    if (options?.category) params.append('category', options.category)
    if (options?.start_date) params.append('start_date', options.start_date)
    if (options?.end_date) params.append('end_date', options.end_date)
    if (options?.page) params.append('page', options.page.toString())
    if (options?.limit) params.append('limit', options.limit.toString())

    const query = params.toString()
    return await fetchAPI<InteractionListResponse>(`/interactions/${userId}${query ? `?${query}` : ''}`)
  },

  /**
   * 取得互動統計
   */
  getInteractionStats: async (userId: string): Promise<InteractionStatsResponse> => {
    return await fetchAPI<InteractionStatsResponse>(`/interactions/${userId}/stats`)
  },
}
