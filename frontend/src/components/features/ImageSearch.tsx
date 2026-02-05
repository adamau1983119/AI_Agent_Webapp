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
import { useTranslation } from '@/i18n'

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
 * 從內容中提取關鍵字（改進版：提取簡潔、適合搜尋的關鍵字）
 */
function extractKeywords(topic: Topic | null | undefined, content: Content | null | undefined): string[] {
  const keywords: Set<string> = new Set()
  
  // 停用詞列表（移除這些詞以獲得更好的搜尋結果）
  const stopWords = new Set([
    '對我而言', '他', '她', '它', '的', '是', '在', '有', '和', '與', '及', '或',
    '近乎', '傳奇', '回憶', '巨匠', '大師', '設計師', '時尚', '品牌',
    '大', '必', '吃', '平民', '美食', '推薦', '介紹', '分享', '體驗',
    '一個', '一種', '這個', '那個', '這些', '那些'
  ])
  
  // 從主題標題提取關鍵字
  if (topic?.title) {
    const title = topic.title.trim()
    
    // 1. 提取英文專有名詞（大寫字母開頭的單詞）
    const englishNames = title.match(/\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b/g)
    if (englishNames) {
      englishNames.forEach(name => {
        const cleanName = name.trim()
        // 只保留長度適中的專有名詞（2-50字符）
        if (cleanName.length >= 2 && cleanName.length <= 50) {
          keywords.add(cleanName)
        }
      })
    }
    
    // 2. 提取簡潔的中文關鍵字（移除停用詞）
    let chineseText = title
      .replace(/[A-Za-z0-9]/g, ' ') // 移除英文和數字
      .replace(/[、，,。！？：；]/g, ' ') // 移除標點
      .split(/\s+/)
      .filter(w => w.length > 0)
    
    // 提取2-4字的中文詞組（適合圖片搜尋）
    chineseText.forEach((word, index) => {
      // 單個詞（2-4字）
      if (word.length >= 2 && word.length <= 4 && !stopWords.has(word)) {
        keywords.add(word)
      }
      // 兩個詞的組合（2+2字或2+3字）
      if (index < chineseText.length - 1) {
        const nextWord = chineseText[index + 1]
        if (word.length >= 2 && nextWord.length >= 2 && 
            word.length + nextWord.length <= 6 &&
            !stopWords.has(word) && !stopWords.has(nextWord)) {
          keywords.add(word + ' ' + nextWord)
        }
      }
    })
    
    // 3. 如果標題較短，直接使用簡化版本
    if (title.length <= 30 && keywords.size === 0) {
      const simplified = title
        .replace(/[對我而言他近乎傳奇回憶巨匠大師設計師時尚品牌]/g, '')
        .trim()
      if (simplified.length >= 2 && simplified.length <= 30) {
        keywords.add(simplified)
      }
    }
  }
  
  // 從文章內容提取關鍵字
  if (content?.article) {
    const article = content.article
    
    // 提取英文專有名詞
    const articleEnglishNames = article.match(/\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b/g)
    if (articleEnglishNames) {
      articleEnglishNames.forEach(name => {
        const cleanName = name.trim()
        if (cleanName.length >= 2 && cleanName.length <= 50) {
          keywords.add(cleanName)
        }
      })
    }
    
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
          if (keyword.length >= 2 && keyword.length <= 10) {
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
          if (keyword.length >= 2 && keyword.length <= 20) {
            keywords.add(keyword)
          }
        })
      }
    })
  }
  
  // 按長度排序，優先返回簡潔的關鍵字（更適合圖片搜尋）
  const sortedKeywords = Array.from(keywords)
    .filter(k => k.length >= 2 && k.length <= 50) // 過濾太長或太短的關鍵字
    .sort((a, b) => {
      // 優先返回：1. 英文專有名詞 2. 較短的關鍵字
      const aIsEnglish = /^[A-Z]/.test(a)
      const bIsEnglish = /^[A-Z]/.test(b)
      if (aIsEnglish && !bIsEnglish) return -1
      if (!aIsEnglish && bIsEnglish) return 1
      return a.length - b.length
    })
    .slice(0, 8) // 最多返回 8 個關鍵字
  
  return sortedKeywords
}

export default function ImageSearch({
  topicId,
  topic,
  content,
  onImageSelect,
  onClose,
}: ImageSearchProps) {
  const { t } = useTranslation()
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
      showSuccess(t('common.success'))
      onImageSelect({
        url: '',
        source: '',
        license: '',
      })
    },
    onError: (error) => {
      showError(t('common.failed'))
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
        <h2 className="text-xl font-bold text-gray-800">{t('images.searchTitle')}</h2>
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
          <p className="text-sm text-gray-600 mb-2">{t('images.suggestedKeywords')}</p>
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
            placeholder={t('images.searchPlaceholder')}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            aria-label={t('images.searchTitle')}
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
            aria-label={t('images.sourceLabel')}
          >
            <option value="">{t('images.allSources')}</option>
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
            {t('common.search')}
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
          {t('images.diagnosticMode')}
        </label>
      </div>

      {/* 搜尋結果 */}
      {isLoading ? (
        <LoadingSpinner />
      ) : error ? (
        <ErrorDisplay error={error} onRetry={() => refetch()} />
      ) : searchResults.length === 0 && keywords ? (
        <div>
          <EmptyState message={t('images.noResults')} description={t('images.tryDifferentKeywords')} />
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
