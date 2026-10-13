/**
 * 我的自選頻道 — 切換已成立頻道、產出主題卡、三欄格子。
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
  categoryI18nKeys,
  regionI18nKeys,
} from '../api/channels';
import toast from 'react-hot-toast';
import TopicCard from '@/components/ui/TopicCard';
import type { Topic } from '@/types';

export default function ChannelDetail() {
  const { id } = useParams<{ id: string }>();
  const { t, language } = useTranslation();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();

  const [channel, setChannel] = useState<Channel | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCollecting, setIsCollecting] = useState(false);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [topicsTotal, setTopicsTotal] = useState(0);
  const [topicsLoading, setTopicsLoading] = useState(false);
  const [siblings, setSiblings] = useState<Channel[]>([]);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    if (id) {
      loadChannel();
      loadChannelTopics();
    }
    channelsApi.getMyChannels().then((res) => {
      setSiblings(Array.isArray(res.channels) ? res.channels : []);
    }).catch(() => {
      setSiblings([]);
    });
  }, [id, isAuthenticated, navigate, language]);

  const loadChannelTopics = async () => {
    if (!id) return;
    setTopicsLoading(true);
    try {
      const res = await channelsApi.getChannelTopics(id, 1, 50, language);
      setTopics(res.data);
      setTopicsTotal(res.pagination.total);
    } catch (err: any) {
      console.error('loadChannelTopics failed', err);
      setTopics([]);
      setTopicsTotal(0);
    } finally {
      setTopicsLoading(false);
    }
  };

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
      const result = await channelsApi.triggerCollection(id, language);
      const count = result?.topics_collected ?? 0;
      if (count > 0) {
        toast.success(t('channels.collectSuccessCount', { count }));
      } else {
        toast.error(t('channels.collectNoMatches'));
      }
      await loadChannel();
      await loadChannelTopics();
    } catch (err: any) {
      toast.error(err.message || t('channels.triggerFailed'));
    } finally {
      setIsCollecting(false);
    }
  };

  if (!isAuthenticated) {
    return null;
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#FAF9F7] dark:bg-gray-900 py-8">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !channel) {
    return (
      <div className="min-h-screen bg-[#FAF9F7] dark:bg-gray-900 py-8">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <p className="text-red-800 dark:text-red-200">{error || t('channels.notFound')}</p>
            <button
              onClick={() => navigate('/my-channel')}
              data-testid="btn-channel-detail-back"
              className="mt-4 px-4 py-2 bg-black text-white rounded-lg min-h-[44px]"
            >
              {t('common.back')}
            </button>
          </div>
        </div>
      </div>
    );
  }

  const switchList = siblings.length > 0 ? siblings : [channel];

  return (
    <div className="min-h-screen bg-[#FAF9F7] dark:bg-gray-900 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <button
          onClick={() => navigate('/my-channel')}
          data-testid="btn-channel-detail-back"
          className="mb-6 flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors min-h-[44px]"
        >
          {t('common.back')}
        </button>

        <h1 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4" data-testid="heading-my-channel-personal">
          {t('myChannel.personalTitle')}
        </h1>

        <div className="flex flex-wrap gap-2 mb-6" data-testid="list-my-channel-switch">
          {switchList.map((item) => {
            const selected = item.id === channel.id;
            return (
              <Link
                key={item.id}
                to={`/channels/${item.id}`}
                data-testid={`btn-my-channel-switch-${item.id}`}
                className={`min-h-[44px] inline-flex items-center px-4 rounded-full text-sm ${
                  selected
                    ? 'bg-black text-white'
                    : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-800 dark:text-gray-100'
                }`}
              >
                {item.name}
              </Link>
            );
          })}
        </div>

        <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
          {channel.name}
          {' · '}
          {t(categoryI18nKeys[channel.category as ChannelCategory])}
          {' · '}
          {t(regionI18nKeys[channel.region as ChannelRegion])}
        </p>

        <button
          onClick={handleTriggerCollection}
          disabled={isCollecting || channel.collection_status === 'collecting'}
          data-testid="btn-channel-detail-collect"
          className="mb-8 min-h-[44px] px-6 rounded-full bg-black text-white text-sm disabled:opacity-50"
        >
          {isCollecting || channel.collection_status === 'collecting'
            ? t('channels.collecting')
            : t('channels.produceTen')}
        </button>

        <div data-testid="channel-detail-topics-grid">
          {topicsLoading && (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-black" />
            </div>
          )}

          {!topicsLoading && topics.length === 0 && (
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              {t('channels.channelTopicsEmpty')}
            </p>
          )}

          {!topicsLoading && topics.length > 0 && (
            <>
              {topicsTotal > 0 && (
                <p className="text-sm text-gray-500 mb-3">{t('topics.total', { count: topicsTotal })}</p>
              )}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {topics.map((topic) => (
                  <div key={topic.id} className="h-full">
                    <TopicCard topic={topic} />
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
