/**
 * 最近活動組件
 * Style: Lane Crawford 風格 - 極簡黑白
 */
export default function RecentActivities() {
  // 暫時移除 mock 數據，等待真實 API
  const activities: Array<{ icon: string; title: string; time: string; color: string }> = []
  const activityCount = activities.length

  return (
    <div className="bg-white border border-gray-100 p-4 transition-all duration-300 hover:border-gray-300">
      {/* 標題 */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-[10px] tracking-[0.15em] uppercase text-gray-500 font-light">
          最近活動
        </h3>
        <span className="text-[10px] text-gray-400 font-light">
          {activityCount > 0 ? '100%' : '0%'}
        </span>
      </div>
      
      {/* 進度條 */}
      <div className="w-full h-px bg-gray-100 mb-3">
        <div 
          className="h-full bg-black transition-all duration-500"
          style={{ width: activityCount > 0 ? '100%' : '0%' }}
        />
      </div>
      
      {/* 數值 */}
      <p className="text-xl font-light tracking-wide text-black mb-1">{activityCount}</p>
      
      {/* 訊息 */}
      <p className="text-[10px] text-gray-400 font-light tracking-wide">
        {activityCount > 0 ? '有活動' : '暫無活動'}
      </p>
    </div>
  )
}
