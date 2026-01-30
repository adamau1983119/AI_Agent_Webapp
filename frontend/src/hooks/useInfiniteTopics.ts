/**
 * useInfiniteTopics Hook
 * Phase 1: 無限滾動主題載入
 * 
 * 功能：
 * - 支援無限滾動載入主題
 * - 支援篩選條件
 * - 支援時間分組
 */

import { useInfiniteQuery } from '@tanstack/react-query'
import { topicsAPI, type TopicFilters } from '@/api/topics'
import type { Topic } from '@/types'
import { useMemo } from 'react'
import { groupByTime, type TimeGroup } from '@/components/ui/TimeGroupLabel'

interface UseInfiniteTopicsOptions {
  filters?: Omit<TopicFilters, 'page'>
  enabled?: boolean
  pageSize?: number
}

interface InfiniteTopicsResult {
  /** 所有已載入的主題 */
  topics: Topic[]
  /** 按時間分組的主題 */
  groupedTopics: Map<TimeGroup, Topic[]>
  /** 是否有更多資料 */
  hasMore: boolean
  /** 是否正在載入第一頁 */
  isLoading: boolean
  /** 是否正在載入更多 */
  isFetchingMore: boolean
  /** 錯誤 */
  error: Error | null
  /** 總數量 */
  total: number
  /** 載入更多 */
  loadMore: () => void
  /** 重新整理 */
  refresh: () => void
}

export function useInfiniteTopics({
  filters = {},
  enabled = true,
  pageSize = 20,
}: UseInfiniteTopicsOptions = {}): InfiniteTopicsResult {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isLoading,
    isFetchingNextPage,
    error,
    refetch,
  } = useInfiniteQuery({
    queryKey: ['topics', 'infinite', filters, pageSize],
    queryFn: async ({ pageParam = 1 }) => {
      const response = await topicsAPI.getTopics({
        ...filters,
        page: pageParam,
        limit: pageSize,
      })
      return response
    },
    getNextPageParam: (lastPage) => {
      const { page, totalPages } = lastPage.pagination
      return page < totalPages ? page + 1 : undefined
    },
    initialPageParam: 1,
    enabled,
  })

  // 合併所有頁面的主題
  const topics = useMemo(() => {
    if (!data?.pages) return []
    return data.pages.flatMap((page) => page.data)
  }, [data?.pages])

  // 按時間分組
  const groupedTopics = useMemo(() => {
    return groupByTime(topics)
  }, [topics])

  // 計算總數
  const total = useMemo(() => {
    if (!data?.pages || data.pages.length === 0) return 0
    return data.pages[0].pagination.total
  }, [data?.pages])

  return {
    topics,
    groupedTopics,
    hasMore: hasNextPage ?? false,
    isLoading,
    isFetchingMore: isFetchingNextPage,
    error: error as Error | null,
    total,
    loadMore: () => fetchNextPage(),
    refresh: () => refetch(),
  }
}

