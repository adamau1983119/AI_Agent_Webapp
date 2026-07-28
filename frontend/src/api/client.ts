/**
 * API 客戶端設定
 * 只使用真實後端 API，不使用 Mock 數據
 */

import {
  requestInterceptor,
  responseInterceptor,
  paginationResponseInterceptor,
  type RequestConfig,
} from './interceptors'
import { handleAPIError } from './errors'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

/**
 * HTTP 請求輔助函數（簡化版，保留必要功能）
 * 使用攔截器系統處理認證、錯誤等
 */
async function fetchAPI<T>(
  endpoint: string,
  options?: RequestConfig
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`
  const timeout = options?.timeout || 10000 // 預設 10 秒超時

  try {
    // 1. 請求攔截器處理（添加認證、請求頭等）
    const config = requestInterceptor(options || {})

    // 2. 發送請求（帶超時控制）
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeout)
    
    try {
      const response = await fetch(url, {
        ...config,
        signal: controller.signal,
      })
      clearTimeout(timeoutId)

      // 3. 響應攔截器處理（統一錯誤處理、分頁等）
      const data = await responseInterceptor(response, options?.skipErrorHandler)
      return data as T
    } catch (fetchError: any) {
      clearTimeout(timeoutId)
      if (fetchError.name === 'AbortError') {
        throw new Error(`Request timeout (${timeout}ms): ${endpoint}`)
      }
      throw fetchError
    }
  } catch (error) {
    // 4. 統一錯誤處理
    const apiError = handleAPIError(error)
    
    // 404 錯誤是正常情況（資源不存在），靜默處理
    // 429 錯誤由 React Query 處理，不需要額外日誌
    if (apiError.status === 404 || apiError.status === 429) {
      throw apiError
    }
    
    // 詳細錯誤日誌（開發和生產環境都顯示）
    console.error(`❌ API request failed: ${endpoint}`, {
      url,
      error: apiError,
      message: apiError.message,
      status: apiError.status,
    })
    
    // 網路錯誤提供診斷建議
    if (apiError.message.includes('Failed to fetch') || 
        apiError.message.includes('NetworkError') ||
        apiError.message.includes('Request timeout') ||
        apiError.status === 0) {
      console.error('💡 診斷建議：')
      console.error('  1. 檢查後端服務是否運行：', API_BASE_URL.replace('/api/v1', '/health'))
      console.error('  2. 檢查 VITE_API_URL 環境變數：', API_BASE_URL)
      console.error('  3. 檢查 CORS 設定是否正確')
      console.error('  4. 檢查網路連接')
      // 對於智能匹配照片，超時時間可能需要更長
      if (endpoint.includes('/match')) {
        console.error('  5. 智能匹配照片可能需要更長時間，請檢查後端日誌')
      }
    }
    
    throw apiError
  }
}

/**
 * HTTP 請求：回傳完整 JSON（不拆 data 欄位）。
 * MyChannel 等 envelope 含 balance／empty 與 data 並存時必須用此函式。
 */
async function fetchAPIEnvelope<T>(
  endpoint: string,
  options?: RequestConfig
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`
  const timeout = options?.timeout || 10000

  try {
    const config = requestInterceptor(options || {})
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeout)

    try {
      const response = await fetch(url, {
        ...config,
        signal: controller.signal,
      })
      clearTimeout(timeoutId)

      if (!response.ok) {
        await responseInterceptor(response, options?.skipErrorHandler)
      }

      const contentType = response.headers.get('content-type')
      if (!contentType || !contentType.includes('application/json')) {
        return null as T
      }
      return (await response.json()) as T
    } catch (fetchError: any) {
      clearTimeout(timeoutId)
      if (fetchError.name === 'AbortError') {
        throw new Error(`Request timeout (${timeout}ms): ${endpoint}`)
      }
      throw fetchError
    }
  } catch (error) {
    const apiError = handleAPIError(error)
    if (apiError.status === 404 || apiError.status === 429) {
      throw apiError
    }
    console.error(`❌ API request failed: ${endpoint}`, {
      url,
      error: apiError,
      message: apiError.message,
      status: apiError.status,
    })
    throw apiError
  }
}

