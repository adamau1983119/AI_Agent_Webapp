/**
 * 圖片相關 API
 */

import { fetchAPI, fetchAPIWithPagination, USE_MOCK, delay } from './client'
import { mockImages } from './mockData'
import type { Image } from '@/types'

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
  source?: 'unsplash' | 'pexels' | 'pixabay'
  page?: number
  limit?: number
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
 * 圖片 API
 */
export const imagesAPI = {
  /**
   * 取得主題圖片列表
   */
  getImages: async (topicId: string): Promise<Image[]> => {
    if (USE_MOCK) {
      await delay(300)
      return mockImages[topicId] || []
    }

    try {
      const response = await fetchAPI<any>(`/images/${topicId}`)
      // 後端可能返回 { data: [...] } 或直接返回陣列
      const images = Array.isArray(response) ? response : response.data || []
      return images.map(convertImage)
    } catch (error) {
      console.error('Failed to fetch images, falling back to mock data', error)
      await delay(300)
      return mockImages[topicId] || []
    }
  },

  /**
   * 搜尋圖片（支援分頁）
   */
  searchImages: async (
    params: ImageSearchParams
  ): Promise<{ data: Image[]; pagination: any }> => {
    if (USE_MOCK) {
      await delay(500)
      return {
        data: [],
        pagination: {
          page: params.page || 1,
          limit: params.limit || 20,
          total: 0,
          totalPages: 0,
        },
      }
    }

    try {
      const urlParams = new URLSearchParams({
        keywords: params.keywords,
        page: (params.page || 1).toString(),
        limit: (params.limit || 20).toString(),
      })
      if (params.source) {
        urlParams.append('source', params.source)
      }

      const response = await fetchAPIWithPagination<any>(
        `/images/search?${urlParams.toString()}`
      )

      const page = params.page || 1
      const limit = params.limit || 20
      const pagination = response.pagination || {
        page,
        limit,
        total: response.data.length,
        totalPages: Math.ceil(response.data.length / limit),
      }

      return {
        data: response.data.map(convertImage),
        pagination: {
          page: pagination.page || page,
          limit: pagination.limit || limit,
          total: pagination.total || response.data.length,
          totalPages:
            pagination.totalPages ||
            Math.ceil((pagination.total || response.data.length) / (pagination.limit || limit)),
        },
      }
    } catch (error) {
      console.error('Failed to search images', error)
      return {
        data: [],
        pagination: {
          page: params.page || 1,
          limit: params.limit || 20,
          total: 0,
          totalPages: 0,
        },
      }
    }
  },

  /**
   * 新增圖片到主題
   */
  createImage: async (
    topicId: string,
    data: ImageCreate
  ): Promise<Image> => {
    if (USE_MOCK) {
      await delay(300)
      return {
        id: `image_${Date.now()}`,
        topicId,
        ...data,
        photographer: data.photographer || '',
        order: data.order || 0,
      }
    }

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
    if (USE_MOCK) {
      await delay(300)
      return {
        id: imageId,
        topicId,
        url: data.url || '',
        source: data.source || '',
        photographer: data.photographer || '',
        license: data.license || '',
        order: data.order || 0,
      }
    }

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
    if (USE_MOCK) {
      await delay(300)
      return
    }

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
    if (USE_MOCK) {
      await delay(300)
      return
    }

    await fetchAPI(`/images/${topicId}/reorder`, {
      method: 'PUT',
      body: JSON.stringify({
        image_orders: orders,
      }),
    })
  },
}
