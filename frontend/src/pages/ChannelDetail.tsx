/**
 * 頻道詳情頁
 * Phase 3: 內容功能
 */
import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useTranslation } from '../i18n';
import { useAuthStore } from '../stores/authStore';
import {
  channelsApi,
  Channel,
  ChannelCategory,
  ChannelRegion,
  categoryLabels,
  regionLabels,
  categoryIcons,
} from '../api/channels';
import toast from 'react-hot-toast';

export default function ChannelDetail() {
  const { id } = useParams<{ id: string }>();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();
  
  const [channel, setChannel] = useState<Channel | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCollecting, setIsCollecting] = useState(false);
  
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    
    if (id) {
      loadChannel();
    }
  }, [id, isAuthenticated, navigate]);
  
  const loadChannel = async () => {
    if (!id) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await channelsApi.getChannel(id);
      setChannel(data);
    } catch (err: any) {
      setError(err.message || t('channels.loadFailed'));
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleTriggerCollection = async () => {
    if (!id) return;
    
    setIsCollecting(true);
    try {
      await channelsApi.triggerCollection(id);
      toast.success(t('channels.collectTriggered'));
      // 重新載入頻道資訊
      await loadChannel();
    } catch (err: any) {
      toast.error(err.message || t('channels.triggerFailed'));
    } finally {
      setIsCollecting(false);
    }
  };
  
  // 未登入
  if (!isAuthenticated) {
    return null;
  }
  
  // 載入中
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
          </div>
        </div>
      </div>
    );
  }
  
  // 錯誤
  if (error || !channel) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <p className="text-red-800 dark:text-red-200">{error || t('channels.notFound')}</p>
            <button
              onClick={() => navigate('/channels')}
              data-testid="btn-channel-detail-back"
              className="mt-4 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
            >
              {t('common.back')}
            </button>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 返回按鈕 */}
        <button
          onClick={() => navigate('/channels')}
          data-testid="btn-channel-detail-back"
          className="mb-6 flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          {t('common.back')}
        </button>
        
        {/* 頻道資訊卡片 */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 sm:p-8 shadow-lg mb-6">
          {/* 標題區 */}
          <div className="flex items-start justify-between mb-6">
            <div className="flex items-center gap-4">
              <span className="text-5xl">
                {categoryIcons[channel.category as ChannelCategory]}
              </span>
              <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                  {channel.name}
                </h1>
                <p className="text-gray-500 dark:text-gray-400">
                  {categoryLabels[channel.category as ChannelCategory]} · {regionLabels[channel.region as ChannelRegion]}
                </p>
              </div>
            </div>
            
            {/* 狀態指示器 */}
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${
                channel.status === 'active'
                  ? 'bg-green-500'
                  : channel.status === 'paused'
                  ? 'bg-yellow-500'
                  : 'bg-gray-400'
              }`} />
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {channel.status === 'active' ? t('channels.statusActive') : 
                 channel.status === 'paused' ? t('channels.statusPaused') : 
                 t('channels.statusDeleted')}
              </span>
            </div>
          </div>
          
          {/* 描述 */}
          {channel.description && (
            <div className="mb-6">
              <p className="text-gray-700 dark:text-gray-300">{channel.description}</p>
            </div>
          )}
          
          {/* 關鍵字 */}
          {channel.custom_keywords && channel.custom_keywords.length > 0 && (
            <div className="mb-6">
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">{t('channels.keywords')}</p>
              <div className="flex flex-wrap gap-2">
                {channel.custom_keywords.map((keyword, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded-full text-sm"
                  >
                    {keyword}
                  </span>
                ))}
              </div>
            </div>
          )}
          
          {/* 統計資訊 */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-6 border-t border-gray-200 dark:border-gray-700">
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">{t('channels.topicCount')}</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{channel.topic_count}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">{t('channels.lastCollected')}</p>
              <p className="text-sm text-gray-900 dark:text-white">
                {channel.last_collected_at
                  ? new Date(channel.last_collected_at).toLocaleDateString()
                  : t('channels.neverCollected')}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">{t('channels.collectionStatus')}</p>
              <p className="text-sm text-gray-900 dark:text-white">
                {channel.collection_status === 'collecting' ? t('channels.collecting') :
                 channel.collection_status === 'completed' ? t('channels.completed') :
                 channel.collection_status === 'failed' ? t('channels.failed') :
                 t('channels.idle')}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">{t('channels.createdAt')}</p>
              <p className="text-sm text-gray-900 dark:text-white">
                {new Date(channel.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>
        
        {/* 操作按鈕 */}
        <div className="flex flex-col sm:flex-row gap-3 mb-6">
          <button
            onClick={handleTriggerCollection}
            disabled={isCollecting || channel.collection_status === 'collecting'}
            data-testid="btn-channel-detail-collect"
            className="flex-1 px-6 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 min-h-[44px]"
          >
            {isCollecting || channel.collection_status === 'collecting' ? (
              <>
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                {t('channels.collecting')}
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                {t('channels.collectNow')}
              </>
            )}
          </button>
          <Link
            to={`/channels/${channel.id}/edit`}
            data-testid="btn-channel-detail-edit"
            className="flex-1 px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors flex items-center justify-center gap-2 min-h-[44px]"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            {t('channels.editChannel')}
          </Link>
        </div>
        
        {/* RSS 健康度指示 */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            {t('channels.rssHealth')}
          </h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">{t('channels.rssStatus')}</span>
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                channel.collection_status === 'completed'
                  ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                  : channel.collection_status === 'failed'
                  ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                  : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
              }`}>
                {channel.collection_status === 'completed' ? t('channels.healthy') :
                 channel.collection_status === 'failed' ? t('channels.unhealthy') :
                 t('channels.checking')}
              </span>
            </div>
            {channel.last_collected_at && (
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">{t('channels.lastCheck')}</span>
                <span className="text-sm text-gray-900 dark:text-white">
                  {new Date(channel.last_collected_at).toLocaleString()}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

