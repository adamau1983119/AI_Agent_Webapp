/**
 * 圖片相關 API
 * 只使用真實後端 API，不使用 Mock 數據
 */

import { fetchAPI } from './client'
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

    // 直接使用 fetch 獲取完整響應，避免 responseInterceptor 提取 data 欄位
    const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
    const url = `${API_BASE_URL}/images/search?${urlParams.toString()}`
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`)
    }

    // 解析完整的 JSON 響應（包含 data, pagination, source, attempts, trace_id）
    const responseData = await response.json()

    const page = params.page || 1
    const limit = params.limit || 20
    const pagination = responseData.pagination || {
      page,
      limit,
      total: responseData.data?.length || 0,
      totalPages: Math.ceil((responseData.data?.length || 0) / limit),
    }

    return {
      data: (responseData.data || []).map(convertImage),
      pagination: {
        page: pagination.page || page,
        limit: pagination.limit || limit,
        total: pagination.total || responseData.data?.length || 0,
        totalPages:
          pagination.totalPages ||
          Math.ceil((pagination.total || responseData.data?.length || 0) / (pagination.limit || limit)),
      },
      source: responseData.source,
      attempts: responseData.attempts || [],
      trace_id: responseData.trace_id,
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
    minCount: number = 4
  ): Promise<Image[]> => {
    try {
      // 構建 URL，確保正確使用 ? 而不是 @
      const endpoint = `/images/${topicId}/match?min_count=${minCount}`
      const response = await fetchAPI<any>(endpoint, {
        method: 'POST',
        timeout: 60000, // 智能匹配照片需要更長時間（60秒）
      })
      
      // responseInterceptor 已經提取了 data 欄位，所以 response 應該是數組
      // 但為了兼容性，仍然檢查多種格式
      let images: any[] = []
      
      if (Array.isArray(response)) {
        // 情況 1: response 已經是數組（最常見）
        images = response
      } else if (response && typeof response === 'object') {
        // 情況 2: response 是對象，嘗試提取 data 欄位
        if (Array.isArray(response.data)) {
          images = response.data
        } else if (Array.isArray(response.matched_photos)) {
          // 情況 3: 後端直接返回 matched_photos（如果 responseInterceptor 沒有提取）
          images = response.matched_photos
        } else if (response.data && typeof response.data === 'object' && Array.isArray(response.data.data)) {
          // 情況 4: 嵌套的 data 結構
          images = response.data.data
        } else {
          console.warn('匹配照片返回的數據格式異常:', { 
            response, 
            responseType: typeof response,
            hasData: !!response.data,
            hasMatchedPhotos: !!response.matched_photos,
            keys: Object.keys(response || {})
          })
          return []
        }
      } else {
        console.warn('匹配照片返回的數據格式異常: 不是數組也不是對象', { response })
        return []
      }
      
      if (!Array.isArray(images) || images.length === 0) {
        console.warn('匹配照片返回空數組或格式錯誤:', { response, images })
        return []
      }
      
      return images.map(convertImage)
    } catch (error: any) {
      console.error('匹配照片 API 調用失敗:', error)
      throw error
    }
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
