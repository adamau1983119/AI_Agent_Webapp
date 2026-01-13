/**
 * 圖片搜尋元件
 */

import { useState, useEffect, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { imagesAPI, API_BASE_URL } from '@/api/client'
import { showSuccess, showError } from '@/utils/toast'
import type { Topic, Content, ImageSource, Image } from '@/types'
import Pagination from '@/components/ui/Pagination'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import ErrorDisplay from '@/components/ui/ErrorDisplay'
import EmptyState from '@/components/ui/EmptyState'

/**
 * 生成圖片代理 URL
 */
function getProxyImageUrl(imageUrl: string): string {
  if (!imageUrl) return ''
  // 如果 URL 已經是代理 URL，直接返回
  if (imageUrl.includes('/images/proxy')) return imageUrl
  // 構建代理 URL
  return `${API_BASE_URL}/images/proxy?url=${encodeURIComponent(imageUrl)}`
}

/**
 * 占位符 SVG（用於圖片載入失敗時）
 */
const PlaceholderSVG = ({ className }: { className?: string }) => (
  <svg
    className={className || 'w-full h-full'}
    viewBox="0 0 400 400"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <rect width="400" height="400" fill="#F3F4F6" />
    <path
      d="M150 150L200 200L250 150L300 200V300H100V200L150 150Z"
      stroke="#9CA3AF"
      strokeWidth="2"
      fill="none"
    />
    <circle cx="150" cy="150" r="20" fill="#9CA3AF" />
    <text
      x="200"
      y="250"
      textAnchor="middle"
      fill="#9CA3AF"
      fontSize="16"
      fontFamily="Arial, sans-serif"
    >
      圖片無法載入
    </text>
  </svg>
)

interface ImageSearchProps {
  topicId: string
  topic?: Topic | null
  content?: Content | null
  onImageSelect: (image: { url: string; source: string; photographer?: string; license: string }) => void
  onClose: () => void
}

/**
 * 圖片項目組件（處理圖片加載狀態和錯誤）
 */
function ImageItem({
  image,
  diagnosticMode,
  onSelect,
  isPending,
}: {
  image: Image
  diagnosticMode: boolean
  onSelect: () => void
  isPending: boolean
}) {
  const [imageError, setImageError] = useState(false)
  const [imageLoading, setImageLoading] = useState(true)
  const [retryCount, setRetryCount] = useState(0)
  const maxRetries = 1 // 最多重試 1 次

  // 使用代理 URL
  const proxyUrl = useMemo(() => getProxyImageUrl(image.url), [image.url])

  const handleImageError = () => {
    setImageLoading(false)
    if (retryCount < maxRetries) {
      // 重試一次（可能是暫時的網路問題）
      setRetryCount(prev => prev + 1)
      setImageError(false)
      setImageLoading(true)
      // 強制重新載入
      const img = new Image()
      img.onload = () => {
        setImageLoading(false)
        setImageError(false)
      }
      img.onerror = () => {
        setImageError(true)
        setImageLoading(false)
        if (diagnosticMode) {
          console.error('圖片載入失敗（已重試）:', {
            id: image.id,
            originalUrl: image.url,
            proxyUrl: proxyUrl,
            source: image.source,
            retryCount: retryCount + 1
          })
        }
      }
      img.src = proxyUrl
    } else {
      setImageError(true)
      if (diagnosticMode) {
        console.error('圖片載入失敗:', {
          id: image.id,
          originalUrl: image.url,
          proxyUrl: proxyUrl,
          source: image.source,
          retryCount: retryCount + 1
        })
      }
    }
  }

  return (
    <div className="relative group aspect-square rounded-lg overflow-hidden bg-gray-100 cursor-pointer">
      {imageLoading && !imageError && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-200 z-10">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
        </div>
      )}
      {imageError ? (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-gray-200 p-2 z-10">
          {/* 占位符 SVG */}
          <div className="w-24 h-24 mb-2">
            <PlaceholderSVG />
          </div>
          <div className="text-xs text-gray-500 text-center mb-1 font-medium">
            ⚠️ 圖片無法載入
          </div>
          {diagnosticMode && (
            <>
              <div className="text-xs text-gray-400 text-center truncate w-full px-2" title={image.url}>
                原始 URL: {image.url.length > 40 ? `${image.url.substring(0, 40)}...` : image.url}
              </div>
              <div className="text-xs text-gray-400 text-center truncate w-full px-2 mt-1" title={proxyUrl}>
                代理 URL: {proxyUrl.length > 40 ? `${proxyUrl.substring(0, 40)}...` : proxyUrl}
              </div>
              <div className="text-xs text-gray-400 mt-1">
                可能原因: CORS 限制、URL 無效或伺服器錯誤
              </div>
            </>
          )}
          <button
            onClick={onSelect}
            disabled={isPending}
            className="mt-3 px-4 py-1.5 bg-primary text-white rounded text-xs font-medium hover:bg-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
          >
            {isPending ? '新增中...' : '仍可選擇'}
          </button>
        </div>
      ) : (
        <>
          <img
            src={proxyUrl}
            alt={image.id}
            className="w-full h-full object-cover"
            onLoad={() => {
              setImageLoading(false)
              setImageError(false)
            }}
            onError={handleImageError}
            loading="lazy"
          />
          <div className="absolute inset-0 bg-black/0 group-hover:bg-black/50 transition-all duration-200 flex items-center justify-center opacity-0 group-hover:opacity-100">
            <button
              onClick={onSelect}
              disabled={isPending}
              className="px-4 py-2 bg-white text-gray-800 rounded text-sm font-medium hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
            >
              {isPending ? '新增中...' : '選擇'}
            </button>
          </div>
          <div className="absolute bottom-0 left-0 right-0 bg-black/50 text-white text-xs p-2">
            {image.source}
          </div>
        </>
      )}
    </div>
  )
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
  const [source, setSource] = useState<ImageSource | undefined>()
  const [page, setPage] = useState(1)
  const [diagnosticMode, setDiagnosticMode] = useState(false) // 診斷模式開關
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
  const attempts = searchResponse?.attempts || []
  const usedSource = searchResponse?.source  // 重命名避免與狀態變數衝突
  const traceId = searchResponse?.trace_id

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
            aria-label="圖片搜尋關鍵字"
            autoComplete="off"
          />
          <select
            value={source || ''}
            onChange={(e) =>
              setSource(
                e.target.value ? (e.target.value as ImageSource) : undefined
              )
            }
            className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            aria-label="圖片來源選擇"
          >
            <option value="">所有來源</option>
            <option value="unsplash">Unsplash</option>
            <option value="pexels">Pexels</option>
            <option value="pixabay">Pixabay</option>
            <option value="google_custom_search">Google</option>
            <option value="duckduckgo">DuckDuckGo</option>
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

      {/* 診斷模式開關 */}
      <div className="mb-4 flex items-center justify-between">
        <div className="text-sm text-gray-600">
          {usedSource && (
            <span>使用來源: <strong>{usedSource}</strong></span>
          )}
          {traceId && diagnosticMode && (
            <span className="ml-4">追蹤 ID: <code className="text-xs bg-gray-100 px-1 rounded">{traceId}</code></span>
          )}
        </div>
        <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
          <input
            type="checkbox"
            checked={diagnosticMode}
            onChange={(e) => setDiagnosticMode(e.target.checked)}
            className="rounded"
          />
          診斷模式
        </label>
      </div>

      {/* 搜尋結果 */}
      {isLoading ? (
        <LoadingSpinner />
      ) : error ? (
        <ErrorDisplay error={error} onRetry={() => refetch()} />
      ) : searchResults.length === 0 && keywords ? (
        <div>
          <EmptyState message="沒有找到圖片" description="嘗試使用不同的關鍵字" />
          {/* 顯示 attempts 資訊 */}
          {attempts.length > 0 && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <h4 className="text-sm font-semibold text-gray-700 mb-2">搜尋嘗試記錄：</h4>
              <ul className="space-y-2">
                {attempts.map((attempt: any, idx: number) => (
                  <li key={idx} className="text-sm text-gray-600">
                    <span className="font-medium">{attempt.source}:</span>{' '}
                    {attempt.status === 'success' && (
                      <span className="text-green-600">成功 ({attempt.count} 張)</span>
                    )}
                    {attempt.status === 'no_results' && (
                      <span className="text-yellow-600">無結果</span>
                    )}
                    {attempt.status === 'error' && (
                      <span className="text-red-600">
                        錯誤 ({attempt.code}): {attempt.message}
                        {diagnosticMode && attempt.details && (
                          <pre className="mt-1 text-xs bg-white p-2 rounded overflow-auto">
                            {JSON.stringify(attempt.details, null, 2)}
                          </pre>
                        )}
                      </span>
                    )}
                    {attempt.status === 'unavailable' && (
                      <span className="text-gray-500">不可用 ({attempt.message})</span>
                    )}
                    {attempt.status === 'exception' && (
                      <span className="text-red-600">
                        異常: {attempt.message}
                        {diagnosticMode && attempt.exception_type && (
                          <span className="ml-2 text-xs">({attempt.exception_type})</span>
                        )}
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-6">
            {searchResults.map((image) => (
              <ImageItem
                key={image.id}
                image={image}
                diagnosticMode={diagnosticMode}
                onSelect={() => handleSelectImage(image)}
                isPending={createMutation.isPending}
              />
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
