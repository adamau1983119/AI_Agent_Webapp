import { Link } from 'react-router-dom'
import { useTranslation, languageOptions, Language } from '@/i18n'
import BrandMark from '@/components/brand/BrandMark'
import PublicLegalFooter from '@/components/layout/PublicLegalFooter'
import { usePublicPageSeo } from '@/hooks/usePublicPageSeo'

const LANG_HREF: Record<Language, string> = {
  'zh-TW': '/welcome',
  en: '/en',
  ja: '/ja',
}

const LANG_TESTID: Record<Language, string> = {
  'zh-TW': 'link-sitemap-zh',
  en: 'link-sitemap-en',
  ja: 'link-sitemap-ja',
}

export default function Sitemap() {
  const { t } = useTranslation()
  usePublicPageSeo(
    `${t('landing.footer.sitemap')}｜${t('brand.name')}`,
    t('seo.home.description'),
  )

  return (
    <div className="min-h-screen bg-[#FAF9F7] font-sans flex flex-col">
      <header className="flex items-center justify-center px-8 py-6 border-b border-gray-100">
        <Link
          to="/welcome"
          className="flex items-center gap-2 font-display text-lg tracking-[0.2em] uppercase"
        >
          <BrandMark />
          {t('brand.name')}
        </Link>
      </header>
      <main className="max-w-3xl w-full mx-auto px-8 py-16">
        <h1 className="font-display text-3xl tracking-[0.15em] font-light text-black mb-8">
          {t('landing.footer.sitemap')}
        </h1>
        <div className="w-16 h-px bg-black mb-8" />
        <ul className="space-y-4 text-sm text-[#1a1a1a] normal-case tracking-normal">
          {languageOptions.map((opt) => (
            <li key={opt.code}>
              <Link to={LANG_HREF[opt.code]} data-testid={LANG_TESTID[opt.code]} className="hover:underline">
                {opt.name}
              </Link>
            </li>
          ))}
          <li>
            <Link to="/terms" data-testid="link-sitemap-terms" className="hover:underline">
              {t('landing.footer.terms')}
            </Link>
          </li>
          <li>
            <Link to="/privacy" data-testid="link-sitemap-privacy" className="hover:underline">
              {t('landing.footer.privacy')}
            </Link>
          </li>
        </ul>
      </main>
      <PublicLegalFooter
        privacyTestId="link-landing-privacy"
        termsTestId="link-landing-terms"
        sitemapTestId="link-landing-sitemap"
        langTestId={(code) => `btn-landing-footer-lang-${code === 'zh-TW' ? 'zh' : code}`}
      />
    </div>
  )
}
