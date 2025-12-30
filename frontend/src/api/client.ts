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
 * HTTP 請求輔助函數（使用攔截器）
 */
async function fetchAPI<T>(
  endpoint: string,
  options?: RequestConfig
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`

  try {
    // 1. 請求攔截器處理
    const config = requestInterceptor(options || {})

    // 2. 發送請求
    const response = await fetch(url, config)

    // 3. 響應攔截器處理
    const data = await responseInterceptor(response, options?.skipErrorHandler)

    return data as T
  } catch (error) {
    // 4. 統一錯誤處理
    const apiError = handleAPIError(error)
    
    // 詳細錯誤日誌（開發環境）
    if (import.meta.env.DEV) {
      console.error(`❌ API request failed: ${endpoint}`, {
        url,
        error: apiError,
        message: apiError.message,
        status: apiError.status,
      })
      
      // 提供診斷建議
      if (apiError.message.includes('Failed to fetch') || apiError.message.includes('NetworkError')) {
        console.error('💡 診斷建議：')
        console.error('  1. 檢查後端服務是否運行：', API_BASE_URL.replace('/api/v1', '/health'))
        console.error('  2. 檢查 VITE_API_URL 環境變數：', API_BASE_URL)
        console.error('  3. 檢查 CORS 設定是否正確')
        console.error('  4. 檢查網路連接')
      }
    }
    
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
    // 1. 請求攔截器處理
    const config = requestInterceptor(options || {})

    // 2. 發送請求
    const response = await fetch(url, config)

    // 3. 分頁響應攔截器處理
    const result = await paginationResponseInterceptor(
      response,
      options?.skipErrorHandler
    )

    return result as { data: T[]; pagination: any }
  } catch (error) {
    // 4. 統一錯誤處理
    const apiError = handleAPIError(error)
    console.error(`API request failed: ${endpoint}`, apiError)
    throw apiError
  }
}

// 導出基礎函數供專用模組使用
export { fetchAPI, fetchAPIWithPagination, API_BASE_URL }

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
import { validateAPI } from './validate'
// delay 已在同檔案中定義（第 20 行），不需要導入

export const api = {
  // 主題相關（使用專用 API）
  getTopics: topicsAPI.getTopics,
  getTopic: topicsAPI.getTopic,
  updateTopic: topicsAPI.updateTopic,
  updateTopicStatus: topicsAPI.updateTopicStatus,
  deleteTopic: topicsAPI.deleteTopic,

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
  validateAPI,
}
