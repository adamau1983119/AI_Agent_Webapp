import React from 'react'
import type { Schedule, Topic } from '@/types'
import { getProxyUrl } from '@/utils/imageProxy'

interface TodayTopicsProps {
  schedules?: Schedule[]  // 可選，目前未使用
  topics: Topic[]
}

export default function TodayTopics({ topics }: TodayTopicsProps) {
  // 分類配置
  const categories = [
    { 
      key: 'fashion', 
      label: '時尚趨勢', 
      timeSlot: '07:00',
    },
    { 
      key: 'food', 
      label: '美食推薦', 
      timeSlot: '12:00',
    },
    { 
      key: 'trend', 
      label: '社會趨勢', 
      timeSlot: '18:00',
    },
  ]

  // 獲取今日主題（過濾今天的）
  // 使用 useMemo 優化性能，避免每次渲染都重新計算
  const todayTopics = React.useMemo(() => {
    // 使用 UTC 日期進行比較，確保與後端一致
    const now = new Date()
    const todayUTC = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()))
    const today = todayUTC.toISOString().split('T')[0]
    
    const filtered = topics.filter((t) => {
      try {
        // 優先使用 generated_at（後端實際返回的字段），然後檢查其他可能的日期字段
        const dateValue = (t as any).generated_at || (t as any).generatedAt || 
                         (t as any).created_at || (t as any).createdAt
        
        if (!dateValue) {
          if (!import.meta.env.PROD) {
            console.warn('TodayTopics: Topic missing date field:', t.id, t.title)
          }
          return false
        }
        
        // 處理日期：支持 ISO 字符串和 Date 對象
        let date: Date
        if (typeof dateValue === 'string') {
          date = new Date(dateValue)
        } else if (dateValue instanceof Date) {
          date = dateValue
        } else {
          date = new Date(dateValue)
        }
        
        if (isNaN(date.getTime())) {
          if (!import.meta.env.PROD) {
            console.warn('TodayTopics: Topic date invalid:', t.id, dateValue)
          }
          return false
        }
        
        // 使用 UTC 日期進行比較，避免時區問題
        // 將主題日期轉換為 UTC 日期（只取年月日）
        const topicDateUTC = new Date(Date.UTC(
          date.getUTCFullYear(),
          date.getUTCMonth(),
          date.getUTCDate()
        ))
        const topicDate = topicDateUTC.toISOString().split('T')[0]
        const isToday = topicDate === today
        
        return isToday
      } catch (error) {
        if (!import.meta.env.PROD) {
          console.warn('TodayTopics: Error processing topic date:', error, t)
        }
        return false
      }
    })
    
    // Debug info (development only)
    if (!import.meta.env.PROD && topics.length > 0) {
      console.log('📊 TodayTopics Debug:', {
        totalTopics: topics.length,
        todayTopicsCount: filtered.length,
        todayDate: today,
        first3TopicsDates: topics.slice(0, 3).map(t => {
          const dateValue = (t as any).generated_at || (t as any).generatedAt || 
                           (t as any).created_at || (t as any).createdAt
          if (!dateValue) return 'No date'
          try {
            const date = new Date(dateValue)
            return date.toISOString().split('T')[0]
          } catch {
            return 'Date parse failed'
          }
        })
      })
    }
    
    return filtered
  }, [topics])

  // 按分類分組主題
  const getTopicsByCategory = (category: string) => {
    return todayTopics
      .filter(t => t.category === category)
      .slice(0, 10) // 最多顯示 10 個
  }

  // 獲取主題的圖片（優先使用 previewImages，如果沒有則使用佔位圖）
  const getTopicImage = (topic: Topic) => {
    // 處理 null、undefined 和空數組的情況
    const previewImages = (topic as any).previewImages || (topic as any).preview_images
    // 確保 previewImages 是數組且不為 null
    const imageArray = Array.isArray(previewImages) && previewImages.length > 0 ? previewImages : []
    
    if (imageArray.length > 0 && imageArray[0]) {
      // 確保圖片 URL 是有效的
      const imageUrl = imageArray[0]
      if (typeof imageUrl === 'string' && imageUrl.trim().length > 0) {
        // ✅ 使用代理 URL 載入圖片，避免 CORS 問題
        return getProxyUrl(imageUrl)
      }
    }
    // 如果沒有圖片，返回佔位圖（使用更簡單的 URL）
    const titleText = topic.title ? topic.title.substring(0, 10).replace(/\s+/g, '') : 'NoImage'
    return `https://via.placeholder.com/120x80/e5e7eb/6b7280?text=${encodeURIComponent(titleText)}`
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="font-bold text-gray-800 mb-6 text-lg">今日主題</h3>
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
                  {topicsCount} 個主題
                </span>
              </div>
              
              {/* 主題列表 */}
              {categoryTopics.length > 0 ? (
                <div className="space-y-3">
                  {categoryTopics.map((topic) => {
                    const imageUrl = getTopicImage(topic)
                    const source = topic.source || '未知來源'
                    
                    return (
                      <div 
                        key={topic.id} 
                        className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer group"
                      >
                        {/* 圖片縮圖 */}
                        <div className="flex-shrink-0">
                          <div className="relative w-24 h-16 rounded overflow-hidden bg-gray-200 flex items-center justify-center">
                            <img 
                              src={imageUrl}
                              alt={topic.title || '主題圖片'}
                              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                              loading="lazy"
                              onError={(e) => {
                                // 圖片載入失敗時顯示佔位圖
                                const target = e.target as HTMLImageElement
                                const titleText = topic.title ? topic.title.substring(0, 10).replace(/\s+/g, '') : 'NoImage'
                                target.src = `https://via.placeholder.com/120x80/e5e7eb/6b7280?text=${encodeURIComponent(titleText)}`
                                target.onerror = null // 防止無限循環
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
                            {topic.title}
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
                <div className="text-center py-8 text-gray-400">
                  <p className="text-sm">尚未生成主題</p>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

