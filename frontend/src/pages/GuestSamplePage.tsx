/**
 * Sample only: open Dashboard in the browser language (or ?lang=).
 * Does not change `/` or the language picker.
 */
import { useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import Dashboard from '@/pages/Dashboard'
import { useTranslation, type Language } from '@/i18n'
import { mapGuestLanguage } from '@/lib/mapGuestLanguage'

const CHOICES: Language[] = ['zh-TW', 'en', 'ja']

export default function GuestSamplePage() {
  const { t, language, setLanguage } = useTranslation()
  const [params, setParams] = useSearchParams()
  const langParam = params.get('lang')
  const browserTag = typeof navigator !== 'undefined' ? navigator.language : ''
  const requested = mapGuestLanguage(langParam || browserTag)
  const source = langParam ? t('guestSample.sourceQuery') : t('guestSample.sourceBrowser')

  useEffect(() => {
    if (language !== requested) setLanguage(requested)
  }, [language, requested, setLanguage])

  const choose = (code: Language) => {
    const next = new URLSearchParams(params)
    next.set('lang', code)
    setParams(next, { replace: true })
  }

  return (
    <div data-testid="page-guest-sample">
      <div className="max-w-5xl mx-auto px-4 pt-6">
        <p className="text-xs tracking-[0.2em] uppercase text-gray-500">{t('guestSample.kicker')}</p>
        <p className="mt-2 text-sm text-gray-600">{t('guestSample.note')}</p>
        <p className="mt-2 text-sm text-gray-900" data-testid="text-guest-sample-showing">
          {t('guestSample.showing', {
            lang: t(`language.${requested}` as 'language.zh-TW'),
            source,
          })}
        </p>
        <p className="mt-1 text-xs text-gray-500">
          {t('guestSample.browserTag', { tag: browserTag || '—' })}
        </p>
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <span className="text-xs text-gray-500">{t('guestSample.switch')}</span>
          {CHOICES.map((code) => (
            <button
              key={code}
              type="button"
              data-testid={`btn-guest-sample-lang-${code === 'zh-TW' ? 'zh' : code}`}
              onClick={() => choose(code)}
              className={`min-h-[44px] px-3 rounded-full border text-xs ${
                requested === code
                  ? 'border-[#1a1a1a] bg-[#1a1a1a] text-white'
                  : 'border-gray-300 text-gray-700'
              }`}
            >
              {t(`language.${code}` as 'language.zh-TW')}
            </button>
          ))}
        </div>
      </div>
      <Dashboard />
    </div>
  )
}
