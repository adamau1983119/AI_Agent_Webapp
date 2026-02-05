/**
 * 錯誤顯示元件
 */

import { APIError } from '@/api/errors'
import { useTranslation } from '@/i18n'

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
  const { t } = useTranslation()
  const apiError = error instanceof APIError ? error : new APIError(t('error.unknown'), 0)

  const getErrorMessage = () => {
    if (apiError.status === 404) {
      return t('error.notFound')
    }
    if (apiError.status === 401) {
      return t('error.unauthorized')
    }
    if (apiError.status === 403) {
      return t('error.forbidden')
    }
    if (apiError.status === 500) {
      return t('error.server')
    }
    return apiError.message || t('error.networkError')
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
          <h3 className="text-sm font-medium text-red-800">{t('common.error')}</h3>
          <p className="mt-2 text-sm text-red-700">{getErrorMessage()}</p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-4 text-sm font-medium text-red-800 hover:text-red-900 underline"
            >
              {t('common.retry')}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
