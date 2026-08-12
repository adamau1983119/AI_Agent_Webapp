/**
 * InfiniteTopicsList Component
 * Phase 1: 無限滾動主題列表（含時間分組）
 * 
 * 功能：
 * - 無限滾動載入主題
 * - 時間分組顯示（今天/昨天/本週/更早）
 * - 支援篩選
 */

import { useMemo, Fragment } from 'react'
import { useNavigate } from 'react-router-dom'
import { useInfiniteTopics } from '@/hooks/useInfiniteTopics'
import type { TopicFilters } from '@/api/topics'
import TopicCard from '@/components/ui/TopicCard'
import InfiniteScroll from '@/components/ui/InfiniteScroll'
import TimeGroupLabel, { type TimeGroup, getTimeGroup } from '@/components/ui/TimeGroupLabel'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import EmptyState from '@/components/ui/EmptyState'
import { useTranslation } from '@/i18n'

interface InfiniteTopicsListProps {
  /** 篩選條件 */
  filters?: Omit<TopicFilters, 'page'>
  /** 每頁數量 */
  pageSize?: number
  /** 是否顯示時間分組 */
  showTimeGroups?: boolean
  /** 卡片列數（響應式）*/
  columns?: 1 | 2 | 3 | 4
  /** 自定義空狀態訊息 */
  emptyMessage?: string
}

// 時間分組的順序
const TIME_GROUP_ORDER: TimeGroup[] = ['today', 'yesterday', 'thisWeek', 'earlier']

export default function InfiniteTopicsList({
  filters = {},
  pageSize = 20,
  showTimeGroups = true,
  columns = 3,
  emptyMessage,
}: InfiniteTopicsListProps) {
  const navigate = useNavigate()
  const { t, language } = useTranslation()
  
  const localeFilters = useMemo(
    () => ({ ...filters, lang: language }),
    [filters, language]
  )
  
  const {
    topics,
    groupedTopics,
    hasMore,
    isLoading,
    isFetchingMore,
    error,
    total,
    loadMore,
    refresh,
  } = useInfiniteTopics({ filters: localeFilters, pageSize })

  const defaultEmptyMessage = emptyMessage || t('topics.noTopics')

  // 處理主題點擊
  const handleTopicClick = (topicId: string) => {
    navigate(`/topics/${topicId}`)
  }

  // 根據列數設定 grid 樣式
  const gridClass = useMemo(() => {
    switch (columns) {
      case 1:
        return 'grid-cols-1'
      case 2:
        return 'grid-cols-1 md:grid-cols-2'
      case 3:
        return 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
      case 4:
        return 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'
      default:
        return 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
    }
  }, [columns])

  // 初始載入中
  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-20">
        <LoadingSpinner />
      </div>
    )
  }

  // 空狀態
  if (!isLoading && topics.length === 0) {
    return (
      <EmptyState
        message={defaultEmptyMessage}
        description={t('topics.tryAdjustFilters')}
      />
    )
  }

  // 渲染主題卡片列表
  const renderTopicCards = (topicsToRender: typeof topics) => (
    <div className={`grid ${gridClass} gap-6`}>
      {topicsToRender.map((topic) => (
        <div
          key={topic.id}
          onClick={() => handleTopicClick(topic.id)}
          className="cursor-pointer transition-transform duration-200 hover:scale-[1.02]"
        >
          <TopicCard topic={topic} />
        </div>
      ))}
    </div>
  )

  // 渲染時間分組列表
  const renderGroupedList = () => {
    // 追蹤已渲染的主題，避免重複
    let lastGroup: TimeGroup | null = null
    
    return (
      <>
        {TIME_GROUP_ORDER.map((group) => {
          const groupTopics = groupedTopics.get(group) || []
          if (groupTopics.length === 0) return null
          
          return (
            <Fragment key={group}>
              <TimeGroupLabel group={group} count={groupTopics.length} />
              {renderTopicCards(groupTopics)}
            </Fragment>
          )
        })}
      </>
    )
  }

  // 渲染普通列表（不分組）
  const renderFlatList = () => renderTopicCards(topics)

  return (
    <div>
      {/* 統計資訊 */}
      <div className="mb-4 text-sm text-gray-600">
        {t('topics.total', { count: String(total) })}，{t('topics.loaded', { count: String(topics.length) })}
      </div>

      {/* 無限滾動容器 */}
      <InfiniteScroll
        hasMore={hasMore}
        isLoading={isFetchingMore}
        onLoadMore={loadMore}
        error={error}
        onRetry={refresh}
        threshold={300}
        className="space-y-6"
      >
        {showTimeGroups ? renderGroupedList() : renderFlatList()}
      </InfiniteScroll>
    </div>
  )
}

