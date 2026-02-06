/**
 * 即將到來的事件組件
 * Style: Lane Crawford 風格 - 極簡黑白
 */
import { useTranslation } from '@/i18n'

export default function UpcomingEvents() {
  const { t } = useTranslation()
  // 暫時移除 mock 數據，等待真實 API
  const events: Array<{ title: string; date: string; time: string }> = []
  const eventCount = events.length

  return (
    <div className="bg-white border border-gray-100 p-4 transition-all duration-300 hover:border-gray-300">
      {/* 標題 */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-[10px] tracking-[0.15em] uppercase text-gray-500 font-light">
          {t('dashboard.upcoming')}
        </h3>
        <span className="text-[10px] text-gray-400 font-light">
          {eventCount > 0 ? '100%' : '0%'}
        </span>
      </div>
      
      {/* 進度條 */}
      <div className="w-full h-px bg-gray-100 mb-3">
        <div 
          className="h-full bg-black transition-all duration-500"
          style={{ width: eventCount > 0 ? '100%' : '0%' }}
        />
      </div>
      
      {/* 數值 */}
      <p className="text-xl font-light tracking-wide text-black mb-1">{eventCount}</p>
      
      {/* 訊息 */}
      <p className="text-[10px] text-gray-400 font-light tracking-wide">
        {eventCount > 0 ? t('dashboard.scheduled') : t('dashboard.noEvents')}
      </p>
    </div>
  )
}
