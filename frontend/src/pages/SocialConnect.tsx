/**
 * 社交平台連接頁面
 * Phase 5: 分發與整合 — 方案 A：一平台一卡
 */
import { useState, useEffect, type ReactNode } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { useTranslation } from '../i18n'
import {
  socialApi,
  SocialConnection,
  SocialPlatform,
  platformLabels,
} from '../api/social'
import PlatformIcon from '@/components/ui/PlatformIcon'
import toast from 'react-hot-toast'

function PlatformCard({
  platform,
  description,
  connected,
  username,
  comingSoon,
  isConnecting,
  onConnect,
  onDisconnect,
  connectNote,
  testIdConnect,
}: {
  platform: SocialPlatform
  description: string
  connected: boolean
  username?: string
  comingSoon?: boolean
  isConnecting?: boolean
  onConnect?: () => void
  onDisconnect?: () => void
  connectNote?: string
  testIdConnect?: string
}) {
  const { t } = useTranslation()

  let action: ReactNode
  if (comingSoon) {
    action = (
      <span className="px-3 py-1 bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400 text-sm rounded-full shrink-0">
        {t('social.threadsComingSoon')}
      </span>
    )
  } else if (connected) {
    action = (
      <div className="flex items-center gap-2 shrink-0">
        <span className="text-green-600 dark:text-green-400 text-sm flex items-center gap-1">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          {t('social.connected')}
        </span>
        <button
          type="button"
          onClick={onDisconnect}
          className="text-red-500 hover:text-red-600 text-sm min-h-[44px] px-2"
          data-testid={`btn-social-disconnect-${platform}`}
        >
          {t('social.disconnect')}
        </button>
      </div>
    )
  } else {
    action = (
      <button
        type="button"
        onClick={onConnect}
        disabled={isConnecting}
        data-testid={testIdConnect ?? `btn-social-connect-${platform}`}
        className="shrink-0 px-4 py-2 text-sm font-medium rounded-lg bg-gray-900 dark:bg-white text-white dark:text-gray-900 hover:opacity-90 disabled:opacity-50 min-h-[44px] transition-opacity"
      >
        {isConnecting ? t('common.loading') : t('social.connect')}
      </button>
    )
  }

  return (
    <div
      className={`bg-white dark:bg-gray-800 rounded-2xl p-5 sm:p-6 shadow-lg border ${
        connected
          ? 'border-green-200 dark:border-green-800'
          : 'border-gray-100 dark:border-gray-700'
      } ${comingSoon ? 'opacity-70' : ''}`}
      data-testid={`card-social-platform-${platform}`}
    >
      <div className="flex flex-col sm:flex-row sm:items-center gap-4 sm:justify-between">
        <div className="flex items-start gap-3 min-w-0">
          <PlatformIcon platform={platform} size="lg" label={platformLabels[platform]} />
          <div className="min-w-0">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              {platformLabels[platform]}
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5 line-clamp-3 break-words">
              {description}
            </p>
            {connected && username && (
              <p className="text-sm text-gray-600 dark:text-gray-300 mt-1 truncate">@{username}</p>
            )}
            {!connected && connectNote && onConnect && (
              <p className="text-xs text-gray-400 dark:text-gray-500 mt-2 line-clamp-2">{connectNote}</p>
            )}
          </div>
        </div>
        {action}
      </div>
    </div>
  )
}

