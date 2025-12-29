/**
 * 圖片搜尋元件
 */

import { useState, useEffect, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { imagesAPI } from '@/api/client'
import { showSuccess, showError } from '@/utils/toast'
import type { Topic, Content } from '@/types'
import Pagination from '@/components/ui/Pagination'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import ErrorDisplay from '@/components/ui/ErrorDisplay'
import EmptyState from '@/components/ui/EmptyState'

interface ImageSearchProps {
  topicId: string
  topic?: Topic | null
  content?: Content | null
  onImageSelect: (image: { url: string; source: string; photographer?: string; license: string }) => void
  onClose: () => void
}

/**
 * 從內容中提取關鍵字
 */
function extractKeywords(topic: Topic | null | undefined, content: Content | null | undefined): string[] {
  const keywords: Set<string> = new Set()
  
  // 從主題標題提取關鍵字
  if (topic?.title) {
    // 移除常見的停用詞和數字
    const titleWords = topic.title
      .replace(/[0-9]/g, '') // 移除數字
      .replace(/[大必吃平民美食推薦]/g, '') // 移除常見詞
      .split(/[、，,]/)
      .map(w => w.trim())
      .filter(w => w.length > 1)
    
    titleWords.forEach(word => {
      if (word.length > 1) {
        keywords.add(word)
      }
    })
  }
  
  // 從文章內容提取關鍵字
  if (content?.article) {
    const article = content.article
    
    // 提取常見的食物名稱（中文）
    const foodKeywords = [
      '老婆餅', '雞蛋仔', '腸粉', '燒賣', '叉燒包', '蝦餃', '燒鵝', '燒肉',
      '雲吞', '魚蛋', '牛腩', '煲仔飯', '車仔麵', '絲襪奶茶', '菠蘿包',
      '蛋撻', '燒餅', '油條', '豆漿', '小籠包', '生煎包', '鍋貼', '餃子',
      '拉麵', '烏冬', '壽司', '刺身', '天婦羅', '章魚燒', '大阪燒',
      '漢堡', '披薩', '義大利麵', '牛排', '沙拉', '三明治', '熱狗',
      '蛋糕', '餅乾', '巧克力', '冰淇淋', '布丁', '馬卡龍', '可頌'
    ]
    
    foodKeywords.forEach(keyword => {
      if (article.includes(keyword)) {
        keywords.add(keyword)
      }
    })
    
    // 提取常見的形容詞+名詞組合
    const patterns = [
      /傳統[\u4e00-\u9fa5]+/g,  // 傳統XX
      /街頭[\u4e00-\u9fa5]+/g,  // 街頭XX
      /經典[\u4e00-\u9fa5]+/g,  // 經典XX
      /特色[\u4e00-\u9fa5]+/g,  // 特色XX
      /招牌[\u4e00-\u9fa5]+/g,  // 招牌XX
    ]
    
    patterns.forEach(pattern => {
      const matches = article.match(pattern)
      if (matches) {
        matches.forEach(match => {
          const keyword = match.replace(/傳統|街頭|經典|特色|招牌/g, '').trim()
          if (keyword.length > 1) {
            keywords.add(keyword)
          }
        })
      }
    })
  }
  
  // 從腳本內容提取關鍵字
  if (content?.script) {
    const script = content.script
    
    // 提取場景描述中的關鍵字
    const scenePatterns = [
      /\[鏡頭[^\]]+\]/g,
      /特寫[^\s]+/g,
      /近景[^\s]+/g,
      /遠景[^\s]+/g,
    ]
    
    scenePatterns.forEach(pattern => {
      const matches = script.match(pattern)
      if (matches) {
        matches.forEach(match => {
          const keyword = match
            .replace(/\[|\]|鏡頭|特寫|近景|遠景/g, '')
            .trim()
          if (keyword.length > 1) {
            keywords.add(keyword)
          }
        })
      }
    })
  }
  
  return Array.from(keywords).slice(0, 10) // 最多返回 10 個關鍵字
}

export default function ImageSearch({
  topicId,
  topic,
  content,
  onImageSelect,
  onClose,
}: ImageSearchProps) {
  const queryClient = useQueryClient()
  const [keywords, setKeywords] = useState('')
  const [source, setSource] = useState<'unsplash' | 'pexels' | 'pixabay' | undefined>()
  const [page, setPage] = useState(1)
  const limit = 20
  
  // 提取建議的關鍵字
  const suggestedKeywords = useMemo(() => {
    return extractKeywords(topic, content)
  }, [topic, content])
  
  // 當打開對話框時，如果有建議關鍵字，自動填入第一個
  useEffect(() => {
    if (suggestedKeywords.length > 0 && !keywords) {
      setKeywords(suggestedKeywords[0])
    }
  }, [suggestedKeywords])

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
      queryClient.invalidateQueries({ queryKey: ['images', topicId] })
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

      {/* 建議關鍵字 */}
      {suggestedKeywords.length > 0 && (
        <div className="mb-4">
          <p className="text-sm text-gray-600 mb-2">建議關鍵字（從內容中提取）：</p>
          <div className="flex flex-wrap gap-2">
            {suggestedKeywords.map((keyword, index) => (
              <button
                key={index}
                type="button"
                onClick={() => {
                  setKeywords(keyword)
                  setPage(1)
                }}
                className={`px-3 py-1 text-sm rounded-full border transition-colors ${
                  keywords === keyword
                    ? 'bg-primary text-white border-primary'
                    : 'bg-white text-gray-700 border-gray-300 hover:border-primary hover:text-primary'
                }`}
              >
                {keyword}
              </button>
            ))}
          </div>
        </div>
      )}

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
