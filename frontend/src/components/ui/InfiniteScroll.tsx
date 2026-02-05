/**
 * InfiniteScroll Component
 * Phase 1: 無限滾動列表元件
 * 
 * 功能：
 * - 滾動到底部自動載入更多
 * - 支援載入中狀態
 * - 支援錯誤處理和重試
 */

import { useEffect, useRef, useCallback } from 'react'
import LoadingSpinner from './LoadingSpinner'
import { useTranslation } from '@/i18n'

interface InfiniteScrollProps {
  /** 子元素 */
  children: React.ReactNode
  /** 是否有更多資料 */
  hasMore: boolean
  /** 是否正在載入 */
  isLoading: boolean
  /** 載入更多的回調函數 */
  onLoadMore: () => void
  /** 載入閾值（距離底部多少像素時觸發載入） */
  threshold?: number
  /** 載入中顯示的元素 */
  loader?: React.ReactNode
  /** 沒有更多資料時顯示的元素 */
  endMessage?: React.ReactNode
  /** 容器的 className */
  className?: string
  /** 錯誤訊息 */
  error?: Error | null
  /** 重試回調 */
  onRetry?: () => void
}

export default function InfiniteScroll({
  children,
  hasMore,
  isLoading,
  onLoadMore,
  threshold = 200,
  loader,
  endMessage,
  className = '',
  error,
  onRetry,
}: InfiniteScrollProps) {
  const { t } = useTranslation()
  const observerRef = useRef<IntersectionObserver | null>(null)
  const loadMoreRef = useRef<HTMLDivElement>(null)

  // 使用 Intersection Observer 偵測滾動到底部
  const handleObserver = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      const [entry] = entries
      if (entry.isIntersecting && hasMore && !isLoading && !error) {
        onLoadMore()
      }
    },
    [hasMore, isLoading, error, onLoadMore]
  )

  useEffect(() => {
    const options = {
      root: null, // 使用 viewport 作為 root
      rootMargin: `${threshold}px`,
      threshold: 0,
    }

    observerRef.current = new IntersectionObserver(handleObserver, options)

    if (loadMoreRef.current) {
      observerRef.current.observe(loadMoreRef.current)
    }

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect()
      }
    }
  }, [handleObserver, threshold])

  const defaultLoader = (
    <div className="flex justify-center items-center py-8">
      <LoadingSpinner />
      <span className="ml-3 text-gray-600">{t('common.loading')}</span>
    </div>
  )

  const defaultEndMessage = (
    <div className="text-center py-8 text-gray-500">
      <div className="flex items-center justify-center gap-2">
        <div className="w-8 h-px bg-gray-300" />
        <span>{t('common.noMoreData')}</span>
        <div className="w-8 h-px bg-gray-300" />
      </div>
    </div>
  )

  const errorMessage = (
    <div className="text-center py-8">
      <p className="text-red-500 mb-4">{t('common.failed')}: {error?.message || t('error.unknown')}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          {t('common.retry')}
        </button>
      )}
    </div>
  )

  return (
    <div className={className}>
      {children}

      {/* 載入觸發點 */}
      <div ref={loadMoreRef} />

      {/* 載入中狀態 */}
      {isLoading && (loader || defaultLoader)}

      {/* 錯誤狀態 */}
      {error && !isLoading && errorMessage}

      {/* 沒有更多資料 */}
      {!hasMore && !isLoading && !error && (endMessage || defaultEndMessage)}
    </div>
  )
}

