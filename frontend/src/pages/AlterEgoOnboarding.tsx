/**
 * Alter Ego 首登 onboarding — 貼範文 + 仿文預覽 + Skip（AE-1d）
 */
import { useEffect, useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useTranslation, type Language } from '@/i18n';
import { useAuthStore } from '@/stores/authStore';
import {
  alterEgoApi,
  type AlterEgoPlatform,
  type DnaStatusResponse,
} from '@/api/alterEgo';
import { MY_CHANNEL_PATH, isAlterEgoOnboardingDone } from '@/lib/alterEgoRouting';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

const PLATFORMS: AlterEgoPlatform[] = ['facebook', 'threads', 'x'];

export default function AlterEgoOnboarding() {
  const { t, language } = useTranslation();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();

  const [status, setStatus] = useState<DnaStatusResponse | null>(null);
  const [loadingStatus, setLoadingStatus] = useState(true);
  const [exemplars, setExemplars] = useState(['', '', '']);
  const [platform, setPlatform] = useState<AlterEgoPlatform>('facebook');
  const [previewText, setPreviewText] = useState('');
  const [extracted, setExtracted] = useState(false);
  const [busy, setBusy] = useState<'extract' | 'preview' | 'skip' | null>(null);

  useEffect(() => {
    if (!isAuthenticated) return;
    alterEgoApi
      .getStatus()
      .then(setStatus)
      .catch(() => setStatus({ dna_status: 'pending', has_dna: false }))
      .finally(() => setLoadingStatus(false));
  }, [isAuthenticated]);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (loadingStatus) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#FAF9F7]">
        <LoadingSpinner />
      </div>
    );
  }

  if (isAlterEgoOnboardingDone(status?.dna_status)) {
    return <Navigate to={MY_CHANNEL_PATH} replace />;
  }

  const filledExemplars = exemplars.map((e) => e.trim()).filter(Boolean);

  const handleSkip = async () => {
    setBusy('skip');
    try {
      await alterEgoApi.skip();
      toast.success(t('alterEgo.skipDone'));
      navigate(MY_CHANNEL_PATH, { replace: true });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : t('common.error');
      toast.error(msg);
    } finally {
      setBusy(null);
    }
  };

  const handleExtract = async () => {
    if (filledExemplars.length < 1) {
      toast.error(t('alterEgo.exemplarRequired'));
      return;
    }
    setBusy('extract');
    try {
      await alterEgoApi.extract(filledExemplars, language as Language);
      setExtracted(true);
      toast.success(t('alterEgo.extractDone'));
      const preview = await alterEgoApi.preview(platform, t('alterEgo.defaultTopicHint'));
      setPreviewText(preview.preview_text);
    } catch (err: unknown) {
      const raw = err instanceof Error ? err.message : String(err ?? '');
      let msg = raw || t('common.error');
      if (raw.includes('Request timeout') || raw.includes('timeout')) {
        msg = t('alterEgo.requestTimeout');
      } else if (raw.includes('alter_ego_llm_unavailable') || raw.includes('DeepSeek API') || raw.includes('API Key')) {
        msg = t('alterEgo.llmUnavailable');
      } else if (raw.includes('alter_ego_extract_schema_fail') || raw.includes('extract_schema')) {
        msg = t('alterEgo.extractSchemaFail');
      }
      toast.error(msg);
    } finally {
      setBusy(null);
    }
  };

  const handlePreview = async () => {
    if (!extracted) return;
    setBusy('preview');
    try {
      const preview = await alterEgoApi.preview(platform, t('alterEgo.defaultTopicHint'));
      setPreviewText(preview.preview_text);
    } catch (err: unknown) {
      const raw = err instanceof Error ? err.message : String(err ?? '');
      const msg =
        raw.includes('Request timeout') || raw.includes('timeout')
          ? t('alterEgo.requestTimeout')
          : raw || t('common.error');
      toast.error(msg);
    } finally {
      setBusy(null);
    }
  };

  const handleContinue = () => {
    navigate(MY_CHANNEL_PATH, { replace: true });
  };

  return (
    <div className="min-h-screen bg-[#FAF9F7] font-sans">
      <header className="border-b border-gray-200 bg-[#FAF9F7]/95 sticky top-0 z-10">
        <div className="max-w-2xl mx-auto px-4 py-4 flex items-center justify-between gap-4">
          <h1 className="text-lg font-medium text-black" data-testid="heading-alter-ego-onboarding">
            {t('alterEgo.title')}
          </h1>
          <button
            type="button"
            data-testid="btn-alter-ego-skip"
            onClick={handleSkip}
            disabled={busy !== null}
            className="text-sm text-gray-600 underline min-h-[44px] px-2"
          >
            {busy === 'skip' ? t('common.processing') : t('alterEgo.skip')}
          </button>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-8 space-y-8">
        <p className="text-gray-600 text-sm leading-relaxed">{t('alterEgo.intro')}</p>

        <section>
          <h2 className="text-sm font-medium uppercase tracking-wider text-gray-800 mb-3">
            {t('alterEgo.exemplarsTitle')}
          </h2>
          <p className="text-xs text-gray-500 mb-4">{t('alterEgo.exemplarsHint')}</p>
          {exemplars.map((value, idx) => (
            <textarea
              key={idx}
              data-testid={`input-alter-ego-exemplar-${idx + 1}`}
              value={value}
              onChange={(e) => {
                const next = [...exemplars];
                next[idx] = e.target.value;
                setExemplars(next);
              }}
              rows={4}
              placeholder={t('alterEgo.exemplarPlaceholder', { n: String(idx + 1) })}
              className="w-full mb-3 border border-gray-300 p-3 text-sm resize-y min-h-[100px]"
            />
          ))}
          <button
            type="button"
            data-testid="btn-alter-ego-extract"
            onClick={handleExtract}
            disabled={busy !== null}
            className="w-full sm:w-auto px-6 py-3 bg-black text-white text-sm uppercase tracking-wide min-h-[44px] disabled:opacity-50"
          >
            {busy === 'extract' ? t('common.processing') : t('alterEgo.extract')}
          </button>
        </section>

        {extracted && (
          <section>
            <h2 className="text-sm font-medium uppercase tracking-wider text-gray-800 mb-3">
              {t('alterEgo.previewTitle')}
            </h2>
            <div className="flex gap-2 mb-4 flex-wrap">
              {PLATFORMS.map((p) => (
                <button
                  key={p}
                  type="button"
                  data-testid={`btn-alter-ego-platform-${p}`}
                  onClick={() => setPlatform(p)}
                  className={`px-3 py-2 text-xs uppercase min-h-[44px] border ${
                    platform === p ? 'bg-black text-white border-black' : 'border-gray-300'
                  }`}
                >
                  {t(`alterEgo.platform.${p}`)}
                </button>
              ))}
              <button
                type="button"
                data-testid="btn-alter-ego-refresh-preview"
                onClick={handlePreview}
                disabled={busy !== null}
                className="px-3 py-2 text-xs uppercase min-h-[44px] border border-gray-300"
              >
                {busy === 'preview' ? t('common.processing') : t('alterEgo.refreshPreview')}
              </button>
            </div>
            <div
              data-testid="section-alter-ego-preview"
              className="border border-gray-200 bg-white p-4 text-sm whitespace-pre-wrap min-h-[80px]"
            >
              {previewText || t('alterEgo.previewEmpty')}
            </div>
            <button
              type="button"
              data-testid="btn-alter-ego-continue"
              onClick={handleContinue}
              className="mt-6 w-full sm:w-auto px-6 py-3 bg-black text-white text-sm uppercase tracking-wide min-h-[44px]"
            >
              {t('alterEgo.continue')}
            </button>
          </section>
        )}
      </main>
    </div>
  );
}
