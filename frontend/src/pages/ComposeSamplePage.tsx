/**
 * Compose sample + clickable title-image edit demo (client composite, 0 LLM).
 */
import { Link } from 'react-router-dom'
import TitleImageEditDemo from '@/components/features/TitleImageEditDemo'
import { useTranslation } from '@/i18n'

const REAL_TOPIC_ID = 'www_tom_bateman_love_hypothesis_20260918'
const WWW_URL =
  'https://www.whowhatwear.com/fashion/celebrity/tom-bateman-the-love-hypothesis-interview-2026'

export default function ComposeSamplePage() {
  const { t } = useTranslation()

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-6" data-testid="page-compose-sample">
      <div className="space-y-2">
        <p className="text-xs tracking-[0.2em] uppercase text-gray-500">{t('composer.demoBadge')}</p>
        <h1 className="font-display text-3xl text-gray-900" data-testid="heading-compose-sample">
          {t('composer.sampleTitle')}
        </h1>
        <p className="text-sm text-gray-600">{t('composer.sampleSubtitle')}</p>
        <ol className="text-sm text-gray-600 list-decimal pl-5 space-y-1" data-testid="compose-coach-strip">
          <li>{t('composer.sampleStep1')}</li>
          <li>{t('composer.sampleStep2')}</li>
          <li>{t('composer.sampleStep3')}</li>
        </ol>
      </div>

      <section
        className="bg-white rounded-2xl border border-gray-100 p-5 sm:p-6 space-y-4"
        data-testid="section-real-backend-path"
      >
        <h2 className="font-display text-lg font-semibold">{t('titleImage.realPathTitle')}</h2>
        <p className="text-sm text-gray-600">{t('titleImage.realPathBody')}</p>
        <a
          href={WWW_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm text-primary underline break-all"
          data-testid="link-title-image-sample-source"
        >
          {t('titleImage.sourceLink')}
        </a>
        <Link
          to={`/topics/${REAL_TOPIC_ID}`}
          data-testid="btn-compose-sample-open-real-topic"
          className="w-full inline-flex items-center justify-center min-h-[44px] rounded-xl bg-primary text-white text-sm font-medium"
        >
          {t('titleImage.openRealTopic')}
        </Link>
        <p className="text-xs text-gray-500">{t('titleImage.realPathHint')}</p>
      </section>

      <TitleImageEditDemo />

      <Link
        to="/dashboard"
        data-testid="btn-compose-sample-to-topic"
        className="inline-flex items-center justify-center min-h-[44px] w-full rounded-xl bg-black text-white text-sm"
      >
        {t('composer.sampleToTopic')}
      </Link>
    </div>
  )
}
