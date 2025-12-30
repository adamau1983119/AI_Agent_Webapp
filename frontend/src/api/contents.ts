/**
 * 內容相關 API
 * 只使用真實後端 API，不使用 Mock 數據
 */

import { fetchAPI } from './client'
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
    const content = await fetchAPI<any>(`/contents/${topicId}`)
    return convertContent(content)
  },

  /**
   * 生成內容
   */
  generateContent: async (
    topicId: string,
    params: GenerateContentParams
  ): Promise<Content> => {
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
