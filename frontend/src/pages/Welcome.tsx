/**
 * 登入前介紹頁（Landing / Welcome）
 * v8 · 變現敘事 + 黑白水點墨斑動效（LOCKED-v1）
 */
import { useEffect } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import {
  TrendingUp,
  Sparkles,
  MessageCircle,
  Lightbulb,
  Star,
  Copy,
  Globe,
  Rss,
  ShieldCheck,
} from 'lucide-react';
import { useTranslation, languageOptions, Language } from '@/i18n';
import { useAuthStore } from '@/stores/authStore';
import { resolvePostLoginPath } from '@/lib/alterEgoRouting';
import WelcomeInkBackground from '@/components/welcome/WelcomeInkBackground';

const FEATURE_KEYS = ['trends', 'aiWrite', 'channel', 'inspiration', 'style', 'postKit'] as const;
const FEATURE_ICONS = [TrendingUp, Sparkles, MessageCircle, Lightbulb, Star, Copy];

export default function Welcome() {
  const { t, language, setLanguage } = useTranslation();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();
  const hasLanguage = localStorage.getItem('preferred-language');

  useEffect(() => {
    if (isAuthenticated) {
      resolvePostLoginPath().then((path) => navigate(path, { replace: true }));
    }
  }, [isAuthenticated, navigate]);

  if (isAuthenticated) {
    return null;
  }

  if (!hasLanguage) {
    return <Navigate to="/language" replace />;
  }

  const handleLang = (code: Language) => {
    setLanguage(code);
    localStorage.setItem('preferred-language', code);
  };

  return (
    <div className="relative min-h-screen bg-[#F7F5F2] font-sans text-[#1a1a1a] flex flex-col overflow-x-hidden">
      <WelcomeInkBackground />

      <header className="relative z-10 bg-transparent">
        <div className="max-w-[1120px] mx-auto px-4 sm:px-9 py-5 sm:py-6 flex items-center justify-between gap-4">
          <div className="font-display text-base sm:text-lg tracking-[0.32em] uppercase font-medium">
            {t('brand.name')}
          </div>
          <div className="flex items-center gap-3 sm:gap-4">
            <div className="flex text-[10px] sm:text-[11px] tracking-[0.14em] uppercase">
              {languageOptions.map((opt, idx) => (
                <span key={opt.code} className="flex items-center">
                  {idx > 0 && <span className="mx-1.5 opacity-40">·</span>}
                  <button
                    type="button"
                    data-testid={`btn-landing-lang-${opt.code === 'zh-TW' ? 'zh' : opt.code}`}
                    onClick={() => handleLang(opt.code)}
                    className={`min-h-[44px] min-w-[36px] px-1 transition-opacity ${
                      language === opt.code
                        ? 'opacity-100 underline underline-offset-4'
                        : 'opacity-40 hover:opacity-70'
                    }`}
                    aria-label={opt.name}
                  >
                    {opt.shortName}
                  </button>
                </span>
              ))}
            </div>
            <Link
              to="/login"
              data-testid="btn-landing-login"
              className="hidden sm:inline-flex items-center min-h-[44px] px-4 py-2 text-[11px] tracking-[0.16em] uppercase border border-[#1a1a1a] rounded-full hover:bg-[#1a1a1a] hover:text-white transition-colors"
            >
              {t('landing.cta.login')}
            </Link>
          </div>
        </div>
      </header>

      <main className="relative z-[1] flex-1 flex flex-col">
        <section className="flex flex-col items-center justify-center text-center px-4 sm:px-6 pt-6 sm:pt-10 pb-8 sm:pb-10">
          <h1 className="font-display font-medium text-[clamp(2.1rem,5.2vw,3.5rem)] leading-[1.28] tracking-[0.02em] max-w-[16em]">
            {t('landing.hero.titleLine1')}
            <br />
            {t('landing.hero.titleLine2')}
          </h1>
          <div
            className="w-[7px] h-[7px] my-5 sm:my-6 bg-[#1a1a1a] rotate-45"
            aria-hidden="true"
          />
          <p className="text-base tracking-[0.04em]">{t('landing.hero.mission')}</p>
          <p className="mt-4 text-sm text-[#6b6b6b] max-w-xl leading-relaxed">
            {t('landing.hero.subtitle')}
          </p>
          <div className="mt-8 sm:mt-9 flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4">
            <Link
              to="/register"
              data-testid="btn-landing-register"
              className="w-full sm:w-auto min-w-[9.2rem] min-h-[46px] px-7 py-3 rounded-full text-[11px] tracking-[0.18em] uppercase text-white flex items-center justify-center bg-gradient-to-b from-[#2a2a2a] to-[#0d0d0d] shadow-[inset_0_1px_0_rgba(255,255,255,0.12),0_6px_18px_rgba(0,0,0,0.12)] hover:from-[#333] hover:to-[#111] transition-colors"
            >
              {t('landing.cta.register')}
            </Link>
            <Link
              to="/login"
              data-testid="btn-landing-login-hero"
              className="w-full sm:w-auto min-w-[9.2rem] min-h-[46px] px-7 py-3 rounded-full text-[11px] tracking-[0.18em] uppercase text-[#1a1a1a] border border-[#1a1a1a] flex items-center justify-center hover:bg-[#1a1a1a] hover:text-white transition-colors"
            >
              {t('landing.cta.login')}
            </Link>
          </div>
          <p className="mt-5 text-[11px] text-[#a3a3a3] tracking-[0.1em]">
            {t('landing.cta.loginPrompt')}
          </p>
        </section>

        <section className="relative z-[1] w-full max-w-[1120px] mx-auto px-3 sm:px-6 pb-10 sm:pb-14">
          <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-3 sm:gap-3.5">
            {FEATURE_KEYS.map((key, index) => {
              const Icon = FEATURE_ICONS[index];
              const isPostKit = key === 'postKit';
              return (
                <article
                  key={key}
                  data-testid={`card-landing-feature-${key}`}
                  className="bg-white rounded-2xl px-3 sm:px-4 pt-5 pb-4 text-center border border-black/[0.04] shadow-[0_1px_0_rgba(0,0,0,0.03),0_8px_24px_rgba(0,0,0,0.04)]"
                >
                  <div className="w-12 h-12 mx-auto rounded-full bg-[#ebe8e3] flex items-center justify-center text-[#1a1a1a]">
                    <Icon className="w-[22px] h-[22px]" strokeWidth={1.5} />
                  </div>
                  <div className="mt-3.5 mb-1.5">
                    <h3 className="font-display text-[0.92rem] font-semibold leading-snug text-[#1a1a1a]">
                      {t(`landing.features.${key}.title`)}
                    </h3>
                    {isPostKit && (
                      <span className="inline-block mt-1 text-[9px] tracking-wider uppercase px-2 py-0.5 border border-gray-300 text-gray-500">
                        {t('landing.features.postKit.badge')}
                      </span>
                    )}
                  </div>
                  <p className="text-[10px] sm:text-[11px] text-[#6b6b6b] leading-[1.55] min-h-[2.9em]">
                    {t(`landing.features.${key}.benefit`)}
                  </p>
                  <div className="w-7 h-px bg-black/10 mx-auto mt-3.5" aria-hidden="true" />
                </article>
              );
            })}
          </div>
        </section>

        <section className="relative z-[1] max-w-[1120px] mx-auto px-4 sm:px-6 pb-12 sm:pb-16 w-full">
          <details className="rounded-2xl border border-black/[0.06] bg-white/80 backdrop-blur-sm group">
            <summary className="px-5 sm:px-6 py-4 cursor-pointer text-[11px] tracking-[0.15em] uppercase list-none flex items-center justify-between min-h-[44px]">
              {t('landing.advanced.title')}
              <span className="text-gray-400 group-open:rotate-180 transition-transform text-xs">▼</span>
            </summary>
            <div className="px-5 sm:px-6 pb-6 grid grid-cols-1 sm:grid-cols-3 gap-4 border-t border-gray-100">
              {[
                { icon: Globe, key: 'multilingual' },
                { icon: Rss, key: 'collection' },
                { icon: ShieldCheck, key: 'sources' },
              ].map(({ icon: Icon, key }) => (
                <div key={key} className="pt-4">
                  <Icon className="w-4 h-4 text-gray-400 mb-2" strokeWidth={1.25} />
                  <p className="text-xs text-gray-600">{t(`landing.advanced.${key}`)}</p>
                </div>
              ))}
            </div>
          </details>
        </section>
      </main>

      <footer className="relative z-[2] border-t border-black/[0.06] py-8">
        <div className="max-w-[1120px] mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-[10px] text-[#a3a3a3] tracking-[0.15em] uppercase">
          <span>© 2026 {t('brand.name')}</span>
          <div className="flex gap-6">
            <Link
              to="/terms"
              data-testid="link-landing-terms"
              className="hover:text-black transition-colors min-h-[44px] flex items-center"
            >
              {t('landing.footer.terms')}
            </Link>
            <Link
              to="/privacy"
              data-testid="link-landing-privacy"
              className="hover:text-black transition-colors min-h-[44px] flex items-center"
            >
              {t('landing.footer.privacy')}
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
