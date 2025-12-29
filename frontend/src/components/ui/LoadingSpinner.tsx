/**
 * 載入指示器元件
 */

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  text?: string
  className?: string
}

export default function LoadingSpinner({
  size = 'md',
  text = '載入中...',
  className = '',
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  }

  return (
    <div className={`text-center py-12 ${className}`}>
      <div
        className={`inline-block animate-spin rounded-full border-b-2 border-primary ${sizeClasses[size]}`}
      />
      {text && <p className="mt-4 text-gray-500">{text}</p>}
    </div>
  )
}
