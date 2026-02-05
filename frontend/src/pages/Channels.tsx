/**
 * 頻道管理頁面
 * Phase 3: 內容功能
 */
import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
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

export default function Channels() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();
  
  const [channels, setChannels] = useState<Channel[]>([]);
  const [maxChannels, setMaxChannels] = useState(3);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // 載入頻道
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    
    loadChannels();
  }, [isAuthenticated, navigate]);
  
  const loadChannels = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await channelsApi.getMyChannels();
      setChannels(response.channels);
      setMaxChannels(response.max_channels);
    } catch (err: any) {
      setError(err.message || t('channels.loadFailed'));
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleDeleteChannel = async (channelId: string, channelName: string) => {
    if (!confirm(`${t('channels.deleteChannel')}「${channelName}」?`)) {
      return;
    }
    
    try {
      await channelsApi.deleteChannel(channelId);
      toast.success(t('channels.deleted'));
      loadChannels();
    } catch (err: any) {
      toast.error(err.message || t('channels.deleteFailed'));
    }
  };
  
  const handleTriggerCollection = async (channelId: string) => {
    try {
      await channelsApi.triggerCollection(channelId);
      toast.success(t('channels.collectTriggered'));
    } catch (err: any) {
      toast.error(err.message || t('channels.triggerFailed'));
    }
  };
  
  // 未登入
  if (!isAuthenticated) {
    return null;
  }
  
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 標題 */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              {t('channels.title')}
            </h1>
            <p className="text-gray-500 dark:text-gray-400 mt-1">
              {t('nav.channels')}（{channels.length}/{maxChannels}）
            </p>
          </div>
          
          {channels.length < maxChannels && (
            <Link
              to="/channels/create"
              className="px-6 py-3 bg-gradient-to-r from-purple-500 to-cyan-500 hover:from-purple-600 hover:to-cyan-600 text-white font-medium rounded-lg transition-all duration-200 flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              {t('channels.create')}
            </Link>
          )}
        </div>
        
        {/* 載入中 */}
        {isLoading && (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <svg className="animate-spin h-12 w-12 text-purple-500 mx-auto mb-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <p className="text-gray-500">{t('common.loading')}</p>
            </div>
          </div>
        )}
        
        {/* 錯誤 */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 text-center">
            <p className="text-red-600 dark:text-red-400">{error}</p>
            <button
              onClick={loadChannels}
              className="mt-4 px-4 py-2 bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-lg hover:bg-red-200 dark:hover:bg-red-900/50"
            >
              {t('common.retry')}
            </button>
          </div>
        )}
        
        {/* 空狀態 */}
        {!isLoading && !error && channels.length === 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-12 text-center shadow-lg">
            <div className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-purple-100 to-cyan-100 dark:from-purple-900/30 dark:to-cyan-900/30 rounded-full flex items-center justify-center">
              <svg className="w-12 h-12 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">
              {t('channels.noChannels')}
            </h2>
            <p className="text-gray-500 dark:text-gray-400 mb-6 max-w-md mx-auto">
              {t('channels.createFirst')}
            </p>
            <Link
              to="/channels/create"
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-500 to-cyan-500 text-white font-medium rounded-lg hover:from-purple-600 hover:to-cyan-600 transition-all duration-200"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              {t('channels.createNew')}
            </Link>
          </div>
        )}
        
        {/* 頻道列表 */}
        {!isLoading && !error && channels.length > 0 && (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {channels.map((channel) => (
              <ChannelCard
                key={channel.id}
                channel={channel}
                onDelete={() => handleDeleteChannel(channel.id, channel.name)}
                onTriggerCollection={() => handleTriggerCollection(channel.id)}
              />
            ))}
            
            {/* 新增頻道卡片 */}
            {channels.length < maxChannels && (
              <Link
                to="/channels/create"
                className="bg-white dark:bg-gray-800 rounded-2xl p-6 border-2 border-dashed border-gray-300 dark:border-gray-600 hover:border-purple-500 dark:hover:border-purple-500 transition-colors duration-200 flex flex-col items-center justify-center min-h-[240px] group"
              >
                <div className="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center group-hover:bg-purple-100 dark:group-hover:bg-purple-900/30 transition-colors">
                  <svg className="w-8 h-8 text-gray-400 group-hover:text-purple-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                </div>
                <p className="mt-4 text-gray-500 dark:text-gray-400 group-hover:text-purple-500 transition-colors">
                  {t('channels.createNew')}
                </p>
              </Link>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// 頻道卡片組件
function ChannelCard({
  channel,
  onDelete,
  onTriggerCollection,
}: {
  channel: Channel;
  onDelete: () => void;
  onTriggerCollection: () => void;
}) {
  const { t } = useTranslation();
  const [showMenu, setShowMenu] = useState(false);
  
  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-shadow duration-200">
      {/* 頭部 */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <span className="text-3xl">
            {categoryIcons[channel.category as ChannelCategory]}
          </span>
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white">
              {channel.name}
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {categoryLabels[channel.category as ChannelCategory]} · {regionLabels[channel.region as ChannelRegion]}
            </p>
          </div>
        </div>
        
        {/* 選單 */}
        <div className="relative">
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <circle cx="12" cy="5" r="2" />
              <circle cx="12" cy="12" r="2" />
              <circle cx="12" cy="19" r="2" />
            </svg>
          </button>
          
          {showMenu && (
            <>
              <div
                className="fixed inset-0 z-10"
                onClick={() => setShowMenu(false)}
              />
              <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-700 rounded-lg shadow-lg border border-gray-200 dark:border-gray-600 py-1 z-20">
                <Link
                  to={`/channels/${channel.id}/edit`}
                  className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-600"
                >
                  {t('channels.editChannel')}
                </Link>
                <button
                  onClick={() => {
                    setShowMenu(false);
                    onTriggerCollection();
                  }}
                  className="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-600"
                >
                  {t('channels.collectNow')}
                </button>
                <hr className="my-1 border-gray-200 dark:border-gray-600" />
                <button
                  onClick={() => {
                    setShowMenu(false);
                    onDelete();
                  }}
                  className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                >
                  {t('channels.deleteChannel')}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
      
      {/* 描述 */}
      {channel.description && (
        <p className="text-gray-600 dark:text-gray-300 text-sm mb-4 line-clamp-2">
          {channel.description}
        </p>
      )}
      
      {/* 自定義關鍵字 */}
      {channel.custom_keywords && channel.custom_keywords.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {channel.custom_keywords.slice(0, 3).map((keyword, index) => (
            <span
              key={index}
              className="px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 text-xs rounded-full"
            >
              {keyword}
            </span>
          ))}
          {channel.custom_keywords.length > 3 && (
            <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 text-xs rounded-full">
              +{channel.custom_keywords.length - 3}
            </span>
          )}
        </div>
      )}
      
      {/* 統計 */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-100 dark:border-gray-700">
        <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
          <span>{channel.topic_count} {t('channels.topics')}</span>
          {channel.last_collected_at && (
            <span>
              {new Date(channel.last_collected_at).toLocaleDateString()}
            </span>
          )}
        </div>
        
        {/* 狀態指示器 */}
        <div className={`w-2 h-2 rounded-full ${
          channel.collection_status === 'collecting'
            ? 'bg-yellow-500 animate-pulse'
            : channel.status === 'active'
            ? 'bg-green-500'
            : 'bg-gray-400'
        }`} />
      </div>
    </div>
  );
}

