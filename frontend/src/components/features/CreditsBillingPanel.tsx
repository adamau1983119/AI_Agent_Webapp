/**
 * Settings billing tab: login grants copy + one-time Stripe packs.
 */
import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { billingApi, type CreditPack } from '@/api/billing';
import { APIError } from '@/api/errors';
import { useTranslation } from '@/i18n';
import CreditPackShelf from '@/components/credits/CreditPackShelf';

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
    const params = new URLSearchParams(window.location.search);
    const flag = params.get('billing');
    const sessionId = params.get('session_id');
    if (flag === 'success') {
      toast.success(t('credits.success'));
      if (sessionId) {
        void billingApi
          .confirmCheckout(sessionId)
          .then(() => {
            void balanceQuery.refetch();
          })
          .catch(() => {
            /* webhook may still land; balance refetch below */
          });
      }
      void balanceQuery.refetch();
    }
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
      <div className="p-6 rounded-lg border border-black/10 bg-[#F7F5F2] space-y-2">
        <p className="font-medium" data-testid="text-settings-credits-balance">
          {t('credits.balanceLine', { n: String(snap?.balance ?? 0) })}
        </p>
        <p className="text-sm text-gray-500">
          {t('credits.freeLine', { n: String(snap?.free ?? 0) })}
        </p>
        <p className="text-sm text-gray-500">
          {t('credits.purchasedLine', { n: String(snap?.purchased ?? 0) })}
        </p>
      </div>
      <div className="rounded-2xl bg-[#0d0d0d] text-white p-5 sm:p-6">
        <CreditPackShelf
          packs={packs}
          mode="buy"
          testPrefix="settings"
          buying={buying}
          onBuy={(packId) => void buy(packId)}
        />
      </div>
    </div>
  );
}
