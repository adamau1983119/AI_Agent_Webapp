/**
 * Compose sample / practice page — canned demo, no compose API.
 */
import { Link } from 'react-router-dom'
import PostComposerPanel from '@/components/features/PostComposerPanel'
import { useTranslation } from '@/i18n'

export default function ComposeSamplePage() {
  const { t, language } = useTranslation()

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
      <PostComposerPanel
        mode="demo"
        topicId="demo"
        topicTitle={t('composer.sampleTopicTitle')}
        contextSummary={t('composer.sampleTopicFact')}
        language={language}
        requireAuth={(fn) => fn()}
      />
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
