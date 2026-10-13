/**
 * 我的頻道 — 最多三格設立板。進入後才是「我的自選頻道」。
 */
import { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useTranslation } from '@/i18n';
import { usePageTitle } from '@/hooks/usePageTitle';
import {
  channelsApi,
  Channel,
  ChannelCategory,
  ChannelRegion,
  categoryI18nKeys,
  regionI18nKeys,
} from '@/api/channels';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import McEmptyTourCoach from '@/components/tour/McEmptyTourCoach';
import { MC_TOUR_QUERY } from '@/lib/publicTour';

export default function MyChannel() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  usePageTitle(t('myChannel.pageTitle'));
  const mcTourOn = searchParams.get(MC_TOUR_QUERY) === '1';

  const [channels, setChannels] = useState<Channel[]>([]);
  const [maxChannels, setMaxChannels] = useState(3);
  const [loading, setLoading] = useState(true);
  const loadChannels = useCallback(async () => {
    setLoading(true);
    try {
      const res = await channelsApi.getMyChannels();
      setChannels(Array.isArray(res.channels) ? res.channels : []);
      setMaxChannels(typeof res.max_channels === 'number' ? res.max_channels : 3);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : t('common.error');
      toast.error(msg);
      setChannels([]);
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => {
    loadChannels();
  }, [loadChannels]);

  const emptyCount = Math.max(0, maxChannels - channels.length);

  if (loading) {
    return (
      <div className="min-h-[50vh] flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className={`max-w-5xl mx-auto px-4 py-8 ${mcTourOn ? 'pb-40' : ''}`}>
      <header className="mb-8">
        <h1
          className="text-2xl font-semibold text-gray-900 dark:text-white"
          data-testid="heading-my-channel"
        >
          {t('myChannel.title')}
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-3 leading-relaxed">{t('myChannel.boardLead')}</p>
        <p className="text-gray-600 dark:text-gray-400 mt-2 leading-relaxed">{t('myChannel.boardLead2')}</p>
      </header>

      <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3" data-testid="list-my-channel-slots">
        {channels.map((channel) => (
          <li
            key={channel.id}
            className="rounded-2xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-5 flex flex-col"
          >
            <h2 className="text-lg font-medium text-gray-900 dark:text-white">{channel.name}</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {t(categoryI18nKeys[channel.category as ChannelCategory])}
              {' · '}
              {t(regionI18nKeys[channel.region as ChannelRegion])}
            </p>
            {channel.description ? (
              <p className="text-sm text-gray-600 dark:text-gray-300 mt-3 line-clamp-3">{channel.description}</p>
            ) : null}
            <div className="mt-auto pt-4">
              <Link
                to={`/channels/${channel.id}`}
                data-testid={`btn-my-channel-enter-${channel.id}`}
                className="min-h-[44px] inline-flex items-center justify-center rounded-full bg-black text-white text-sm w-full"
              >
                {t('myChannel.enterChannel')}
              </Link>
            </div>
          </li>
        ))}
        {Array.from({ length: emptyCount }).map((_, index) => (
          <li key={`empty-${index}`}>
            <Link
              to="/channels/create"
              data-testid={index === 0 ? 'btn-my-channel-add-slot' : `btn-my-channel-add-slot-${index}`}
              className="min-h-[180px] h-full rounded-2xl border border-dashed border-gray-300 dark:border-gray-600 flex flex-col items-center justify-center gap-2 text-gray-700 dark:text-gray-200 hover:border-black"
            >
              <span className="text-lg">{t('myChannel.addSlot')}</span>
              <span className="text-sm text-gray-500">{t('myChannel.slotRemaining', { n: String(emptyCount) })}</span>
            </Link>
          </li>
        ))}
      </ul>

      {mcTourOn ? (
        <McEmptyTourCoach
          onCreate={() => navigate('/channels/create')}
          onSkip={() => {
            const next = new URLSearchParams(searchParams);
            next.delete(MC_TOUR_QUERY);
            setSearchParams(next, { replace: true });
          }}
        />
      ) : null}
    </div>
  );
}
