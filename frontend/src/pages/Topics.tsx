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
import InfiniteTopicsList from '@/components/features/InfiniteTopicsList'
import { usePageTitle } from '@/hooks/usePageTitle'
import { useTranslation } from '@/i18n'
import { showError } from '@/utils/toast'

// Phase 1: 顯示模式
type ViewMode = 'infinite' | 'pagination'

function parseTopicCategory(
  raw: string | null
): 'fashion' | 'food' | 'trend' | undefined {
  if (raw === 'fashion' || raw === 'food' || raw === 'trend') return raw
  return undefined
}

export default function Topics() {
  usePageTitle()
  const { t, language } = useTranslation()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const categoryFromUrl = parseTopicCategory(searchParams.get('category'))
  // Phase 1: 預設使用無限滾動模式
  const [viewMode, setViewMode] = useState<ViewMode>('infinite')
  const [filters, setFilters] = useState<TopicFiltersType>({
    page: 1,
    limit: 12,
    search: searchParams.get('search') || undefined,
    category: categoryFromUrl,
    lang: language,
  })

  useEffect(() => {
    setFilters((prev) => (prev.lang === language ? prev : { ...prev, lang: language, page: 1 }))
  }, [language])

  // 當 URL 參數變化時，更新 filters
  useEffect(() => {
    const searchQuery = searchParams.get('search')
    const categoryQuery = parseTopicCategory(searchParams.get('category'))
    if (searchQuery !== filters.search || filters.category !== categoryQuery) {
      // 驗證 URL 參數中的搜尋關鍵字
      if (searchQuery) {
        const trimmedQuery = searchQuery.trim()
        
        // 驗證最小長度
        if (trimmedQuery.length > 0 && trimmedQuery.length < 2) {
          showError(t('topics.search.minLength'))
          // 清除無效的搜尋關鍵字
          setFilters((prev) => ({
            ...prev,
            search: undefined,
            category: categoryQuery,
            page: 1,
          }))
          return
        }
        
        // 驗證最大長度
        if (trimmedQuery.length > 100) {
          showError(t('topics.search.maxLength'))
          // 截斷到最大長度
          setFilters((prev) => ({
            ...prev,
            search: trimmedQuery.substring(0, 100),
            category: categoryQuery,
            page: 1,
          }))
          return
        }
      }
      
      setFilters((prev) => ({
        ...prev,
        search: searchQuery || undefined,
        category: categoryQuery,
        page: 1, // 重置到第一頁
      }))
    }
  }, [searchParams, t])

  // 判斷是否使用新的搜尋端點（當有搜尋關鍵字時）
  const useSearchEndpoint = Boolean(filters.search && filters.search.trim().length >= 2)
  // 判斷是否有搜尋條件（用於隱藏時間分組）
  const hasSearchQuery = Boolean(filters.search && filters.search.trim().length >= 2)

  // 使用新的搜尋端點
  const {
    data: searchResponse,
    isLoading: isSearchLoading,
    error: searchError,
    refetch: refetchSearch,
  } = useQuery<SearchResponse>({
    queryKey: ['topics', 'search', filters.search, filters.category, filters.page, filters.limit, language],
    queryFn: () =>
      topicsAPI.searchTopics({
        query: filters.search!,
        category: filters.category,
        page: filters.page || 1,
        limit: filters.limit || 12,
        role: 'user',
        lang: language,
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
    queryKey: ['topics', 'list', filters, language],
    queryFn: () => topicsAPI.getTopics({ ...filters, lang: language }),
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
    // 驗證搜尋關鍵字（如果提供）
    if (newFilters.search) {
      const trimmedQuery = newFilters.search.trim()
      
      // 驗證最小長度
      if (trimmedQuery.length > 0 && trimmedQuery.length < 2) {
        showError(t('topics.search.minLength'))
        // 清除無效的搜尋關鍵字
        setFilters({ ...newFilters, search: undefined })
        return
      }
      
      // 驗證最大長度
      if (trimmedQuery.length > 100) {
        showError(t('topics.search.maxLength'))
        // 截斷到最大長度
        setFilters({ ...newFilters, search: trimmedQuery.substring(0, 100) })
        return
      }
    }
    
    setFilters(newFilters)
  }

  const handleTopicClick = (topicId: string) => {
    navigate(`/topics/${topicId}`)
  }

  // Phase 1: 渲染分頁模式的內容
  const renderPaginationMode = () => (
    <>
      {/* 顯示搜尋來源（如果使用新的搜尋端點） */}
      {useSearchEndpoint && searchResponse?.source && (
        <div className="mb-4 text-sm text-gray-600">
          {t('topics.searchSource')}: {searchResponse.source === 'es' ? 'Elasticsearch' : searchResponse.source === 'cache' ? 'Cache' : 'MongoDB'}
        </div>
      )}

      {isLoading ? (
        <LoadingSpinner />
      ) : error ? (
        <ErrorDisplay error={error} onRetry={() => refetch()} />
      ) : topics.length === 0 ? (
        <EmptyState
          message={useSearchEndpoint ? t('topics.noSearchResults') : t('topics.noTopics')}
          description={t('topics.tryAdjustFilters')}
        />
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 mb-6">
            {topics.map((topic) => (
              <div
                key={topic.id}
                onClick={() => handleTopicClick(topic.id)}
                data-testid={`topic-card-${topic.id}`}
                className="cursor-pointer"
              >
                <TopicCard topic={topic} hideCacheBadge />
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
                  // 更新 filters 並觸發查詢
                  const newFilters = { ...filters, page }
                  setFilters(newFilters)
                  // 確保查詢會重新執行（React Query 會根據 queryKey 自動觸發）
                }}
              />
            </div>
          )}
        </>
      )}
    </>
  )

  // Phase 1: 渲染無限滾動模式的內容
  const renderInfiniteMode = () => (
    <InfiniteTopicsList
      filters={{
        category: filters.category,
        status: filters.status,
        date: filters.date,
        search: filters.search,
        sort: filters.sort,
        order: filters.order,
      }}
      showTimeGroups={!hasSearchQuery} // 搜尋時不顯示時間分組
      pageSize={20}
      emptyMessage={filters.search ? t('topics.noSearchResults') : t('topics.noTopics')}
    />
  )

  return (
    <div className="p-4 sm:p-6 min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">{t('topics.overview')}</h1>
        
        {/* Phase 1: 顯示模式切換 */}
        <div className="flex items-center gap-2 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
          <button
            onClick={() => setViewMode('infinite')}
            data-testid="btn-topics-view-infinite"
            className={`px-3 py-2 sm:py-1.5 rounded-md text-sm font-medium transition-colors min-h-[44px] sm:min-h-0 ${
              viewMode === 'infinite'
                ? 'bg-white dark:bg-gray-700 text-blue-600 dark:text-blue-400 shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200'
            }`}
          >
            <span className="flex items-center gap-1">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
              <span className="hidden sm:inline">{t('topics.infiniteScroll')}</span>
              <span className="sm:hidden">{t('topics.infiniteScroll').substring(0, 2)}</span>
            </span>
          </button>
          <button
            onClick={() => setViewMode('pagination')}
            data-testid="btn-topics-view-pagination"
            className={`px-3 py-2 sm:py-1.5 rounded-md text-sm font-medium transition-colors min-h-[44px] sm:min-h-0 ${
              viewMode === 'pagination'
                ? 'bg-white dark:bg-gray-700 text-blue-600 dark:text-blue-400 shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200'
            }`}
          >
            <span className="flex items-center gap-1">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
              <span className="hidden sm:inline">{t('topics.pagination')}</span>
              <span className="sm:hidden">{t('topics.pagination').substring(0, 2)}</span>
            </span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-4 sm:gap-6">
        {/* 左側：篩選器 */}
        <div className="col-span-12 lg:col-span-3">
          <TopicFilters
            key={categoryFromUrl || 'all'}
            initialCategory={categoryFromUrl || ''}
            onFilterChange={handleFilterChange}
          />
        </div>

        {/* 右側：主題列表 */}
        <div className="col-span-12 lg:col-span-9">
          {viewMode === 'infinite' ? renderInfiniteMode() : renderPaginationMode()}
        </div>
      </div>
    </div>
  )
}

