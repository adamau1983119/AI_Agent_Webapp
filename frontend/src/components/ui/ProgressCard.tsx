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
  const circumference = 2 * Math.PI * 28
  const offset = circumference - (percentage / 100) * circumference

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-700">{title}</h3>
        <div className="relative w-16 h-16">
          <svg className="progress-ring w-16 h-16 transform -rotate-90">
            <circle
              cx="32"
              cy="32"
              r="28"
              stroke="#E5E7EB"
              strokeWidth="4"
              fill="transparent"
            />
            <circle
              className={`progress-ring-circle ${colorClasses[color]}`}
              cx="32"
              cy="32"
              r="28"
              stroke="currentColor"
              strokeWidth="4"
              fill="transparent"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className={`text-sm font-bold ${colorClasses[color]}`}>{percentage}%</span>
          </div>
        </div>
      </div>
      <p className="text-2xl font-bold text-gray-800">{value}</p>
      <p className="text-sm text-gray-500 mt-2">{message}</p>
    </div>
  )
}

