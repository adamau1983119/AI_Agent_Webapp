export default function UpcomingEvents() {
  const events = [
    {
      title: 'Webinar: AI 內容生成',
      date: '08.06.2024',
      time: '18:00-20:00',
    },
    {
      title: 'Conference: 社群媒體趨勢',
      date: '17.06.2024',
      time: '10:00-16:00',
    },
  ]

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-bold text-gray-800">即將到來的事件</h3>
        <button className="text-sm text-primary hover:text-primary-dark">View more</button>
      </div>
      <div className="space-y-4">
        {events.map((event, index) => (
          <div key={index} className="border-l-4 border-primary pl-4">
            <p className="font-semibold text-gray-800">{event.title}</p>
            <p className="text-sm text-gray-500">
              {event.date}, {event.time}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}

