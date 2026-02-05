import { usePageTitle } from '@/hooks/usePageTitle'
import { useTranslation } from '@/i18n'

export default function Schedule() {
  usePageTitle()
  const { t } = useTranslation()
  
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">{t('schedule.title')}</h1>
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-600">{t('schedule.developing')}</p>
      </div>
    </div>
  )
}

