import { Link } from 'react-router-dom'
import type { Topic } from '@/types'
import { API_BASE_URL } from '@/api/client'
import { useTranslation } from '@/i18n'

/**
 * 生成圖片代理 URL（如果需要）
 */
function getProxyImageUrl(imageUrl: string): string {
  if (!imageUrl) return ''
  // 如果 URL 已經是代理 URL 或是相對路徑，直接返回
  if (imageUrl.includes('/images/proxy') || imageUrl.startsWith('/')) return imageUrl
  // 如果是完整 URL，使用代理
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
    return `${API_BASE_URL}/images/proxy?url=${encodeURIComponent(imageUrl)}`
  }
  return imageUrl
}

interface TopicCardProps {
  topic: Topic
}

const gradientClasses = {
  fashion: 'from-purple-400 to-blue-400',
  food: 'from-orange-400 to-pink-400',
  trend: 'from-green-400 to-blue-400',
}

export default function TopicCard({ topic }: TopicCardProps) {
  const { t } = useTranslation()
  // 從 topic 數據計算進度
  const contentProgress = (topic.wordCount || 0) > 0 ? Math.min(100, ((topic.wordCount || 0) / 500) * 100) : 0
  const imageProgress = (topic.imageCount || 0) >= 8 ? 100 : Math.min(100, ((topic.imageCount || 0) / 8) * 100)
  
  // 階段 1：優先使用預覽圖片，如果沒有則使用漸層背景
  // 同時支持 previewImages（前端格式）和 preview_images（後端格式）
  const previewImages = (topic as any).previewImages || (topic as any).preview_images || []
  const previewImage = Array.isArray(previewImages) && previewImages.length > 0 
    ? previewImages[0] 
    : null
  const isExpanded = topic.isExpanded || false
  
  // 調試：開發環境下顯示圖片信息
  if (!import.meta.env.PROD && previewImage) {
    console.log(`📷 TopicCard [${topic.id.substring(0, 20)}...]:`, {
      title: topic.title,
      previewImage,
      previewImagesCount: previewImages.length,
      imageCount: topic.imageCount
    })
  }

  return (
    <Link to={`/topics/${topic.id}`} className="block h-full">
      <div className="bg-white rounded-lg shadow overflow-hidden hover:shadow-lg transition-shadow p-3 md:p-4 h-full min-h-[140px] flex flex-col">
        {/* 標題區域：包含左上角圖片和標題 */}
        <div className="flex items-start gap-3 mb-2 md:mb-3">
          {/* 左上角：小圖片圖標 */}
          <div className="flex-shrink-0">
            {previewImage ? (
              <div className="relative w-12 h-12 md:w-16 md:h-16 rounded overflow-hidden bg-gray-100">
                <img 
                  src={getProxyImageUrl(previewImage)} 
                  alt={topic.title}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    // 如果圖片載入失敗，顯示漸層背景
                    e.currentTarget.style.display = 'none'
                    e.currentTarget.parentElement!.className = `relative w-12 h-12 md:w-16 md:h-16 rounded overflow-hidden bg-gradient-to-br ${gradientClasses[topic.category]}`
                  }}
                />
              </div>
            ) : (
              <div className={`w-12 h-12 md:w-16 md:h-16 rounded bg-gradient-to-br ${gradientClasses[topic.category]}`}></div>
            )}
          </div>
          
          {/* 標題 */}
          <div className="flex-1 min-w-0">
            <h3 className="font-bold text-sm md:text-base lg:text-lg line-clamp-2 leading-tight">{topic.title}</h3>
          </div>
        </div>
        
        {/* 內容區域：主要顯示文字內容 */}
        <div className="flex-1 flex flex-col justify-between min-h-0">
          <div className="flex-1 min-h-0">
            {/* 30字內容撮要 - 始終顯示 */}
            <div className="mb-3 md:mb-4">
              <p className="text-xs md:text-sm text-gray-600 line-clamp-2 leading-snug">
                {topic.description ? (
                  topic.description
                ) : (
                  <span className="text-gray-400 italic">{t('topics.noContent')}</span>
                )}
              </p>
            </div>
            
            {/* 進度條 */}
            <div className="space-y-1.5 md:space-y-2">
              <div>
                <div className="flex justify-between text-xs mb-0.5 md:mb-1">
                  <span className="text-gray-600">{t('topics.contentProgress')}</span>
                  <span className="font-semibold">{contentProgress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-1.5">
                  <div
                    className="bg-primary h-1.5 rounded-full transition-all"
                    style={{ width: `${contentProgress}%` }}
                  ></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs mb-0.5 md:mb-1">
                  <span className="text-gray-600">{t('topics.imageProgress')}</span>
                  <span className="font-semibold">{imageProgress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-1.5">
                  <div
                    className="bg-secondary h-1.5 rounded-full transition-all"
                    style={{ width: `${imageProgress}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
          
          {/* 展開按鈕 */}
          <button className="text-primary hover:text-primary-dark font-medium text-xs md:text-sm mt-3 md:mt-4 self-start">
            {t('common.viewDetails')} →
          </button>
        </div>
      </div>
    </Link>
  )
}

