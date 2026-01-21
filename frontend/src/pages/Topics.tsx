import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { topicsAPI } from '@/api/client'
import type { TopicFilters as TopicFiltersType, SearchResponse } from '@/api/topics'
import TopicCard from '@/components/ui/TopicCard'
import TopicFilters from '@/components/features/TopicFilters'
import Pagination from '@/components/ui/Pagination'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import ErrorDisplay from '@/components/ui/ErrorDisplay'
import EmptyState from '@/components/ui/EmptyState'
import { usePageTitle } from '@/hooks/usePageTitle'

export default function Topics() {
  usePageTitle()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [filters, setFilters] = useState<TopicFiltersType>({
    page: 1,
    limit: 12,
    search: searchParams.get('search') || undefined,
  })

  // 當 URL 參數變化時，更新 filters
  useEffect(() => {
    const searchQuery = searchParams.get('search')
    if (searchQuery !== filters.search) {
      setFilters((prev) => ({
        ...prev,
        search: searchQuery || undefined,
        page: 1, // 重置到第一頁
      }))
    }
  }, [searchParams])

  // 判斷是否使用新的搜尋端點（當有搜尋關鍵字時）
  const useSearchEndpoint = Boolean(filters.search && filters.search.trim().length >= 2)

  // 使用新的搜尋端點
  const {
    data: searchResponse,
    isLoading: isSearchLoading,
    error: searchError,
    refetch: refetchSearch,
  } = useQuery<SearchResponse>({
    queryKey: ['topics', 'search', filters.search, filters.category, filters.page, filters.limit],
    queryFn: () =>
      topicsAPI.searchTopics({
        query: filters.search!,
        category: filters.category,
        page: filters.page || 1,
        limit: filters.limit || 12,
        role: 'user', // 可以從用戶狀態獲取
      }),
    enabled: useSearchEndpoint,
  })

  // 使用原有的列表端點（當沒有搜尋關鍵字時）
  const {
    data: topicsResponse,
    isLoading: isListLoading,
    error: listError,
    refetch: refetchList,
  } = useQuery({
    queryKey: ['topics', 'list', filters],
    queryFn: () => topicsAPI.getTopics(filters),
    enabled: !useSearchEndpoint,
  })

  // 統一處理響應
  const isLoading = useSearchEndpoint ? isSearchLoading : isListLoading
  const error = useSearchEndpoint ? searchError : listError
  const refetch = useSearchEndpoint ? refetchSearch : refetchList

  // 統一處理結果
  const topics = useSearchEndpoint
    ? searchResponse?.results || []
    : topicsResponse?.data || []

  const pagination = useSearchEndpoint
    ? searchResponse?.pagination
      ? {
          page: searchResponse.pagination.page,
          limit: searchResponse.pagination.limit,
          total: searchResponse.pagination.total,
          totalPages: searchResponse.pagination.pages,
        }
      : undefined
    : topicsResponse?.pagination

  const handleFilterChange = (newFilters: TopicFiltersType) => {
    setFilters(newFilters)
  }

  const handleTopicClick = (topicId: string) => {
    navigate(`/topics/${topicId}`)
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">主題總覽</h1>
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* 左側：篩選器 */}
        <div className="col-span-12 lg:col-span-3">
          <TopicFilters onFilterChange={handleFilterChange} />
        </div>

        {/* 右側：主題列表 */}
        <div className="col-span-12 lg:col-span-9">
          {/* 顯示搜尋來源（如果使用新的搜尋端點） */}
          {useSearchEndpoint && searchResponse?.source && (
            <div className="mb-4 text-sm text-gray-600">
              搜尋來源: {searchResponse.source === 'es' ? 'Elasticsearch' : searchResponse.source === 'cache' ? '快取' : 'MongoDB'}
            </div>
          )}

          {isLoading ? (
            <LoadingSpinner />
          ) : error ? (
            <ErrorDisplay error={error} onRetry={() => refetch()} />
          ) : topics.length === 0 ? (
            <EmptyState
              message={useSearchEndpoint ? '沒有找到符合搜尋條件的主題' : '沒有找到主題'}
              description="嘗試調整篩選條件或稍後再試"
            />
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
                {topics.map((topic) => (
                  <div
                    key={topic.id}
                    onClick={() => handleTopicClick(topic.id)}
                    className="cursor-pointer"
                  >
                    <TopicCard topic={topic} />
                  </div>
                ))}
              </div>

              {/* 分頁控制 */}
              {pagination && pagination.totalPages > 1 && (
                <div className="mt-6">
                  <Pagination
                    currentPage={pagination.page}
                    totalPages={pagination.totalPages}
                    pageSize={pagination.limit}
                    totalItems={pagination.total}
                    onPageChange={(page) => {
                      setFilters({ ...filters, page })
                    }}
                  />
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

