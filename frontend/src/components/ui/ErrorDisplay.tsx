/**
 * 錯誤顯示元件
 */

import { APIError } from '@/api/errors'

interface ErrorDisplayProps {
  error: unknown
  onRetry?: () => void
  className?: string
}

export default function ErrorDisplay({
  error,
  onRetry,
  className = '',
}: ErrorDisplayProps) {
  const apiError = error instanceof APIError ? error : new APIError('未知錯誤', 0)

  const getErrorMessage = () => {
    if (apiError.status === 404) {
      return '找不到請求的資源'
    }
    if (apiError.status === 401) {
      return '未授權，請重新登入'
    }
    if (apiError.status === 403) {
      return '無權限訪問此資源'
    }
    if (apiError.status === 500) {
      return '伺服器錯誤，請稍後再試'
    }
    return apiError.message || '發生錯誤，請稍後再試'
  }

  return (
    <div className={`bg-red-50 border border-red-200 rounded-lg p-6 ${className}`}>
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <svg
            className="h-5 w-5 text-red-400"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clipRule="evenodd"
            />
          </svg>
        </div>
        <div className="ml-3 flex-1">
          <h3 className="text-sm font-medium text-red-800">錯誤</h3>
          <p className="mt-2 text-sm text-red-700">{getErrorMessage()}</p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-4 text-sm font-medium text-red-800 hover:text-red-900 underline"
            >
              重試
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
