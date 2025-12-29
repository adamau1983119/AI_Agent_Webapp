import type { Schedule } from '@/types'

interface TodayTopicsProps {
  schedules: Schedule[]
}

export default function TodayTopics({ schedules }: TodayTopicsProps) {
  const timeSlots = ['07:00', '12:00', '18:00']

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="font-bold text-gray-800 mb-4">今日主題</h3>
      <div className="space-y-4">
        {timeSlots.map((timeSlot) => {
          const schedule = schedules.find((s) => s.timeSlot === timeSlot)
          const status = schedule?.status || 'pending'
          const topicsCount = schedule?.topicsCount || 0

          return (
            <div key={timeSlot} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <p className="font-semibold text-gray-800">
                  {timeSlot} {timeSlot === '07:00' ? '時尚趨勢' : timeSlot === '12:00' ? '美食推薦' : '社會趨勢'}
                </p>
                <p className="text-sm text-gray-500">
                  {topicsCount}/3 主題完成
                </p>
              </div>
              <span className="text-sm text-gray-500">{timeSlot}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}

