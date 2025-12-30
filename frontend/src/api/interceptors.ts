/**
 * API 請求/響應攔截器
 */

import { handleHTTPError, showErrorToUser, type APIError } from './errors'

/**
 * 請求配置類型
 */
export interface RequestConfig extends RequestInit {
  skipAuth?: boolean // 跳過認證
  skipErrorHandler?: boolean // 跳過錯誤處理
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
    }
  }

  // 2. 統一添加請求頭
  if (!headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  // 3. 添加其他通用請求頭
  headers.set('Accept', 'application/json')

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

    const error = handleHTTPError(response.status, errorData)

    // 2. 顯示錯誤給用戶（如果沒有跳過）
    // 注意：404 錯誤通常由調用方處理，這裡不顯示給用戶
    if (!skipErrorHandler && response.status !== 404) {
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
