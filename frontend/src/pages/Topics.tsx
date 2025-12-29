import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { topicsAPI } from '@/api/client'
import type { TopicFilters } from '@/api/topics'
import TopicCard from '@/components/ui/TopicCard'
import TopicFilters from '@/components/features/TopicFilters'
import Pagination from '@/components/ui/Pagination'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import ErrorDisplay from '@/components/ui/ErrorDisplay'
import EmptyState from '@/components/ui/EmptyState'

export default function Topics() {
  const navigate = useNavigate()
  const [filters, setFilters] = useState<TopicFilters>({
    page: 1,
    limit: 12,
  })

  const {
    data: topicsResponse,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['topics', filters],
    queryFn: () => topicsAPI.getTopics(filters),
  })

  const topics = topicsResponse?.data || []
  const pagination = topicsResponse?.pagination

  const handleFilterChange = (newFilters: TopicFilters) => {
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
          {isLoading ? (
            <LoadingSpinner />
          ) : error ? (
            <ErrorDisplay error={error} onRetry={() => refetch()} />
          ) : topics.length === 0 ? (
            <EmptyState
              message="沒有找到主題"
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

