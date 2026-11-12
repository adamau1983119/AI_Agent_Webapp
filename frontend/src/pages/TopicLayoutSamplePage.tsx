/**
 * Sample only. Portrait topic page: title, full text, then small related cards.
 */
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { topicsAPI } from '@/api/topics'
import { MobileTopicList } from '@/components/topics/MobileTopicList'
import { useNoindex } from '@/hooks/useNoindex'
import { useTranslation } from '@/i18n'
import { todayHktDateString } from '@/lib/topicDayHkt'

export default function TopicLayoutSamplePage() {
  const { t, language } = useTranslation()
  useNoindex()
  const today = todayHktDateString()
  const query = useQuery({
    queryKey: ['topic-layout-sample', language, today],
    queryFn: () => topicsAPI.getTopics({ limit: 15, lang: language, date: today }),
    retry: false,
  })
  const topics = query.data?.data || []
  const current = topics[0]
  const related = topics.slice(1, 4)
  const fullText = current?.summaryFlash || current?.summary_flash || current?.description || ''

  const jump = () => {
    document.getElementById('sample-compose')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  return (
    <div data-testid="page-topic-layout-sample" className="min-h-screen bg-[#F7F5F2] px-4 py-6 text-[#1a1a1a]">
      <main className="mx-auto max-w-md space-y-4">
        <Link to="/dashboard" data-testid="btn-topic-layout-back" className="inline-flex min-h-[44px] items-center text-sm">
          {t('topicLayout.back')}
        </Link>
        {query.isLoading ? <p className="text-sm text-[#6b6b6b]">{t('welcomeSample.loading')}</p> : null}
        {!query.isLoading && !current ? <p className="text-sm text-[#6b6b6b]">{t('topicLayout.empty')}</p> : null}
        {current ? (
          <>
            <p className="text-xs uppercase tracking-[0.14em] text-[#6b6b6b]">{current.category}</p>
            <h1 className="font-display text-4xl leading-tight">{current.title}</h1>
            <h2 className="pt-4 font-display text-lg">{t('topicLayout.fullText')}</h2>
            <p className="whitespace-pre-line text-sm leading-relaxed">{fullText}</p>
            <p className="text-xs text-[#6b6b6b]">{t('topicLayout.related')}</p>
            {related.length === 0 ? (
              <p className="text-sm text-[#6b6b6b]">{t('topicLayout.empty')}</p>
            ) : (
              <MobileTopicList topics={related} testId="list-topic-layout-related" compact />
            )}
            <button
              type="button"
              data-testid="btn-topic-layout-jump"
              onClick={jump}
              className="flex min-h-[46px] w-full items-center justify-center rounded-full border border-[#1a1a1a] text-xs tracking-[0.16em]"
            >
              {t('topicLayout.jump')}
            </button>
            <p id="sample-compose" className="pb-16 text-sm text-[#6b6b6b]">
              {t('topicLayout.jump')}
            </p>
          </>
        ) : null}
      </main>
    </div>
  )
}
