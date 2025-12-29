/**
 * 主題相關 API
 */

import { fetchAPI, fetchAPIWithPagination, USE_MOCK, delay } from './client'
import { mockTopics } from './mockData'
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
    if (USE_MOCK) {
      await delay(500)
      let topics = [...mockTopics]
      if (filters?.category) {
        topics = topics.filter((t) => t.category === filters.category)
      }
      if (filters?.status) {
        topics = topics.filter((t) => t.status === filters.status)
      }

      // Mock 分頁
      const page = filters?.page || 1
      const limit = filters?.limit || 12
      const start = (page - 1) * limit
      const end = start + limit
      const paginatedTopics = topics.slice(start, end)
      const totalPages = Math.ceil(topics.length / limit)

      return {
        data: paginatedTopics,
        pagination: {
          page,
          limit,
          total: topics.length,
          totalPages,
        },
      }
    }

    try {
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
    } catch (error) {
      console.error('Failed to fetch topics, falling back to mock data', error)
      await delay(500)
      // 返回 Mock 資料的分頁格式
      const page = filters?.page || 1
      const limit = filters?.limit || 12
      const start = (page - 1) * limit
      const end = start + limit
      const paginatedTopics = mockTopics.slice(start, end)
      const totalPages = Math.ceil(mockTopics.length / limit)

      return {
        data: paginatedTopics,
        pagination: {
          page,
          limit,
          total: mockTopics.length,
          totalPages,
        },
      }
    }
  },

  /**
   * 取得主題詳情
   */
  getTopic: async (id: string): Promise<Topic | null> => {
    if (USE_MOCK) {
      await delay(300)
      return mockTopics.find((t) => t.id === id) || null
    }

    try {
      const topic = await fetchAPI<any>(`/topics/${id}`)
      if (!topic) {
        console.warn(`Topic not found: ${id}`)
        return null
      }
      return convertTopic(topic)
    } catch (error: any) {
      // 如果是 404 錯誤，直接返回 null（主題不存在）
      if (error?.status === 404) {
        console.warn(`Topic not found (404): ${id}`, error)
        return null
      }
      // 其他錯誤，記錄並嘗試使用 mock 數據
      console.error(`Failed to fetch topic ${id}, falling back to mock data`, error)
      await delay(300)
      return mockTopics.find((t) => t.id === id) || null
    }
  },

  /**
   * 更新主題
   */
  updateTopic: async (id: string, data: TopicUpdate): Promise<Topic> => {
    if (USE_MOCK) {
      await delay(300)
      const topic = mockTopics.find((t) => t.id === id)
      if (!topic) throw new Error('Topic not found')
      return { ...topic, ...data }
    }

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
    if (USE_MOCK) {
      await delay(300)
      const topic = mockTopics.find((t) => t.id === id)
      if (!topic) throw new Error('Topic not found')
      return { ...topic, status }
    }

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
    if (USE_MOCK) {
      await delay(300)
      return
    }

    await fetchAPI(`/topics/${id}`, {
      method: 'DELETE',
    })
  },
}
