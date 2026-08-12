/**
 * MyChannel 首屏 — feed + 點數解鎖 + 熱門模板（MC-4～MC-6）
 */
import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useTranslation } from '@/i18n';
import { usePageTitle } from '@/hooks/usePageTitle';
import {
  myChannelApi,
  type ChannelTemplate,
  type MyChannelFeedCard,
  type UnlockResponse,
} from '@/api/myChannel';
import { APIError } from '@/api/errors';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

type UnlockedMap = Record<string, UnlockResponse>;

function unlockKey(topicId: string, lang: string): string {
  return `mc-unlock:${topicId}:${lang}`;
}

function templateCreateHref(tpl: ChannelTemplate): string {
  const q = new URLSearchParams({
    category: tpl.category,
    region: tpl.region,
    name: tpl.suggested_name,
  });
  return `/channels/create?${q.toString()}`;
}

export default function MyChannel() {
  const { t, language } = useTranslation();
  usePageTitle(t('myChannel.pageTitle'));

  const [cards, setCards] = useState<MyChannelFeedCard[]>([]);
  const [balance, setBalance] = useState(0);
  const [loading, setLoading] = useState(true);
  const [empty, setEmpty] = useState(false);
  const [hasChannels, setHasChannels] = useState(true);
  const [templates, setTemplates] = useState<ChannelTemplate[]>([]);
  const [unlockingId, setUnlockingId] = useState<string | null>(null);
  const [unlocked, setUnlocked] = useState<UnlockedMap>({});

  const loadFeed = useCallback(async () => {
    setLoading(true);
    try {
      const res = await myChannelApi.getFeed(language);
      setCards(Array.isArray(res.data) ? res.data : []);
      setBalance(typeof res.balance === 'number' ? res.balance : 0);
      setEmpty(Boolean(res.empty));
      setHasChannels(Boolean(res.has_channels));
      if (!res.has_channels) {
        const tpl = await myChannelApi.getChannelTemplates();
        setTemplates(Array.isArray(tpl.data) ? tpl.data : []);
      } else {
        setTemplates([]);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : t('common.error');
      toast.error(msg);
      setCards([]);
      setEmpty(true);
      setHasChannels(false);
      setTemplates([]);
    } finally {
      setLoading(false);
    }
  }, [language, t]);

  useEffect(() => {
    loadFeed();
    setUnlocked({});
  }, [loadFeed]);

  const handleUnlock = async (topicId: string) => {
    if (unlockingId) return;
    setUnlockingId(topicId);
    try {
      const res = await myChannelApi.unlock(topicId, unlockKey(topicId, language), language);
      setUnlocked((prev) => ({ ...prev, [topicId]: res }));
      setBalance(res.balance);
      toast.success(t('myChannel.unlockSuccess'));
    } catch (err: unknown) {
      if (err instanceof APIError && err.status === 402) {
        toast.error(t('myChannel.insufficientCredits'));
      } else {
        const msg = err instanceof Error ? err.message : t('common.error');
        toast.error(msg);
      }
    } finally {
      setUnlockingId(null);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[50vh] flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <header className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 dark:text-white" data-testid="heading-my-channel">
            {t('myChannel.title')}
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">{t('myChannel.subtitle')}</p>
        </div>
        <p className="text-sm font-medium text-gray-800 dark:text-gray-200" data-testid="text-my-channel-balance">
          {t('myChannel.balance', { n: String(balance) })}
        </p>
      </header>

      {!hasChannels && templates.length > 0 && (
        <section className="mb-8" data-testid="panel-my-channel-templates">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            {t('myChannel.templatesTitle')}
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">{t('myChannel.templatesSubtitle')}</p>
          <ul className="grid gap-3 sm:grid-cols-2">
            {templates.map((tpl) => (
              <li key={tpl.id}>
                <Link
                  to={templateCreateHref(tpl)}
                  data-testid={`btn-my-channel-template-${tpl.id}`}
                  className="block rounded-lg border border-gray-200 dark:border-gray-700 p-4 hover:border-gray-400 min-h-[44px]"
                >
                  <p className="font-medium text-gray-900 dark:text-white">{t(tpl.name_key)}</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{t(tpl.desc_key)}</p>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}

      {empty ? (
        <div
          className="rounded-lg border border-dashed border-gray-300 dark:border-gray-600 p-10 text-center"
          data-testid="panel-my-channel-empty"
        >
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            {hasChannels ? t('myChannel.emptyFeed') : t('myChannel.emptyNoChannel')}
          </p>
          <div className="flex flex-wrap justify-center gap-3">
            <Link
              to="/channels/create"
              data-testid="btn-my-channel-create-channel"
              className="px-5 py-3 bg-black text-white text-sm tracking-wide uppercase min-h-[44px] inline-flex items-center"
            >
              {t('myChannel.createChannel')}
            </Link>
            <Link
              to="/discover"
              data-testid="btn-my-channel-go-discover"
              className="px-5 py-3 border border-gray-300 text-gray-900 text-sm tracking-wide uppercase min-h-[44px] inline-flex items-center"
            >
              {t('myChannel.goDiscover')}
            </Link>
          </div>
        </div>
      ) : (
        <ul className="space-y-4" data-testid="list-my-channel-feed">
          {cards.map((card) => {
            const unlockData = unlocked[card.id];
            return (
              <li
                key={card.id}
                className="rounded-lg border border-gray-200 dark:border-gray-700 p-4 sm:p-5 bg-white dark:bg-gray-800"
                data-testid={`card-my-channel-${card.id}`}
              >
                <div className="flex gap-4">
                  {card.image_url && (
                    <img
                      src={card.image_url}
                      alt=""
                      className="w-20 h-20 rounded object-cover flex-shrink-0 hidden sm:block"
                    />
                  )}
                  <div className="flex-1 min-w-0">
                    <h2 className="font-medium text-gray-900 dark:text-white truncate">{card.heading}</h2>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{card.intro}</p>
                    {unlockData ? (
                      <div className="mt-3 space-y-2" data-testid={`panel-my-channel-unlocked-${card.id}`}>
                        <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-line">
                          {unlockData.digest_300}
                        </p>
                        <a
                          href={unlockData.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          data-testid={`link-my-channel-source-${card.id}`}
                          className="text-sm text-primary underline min-h-[44px] inline-flex items-center"
                        >
                          {t('myChannel.openSource')}
                        </a>
                      </div>
                    ) : (
                      <button
                        type="button"
                        data-testid={`btn-my-channel-unlock-${card.id}`}
                        disabled={unlockingId === card.id}
                        onClick={() => handleUnlock(card.id)}
                        className="mt-3 px-4 py-2 text-sm font-medium bg-primary text-white rounded-md min-h-[44px] disabled:opacity-50"
                      >
                        {unlockingId === card.id ? t('common.processing') : t('myChannel.unlockCta')}
                      </button>
                    )}
                  </div>
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
