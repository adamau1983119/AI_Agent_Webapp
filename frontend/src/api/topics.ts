/**
 * 主題相關 API
 * 只使用真實後端 API，不使用 Mock 數據
 */

import { fetchAPI, fetchAPIWithPagination } from './client'
import type { Topic } from '@/types'

/**
 * 類型轉換函數：API Topic → Frontend Topic
 */
export function convertTopic(apiTopic: any): Topic {
  return {
    id: apiTopic.id,
    title: apiTopic.title,
    category: apiTopic.category,
    status: apiTopic.status,
    source: apiTopic.source || '',
    sources: apiTopic.sources || [],  // 保留來源列表（包含原始文章連結）
    generatedAt: apiTopic.generated_at || apiTopic.generatedAt,
    updatedAt: apiTopic.updated_at || apiTopic.updatedAt,
    imageCount: apiTopic.image_count || 0,
    wordCount: apiTopic.word_count || 0,
    // 階段 1 新增欄位
    previewImages: apiTopic.preview_images || [],
    isExpanded: apiTopic.is_expanded || false,
    description: apiTopic.description || undefined,
    summaryFlash: apiTopic.summary_flash || apiTopic.summaryFlash,
    summary_flash: apiTopic.summary_flash || apiTopic.summaryFlash,
    sourceContentI18n: apiTopic.source_content_i18n || apiTopic.sourceContentI18n,
    source_content_i18n: apiTopic.source_content_i18n || apiTopic.sourceContentI18n,
    translatedSourceContent: apiTopic.translated_source_content || apiTopic.translatedSourceContent,
    translated_source_content: apiTopic.translated_source_content || apiTopic.translatedSourceContent,
    // Phase 7: 多語言支援
    displayLanguage: apiTopic.display_language || apiTopic.displayLanguage || undefined,
    originalTitle: apiTopic.original_title || apiTopic.originalTitle || undefined,
    titlesI18n: apiTopic.titles_i18n || apiTopic.titlesI18n,
    descriptionI18n: apiTopic.description_i18n || apiTopic.descriptionI18n,
    titleScriptMismatch:
      apiTopic.title_script_mismatch ?? apiTopic.titleScriptMismatch,
    contentLocale: apiTopic.content_locale || apiTopic.contentLocale,
    localeResolved: apiTopic.locale_resolved ?? apiTopic.localeResolved,
  }
}

export interface TopicTranslateDisplayResult {
  topic_id: string
  title: string
  description?: string | null
  target_language: string
  display_language: string
  original_title?: string | null
  cached: boolean
  titles_i18n?: Record<string, string>
  description_i18n?: Record<string, string>
}

/**
 * 主題篩選參數
 */
export interface TopicFilters {
  category?: 'fashion' | 'food' | 'trend'
  status?: 'pending' | 'confirmed' | 'deleted'
  date?: string // YYYY-MM-DD
  search?: string // 搜尋關鍵字
  page?: number
  limit?: number
  sort?: string
  order?: 'asc' | 'desc'
  /** Content Locale：伺服器端解析標題／摘要 */
  lang?: string
}

/**
 * 搜尋參數（使用新的搜尋端點）
 */
export interface SearchParams {
  query: string // 搜尋關鍵字（2-100字元）
  category?: 'fashion' | 'food' | 'trend' // 分類篩選
  page?: number // 頁碼（1-100）
  limit?: number // 每頁數量（1-50）
  role?: 'guest' | 'user' | 'premium' | 'admin' // 用戶角色
  lang?: string // Content Locale ui_lang
}

/**
 * 搜尋響應
 */
export interface SearchResponse {
  source: 'es' | 'db' | 'cache' // 資料來源
  results: Topic[] // 搜尋結果
  pagination: {
    page: number
    limit: number
    total: number
    pages: number // 注意：後端返回的是 pages，不是 totalPages
  }
}

/**
 * 主題更新資料
 */
export interface TopicUpdate {
  title?: string
  category?: 'fashion' | 'food' | 'trend'
  status?: 'pending' | 'confirmed' | 'deleted'
  source?: string
}

/**
 * 主題狀態更新
 */
export interface TopicStatusUpdate {
  status: 'pending' | 'confirmed' | 'deleted'
}

/**
 * 分頁響應
 */
export interface PaginatedResponse<T> {
  data: T[]
  pagination: {
    page: number
    limit: number
    total: number
    totalPages: number
  }
}

/**
 * 主題 API
 */
