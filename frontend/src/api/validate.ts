/**
 * Validate API
 * 資料驗證相關 API
 * 只使用真實後端 API，不使用 Mock 數據
 */

import { fetchAPI } from './client'

/**
 * 驗證來源請求
 */
export interface ValidateSourcesRequest {
  topic_id: string
  sources: Array<{
    url: string
    name: string
  }>
}

/**
 * 驗證來源回應
 */
export interface ValidateSourcesResponse {
  topic_id: string
  validated_sources: Array<{
    valid: boolean
    url: string
    name: string
    content_snippet?: string
    screenshot_url?: string
    fetched_at: string
    reliability: string
  }>
  validation_summary: {
    total_sources: number
    verified_sources: number
    failed_sources: number
  }
  failed_sources: Array<{
    source: {
      url: string
      name: string
    }
    reason: string
  }>
}

/**
 * 驗證一致性請求
 */
export interface ValidateConsistencyRequest {
  keyword: string
  category: 'fashion' | 'food' | 'trend'
  sources: Array<{
    url: string
    name: string
    title?: string
  }>
}

/**
 * 驗證一致性回應
 */
export interface ValidateConsistencyResponse {
  valid: boolean
  confidence: number
  consistency_score: number
  sources_verified: number
  is_factual: boolean
  warnings: string[]
}

/**
 * 來源健康度回應
 */
export interface SourceHealthResponse {
  health_score: number
  status: 'healthy' | 'degraded' | 'unhealthy'
  response_time?: number
  status_code?: number
  error?: string
}

/**
 * Validate API
 */
export const validateAPI = {
  /**
   * 驗證並抓取來源資料
   */
  validateSources: async (data: ValidateSourcesRequest): Promise<ValidateSourcesResponse> => {
    return await fetchAPI<ValidateSourcesResponse>('/validate/sources', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  /**
   * 驗證主題的跨來源一致性
   */
  validateTopicConsistency: async (
    data: ValidateConsistencyRequest
  ): Promise<ValidateConsistencyResponse> => {
    return await fetchAPI<ValidateConsistencyResponse>('/validate/topic-consistency', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  /**
   * 檢查來源健康度
   */
  checkSourceHealth: async (sourceUrl: string): Promise<SourceHealthResponse> => {
    // URL 編碼
    const encodedUrl = encodeURIComponent(sourceUrl)
    return await fetchAPI<SourceHealthResponse>(`/validate/source-health/${encodedUrl}`)
  },
}
