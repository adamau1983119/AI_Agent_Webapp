/**
 * 圖片搜尋元件
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { imagesAPI } from '@/api/client'
import { showSuccess, showError } from '@/utils/toast'
import type { ImageSearchParams } from '@/api/images'
import Pagination from '@/components/ui/Pagination'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import ErrorDisplay from '@/components/ui/ErrorDisplay'
import EmptyState from '@/components/ui/EmptyState'

interface ImageSearchProps {
  topicId: string
  onImageSelect: (image: { url: string; source: string; photographer?: string; license: string }) => void
  onClose: () => void
}

export default function ImageSearch({
  topicId,
  onImageSelect,
  onClose,
}: ImageSearchProps) {
  const queryClient = useQueryClient()
  const [keywords, setKeywords] = useState('')
  const [source, setSource] = useState<'unsplash' | 'pexels' | 'pixabay' | undefined>()
  const [page, setPage] = useState(1)
  const limit = 20

  // 搜尋圖片
  const {
    data: searchResponse,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['images', 'search', keywords, source, page],
    queryFn: () =>
      imagesAPI.searchImages({
        keywords,
        source,
        page,
        limit,
      }),
    enabled: keywords.length > 0,
  })

  const searchResults = searchResponse?.data || []
  const pagination = searchResponse?.pagination

  // 新增圖片到主題
  const createMutation = useMutation({
    mutationFn: (imageData: {
      url: string
      source: string
      photographer?: string
      license: string
    }) =>
      imagesAPI.createImage(topicId, {
        url: imageData.url,
        source: imageData.source,
        photographer: imageData.photographer,
        license: imageData.license,
        order: 0, // 將在後端自動設定
      }),
    onSuccess: () => {
      queryClient.invalidateQueries(['images', topicId])
      showSuccess('圖片已成功新增')
      onImageSelect({
        url: '',
        source: '',
        license: '',
      })
    },
    onError: (error) => {
      showError('新增圖片失敗，請稍後再試')
      console.error('Failed to add image:', error)
    },
  })

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (keywords.trim()) {
      setPage(1)
      refetch()
    }
  }

  const handleSelectImage = (image: any) => {
    createMutation.mutate({
      url: image.url,
      source: image.source,
      photographer: image.photographer,
      license: image.license || 'Unknown',
    })
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-gray-800">搜尋圖片</h2>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
        >
          ×
        </button>
      </div>

      {/* 搜尋表單 */}
      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex gap-2">
          <input
            type="text"
            value={keywords}
            onChange={(e) => setKeywords(e.target.value)}
            placeholder="輸入關鍵字搜尋圖片..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
          />
          <select
            value={source || ''}
            onChange={(e) =>
              setSource(
                e.target.value
                  ? (e.target.value as 'unsplash' | 'pexels' | 'pixabay')
                  : undefined
              )
            }
            className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
          >
            <option value="">所有來源</option>
            <option value="unsplash">Unsplash</option>
            <option value="pexels">Pexels</option>
            <option value="pixabay">Pixabay</option>
          </select>
          <button
            type="submit"
            disabled={!keywords.trim()}
            className="px-6 py-2 bg-primary text-white rounded-md hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            搜尋
          </button>
        </div>
      </form>

      {/* 搜尋結果 */}
      {isLoading ? (
        <LoadingSpinner />
      ) : error ? (
        <ErrorDisplay error={error} onRetry={() => refetch()} />
      ) : searchResults.length === 0 && keywords ? (
        <EmptyState message="沒有找到圖片" description="嘗試使用不同的關鍵字" />
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-6">
            {searchResults.map((image) => (
              <div
                key={image.id}
                className="relative group aspect-square rounded-lg overflow-hidden bg-gray-100 cursor-pointer"
              >
                <img
                  src={image.url}
                  alt={image.id}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    e.currentTarget.src =
                      'https://via.placeholder.com/400x400?text=Image'
                  }}
                />
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/50 transition-all duration-200 flex items-center justify-center opacity-0 group-hover:opacity-100">
                  <button
                    onClick={() => handleSelectImage(image)}
                    disabled={createMutation.isPending}
                    className="px-4 py-2 bg-white text-gray-800 rounded text-sm font-medium hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {createMutation.isPending ? '新增中...' : '選擇'}
                  </button>
                </div>
                <div className="absolute bottom-0 left-0 right-0 bg-black/50 text-white text-xs p-2">
                  {image.source}
                </div>
              </div>
            ))}
          </div>

          {/* 分頁控制 */}
          {pagination && pagination.totalPages > 1 && (
            <div className="mt-4">
              <Pagination
                currentPage={pagination.page}
                totalPages={pagination.totalPages}
                pageSize={pagination.limit}
                totalItems={pagination.total}
                onPageChange={(newPage) => setPage(newPage)}
                showTotal={true}
                showJump={false}
              />
            </div>
          )}
        </>
      )}
    </div>
  )
}
