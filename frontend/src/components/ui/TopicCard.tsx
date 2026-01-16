import { Link } from 'react-router-dom'
import type { Topic } from '@/types'
import { API_BASE_URL } from '@/api/client'

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
  // 從 topic 數據計算進度
  const contentProgress = topic.wordCount > 0 ? Math.min(100, (topic.wordCount / 500) * 100) : 0
  const imageProgress = topic.imageCount >= 8 ? 100 : Math.min(100, (topic.imageCount / 8) * 100)
  
  // 階段 1：優先使用預覽圖片，如果沒有則使用漸層背景
  const previewImage = topic.previewImages && topic.previewImages.length > 0 
    ? topic.previewImages[0] 
    : null
  const isExpanded = topic.isExpanded || false

  return (
    <Link to={`/topics/${topic.id}`}>
      <div className="bg-white rounded-lg shadow overflow-hidden hover:shadow-lg transition-shadow">
        {/* 階段 1：如果有預覽圖片則顯示，否則使用漸層背景 */}
        {previewImage ? (
          <div className="h-32 relative overflow-hidden">
            <img 
              src={getProxyImageUrl(previewImage)} 
              alt={topic.title}
              className="w-full h-full object-cover"
              onError={(e) => {
                // 如果圖片載入失敗，隱藏圖片顯示漸層背景
                e.currentTarget.style.display = 'none'
                e.currentTarget.parentElement!.className = `h-32 bg-gradient-to-br ${gradientClasses[topic.category]}`
              }}
            />
            {!isExpanded && (
              <div className="absolute top-2 right-2 bg-black/50 text-white text-xs px-2 py-1 rounded">
                預覽
              </div>
            )}
          </div>
        ) : (
          <div className={`h-32 bg-gradient-to-br ${gradientClasses[topic.category]}`}></div>
        )}
        <div className="p-4">
          <h3 className="font-bold text-lg mb-3">{topic.title}</h3>
          <div className="space-y-2 mb-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">內容完成度</span>
                <span className="font-semibold">{contentProgress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-primary h-2 rounded-full"
                  style={{ width: `${contentProgress}%` }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">圖片完成度</span>
                <span className="font-semibold">{imageProgress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-secondary h-2 rounded-full"
                  style={{ width: `${imageProgress}%` }}
                ></div>
              </div>
            </div>
          </div>
          <button className="text-primary hover:text-primary-dark font-medium text-sm">
            {isExpanded ? 'View details →' : '展開內容 →'}
          </button>
        </div>
      </div>
    </Link>
  )
}

