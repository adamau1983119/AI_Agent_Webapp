/**
 * Settings billing tab: login grants copy + one-time Stripe packs.
 */
import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { billingApi, type CreditPack } from '@/api/billing';
import { APIError } from '@/api/errors';
import { useTranslation } from '@/i18n';

const FALLBACK_PACKS: CreditPack[] = [
  { id: 'usd3', credits: 180, amount_cents: 300, currency: 'usd' },
  { id: 'usd5', credits: 350, amount_cents: 500, currency: 'usd' },
  { id: 'usd10', credits: 800, amount_cents: 1000, currency: 'usd' },
];

export default function CreditsBillingPanel() {
  const { t } = useTranslation();
  const [buying, setBuying] = useState<string | null>(null);
  const balanceQuery = useQuery({
    queryKey: ['creditsBalance'],
    queryFn: billingApi.getBalance,
  });
  const packsQuery = useQuery({
    queryKey: ['creditPacks'],
    queryFn: billingApi.getPacks,
  });

  useEffect(() => {
    const flag = new URLSearchParams(window.location.search).get('billing');
    if (flag === 'success') toast.success(t('credits.success'));
    if (flag === 'cancel') toast.error(t('credits.cancel'));
  }, [t]);

  const snap = balanceQuery.data;
  const packs: CreditPack[] =
    packsQuery.data && packsQuery.data.length > 0 ? packsQuery.data : FALLBACK_PACKS;

  const buy = async (packId: string) => {
    setBuying(packId);
    try {
      const res = await billingApi.startCheckout(packId);
      if (res?.checkout_url) {
        window.location.href = res.checkout_url;
        return;
      }
      toast.error(t('credits.unavailable'));
    } catch (err) {
      if (err instanceof APIError && err.status === 503) {
        toast.error(t('credits.unavailable'));
      } else {
        toast.error(t('common.failed'));
      }
    } finally {
      setBuying(null);
    }
  };

  return (
    <div className="space-y-6" data-testid="panel-settings-billing">
      <h2 className="text-xl font-semibold mb-6">{t('credits.title')}</h2>
      <p className="text-sm text-gray-400">{t('credits.subtitle')}</p>
      <p className="text-sm text-gray-400">{t('credits.hintWelcome')}</p>
      <p className="text-sm text-gray-400">{t('credits.hintDaily')}</p>
      <div className="p-6 bg-slate-700/30 rounded-lg space-y-2">
        <p className="font-medium" data-testid="text-settings-credits-balance">
          {t('credits.balanceLine', { n: String(snap?.balance ?? 0) })}
        </p>
        <p className="text-sm text-gray-400">
          {t('credits.freeLine', { n: String(snap?.free ?? 0) })}
        </p>
        <p className="text-sm text-gray-400">
          {t('credits.purchasedLine', { n: String(snap?.purchased ?? 0) })}
        </p>
      </div>
      <div className="grid gap-3 sm:grid-cols-3">
        {packs.map((pack) => (
          <button
            key={pack.id}
            type="button"
            data-testid={`btn-settings-buy-${pack.id}`}
            disabled={buying !== null}
            onClick={() => void buy(pack.id)}
            className="px-4 py-3 min-h-[44px] bg-purple-500 hover:bg-purple-600 disabled:opacity-50 text-white rounded-lg"
          >
            {pack.id === 'usd5'
              ? t('credits.packUsd5')
              : pack.id === 'usd10'
                ? t('credits.packUsd10')
                : t('credits.packUsd3')}
          </button>
        ))}
      </div>
    </div>
  );
}
