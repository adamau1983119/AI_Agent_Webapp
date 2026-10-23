import { Link } from 'react-router-dom'
import { useTranslation, languageOptions, Language } from '@/i18n'

type PublicLegalFooterProps = {
  privacyTestId: string
  termsTestId: string
  sitemapTestId: string
  langTestId: (code: Language) => string
}

/** 公開頁最底法律列。切語言只寫 preferred-language，不改網址。 */
export default function PublicLegalFooter({
  privacyTestId,
  termsTestId,
  sitemapTestId,
  langTestId,
}: PublicLegalFooterProps) {
  const { t, language, setLanguage } = useTranslation()

  const handleLang = (code: Language) => {
    setLanguage(code)
    localStorage.setItem('preferred-language', code)
  }

  return (
    <footer className="relative z-[2] mt-auto border-t border-black/[0.08]">
      <div className="max-w-[1120px] mx-auto px-4 sm:px-6 py-3 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between text-xs font-normal normal-case tracking-normal text-[#424245]">
        <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
          <span>© 2026 {t('brand.name')}. {t('landing.footer.rights')}</span>
          <span aria-hidden="true">|</span>
          <Link to="/privacy" data-testid={privacyTestId} className="hover:underline">
            {t('landing.footer.privacy')}
          </Link>
          <span aria-hidden="true">|</span>
          <Link to="/terms" data-testid={termsTestId} className="hover:underline">
            {t('landing.footer.terms')}
          </Link>
          <span aria-hidden="true">|</span>
          <Link to="/sitemap" data-testid={sitemapTestId} className="hover:underline">
            {t('landing.footer.sitemap')}
          </Link>
        </div>
        <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
          {languageOptions.map((opt, idx) => (
            <span key={opt.code} className="flex items-center gap-x-2">
              {idx > 0 && <span aria-hidden="true">|</span>}
              <button
                type="button"
                data-testid={langTestId(opt.code)}
                onClick={() => handleLang(opt.code)}
                className={language === opt.code ? 'underline underline-offset-2' : 'hover:underline'}
                aria-label={opt.name}
              >
                {opt.name}
              </button>
            </span>
          ))}
        </div>
      </div>
    </footer>
  )
}
