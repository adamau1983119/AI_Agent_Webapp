interface ProgressCardProps {
  title: string
  value: string
  percentage: number
  message: string
  color?: 'primary' | 'secondary' | 'green' | 'orange'
}

const colorClasses = {
  primary: 'text-primary stroke-primary',
  secondary: 'text-secondary stroke-secondary',
  green: 'text-green-600 stroke-green-600',
  orange: 'text-orange-600 stroke-orange-600',
}

export default function ProgressCard({
  title,
  value,
  percentage,
  message,
  color = 'primary',
}: ProgressCardProps) {
  // 縮小 50%：半徑從 28 改為 14
  const radius = 14
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (percentage / 100) * circumference
  const center = 16 // SVG 中心點：半徑 14 + strokeWidth 2 = 16

  return (
    <div className="bg-white rounded-lg shadow p-3">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-semibold text-gray-700 text-sm">{title}</h3>
        <div className="relative w-8 h-8">
          <svg className="progress-ring w-8 h-8 transform -rotate-90">
            <circle
              cx={center}
              cy={center}
              r={radius}
              stroke="#E5E7EB"
              strokeWidth="2"
              fill="transparent"
            />
            <circle
              className={`progress-ring-circle ${colorClasses[color]}`}
              cx={center}
              cy={center}
              r={radius}
              stroke="currentColor"
              strokeWidth="2"
              fill="transparent"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className={`text-xs font-bold ${colorClasses[color]}`}>{percentage}%</span>
          </div>
        </div>
      </div>
      <p className="text-xl font-bold text-gray-800">{value}</p>
      <p className="text-xs text-gray-500 mt-1">{message}</p>
    </div>
  )
}

