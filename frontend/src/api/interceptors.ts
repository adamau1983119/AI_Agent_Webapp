/**
 * API 請求/響應攔截器
 */

import { handleHTTPError, showErrorToUser, APIError } from './errors'

/**
 * 請求配置類型
 */
export interface RequestConfig extends RequestInit {
  skipAuth?: boolean // 跳過認證
  skipErrorHandler?: boolean // 跳過錯誤處理
  timeout?: number // 請求超時時間（毫秒），預設 10000
}

/**
 * 請求攔截器
 * 統一處理所有 API 請求
 */
export function requestInterceptor(config: RequestConfig): RequestConfig {
  const headers = new Headers(config.headers)

  // 1. 添加認證 Token（如果有的話）
  if (!config.skipAuth) {
    const token = localStorage.getItem('auth_token')
    if (token) {
      headers.set('Authorization', `Bearer ${token}`)
    } else if (import.meta.env.DEV) {
      // 調試：記錄缺少 token 的情況（僅在開發環境）
      console.warn('⚠️ API 請求缺少 auth_token', {
        localStorage: {
          auth_token: localStorage.getItem('auth_token'),
          auth_storage: localStorage.getItem('auth-storage'),
        }
      })
    }
  }

  // 2. 統一添加請求頭
  if (!headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  // 3. 添加其他通用請求頭
  headers.set('Accept', 'application/json')

  // 4. 添加用戶選擇的語言（從 i18n store 讀取）
  try {
    const i18nRaw = localStorage.getItem('i18n-storage')
    if (i18nRaw) {
      const i18nData = JSON.parse(i18nRaw)
      const lang = i18nData?.state?.language
      if (lang) {
        headers.set('X-Language', lang)
      }
    }
  } catch {
    // 靜默處理，使用後端預設語言
  }

  return {
    ...config,
    headers,
  }
}

/**
 * 響應攔截器
 * 統一處理所有 API 響應
 */
export async function responseInterceptor(
  response: Response,
  skipErrorHandler?: boolean
): Promise<any> {
  // 1. 檢查 HTTP 狀態碼
  if (!response.ok) {
    let errorData: any
    try {
      errorData = await response.json()
    } catch {
      errorData = { detail: response.statusText }
    }

    // 2. 針對不同狀態碼提供更友好的錯誤訊息
    let error: APIError
    if (response.status === 400) {
      // 400 錯誤：通常是資料庫未連接或用戶操作錯誤
      const message = errorData?.message || errorData?.detail || 'Bad request'
      const suggestion = errorData?.suggestion || ''
      error = new APIError(
        suggestion ? `${message}\n${suggestion}` : message,
        response.status,
        'BAD_REQUEST',
        errorData
      )
    } else if (response.status === 500) {
      // 500 錯誤：系統內部錯誤
      const message = errorData?.message || errorData?.detail || 'Internal server error'
      error = new APIError(
        message,
        response.status,
        'INTERNAL_ERROR',
        errorData
      )
    } else {
      error = handleHTTPError(response.status, errorData)
    }
    
    // 3. 對於 429 錯誤，添加 Retry-After 資訊
    if (response.status === 429) {
      const retryAfter = response.headers.get('Retry-After')
      if (retryAfter) {
        error.details = {
          ...error.details,
          retryAfter: parseInt(retryAfter, 10),
        }
      }
    }

    // 4. 顯示錯誤給用戶（如果沒有跳過）
    // 注意：404 和 429 錯誤通常由調用方處理，這裡不顯示給用戶
    if (!skipErrorHandler && response.status !== 404 && response.status !== 429) {
      showErrorToUser(error)
    }

    throw error
  }

  // 3. 處理空響應
  const contentType = response.headers.get('content-type')
  if (!contentType || !contentType.includes('application/json')) {
    return null
  }

  // 4. 解析 JSON 響應
  const data = await response.json()

  // 5. 統一資料格式轉換
  // 如果響應有 data 欄位，返回 data；否則返回整個響應
  return data.data !== undefined ? data.data : data
}

/**
 * 分頁響應攔截器
 * 專門處理包含分頁資訊的響應
 */
export async function paginationResponseInterceptor(
  response: Response,
  skipErrorHandler?: boolean
): Promise<{ data: any[]; pagination: any }> {
  // 1. 檢查 HTTP 狀態碼
  if (!response.ok) {
    let errorData: any
    try {
      errorData = await response.json()
    } catch {
      errorData = { detail: response.statusText }
    }

    const error = handleHTTPError(response.status, errorData)

    if (!skipErrorHandler) {
      showErrorToUser(error)
    }

    throw error
  }

  // 2. 解析 JSON 響應
  const result = await response.json()

  // 3. 確保返回格式一致
  return {
    data: result.data || [],
    pagination: result.pagination || {},
  }
}
