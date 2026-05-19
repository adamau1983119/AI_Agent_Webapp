import { useId } from 'react'
import type { SocialPlatform } from '@/api/social'

export type PlatformIconSize = 'sm' | 'md' | 'lg'

const sizePx: Record<PlatformIconSize, number> = {
  sm: 20,
  md: 24,
  lg: 32,
}

export interface PlatformIconProps {
  platform: SocialPlatform
  size?: PlatformIconSize
  className?: string
  /** 供螢幕閱讀器；裝飾用時可省略 */
  label?: string
}

export default function PlatformIcon({
  platform,
  size = 'md',
  className = '',
  label,
}: PlatformIconProps) {
  const px = sizePx[size]
  const ariaProps = label ? { role: 'img' as const, 'aria-label': label } : { 'aria-hidden': true as const }

  const common = {
    width: px,
    height: px,
    className: `shrink-0 ${className}`,
    ...ariaProps,
  }

  const igGradId = useId()

  switch (platform) {
    case 'instagram':
      return (
        <svg viewBox="0 0 24 24" fill="none" {...common}>
          <defs>
            <linearGradient id={igGradId} x1="2" y1="22" x2="22" y2="2" gradientUnits="userSpaceOnUse">
              <stop stopColor="#F58529" />
              <stop offset="0.5" stopColor="#DD2A7B" />
              <stop offset="1" stopColor="#8134AF" />
            </linearGradient>
          </defs>
          <rect x="2" y="2" width="20" height="20" rx="6" fill={`url(#${igGradId})`} />
          <circle cx="12" cy="12" r="4.25" stroke="white" strokeWidth="1.75" />
          <circle cx="17.4" cy="6.6" r="1.1" fill="white" />
        </svg>
      )
    case 'facebook':
      return (
        <svg viewBox="0 0 24 24" fill="none" {...common}>
          <rect width="24" height="24" rx="6" fill="#1877F2" />
          <path
            d="M13.5 8.5H15.5V5.5H13.5C11.57 5.5 10 7.07 10 9V11H8V14H10V20.5H13V14H15.2L15.6 11H13V9.75C13 9.06 13.56 8.5 14.25 8.5H13.5Z"
            fill="white"
          />
        </svg>
      )
    case 'threads':
      return (
        <svg viewBox="0 0 24 24" fill="none" {...common}>
          <rect width="24" height="24" rx="6" className="fill-gray-900 dark:fill-white" />
          <path
            className="fill-white dark:fill-gray-900"
            d="M12 6.2c2.1 0 3.8 1.6 4 3.6-.5-.1-1-.2-1.5-.2-2.2 0-4 1.5-4.3 3.5-.3 1.8.8 3.4 2.5 4 1 .4 2.1.3 3-.2 1.2.7 2.7 1.1 4.2 1.1 1.1 0 2.1-.2 3-.6-1.2 2.2-3.6 3.7-6.4 3.7-3.9 0-7.1-3-7.1-6.7 0-3.2 2.3-5.9 5.4-6.4Z"
          />
        </svg>
      )
    case 'tiktok':
      return (
        <svg viewBox="0 0 24 24" fill="none" {...common}>
          <rect width="24" height="24" rx="6" fill="#000000" />
          <path
            d="M15.5 6.8c.9.7 2 1.1 3.1 1.1V11c-1.1 0-2.1-.3-3-.8v4.4c0 2.4-1.9 4.3-4.3 4.3S7 17 7 14.6s1.9-4.3 4.3-4.3c.4 0 .7 0 1.1.1v2.2a2.2 2.2 0 00-1.1-.3c-1.2 0-2.2 1-2.2 2.2s1 2.2 2.2 2.2 2.2-1 2.2-2.2V6.8h2.2z"
            fill="#25F4EE"
          />
          <path
            d="M15.5 7.4c.9.7 2 1.1 3.1 1.1v2.4c-1.1 0-2.1-.3-3-.8v4.4c0 2.4-1.9 4.3-4.3 4.3S7 16.4 7 14s1.9-4.3 4.3-4.3c.4 0 .7 0 1.1.1v1.4a2.6 2.6 0 00-1.1-.2c-1.4 0-2.6 1.2-2.6 2.6s1.2 2.6 2.6 2.6 2.6-1.2 2.6-2.6V7.4h1.6z"
            fill="#FE2C55"
            opacity="0.9"
          />
        </svg>
      )
    case 'twitter':
      return (
        <svg viewBox="0 0 24 24" fill="none" {...common}>
          <rect width="24" height="24" rx="6" className="fill-gray-900 dark:fill-white" />
          <path
            className="fill-white dark:fill-gray-900"
            d="M13.2 11.2 18.5 5h-1.3l-4.6 5.4L9.4 5H5.5l5.6 8.1L5.5 19h1.3l4.9-5.7 4.1 5.7h3.9l-5.8-8.3Zm-1.8 2.1-.57-.8-4.5-6.4h1.9l3.6 5.2.57.8 4.7 6.7h-1.9l-3.8-5.5Z"
          />
        </svg>
      )
    default:
      return null
  }
}
