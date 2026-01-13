export default function RecentActivities() {
  // 暫時移除 mock 數據，等待真實 API
  const activities: Array<{ icon: string; title: string; time: string; color: string }> = []
  const activityCount = activities.length

  return (
    <div className="bg-white rounded-lg shadow p-3">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-semibold text-gray-700 text-sm">最近活動</h3>
        <div className="relative w-8 h-8">
          <svg className="progress-ring w-8 h-8 transform -rotate-90">
            <circle
              cx={16}
              cy={16}
              r={14}
              stroke="#E5E7EB"
              strokeWidth="2"
              fill="transparent"
            />
            <circle
              className="progress-ring-circle text-indigo-600 stroke-indigo-600"
              cx={16}
              cy={16}
              r={14}
              stroke="currentColor"
              strokeWidth="2"
              fill="transparent"
              strokeDasharray={87.96}
              strokeDashoffset={activityCount > 0 ? 0 : 87.96}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-xs font-bold text-indigo-600">{activityCount > 0 ? 100 : 0}%</span>
          </div>
        </div>
      </div>
      <p className="text-xl font-bold text-gray-800">{activityCount}</p>
      <p className="text-xs text-gray-500 mt-1">{activityCount > 0 ? "有活動" : "暫無活動"}</p>
    </div>
  )
}

