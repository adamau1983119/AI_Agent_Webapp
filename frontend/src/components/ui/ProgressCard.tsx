/**
 * 進度卡片組件
 * Style: Lane Crawford 風格 - 極簡黑白
 */
interface ProgressCardProps {
  title: string
  value: string
  percentage: number
  message: string
  color?: 'primary' | 'secondary' | 'green' | 'orange'
}

export default function ProgressCard({
  title,
  value,
  percentage,
  message,
}: ProgressCardProps) {
  return (
    <div className="bg-white border border-gray-100 p-4 transition-all duration-300 hover:border-gray-300">
      {/* 標題 */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-[10px] tracking-[0.15em] uppercase text-gray-500 font-light">
          {title}
        </h3>
        <span className="text-[10px] text-gray-400 font-light">
          {percentage}%
        </span>
      </div>
      
      {/* 進度條 */}
      <div className="w-full h-px bg-gray-100 mb-3">
        <div 
          className="h-full bg-black transition-all duration-500"
          style={{ width: `${percentage}%` }}
        />
      </div>
      
      {/* 數值 */}
      <p className="text-xl font-light tracking-wide text-black mb-1">{value}</p>
      
      {/* 訊息 */}
      <p className="text-[10px] text-gray-400 font-light tracking-wide">{message}</p>
    </div>
  )
}
