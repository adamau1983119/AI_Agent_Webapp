/**
 * 圖片相關 API
 * 只使用真實後端 API，不使用 Mock 數據
 */

import { fetchAPI, fetchAPIWithPagination } from './client'
import type { Image, ImageSource } from '@/types'

/**
 * 類型轉換函數：API Image → Frontend Image
 */
function convertImage(apiImage: any): Image {
  return {
    id: apiImage.id,
    topicId: apiImage.topic_id || '',
    url: apiImage.url,
    source: apiImage.source,
    photographer: apiImage.photographer || '',
    license: apiImage.license || '',
    order: apiImage.order || 0,
  }
}

/**
 * 圖片搜尋參數
 */
export interface ImageSearchParams {
  keywords: string
  source?: ImageSource
  page?: number
  limit?: number
}

/**
 * 圖片搜尋嘗試記錄
 */
export interface ImageSearchAttempt {
  source: string
  status: 'success' | 'no_results' | 'error' | 'unavailable' | 'exception'
  count?: number
  code?: string
  message?: string
  details?: any
  exception_type?: string
}

/**
 * 圖片搜尋響應
 */
export interface ImageSearchResponse {
  data: Image[]
  pagination: {
    page: number
    limit: number
    total: number
    totalPages: number
  }
  source?: string
  attempts?: ImageSearchAttempt[]
  trace_id?: string
}

/**
 * 圖片建立資料
 */
export interface ImageCreate {
  url: string
  source: string
  photographer?: string
  license: string
  order?: number
}

/**
 * 圖片更新資料
 */
export interface ImageUpdate {
  url?: string
  source?: string
  photographer?: string
  license?: string
  order?: number
}

/**
 * 圖片重新排序項目
 */
export interface ImageReorderItem {
  image_id: string
  order: number
}

/**
 * 圖片列表響應
 */
export interface ImageListResponse {
  data: Image[]
}

/**
 * 圖片 API
 */
export const imagesAPI = {
  /**
   * 取得主題圖片列表
   */
  getImages: async (topicId: string): Promise<Image[]> => {
    const response = await fetchAPI<any>(`/images/${topicId}`)
    // 後端可能返回 { data: [...] } 或直接返回陣列
    const images = Array.isArray(response) ? response : response.data || []
    return images.map(convertImage)
  },

  /**
   * 搜尋圖片（支援分頁）
   */
  searchImages: async (
    params: ImageSearchParams
  ): Promise<ImageSearchResponse> => {
    const urlParams = new URLSearchParams({
      keywords: params.keywords,
      page: (params.page || 1).toString(),
      limit: (params.limit || 20).toString(),
    })
    if (params.source) {
      // 將前端格式轉換為後端格式
      const sourceMap: Record<ImageSource, string> = {
        'unsplash': 'Unsplash',
        'pexels': 'Pexels',
        'pixabay': 'Pixabay',
        'google_custom_search': 'Google Custom Search',
        'duckduckgo': 'DuckDuckGo',
      }
      urlParams.append('source', sourceMap[params.source] || params.source)
    }

    const response = await fetchAPI<ImageSearchResponse>(
      `/images/search?${urlParams.toString()}`
    )

    const page = params.page || 1
    const limit = params.limit || 20
    const pagination = response.pagination || {
      page,
      limit,
      total: response.data?.length || 0,
      totalPages: Math.ceil((response.data?.length || 0) / limit),
    }

    return {
      data: (response.data || []).map(convertImage),
      pagination: {
        page: pagination.page || page,
        limit: pagination.limit || limit,
        total: pagination.total || response.data?.length || 0,
        totalPages:
          pagination.totalPages ||
          Math.ceil((pagination.total || response.data?.length || 0) / (pagination.limit || limit)),
      },
      source: response.source,
      attempts: response.attempts,
      trace_id: response.trace_id,
    }
  },

  /**
   * 新增圖片到主題
   */
  createImage: async (
    topicId: string,
    data: ImageCreate
  ): Promise<Image> => {
    const image = await fetchAPI<any>(`/images/${topicId}`, {
      method: 'POST',
      body: JSON.stringify({
        topic_id: topicId,
        ...data,
      }),
    })

    return convertImage(image)
  },

  /**
   * 更新圖片
   */
  updateImage: async (
    topicId: string,
    imageId: string,
    data: ImageUpdate
  ): Promise<Image> => {
    const image = await fetchAPI<any>(`/images/${topicId}/${imageId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })

    return convertImage(image)
  },

  /**
   * 刪除圖片
   */
  deleteImage: async (topicId: string, imageId: string): Promise<void> => {
    await fetchAPI(`/images/${topicId}/${imageId}`, {
      method: 'DELETE',
    })
  },

  /**
   * 重新排序圖片
   */
  reorderImages: async (
    topicId: string,
    orders: ImageReorderItem[]
  ): Promise<void> => {
    await fetchAPI(`/images/${topicId}/reorder`, {
      method: 'PUT',
      body: JSON.stringify({
        image_orders: orders,
      }),
    })
  },

  /**
   * 根據文章內容匹配照片（分層閾值檢查）
   */
  matchPhotos: async (
    topicId: string,
    minCount: number = 8
  ): Promise<Image[]> => {
    const response = await fetchAPI<{ data: any[] }>(`/images/${topicId}/match?min_count=${minCount}`, {
      method: 'POST',
    })
    const images = Array.isArray(response) ? response : response.data || []
    return images.map(convertImage)
  },

  /**
   * 驗證照片與文字匹配度
   */
  validateMatch: async (
    topicId: string,
    articleId?: string
  ): Promise<{
    topic_id: string
    validation_results: Array<{
      mentioned_item: string
      has_matching_photo: boolean
      photo_id: string
      match_score: number
    }>
    overall_match: boolean
    warnings: string[]
  }> => {
    return await fetchAPI(`/images/validate-match`, {
      method: 'POST',
      body: JSON.stringify({
        topic_id: topicId,
        article_id: articleId,
      }),
    })
  },
}
