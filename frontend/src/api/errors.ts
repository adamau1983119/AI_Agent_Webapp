/**
 * API 錯誤處理
 */

/**
 * API 錯誤類別
 */
export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string,
    public details?: any
  ) {
    super(message)
    this.name = 'APIError'
    // 確保錯誤堆疊追蹤正確
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, APIError)
    }
  }
}

/**
 * 統一錯誤處理函數
 */
export function handleAPIError(error: unknown): APIError {
  if (error instanceof APIError) {
    return error
  }

  if (error instanceof Error) {
    return new APIError(error.message, 0, 'UNKNOWN_ERROR')
  }

  return new APIError('未知錯誤', 0, 'UNKNOWN_ERROR')
}

/**
 * 根據 HTTP 狀態碼處理錯誤
 */
export function handleHTTPError(status: number, errorData?: any): APIError {
  let message = '請求失敗'
  let code = 'HTTP_ERROR'

  switch (status) {
    case 400:
      message = errorData?.detail || '請求參數錯誤'
      code = 'BAD_REQUEST'
      break
    case 401:
      message = '未授權，請重新登入'
      code = 'UNAUTHORIZED'
      break
    case 403:
      message = '無權限訪問此資源'
      code = 'FORBIDDEN'
      break
    case 404:
      message = errorData?.detail || '資源不存在'
      code = 'NOT_FOUND'
      break
    case 422:
      message = errorData?.detail || '資料驗證失敗'
      code = 'VALIDATION_ERROR'
      break
    case 429:
      message = '請求過於頻繁，請稍後再試'
      code = 'RATE_LIMIT'
      break
    case 500:
      message = '伺服器內部錯誤'
      code = 'INTERNAL_ERROR'
      break
    case 503:
      message = '服務暫時不可用'
      code = 'SERVICE_UNAVAILABLE'
      break
    default:
      message = errorData?.detail || `HTTP 錯誤: ${status}`
      code = `HTTP_${status}`
  }

  return new APIError(message, status, code, errorData)
}

/**
 * 顯示錯誤訊息給用戶（可選，需要整合 UI 通知系統）
 */
export function showErrorToUser(error: APIError) {
  // 這裡可以整合 toast 通知系統
  console.error('API Error:', {
    message: error.message,
    status: error.status,
    code: error.code,
  })

  // 特殊錯誤處理
  if (error.status === 401) {
    // 未授權，可能需要跳轉到登入頁
    // window.location.href = '/login'
  }
}