export default function SocialConnect() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { isAuthenticated } = useAuthStore()

  const [connections, setConnections] = useState<SocialConnection[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [connectingPlatform, setConnectingPlatform] = useState<string | null>(null)

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }

    const success = searchParams.get('success')
    const error = searchParams.get('error')

    if (success === 'true') {
      toast.success(t('common.success'))
    } else if (error) {
      toast.error(`${t('common.failed')}: ${error}`)
    }

    loadData()
  }, [isAuthenticated, navigate, searchParams])

  const loadData = async () => {
    setIsLoading(true)
    try {
      const connectionsRes = await socialApi.getMyConnections()
      setConnections(connectionsRes.connections)
    } catch {
      toast.error(t('common.failed'))
    } finally {
      setIsLoading(false)
    }
  }

  const handleConnectMeta = async (target: 'facebook' | 'instagram') => {
    setConnectingPlatform(target)
    try {
      const { oauth_url } = await socialApi.getMetaOAuthUrl(target)
      window.location.href = oauth_url
    } catch {
      toast.error(t('common.failed'))
      setConnectingPlatform(null)
    }
  }

  const handleConnectTikTok = async () => {
    setConnectingPlatform('tiktok')
    try {
      const { oauth_url } = await socialApi.getTikTokOAuthUrl()
      window.location.href = oauth_url
    } catch {
      toast.error(t('feature.comingSoon'))
      setConnectingPlatform(null)
    }
  }

  const handleDisconnect = async (platform: SocialPlatform) => {
    if (!confirm(`${t('social.disconnect')} ${platformLabels[platform]}?`)) {
      return
    }

    try {
      await socialApi.disconnectPlatform(platform)
      toast.success(t('common.success'))
      loadData()
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : t('common.failed')
      toast.error(message)
    }
  }

  const isConnected = (platform: SocialPlatform) =>
    connections.some((c) => c.platform === platform && c.status === 'connected')

  const getConnection = (platform: SocialPlatform) =>
    connections.find((c) => c.platform === platform)

  const facebookConnecting = connectingPlatform === 'facebook'
  const instagramConnecting = connectingPlatform === 'instagram'

  if (!isAuthenticated) return null

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">{t('social.title')}</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-2">{t('social.pageDesc')}</p>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <svg className="animate-spin h-12 w-12 text-purple-500" fill="none" viewBox="0 0 24 24" aria-hidden>
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          </div>
        ) : (
          <div className="space-y-4">
            <PlatformCard
              platform="instagram"
              description={t('social.instagramDesc')}
              connected={isConnected('instagram')}
              username={getConnection('instagram')?.platform_username}
              isConnecting={instagramConnecting}
              onConnect={() => handleConnectMeta('instagram')}
              onDisconnect={() => handleDisconnect('instagram')}
              connectNote={t('social.instagramConnectNote')}
              testIdConnect="btn-social-connect-instagram"
            />

            <PlatformCard
              platform="facebook"
              description={t('social.facebookDesc')}
              connected={isConnected('facebook')}
              username={getConnection('facebook')?.platform_username}
              isConnecting={facebookConnecting}
              onConnect={() => handleConnectMeta('facebook')}
              onDisconnect={() => handleDisconnect('facebook')}
              connectNote={t('social.facebookConnectNote')}
              testIdConnect="btn-social-connect-facebook"
            />

            <PlatformCard
              platform="threads"
              description={t('social.threadsDesc')}
              connected={isConnected('threads')}
              username={getConnection('threads')?.platform_username}
              comingSoon
            />

            <PlatformCard
              platform="tiktok"
              description={t('social.tiktokDesc')}
              connected={isConnected('tiktok')}
              username={getConnection('tiktok')?.platform_username}
              isConnecting={connectingPlatform === 'tiktok'}
              onConnect={handleConnectTikTok}
              onDisconnect={() => handleDisconnect('tiktok')}
            />

            <PlatformCard
              platform="twitter"
              description={t('social.twitterDesc')}
              connected={false}
              comingSoon
            />

            <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-xl">
              <h3 className="text-sm font-medium text-blue-800 dark:text-blue-300 mb-2">
                {t('social.tips')}
              </h3>
              <ul className="text-sm text-blue-700 dark:text-blue-400 space-y-1 list-none">
                <li>• {t('social.tip1')}</li>
                <li>• {t('social.tip2')}</li>
                <li>• {t('social.tip3')}</li>
                <li>• {t('social.tip4')}</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
