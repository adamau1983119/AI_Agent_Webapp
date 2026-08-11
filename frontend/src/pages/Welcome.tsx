/**
 * 登入前介紹頁（Landing / Welcome）
 * v7 程式段 · 2026-06-18
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

const BRAND = {
  name: 'Alter-ego',
  slogan: 'AI-POWERED CONTENT CREATION',
};

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
    <div className="min-h-screen bg-[#FAF9F7] font-sans flex flex-col">
      <header className="border-b border-gray-200 bg-[#FAF9F7]/95 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between gap-4">
          <div className="font-display text-lg tracking-[0.25em] uppercase text-black">
            {BRAND.name}
          </div>
          <div className="flex items-center gap-2 sm:gap-4">
            <div className="flex border border-gray-200">
              {languageOptions.map((opt) => (
                <button
                  key={opt.code}
                  type="button"
                  data-testid={`btn-landing-lang-${opt.code === 'zh-TW' ? 'zh' : opt.code}`}
                  onClick={() => handleLang(opt.code)}
                  className={`px-2 sm:px-3 py-2 text-[10px] tracking-wider uppercase min-h-[44px] min-w-[44px] transition-colors ${
                    language === opt.code
                      ? 'bg-black text-white'
                      : 'bg-transparent text-black hover:bg-gray-100'
                  }`}
                  aria-label={opt.name}
                >
                  {opt.shortName}
                </button>
              ))}
            </div>
            <Link
              to="/login"
              data-testid="btn-landing-login"
              className="hidden sm:inline text-xs tracking-[0.15em] uppercase text-black hover:underline min-h-[44px] flex items-center"
            >
              {t('landing.cta.login')}
            </Link>
          </div>
        </div>
      </header>

      <main className="flex-1">
        <section className="max-w-6xl mx-auto px-4 sm:px-6 py-12 sm:py-20 text-center">
          <h1 className="font-display text-3xl sm:text-4xl md:text-5xl font-light tracking-wide text-black mb-6">
            {t('landing.hero.title')}
          </h1>
          <p className="text-gray-500 text-sm sm:text-base max-w-2xl mx-auto mb-10 leading-relaxed">
            {t('landing.hero.subtitle')}
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/register"
              data-testid="btn-landing-register"
              className="w-full sm:w-auto min-h-[44px] px-10 py-3 bg-black text-white text-xs tracking-[0.2em] uppercase hover:bg-gray-900 transition-colors flex items-center justify-center"
            >
              {t('landing.cta.register')}
            </Link>
            <Link
              to="/login"
              data-testid="btn-landing-login-hero"
              className="w-full sm:w-auto min-h-[44px] px-10 py-3 border border-black text-black text-xs tracking-[0.2em] uppercase hover:bg-black hover:text-white transition-colors flex items-center justify-center"
            >
              {t('landing.cta.login')}
            </Link>
          </div>
          <p className="mt-6 text-[11px] text-gray-400 tracking-wide">
            {t('landing.cta.loginPrompt')}
          </p>
        </section>

        <section className="max-w-6xl mx-auto px-4 sm:px-6 pb-16">
          <h2 className="font-display text-xl tracking-[0.15em] uppercase text-center text-black mb-10">
            {t('landing.features.title')}
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
            {FEATURE_KEYS.map((key, index) => {
              const Icon = FEATURE_ICONS[index];
              const isPostKit = key === 'postKit';
              return (
                <article
                  key={key}
                  data-testid={`card-landing-feature-${key}`}
                  className="border border-gray-200 bg-white p-6 hover:border-black transition-colors"
                >
                  <div className="flex items-start gap-4">
                    <div className="p-2 border border-gray-200 shrink-0">
                      <Icon className="w-5 h-5 text-black" strokeWidth={1.25} />
                    </div>
                    <div className="text-left min-w-0">
                      <div className="flex flex-wrap items-center gap-2 mb-2">
                        <h3 className="text-sm tracking-[0.1em] uppercase font-light text-black">
                          {t(`landing.features.${key}.title`)}
                        </h3>
                        {isPostKit && (
                          <span className="text-[9px] tracking-wider uppercase px-2 py-0.5 border border-gray-300 text-gray-500">
                            {t('landing.features.postKit.badge')}
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-gray-500 leading-relaxed">
                        {t(`landing.features.${key}.benefit`)}
                      </p>
                    </div>
                  </div>
                </article>
              );
            })}
          </div>
        </section>

        <section className="max-w-6xl mx-auto px-4 sm:px-6 pb-16">
          <details className="border border-gray-200 bg-white group">
            <summary className="px-6 py-4 cursor-pointer text-xs tracking-[0.15em] uppercase text-black list-none flex items-center justify-between min-h-[44px]">
              {t('landing.advanced.title')}
              <span className="text-gray-400 group-open:rotate-180 transition-transform">▼</span>
            </summary>
            <div className="px-6 pb-6 grid grid-cols-1 sm:grid-cols-3 gap-4 border-t border-gray-100">
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

      <footer className="border-t border-gray-200 py-8">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-[10px] text-gray-400 tracking-[0.15em] uppercase">
          <span>© 2026 {BRAND.name}</span>
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
