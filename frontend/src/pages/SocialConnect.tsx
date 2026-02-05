/**
 * 社交平台連接頁面
 * Phase 5: 分發與整合
 */
import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { useTranslation } from '../i18n';
import {
  socialApi,
  SocialConnection,
  PlatformInfo,
  SocialPlatform,
  platformLabels,
  platformIcons,
} from '../api/social';
import toast from 'react-hot-toast';

export default function SocialConnect() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { isAuthenticated } = useAuthStore();
  
  const [connections, setConnections] = useState<SocialConnection[]>([]);
  const [platforms, setPlatforms] = useState<PlatformInfo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [connectingPlatform, setConnectingPlatform] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    
    // 處理 OAuth 回調參數
    const success = searchParams.get('success');
    const error = searchParams.get('error');
    
    if (success === 'true') {
      toast.success(t('common.success'));
    } else if (error) {
      toast.error(`${t('common.failed')}: ${error}`);
    }
    
    loadData();
  }, [isAuthenticated, navigate, searchParams]);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [connectionsRes, platformsRes] = await Promise.all([
        socialApi.getMyConnections(),
        socialApi.getPlatforms(),
      ]);
      setConnections(connectionsRes.connections);
      setPlatforms(platformsRes.platforms);
    } catch (err: any) {
      toast.error(t('common.failed'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleConnectMeta = async () => {
    setConnectingPlatform('meta');
    try {
      const { oauth_url } = await socialApi.getMetaOAuthUrl();
      window.location.href = oauth_url;
    } catch (err: any) {
      toast.error(t('common.failed'));
      setConnectingPlatform(null);
    }
  };

  const handleConnectTikTok = async () => {
    setConnectingPlatform('tiktok');
    try {
      const { oauth_url } = await socialApi.getTikTokOAuthUrl();
      window.location.href = oauth_url;
    } catch (err: any) {
      toast.error(t('feature.comingSoon'));
      setConnectingPlatform(null);
    }
  };

  const handleDisconnect = async (platform: SocialPlatform) => {
    if (!confirm(`${t('social.disconnect')} ${platformLabels[platform]}?`)) {
      return;
    }
    
    try {
      await socialApi.disconnectPlatform(platform);
      toast.success(t('common.success'));
      loadData();
    } catch (err: any) {
      toast.error(err.message || t('common.failed'));
    }
  };

  const isConnected = (platform: SocialPlatform) => {
    return connections.some(
      (c) => c.platform === platform && c.status === 'connected'
    );
  };

  const getConnection = (platform: SocialPlatform) => {
    return connections.find((c) => c.platform === platform);
  };

  if (!isAuthenticated) return null;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 標題 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            {t('social.title')}
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-2">
            {t('social.tip1')}
          </p>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <svg className="animate-spin h-12 w-12 text-purple-500" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          </div>
        ) : (
          <>
            {/* Meta 平台（Instagram + Facebook + Threads） */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg mb-6">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-12 h-12 bg-gradient-to-br from-purple-500 via-pink-500 to-orange-500 rounded-xl flex items-center justify-center text-white text-2xl">
                  M
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                    Meta 平台
                  </h2>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Instagram、Facebook、Threads 一次連接
                  </p>
                </div>
              </div>

              <div className="space-y-4">
                {['instagram', 'facebook', 'threads'].map((platform) => {
                  const p = platform as SocialPlatform;
                  const connection = getConnection(p);
                  const connected = isConnected(p);

                  return (
                    <div
                      key={platform}
                      className={`flex items-center justify-between p-4 rounded-xl border-2 ${
                        connected
                          ? 'border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/20'
                          : 'border-gray-200 dark:border-gray-700'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">{platformIcons[p]}</span>
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">
                            {platformLabels[p]}
                          </p>
                          {connected && connection && (
                            <p className="text-sm text-gray-500 dark:text-gray-400">
                              @{connection.platform_username}
                            </p>
                          )}
                        </div>
                      </div>
                      
                      {connected ? (
                        <div className="flex items-center gap-2">
                          <span className="text-green-600 dark:text-green-400 text-sm flex items-center gap-1">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                            {t('social.connected')}
                          </span>
                          <button
                            onClick={() => handleDisconnect(p)}
                            className="text-red-500 hover:text-red-600 text-sm"
                          >
                            {t('social.disconnect')}
                          </button>
                        </div>
                      ) : (
                        <span className="text-gray-400 text-sm">{t('social.notConnected')}</span>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* 連接按鈕 */}
              {!isConnected('instagram') && !isConnected('facebook') && (
                <button
                  onClick={handleConnectMeta}
                  disabled={connectingPlatform === 'meta'}
                  className="mt-6 w-full px-6 py-3 bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 text-white font-medium rounded-xl hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
                >
                  {connectingPlatform === 'meta' ? (
                    <>
                      <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                      </svg>
                      {t('common.loading')}
                    </>
                  ) : (
                    <>
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                      </svg>
                      {t('social.connect')} Meta
                    </>
                  )}
                </button>
              )}
            </div>

            {/* TikTok */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg mb-6">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-12 h-12 bg-black rounded-xl flex items-center justify-center text-white text-2xl">
                  🎵
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                    TikTok
                  </h2>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    發布影片內容到 TikTok
                  </p>
                </div>
              </div>

              {isConnected('tiktok') ? (
                <div className="flex items-center justify-between p-4 rounded-xl border-2 border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/20">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">🎵</span>
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">TikTok</p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        @{getConnection('tiktok')?.platform_username}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-green-600 dark:text-green-400 text-sm flex items-center gap-1">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      {t('social.connected')}
                    </span>
                    <button
                      onClick={() => handleDisconnect('tiktok')}
                      className="text-red-500 hover:text-red-600 text-sm"
                    >
                      {t('social.disconnect')}
                    </button>
                  </div>
                </div>
              ) : (
                <button
                  onClick={handleConnectTikTok}
                  disabled={connectingPlatform === 'tiktok'}
                  className="w-full px-6 py-3 bg-black text-white font-medium rounded-xl hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
                >
                  {connectingPlatform === 'tiktok' ? (
                    <>
                      <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                      </svg>
                      {t('common.loading')}
                    </>
                  ) : (
                    <>
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                      </svg>
                      {t('social.connect')} TikTok
                    </>
                  )}
                </button>
              )}
            </div>

            {/* Twitter（暫緩） */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg opacity-60">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-blue-400 rounded-xl flex items-center justify-center text-white text-2xl">
                  🐦
                </div>
                <div className="flex-1">
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                    Twitter/X
                  </h2>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    即將推出（API 成本較高）
                  </p>
                </div>
                <span className="px-3 py-1 bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400 text-sm rounded-full">
                  {t('feature.comingSoon')}
                </span>
              </div>
            </div>

            {/* 說明 */}
            <div className="mt-8 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-xl">
              <h3 className="text-sm font-medium text-blue-800 dark:text-blue-300 mb-2">
                💡 {t('social.tips')}
              </h3>
              <ul className="text-sm text-blue-700 dark:text-blue-400 space-y-1">
                <li>• {t('social.tip1')}</li>
                <li>• {t('social.tip2')}</li>
                <li>• {t('social.tip3')}</li>
                <li>• {t('social.tip4')}</li>
              </ul>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