export const topicsAPI = {
  /**
   * 取得主題列表（支援分頁）
   */
  getTopics: async (
    filters?: TopicFilters
  ): Promise<PaginatedResponse<Topic>> => {
    const params = new URLSearchParams()
    if (filters?.category) params.append('category', filters.category)
    if (filters?.status) params.append('status', filters.status)
    if (filters?.date) params.append('date', filters.date)
    if (filters?.search && filters.search.trim()) params.append('search', filters.search.trim())
    params.append('page', (filters?.page || 1).toString())
    params.append('limit', (filters?.limit || 30).toString())
    if (filters?.sort) params.append('sort', filters.sort)
    if (filters?.order) params.append('order', filters.order)
    if (filters?.lang) params.append('lang', filters.lang)

    const response = await fetchAPIWithPagination<any>(
      `/topics?${params.toString()}`
    )

    // 從後端分頁資訊或計算分頁資訊
    const page = filters?.page || 1
    const limit = filters?.limit || 30
    const pagination = response.pagination || {
      page,
      limit,
      total: response.data.length,
      totalPages: Math.ceil(response.data.length / limit),
    }

    return {
      data: response.data.map(convertTopic),
      pagination: {
        page: pagination.page || page,
        limit: pagination.limit || limit,
        total: pagination.total || response.data.length,
        totalPages:
          pagination.totalPages ||
          Math.ceil((pagination.total || response.data.length) / (pagination.limit || limit)),
      },
    }
  },

  /**
   * 取得主題詳情
   */
  /**
   * 方案 C：譯為目前介面語言（標題／摘要，快取 titles_i18n）
   */
  translateDisplay: async (
    topicId: string,
    targetLanguage?: string,
    translationType: 'standard_translation' | 'kol_style' = 'standard_translation'
  ): Promise<TopicTranslateDisplayResult> => {
    const body: Record<string, string> = {}
    if (targetLanguage) body.target_language = targetLanguage
    if (translationType) body.translation_type = translationType
    return fetchAPI<TopicTranslateDisplayResult>(`/topics/${topicId}/translate-display`, {
      method: 'POST',
      body: JSON.stringify(body),
    })
  },

  getTopic: async (id: string, lang?: string): Promise<Topic | null> => {
    const qs = lang ? `?lang=${encodeURIComponent(lang)}` : ''
    const topic = await fetchAPI<any>(`/topics/${id}${qs}`)
    if (!topic) {
      console.warn(`Topic not found: ${id}`)
      return null
    }
    return convertTopic(topic)
  },

  /**
   * 更新主題
   */
  updateTopic: async (id: string, data: TopicUpdate): Promise<Topic> => {
    const topic = await fetchAPI<any>(`/topics/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })

    return convertTopic(topic)
  },

  /**
   * 更新主題狀態
   */
  updateTopicStatus: async (
    id: string,
    status: 'pending' | 'confirmed' | 'deleted'
  ): Promise<Topic> => {
    const topic = await fetchAPI<any>(`/topics/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    })

    return convertTopic(topic)
  },

  /**
   * 刪除主題
   */
  deleteTopic: async (id: string): Promise<void> => {
    await fetchAPI(`/topics/${id}`, {
      method: 'DELETE',
    })
  },

  /**
   * 批量刪除今日主題
   */
  deleteTodayTopics: async (): Promise<{ deleted_count: number; topic_ids: string[] }> => {
    const response = await fetchAPI<{ deleted_count: number; topic_ids: string[] }>(
      `/topics/today`,
      {
        method: 'DELETE',
      }
    )
    return response
  },

  /**
   * 搜尋主題（使用新的搜尋端點，支援中文全文搜尋）
   * 
   * 使用 Elasticsearch（如果可用）或 MongoDB 進行搜尋
   * 支援 Redis 快取和權限控制
   */
  searchTopics: async (params: SearchParams): Promise<SearchResponse> => {
    const { query, category, page = 1, limit = 10, role = 'user', lang } = params

    // 驗證查詢字串（防禦性檢查，主要驗證應在 UI 層進行）
    // 注意：這裡的錯誤訊息不會顯示給用戶，因為驗證已在組件層完成
    if (!query || query.trim().length < 2) {
      throw new Error('Invalid query: minimum 2 characters required')
    }
    if (query.length > 100) {
      throw new Error('Invalid query: maximum 100 characters allowed')
    }

    // 構建查詢參數
    const urlParams = new URLSearchParams({
      query: query.trim(),
      page: page.toString(),
      limit: limit.toString(),
    })

    if (category) {
      urlParams.append('category', category)
    }
    if (lang) {
      urlParams.append('lang', lang)
    }

    // 使用 fetchAPI 並添加 X-User-Role header
    const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
    const url = `${API_BASE_URL}/topics/search?${urlParams.toString()}`

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-User-Role': role,
      },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Search failed' }))
      throw new Error(error.detail || `Search failed: ${response.status}`)
    }

    const data = await response.json()

    // 轉換結果格式
    return {
      source: data.source || 'db',
      results: (data.results || []).map(convertTopic),
      pagination: {
        page: data.pagination?.page || page,
        limit: data.pagination?.limit || limit,
        total: data.pagination?.total || 0,
        pages: data.pagination?.pages || data.pagination?.total_pages || 0,
      },
    }
  },

  /**
   * 檢查 URL 是否已收錄
   */
  checkUrlExists: async (url: string): Promise<{ exists: boolean; topic_id?: string }> => {
    const urlParams = new URLSearchParams({ url })
    const response = await fetchAPI<{ exists: boolean; topic_id?: string }>(
      `/topics/search/check?${urlParams.toString()}`
    )
    return response
  },

  /**
   * 取得熱門搜尋查詢
   */
  getHotQueries: async (limit: number = 10): Promise<Array<{ query: string; count: number }>> => {
    const urlParams = new URLSearchParams({ limit: limit.toString() })
    const response = await fetchAPI<Array<{ query: string; count: number }>>(
      `/topics/search/hot-queries?${urlParams.toString()}`
    )
    return response
  },
}
