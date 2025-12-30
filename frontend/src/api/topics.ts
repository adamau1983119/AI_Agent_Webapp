/**
 * 主題相關 API
 * 只使用真實後端 API，不使用 Mock 數據
 */

import { fetchAPI, fetchAPIWithPagination } from './client'
import type { Topic } from '@/types'

/**
 * 類型轉換函數：API Topic → Frontend Topic
 */
function convertTopic(apiTopic: any): Topic {
  return {
    id: apiTopic.id,
    title: apiTopic.title,
    category: apiTopic.category,
    status: apiTopic.status,
    source: apiTopic.source || '',
    generatedAt: apiTopic.generated_at || apiTopic.generatedAt,
    updatedAt: apiTopic.updated_at || apiTopic.updatedAt,
    imageCount: apiTopic.image_count || 0,
    wordCount: apiTopic.word_count || 0,
  }
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
    params.append('limit', (filters?.limit || 12).toString())
    if (filters?.sort) params.append('sort', filters.sort)
    if (filters?.order) params.append('order', filters.order)

    const response = await fetchAPIWithPagination<any>(
      `/topics?${params.toString()}`
    )

    // 從後端分頁資訊或計算分頁資訊
    const page = filters?.page || 1
    const limit = filters?.limit || 12
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
  getTopic: async (id: string): Promise<Topic | null> => {
    const topic = await fetchAPI<any>(`/topics/${id}`)
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
}
