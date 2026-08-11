import React from 'react'
import type { Schedule, Topic } from '@/types'
import { getProxyUrl, IMAGE_PLACEHOLDER_DATA_URI } from '@/utils/imageProxy'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from '@/i18n'
import { filterTopicsForHktDay } from '@/lib/topicDayHkt'
import { resolveTopicDisplayCopy } from '@/lib/topicDisplay'

interface TodayTopicsProps {
  schedules?: Schedule[]  // 可選，目前未使用
  topics: Topic[]
}

export default function TodayTopics({ topics }: TodayTopicsProps) {
  const { t, language } = useTranslation()
  const navigate = useNavigate()
  
  // 分類配置
  const categories = [
    { 
      key: 'fashion', 
      label: t('filters.fashion'), 
      timeSlot: '07:00',
    },
    { 
      key: 'food', 
      label: t('filters.food'), 
      timeSlot: '12:00',
    },
    { 
      key: 'trend', 
      label: t('filters.trend'), 
      timeSlot: '18:00',
    },
  ]

  const displayTopics = React.useMemo(
    () => filterTopicsForHktDay(topics as Record<string, unknown>[]) as Topic[],
    [topics]
  )

  // 按分類分組主題
  const getTopicsByCategory = (category: string) => {
    return displayTopics
      .filter(t => t.category === category)
      .slice(0, 10) // 最多顯示 10 個
  }

  // 獲取主題的圖片
  const getTopicImage = (topic: Topic) => {
    const previewImages = (topic as any).previewImages || (topic as any).preview_images
    const imageArray = Array.isArray(previewImages) && previewImages.length > 0 ? previewImages : []
    
    if (imageArray.length > 0 && imageArray[0]) {
      const imageUrl = imageArray[0]
      if (typeof imageUrl === 'string' && imageUrl.trim().length > 0) {
        return getProxyUrl(imageUrl)
      }
    }
    return IMAGE_PLACEHOLDER_DATA_URI
  }

  // 處理點擊主題
  const handleTopicClick = (topicId: string) => {
    navigate(`/topics/${topicId}`)
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="font-bold text-gray-800 text-lg">
          {t('dashboard.todayTopics')}
        </h3>
      </div>
      
      {displayTopics.length === 0 ? (
        <div className="text-center py-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-50 rounded-full mb-4">
            <svg className="w-8 h-8 text-blue-500 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <p className="text-gray-600 font-medium mb-2">{t('dashboard.todayTopicsPreparing')}</p>
          <p className="text-gray-400 text-sm">{t('dashboard.nextCollectionHint')}</p>
        </div>
      ) : (
        <div className="space-y-8">
          {categories.map((category) => {
            const categoryTopics = getTopicsByCategory(category.key)
            const topicsCount = categoryTopics.length

            return (
              <div key={category.key}>
                {/* 分類標題 */}
                <div className="flex items-center justify-between mb-4 pb-2 border-b-2 border-gray-200">
                  <h4 className="font-bold text-gray-800 text-lg">
                    {category.label}
                  </h4>
                  <span className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                    {topicsCount} {t('channels.topics')}
                  </span>
                </div>
                
                {/* 主題列表 */}
                {categoryTopics.length > 0 ? (
                  <div className="space-y-3">
                    {categoryTopics.map((topic) => {
                      const imageUrl = getTopicImage(topic)
                      const source = topic.source || t('topics.source')
                      const display = resolveTopicDisplayCopy(topic, language)
                      
                      return (
                        <div 
                          key={topic.id} 
                          onClick={() => handleTopicClick(topic.id)}
                          className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer group"
                        >
                          {/* 圖片縮圖 */}
                          <div className="flex-shrink-0">
                            <div className="relative w-24 h-16 rounded overflow-hidden bg-gray-200 flex items-center justify-center">
                              <img 
                                src={imageUrl}
                                alt={topic.title || t('topics.image')}
                                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                                loading="lazy"
                                onError={(e) => {
                                  const target = e.target as HTMLImageElement
                                  target.src = IMAGE_PLACEHOLDER_DATA_URI
                                  target.onerror = null
                                }}
                              />
                            </div>
                          </div>
                          
                          {/* 標題和來源 */}
                          <div className="flex-1 min-w-0">
                            <h5 
                              className="font-semibold text-gray-800 text-sm leading-snug mb-1 group-hover:text-primary transition-colors"
                              style={{
                                display: '-webkit-box',
                                WebkitLineClamp: 2,
                                WebkitBoxOrient: 'vertical',
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                              }}
                            >
                              {display.title}
                            </h5>
                            <p className="text-xs text-gray-500 mt-1">
                              {source}
                            </p>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                ) : (
                  <div className="text-center py-6 text-gray-400 bg-gray-50 rounded-lg">
                    <p className="text-sm">{t('dashboard.collecting').replace('{category}', category.label)}</p>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
