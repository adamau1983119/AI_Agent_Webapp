/**
 * 連接錯誤顯示組件
 * 當 API 連接失敗時顯示友善的錯誤訊息和修復建議
 */
import { AlertCircle, RefreshCw, ExternalLink } from 'lucide-react'
import { useTranslation } from '@/i18n'

interface ConnectionErrorDisplayProps {
  error?: Error | string
  onRetry?: () => void
}

export default function ConnectionErrorDisplay({
  error,
  onRetry,
}: ConnectionErrorDisplayProps) {
  const { t } = useTranslation()
  const errorMessage =
    typeof error === 'string' ? error : error?.message || 'Failed to fetch'
  
  const isConnectionError =
    errorMessage.includes('Failed to fetch') ||
    errorMessage.includes('NetworkError') ||
    errorMessage.includes('CORS')

  if (!isConnectionError) {
    return null
  }

  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
  const backendUrl = apiUrl.replace('/api/v1', '')

  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-2xl mx-auto">
      <div className="flex items-start gap-3">
        <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <h3 className="font-semibold text-red-800 mb-2">
            {t('error.cannotConnect')}
          </h3>
          <p className="text-sm text-red-700 mb-4">
            {errorMessage}
          </p>

          <div className="bg-white rounded-lg p-4 mb-4">
            <h4 className="font-medium text-gray-800 mb-2 text-sm">
              🔍 {t('error.diagnosticSteps')}
            </h4>
            <ol className="list-decimal list-inside space-y-1 text-sm text-gray-700">
              <li>
                {t('error.checkBackend')}
                <a
                  href={`${backendUrl}/health`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline ml-1 inline-flex items-center gap-1"
                >
                  {t('error.healthCheck')}
                  <ExternalLink className="w-3 h-3" />
                </a>
              </li>
              <li>
                {t('error.checkApiUrl')}<code className="bg-gray-100 px-1 rounded text-xs">{apiUrl}</code>
              </li>
              <li>{t('error.checkCors')}</li>
              <li>{t('error.checkNetwork')}</li>
            </ol>
          </div>

          <div className="flex gap-2">
            {onRetry && (
              <button
                onClick={onRetry}
                className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm"
              >
                <RefreshCw className="w-4 h-4" />
                {t('common.retry')}
              </button>
            )}
            <a
              href={`${backendUrl}/docs`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm"
            >
              <ExternalLink className="w-4 h-4" />
              {t('error.viewApiDocs')}
            </a>
          </div>

          <p className="text-xs text-gray-500 mt-4">
            💡 {t('error.persistentHint')}
          </p>
        </div>
      </div>
    </div>
  )
}
