type Props = {
  onDark?: boolean
  className?: string
}

/** 黑色 ae 標誌。深色底放在白底上，避免黑標消失。 */
export default function BrandMark({ onDark = false, className = '' }: Props) {
  const img = (
    <img src="/favicon.png" alt="" className="w-10 h-10 object-contain" />
  )
  if (onDark) {
    return (
      <span
        className={`inline-flex items-center justify-center bg-white rounded-xl w-14 h-14 ${className}`}
      >
        {img}
      </span>
    )
  }
  return <span className={`inline-flex ${className}`}>{img}</span>
}