/**
 * 取得完整響應（包含分頁資訊）
 */
async function fetchAPIWithPagination<T>(
  endpoint: string,
  options?: RequestConfig
): Promise<{ data: T[]; pagination: any }> {
  const url = `${API_BASE_URL}${endpoint}`

  try {
    const config = requestInterceptor(options || {})
    const response = await fetch(url, config)
    const result = await paginationResponseInterceptor(
      response,
      options?.skipErrorHandler
    )
    return result as { data: T[]; pagination: any }
  } catch (error) {
    const apiError = handleAPIError(error)
    console.error(`API request failed: ${endpoint}`, apiError)
    throw apiError
  }
}

// 導出基礎函數供專用模組使用
export { fetchAPI, fetchAPIEnvelope, fetchAPIWithPagination, API_BASE_URL }

/**
 * 統一的 API 介面
 * 為了向後兼容，保留原有的 api 物件
 * 建議新代碼使用專用 API 模組（topicsAPI, contentsAPI, imagesAPI）
 */

import { topicsAPI } from './topics'
import { contentsAPI } from './contents'
import { imagesAPI } from './images'
import { schedulesAPI } from './schedules'
import { interactionsAPI } from './interactions'
import { recommendationsAPI } from './recommendations'
import { discoverAPI } from './discover'
import { publicFeedAPI } from './publicFeed'
import { validateAPI } from './validate'
// delay 已在同檔案中定義（第 20 行），不需要導入

export const api = {
  // 主題相關（使用專用 API）
  getTopics: topicsAPI.getTopics,
  getTopic: topicsAPI.getTopic,
  updateTopic: topicsAPI.updateTopic,
  updateTopicStatus: topicsAPI.updateTopicStatus,
  deleteTopic: topicsAPI.deleteTopic,
  // 搜尋相關（新的搜尋端點）
  searchTopics: topicsAPI.searchTopics,
  checkUrlExists: topicsAPI.checkUrlExists,
  getHotQueries: topicsAPI.getHotQueries,

  // 內容相關（使用專用 API）
  getContent: contentsAPI.getContent,
  generateContent: async (
    topicId: string,
    type: 'article' | 'script' | 'both',
    articleLength: number = 500,
    scriptDuration: number = 30
  ) => {
    return contentsAPI.generateContent(topicId, {
      type,
      article_length: articleLength,
      script_duration: scriptDuration,
    })
  },
  updateContent: contentsAPI.updateContent,
  getContentVersions: contentsAPI.getContentVersions,
  regenerateContent: contentsAPI.regenerateContent,

  // 圖片相關（使用專用 API）
  getImages: imagesAPI.getImages,
  searchImages: async (
    keywords: string,
    page: number = 1,
    limit: number = 20
  ) => {
    const result = await imagesAPI.searchImages({ keywords, page, limit })
    return result.data
  },
  createImage: imagesAPI.createImage,
  updateImage: imagesAPI.updateImage,
  deleteImage: imagesAPI.deleteImage,
  reorderImages: imagesAPI.reorderImages,

  // 排程相關（使用專用 API）
  getSchedules: schedulesAPI.getSchedules,
  manualGenerateTopics: schedulesAPI.manualGenerateTopics,
  startScheduler: schedulesAPI.startScheduler,
  stopScheduler: schedulesAPI.stopScheduler,
  getSchedulerStatus: schedulesAPI.getSchedulerStatus,
}

// 導出專用 API 模組供新代碼使用
export {
  topicsAPI,
  contentsAPI,
  imagesAPI,
  schedulesAPI,
  interactionsAPI,
  recommendationsAPI,
  discoverAPI,
  publicFeedAPI,
  validateAPI,
}
export { userPreferencesAPI } from './userPreferences'
