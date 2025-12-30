/**
 * 內容相關 API
 */

import { fetchAPI, USE_MOCK, delay } from './client'
import { mockContents } from './mockData'
import type { Content } from '@/types'

/**
 * 類型轉換函數：API Content → Frontend Content
 */
function convertContent(apiContent: any): Content {
  return {
    id: apiContent.id,
    topicId: apiContent.topic_id,
    article: apiContent.article || '',
    script: apiContent.script || '',
    wordCount: apiContent.word_count || 0,
    estimatedDuration: apiContent.estimated_duration || 0,
    modelUsed: apiContent.model_used || '',
    version: apiContent.version || 1,
  }
}

/**
 * 內容生成類型
 */
export type ContentType = 'article' | 'script' | 'both'

/**
 * 內容生成參數
 */
export interface GenerateContentParams {
  type: ContentType
  article_length?: number
  script_duration?: number
}

/**
 * 內容更新資料
 */
export interface ContentUpdate {
  article?: string
  script?: string
}

/**
 * 內容 API
 */
export const contentsAPI = {
  /**
   * 取得主題內容
   */
  getContent: async (topicId: string): Promise<Content | null> => {
    if (USE_MOCK) {
      await delay(300)
      return mockContents[topicId] || null
    }

    try {
      const content = await fetchAPI<any>(`/contents/${topicId}`)
      return convertContent(content)
    } catch (error) {
      // 生產環境不應該 fallback 到 mock 數據
      console.error('Failed to fetch content from backend', error)
      throw error  // 直接拋出錯誤
    }
  },

  /**
   * 生成內容
   */
  generateContent: async (
    topicId: string,
    params: GenerateContentParams
  ): Promise<Content> => {
    if (USE_MOCK) {
      await delay(2000) // 模擬生成時間
      return (
        mockContents[topicId] || {
          id: `content_${topicId}`,
          topicId,
          article: '生成的短文內容...',
          script: '生成的腳本內容...',
          wordCount: params.article_length || 500,
          estimatedDuration: params.script_duration || 30,
          modelUsed: 'qwen-turbo',
          version: 1,
        }
      )
    }

    const content = await fetchAPI<any>(`/contents/${topicId}/generate`, {
      method: 'POST',
      body: JSON.stringify({
        type: params.type,
        article_length: params.article_length || 500,
        script_duration: params.script_duration || 30,
      }),
    })

    return convertContent(content)
  },

  /**
   * 更新內容
   */
  updateContent: async (
    topicId: string,
    data: ContentUpdate
  ): Promise<Content> => {
    if (USE_MOCK) {
      await delay(300)
      const content = mockContents[topicId]
      if (!content) throw new Error('Content not found')
      return { ...content, ...data }
    }

    const content = await fetchAPI<any>(`/contents/${topicId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })

    return convertContent(content)
  },

  /**
   * 取得內容版本歷史
   */
  getContentVersions: async (topicId: string): Promise<Content[]> => {
    if (USE_MOCK) {
      await delay(300)
      return []
    }

    const versions = await fetchAPI<any[]>(`/contents/${topicId}/versions`)
    return versions.map(convertContent)
  },

  /**
   * 重新生成內容
   */
  regenerateContent: async (
    topicId: string,
    params: GenerateContentParams
  ): Promise<Content> => {
    if (USE_MOCK) {
      await delay(2000)
      return (
        mockContents[topicId] || {
          id: `content_${topicId}`,
          topicId,
          article: '重新生成的短文內容...',
          script: '重新生成的腳本內容...',
          wordCount: params.article_length || 500,
          estimatedDuration: params.script_duration || 30,
          modelUsed: 'qwen-turbo',
          version: 1,
        }
      )
    }

    const content = await fetchAPI<any>(`/contents/${topicId}/regenerate`, {
      method: 'POST',
      body: JSON.stringify({
        type: params.type,
        article_length: params.article_length || 500,
        script_duration: params.script_duration || 30,
      }),
    })

    return convertContent(content)
  },
}
