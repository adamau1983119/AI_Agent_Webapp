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

  // 預設錯誤訊息（實際使用時應通過 i18n 轉換）
  // 注意：這個函數通常在組件外部使用，無法直接使用 i18n
  // 後端應該已經返回多語言的錯誤訊息
  return new APIError('Unknown error', 0, 'UNKNOWN_ERROR')
}

/**
 * 根據 HTTP 狀態碼處理錯誤
 */
/**
 * 根據 HTTP 狀態碼處理錯誤
 * 注意：後端錯誤訊息應該已經使用 i18n，這裡的預設訊息僅作為後備
 * 預設訊息使用英文，因為這是開發者可見的後備訊息
 */
function normalizeDetailMessage(detail: unknown): string | undefined {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    const parts = detail
      .map((item) => {
        if (typeof item === 'string') return item
        if (item && typeof item === 'object' && 'msg' in item) {
          const msg = (item as { msg?: unknown }).msg
          return typeof msg === 'string' ? msg : undefined
        }
        return undefined
      })
      .filter(Boolean)
    return parts.length > 0 ? parts.join('；') : undefined
  }
  if (detail && typeof detail === 'object' && 'message' in (detail as object)) {
    const m = (detail as { message?: unknown }).message
    return typeof m === 'string' ? m : undefined
  }
  return undefined
}

/** 後端 FastAPI HTTPException(detail={ code }) 時位於 body.detail.code */
export function getErrorDetailCode(errorData?: { detail?: unknown }): string | undefined {
  const d = errorData?.detail
  if (d && typeof d === 'object' && 'code' in (d as object)) {
    const c = (d as { code?: unknown }).code
    return typeof c === 'string' ? c : undefined
  }
  return undefined
}

export function handleHTTPError(status: number, errorData?: any): APIError {
  // 優先使用後端返回的錯誤訊息（應該已經是多語言的）
  // 如果後端沒有返回訊息，使用英文作為後備（因為這是開發者可見的）
  let message =
    errorData?.message ||
    normalizeDetailMessage(errorData?.detail) ||
    (typeof errorData?.detail === 'string' ? errorData.detail : undefined) ||
    'Request failed'
  let code = 'HTTP_ERROR'

  switch (status) {
    case 400:
      // 優先使用後端返回的 message，如果沒有則使用 detail
      message = errorData?.message || errorData?.detail || 'Request parameter error'
      // 如果有 suggestion，添加到訊息中
      if (errorData?.suggestion) {
        message = `${message}\n${errorData.suggestion}`
      }
      code = 'BAD_REQUEST'
      break
    case 401:
      message = errorData?.message || errorData?.detail || 'Unauthorized, please login again'
      code = 'UNAUTHORIZED'
      break
    case 403:
      message = errorData?.message || errorData?.detail || 'Forbidden to access this resource'
      code = 'FORBIDDEN'
      break
    case 404:
      message = errorData?.message || errorData?.detail || 'Resource not found'
      code = 'NOT_FOUND'
      break
    case 422:
      message = errorData?.message || errorData?.detail || 'Data validation failed'
      code = 'VALIDATION_ERROR'
      break
    case 429: {
      const biz =
        getErrorDetailCode(errorData) ||
        (typeof errorData?.detail === 'string' ? errorData.detail : undefined)
      message =
        errorData?.message ||
        normalizeDetailMessage(errorData?.detail) ||
        (typeof errorData?.detail === 'string' ? errorData.detail : undefined) ||
        'Too many requests, please try again later'
      code = biz || 'RATE_LIMIT'
      break
    }
    case 500:
      message = errorData?.message || errorData?.detail || 'Internal server error'
      code = 'INTERNAL_ERROR'
      break
    case 503:
      message = errorData?.message || errorData?.detail || 'Service temporarily unavailable'
      code = 'SERVICE_UNAVAILABLE'
      break
    default:
      message = errorData?.message || errorData?.detail || `HTTP error: ${status}`
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
