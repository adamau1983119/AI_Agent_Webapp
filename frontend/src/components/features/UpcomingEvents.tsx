export default function UpcomingEvents() {
  // 暫時移除 mock 數據，等待真實 API
  const events: Array<{ title: string; date: string; time: string }> = []

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-bold text-gray-800">即將到來的事件</h3>
        <button className="text-sm text-primary hover:text-primary-dark">View more</button>
      </div>
      <div className="space-y-4">
        {events.length > 0 ? (
          events.map((event, index) => (
            <div key={index} className="border-l-4 border-primary pl-4">
              <p className="font-semibold text-gray-800">{event.title}</p>
              <p className="text-sm text-gray-500">
                {event.date}, {event.time}
              </p>
            </div>
          ))
        ) : (
          <p className="text-sm text-gray-500 text-center py-4">暫無即將到來的事件</p>
        )}
      </div>
    </div>
  )
}

