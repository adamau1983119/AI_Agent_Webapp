/**
 * 頻道管理：只有編輯與取消。出主題卡在我的自選頻道。
 */
import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
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

export default function Channels() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();
  const [channels, setChannels] = useState<Channel[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pendingDelete, setPendingDelete] = useState<Channel | null>(null);
  const [deleting, setDeleting] = useState(false);

  const loadChannels = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await channelsApi.getMyChannels();
      setChannels(Array.isArray(response.channels) ? response.channels : []);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : t('channels.loadFailed');
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    loadChannels();
  }, [isAuthenticated, navigate]);

  const confirmDelete = async () => {
    if (!pendingDelete || deleting) return;
    setDeleting(true);
    try {
      await channelsApi.deleteChannel(pendingDelete.id);
      toast.success(t('channels.deleted'));
      setPendingDelete(null);
      await loadChannels();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : t('channels.deleteFailed');
      toast.error(msg);
    } finally {
      setDeleting(false);
    }
  };

  if (!isAuthenticated) return null;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1
          className="text-3xl font-bold text-gray-900 dark:text-white mb-8"
          data-testid="heading-channel-manage"
        >
          {t('nav.channelList')}
        </h1>

        {isLoading && (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin h-12 w-12 border-b-2 border-black rounded-full" />
          </div>
        )}

        {!isLoading && error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 text-center">
            <p className="text-red-600 dark:text-red-400">{error}</p>
            <button
              type="button"
              onClick={loadChannels}
              data-testid="btn-channels-manage-retry"
              className="mt-4 px-4 py-2 min-h-[44px] bg-red-100 dark:bg-red-900/30 text-red-600 rounded-lg"
            >
              {t('common.retry')}
            </button>
          </div>
        )}

        {!isLoading && !error && channels.length === 0 && (
          <p
            className="text-lg text-gray-700 dark:text-gray-200 leading-relaxed"
            data-testid="text-channels-manage-empty"
          >
            {t('channels.manageEmptyBefore')}
            <Link
              to="/my-channel"
              data-testid="btn-channels-manage-go-my-channel"
              className="underline font-medium text-gray-900 dark:text-white"
            >
              {t('nav.channels')}
            </Link>
            {t('channels.manageEmptyAfter')}
          </p>
        )}

        {!isLoading && !error && channels.length > 0 && (
          <ul className="grid gap-4 md:grid-cols-2 lg:grid-cols-3" data-testid="list-channels-manage">
            {channels.map((channel) => (
              <li
                key={channel.id}
                className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg flex flex-col"
              >
                <h2 className="font-semibold text-gray-900 dark:text-white">{channel.name}</h2>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  {t(categoryI18nKeys[channel.category as ChannelCategory])}
                  {' · '}
                  {t(regionI18nKeys[channel.region as ChannelRegion])}
                </p>
                <div className="mt-auto pt-4 flex flex-col gap-2">
                  <Link
                    to={`/channels/${channel.id}/edit`}
                    data-testid={`btn-channels-manage-edit-${channel.id}`}
                    className="min-h-[44px] inline-flex items-center justify-center rounded-full border border-gray-300 text-sm"
                  >
                    {t('channels.editChannel')}
                  </Link>
                  <button
                    type="button"
                    data-testid={`btn-channels-manage-cancel-${channel.id}`}
                    onClick={() => setPendingDelete(channel)}
                    className="min-h-[44px] text-sm text-red-600"
                  >
                    {t('myChannel.cancelChannel')}
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}

        {pendingDelete && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-md w-full">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                {t('channels.deleteConfirm')}
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                {t('channels.deleteWarning', { name: pendingDelete.name })}
              </p>
              <div className="flex gap-3">
                <button
                  type="button"
                  data-testid="btn-channels-manage-cancel-dismiss"
                  onClick={() => setPendingDelete(null)}
                  className="flex-1 min-h-[44px] rounded-lg bg-gray-200 dark:bg-gray-600"
                >
                  {t('common.cancel')}
                </button>
                <button
                  type="button"
                  data-testid="btn-channels-manage-cancel-confirm"
                  onClick={confirmDelete}
                  disabled={deleting}
                  className="flex-1 min-h-[44px] rounded-lg bg-red-500 text-white disabled:opacity-50"
                >
                  {deleting ? t('common.deleting') : t('myChannel.cancelChannel')}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
