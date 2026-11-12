/**
 * Sample only. Mobile welcome with today's cards. Does not replace /welcome.
 */
import { Link } from 'react-router-dom'
import { useTranslation } from '@/i18n'
import { useNoindex } from '@/hooks/useNoindex'
import { TodayMobileTopics } from '@/components/topics/MobileTopicList'

const FEATURE_KEYS = ['trends', 'aiWrite', 'channel', 'inspiration'] as const

export default function WelcomeSamplePage() {
  const { t } = useTranslation()
  useNoindex()

  return (
    <div data-testid="page-welcome-sample" className="min-h-screen bg-[#F7F5F2] px-4 py-8 text-[#1a1a1a]">
      <main className="mx-auto max-w-md">
        <h1 className="font-display text-4xl leading-tight">
          {t('landing.hero.titleLine1')}
          <br />
          {t('landing.hero.titleLine2')}
        </h1>
        <div className="mt-6 flex flex-col gap-3">
          <Link
            to="/register"
            data-testid="btn-welcome-sample-register"
            className="flex min-h-[46px] items-center justify-center rounded-full bg-[#1a1a1a] text-xs tracking-[0.16em] text-white"
          >
            {t('landing.cta.register')}
          </Link>
          <Link
            to="/login"
            data-testid="btn-welcome-sample-login"
            className="flex min-h-[46px] items-center justify-center rounded-full border border-[#1a1a1a] text-xs tracking-[0.16em]"
          >
            {t('landing.cta.login')}
          </Link>
        </div>
        <div className="mt-8">
          <TodayMobileTopics testId="list-welcome-sample-topics" />
        </div>
        <ul className="mt-10 space-y-3 text-sm text-[#6b6b6b]">
          {FEATURE_KEYS.map((key) => (
            <li key={key}>{t(`landing.features.${key}.title`)}</li>
          ))}
        </ul>
      </main>
    </div>
  )
}
