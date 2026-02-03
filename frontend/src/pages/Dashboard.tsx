import { useState, useEffect, useRef, useMemo } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { topicsAPI, api, schedulesAPI, recommendationsAPI } from '@/api/client'
import ProgressCard from '@/components/ui/ProgressCard'
import TopicCard from '@/components/ui/TopicCard'
import Calendar from '@/components/features/Calendar'
import TodayTopics from '@/components/features/TodayTopics'
import UpcomingEvents from '@/components/features/UpcomingEvents'
import RecentActivities from '@/components/features/RecentActivities'
import ConnectionErrorDisplay from '@/components/ui/ConnectionErrorDisplay'
import toast from 'react-hot-toast'
import { usePageTitle } from '@/hooks/usePageTitle'

export default function Dashboard() {
  usePageTitle()
  const [isGenerating, setIsGenerating] = useState(false)
  
  // 調試：檢查環境變數是否正確讀取（僅在首次掛載時執行）
  useEffect(() => {
    if (import.meta.env.PROD) {
      console.log('🔍 生產環境調試資訊：')
      console.log('  VITE_API_URL:', import.meta.env.VITE_API_URL || '未設置')
      console.log('  當前 API Base URL:', import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1')
      // 注意：不要清除緩存，這會導致重複請求
    }
  }, []) // 空依賴數組，確保只執行一次

  const {
    data: topicsResponse,
    isLoading: topicsLoading,
    error: topicsError,
    refetch: refetchTopics,
  } = useQuery({
    queryKey: ['topics'],
    queryFn: () => topicsAPI.getTopics({ limit: 30 }),
    retry: false, // 完全關閉自動重試，避免 429 錯誤循環
    staleTime: 30000, // 30 秒內認為數據新鮮
    gcTime: 5 * 60 * 1000, // 5 分鐘緩存
    refetchInterval: 5000, // 每 5 秒自動輪詢一次（降低頻率，避免觸發速率限制）
    refetchOnWindowFocus: false, // 避免視窗聚焦時自動重試
    refetchOnMount: true, // 組件掛載時獲取數據
  })

  const {
    isLoading: schedulesLoading,
    error: schedulesError,
    refetch: refetchSchedules,
  } = useQuery({
    queryKey: ['schedules'],
    queryFn: () => api.getSchedules(),
    retry: false, // 完全關閉自動重試，避免 429 錯誤循環
    staleTime: 30000, // 30 秒內認為數據新鮮
    gcTime: 5 * 60 * 1000, // 5 分鐘緩存
    refetchInterval: false, // 關閉自動輪詢，避免超時問題
    refetchOnWindowFocus: false, // 避免視窗聚焦時自動重試
    refetchOnMount: true, // 組件掛載時獲取數據
    // 增加超時時間到 15 秒
    meta: {
      timeout: 15000,
    },
  })

  // 取得推薦列表（暫時禁用，等待後端修復）
  const {
    data: recommendations,
  } = useQuery({
    queryKey: ['recommendations', 'user_default'],
    queryFn: () => recommendationsAPI.getRecommendations('user_default', { limit: 5 }),
    retry: 2,
    retryDelay: 1000,
    enabled: false, // 暫時禁用，避免 500 錯誤影響 Dashboard
  })

  const isLoading = topicsLoading || schedulesLoading
  const hasError = topicsError || schedulesError

  const handleRetry = () => {
    refetchTopics()
    refetchSchedules()
  }
  
  // 如果有連接錯誤，顯示錯誤訊息
  // 或者如果載入時間過長（超過 10 秒），也顯示錯誤提示
  const shouldShowError = hasError || (isLoading && (topicsError || schedulesError))

  // 從分頁響應中提取 topics 數組
  // 重要：如果有錯誤，不使用緩存數據，返回空數組
  const topics = (topicsError || schedulesError) ? [] : (topicsResponse?.data || [])
  
  // 計算今日主題數量（統一使用 UTC 日期比較）
  const getTodayTopicsCount = () => {
    const now = new Date()
    const todayUTC = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()))
    const today = todayUTC.toISOString().split('T')[0]
    
    return topics.filter((t) => {
      try {
        const dateValue = (t as any).generated_at || (t as any).generatedAt || 
                         (t as any).created_at || (t as any).createdAt
        if (!dateValue) return false
        
        let date: Date
        if (typeof dateValue === 'string') {
          date = new Date(dateValue)
        } else if (dateValue instanceof Date) {
          date = dateValue
        } else {
          date = new Date(dateValue)
        }
        
        if (isNaN(date.getTime())) return false
        
        const topicDateUTC = new Date(Date.UTC(
          date.getUTCFullYear(),
          date.getUTCMonth(),
          date.getUTCDate()
        ))
        const topicDate = topicDateUTC.toISOString().split('T')[0]
        return topicDate === today
      } catch {
        return false
      }
    }).length
  }
  
  const todayTopics = getTodayTopicsCount()

  // 生成今日主題的 mutation
  const generateTodayMutation = useMutation({
    mutationFn: (force: boolean) => schedulesAPI.generateTodayAllTopics(force),
    onMutate: () => {
      setIsGenerating(true)
      // 初始化進度狀態
      const currentCount = getTodayTopicsCount()
      setGenerationProgress({
        isGenerating: true,
        current: currentCount,
        total: 30,
        percentage: Math.round((currentCount / 30) * 100)
      })
      toast.loading('正在生成今日主題...', { id: 'generate-today' })
    },
    onSuccess: async (data) => {
      // 不立即設置 isGenerating 為 false，讓進度顯示繼續運行
      // setIsGenerating(false) 將在 useEffect 中根據主題數量自動更新
      toast.success(data.message || '今日主題生成任務已啟動', { id: 'generate-today' })
      
      // 立即刷新數據
      // React Query 的 refetchInterval 會自動處理後續的輪詢
      refetchTopics()
      refetchSchedules()
    },
    onError: (error: any) => {
      setIsGenerating(false)
      // 根據錯誤狀態碼顯示不同的錯誤訊息
      let errorMessage = '生成今日主題失敗'
      if (error?.status === 400) {
        // 400 錯誤：通常是資料庫未連接
        errorMessage = error?.message || '資料庫未連接，無法生成主題'
        if (error?.details?.suggestion) {
          errorMessage = `${errorMessage}\n${error.details.suggestion}`
        }
      } else if (error?.status === 500) {
        // 500 錯誤：系統內部錯誤
        errorMessage = error?.message || '伺服器內部錯誤，請查看後端日誌'
      } else {
        errorMessage = error?.message || '生成今日主題失敗'
      }
      toast.error(errorMessage, { id: 'generate-today', duration: 5000 })
    },
  })

  const handleGenerateToday = () => {
    if (isGenerating) return
    generateTodayMutation.mutate(false)
  }

  // 刪除今日主題的 mutation
  const deleteTodayMutation = useMutation({
    mutationFn: () => topicsAPI.deleteTodayTopics(),
    onSuccess: async (data) => {
      toast.success(`已刪除 ${data.deleted_count} 個今日主題`, { id: 'delete-today' })
      // 立即刷新數據
      refetchTopics()
      refetchSchedules()
    },
    onError: (error: any) => {
      const errorMessage = error?.message || '刪除今日主題失敗'
      toast.error(errorMessage, { id: 'delete-today', duration: 5000 })
    },
  })

  const handleDeleteToday = () => {
    if (!confirm('確定要刪除所有今日生成的主題嗎？此操作無法復原。')) {
      return
    }
    deleteTodayMutation.mutate()
  }
  
  // Debug: Log topic data (development only)
  useEffect(() => {
    if (!import.meta.env.PROD && topics.length > 0) {
      const today = new Date().toISOString().split('T')[0]
      console.log('📊 Topic Data Debug:')
      console.log(`  Total topics: ${topics.length}`)
      console.log(`  Today's date: ${today}`)
      console.log('  First 3 topics date info:', topics.slice(0, 3).map(t => {
        const dateValue = (t as any).generated_at || (t as any).generatedAt || 
                         (t as any).created_at || (t as any).createdAt
        let parsedDate = null
        let topicDate = null
        if (dateValue) {
          try {
            parsedDate = new Date(dateValue)
            topicDate = parsedDate.toISOString().split('T')[0]
          } catch (e) {
            // ignore
          }
        }
        return {
          id: t.id,
          title: t.title,
          generated_at: (t as any).generated_at,
          generatedAt: (t as any).generatedAt,
          created_at: (t as any).created_at,
          createdAt: (t as any).createdAt,
          parsedDate: parsedDate?.toISOString(),
          topicDate: topicDate,
          isToday: topicDate === today
        }
      }))
    }
  }, [topics])

  // 監聽今日主題數量，顯示進度和完成提示
  // 使用 useRef 避免重複顯示 toast 和無限循環
  const hasShownCompleteToast = useRef(false)
  const previousTopicsCountRef = useRef(0)
  const [generationProgress, setGenerationProgress] = useState<{
    isGenerating: boolean
    current: number
    total: number
    percentage: number
  }>({
    isGenerating: false,
    current: 0,
    total: 30,
    percentage: 0
  })
  
  // 計算今日主題數量（使用 useMemo 避免重複計算）
  const todayTopicsCount = useMemo(() => getTodayTopicsCount(), [topics])
  
  // Debug: Log detailed date comparison (development only) - 只在 topics 變化時執行
  useEffect(() => {
    if (!import.meta.env.PROD && topics.length > 0) {
      const now = new Date()
      const todayUTC = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()))
      const today = todayUTC.toISOString().split('T')[0]
      
      console.log('='.repeat(60))
      console.log('📊 Date Filtering Debug:')
      console.log(`  Total topics: ${topics.length}`)
      console.log(`  Today's date (UTC): ${today}`)
      console.log(`  Today's topics count: ${todayTopicsCount}`)
      console.log('='.repeat(60))
      
      // 詳細調試信息（所有主題，但只顯示前5個）
      topics.slice(0, 5).forEach((t, index) => {
        try {
          const dateValue = (t as any).generated_at || (t as any).generatedAt || 
                           (t as any).created_at || (t as any).createdAt
          if (!dateValue) {
            console.warn(`❌ Topic ${index + 1} missing date field:`, t.id, t.title)
            return
          }
          
          let date: Date
          if (typeof dateValue === 'string') {
            date = new Date(dateValue)
          } else if (dateValue instanceof Date) {
            date = dateValue
          } else {
            date = new Date(dateValue)
          }
          
          if (isNaN(date.getTime())) {
            console.warn(`❌ Topic ${index + 1} date invalid:`, t.id, dateValue)
            return
          }
          
          const topicDateUTC = new Date(Date.UTC(
            date.getUTCFullYear(),
            date.getUTCMonth(),
            date.getUTCDate()
          ))
          const topicDate = topicDateUTC.toISOString().split('T')[0]
          const isToday = topicDate === today
          
          console.log(`🔍 Topic ${index + 1} (${t.id.substring(0, 20)}...):`, {
            title: t.title,
            dateValue,
            parsedDate: date.toISOString(),
            topicDateUTC: topicDateUTC.toISOString(),
            topicDate,
            today,
            isToday: isToday ? '✅ YES' : '❌ NO'
          })
        } catch (error) {
          console.warn(`❌ Error processing topic ${index + 1}:`, error, t)
        }
      })
      
      console.log('='.repeat(60))
      console.log(`✅ Final result: ${todayTopicsCount} today's topics out of ${topics.length} total`)
      console.log('='.repeat(60))
    }
  }, [topics, todayTopicsCount]) // 只在 topics 或 todayTopicsCount 變化時執行
  
  // 更新進度狀態（避免無限循環）
  useEffect(() => {
    // 只在主題數量或生成狀態真正變化時更新
    const currentCount = todayTopicsCount
    const previousCount = previousTopicsCountRef.current
    
    // 如果數量沒有變化且生成狀態沒有變化，跳過更新
    if (currentCount === previousCount && 
        generationProgress.isGenerating === isGenerating &&
        generationProgress.current === currentCount) {
      return
    }
    
    // 更新 ref
    previousTopicsCountRef.current = currentCount
    
    // 計算百分比
    const percentage = Math.round((currentCount / 30) * 100)
    
    // 判斷是否應該顯示「正在生成中」
    const shouldShowGenerating = isGenerating || 
      (currentCount > 0 && currentCount < 30 && currentCount >= previousCount)
    
    // 更新進度狀態（只在真正需要時更新）
    if (currentCount === 0 && !isGenerating) {
      if (generationProgress.isGenerating || generationProgress.current > 0) {
        setGenerationProgress({
          isGenerating: false,
          current: 0,
          total: 30,
          percentage: 0
        })
      }
    } else {
      // 只在狀態真正需要改變時更新
      if (generationProgress.isGenerating !== shouldShowGenerating ||
          generationProgress.current !== currentCount ||
          generationProgress.percentage !== percentage) {
        setGenerationProgress({
          isGenerating: shouldShowGenerating,
          current: currentCount,
          total: 30,
          percentage
        })
      }
    }

    // 如果達到30個主題，顯示完成提示（只顯示一次）
    if (currentCount >= 30 && !hasShownCompleteToast.current) {
      hasShownCompleteToast.current = true
      setIsGenerating(false)
      setGenerationProgress(prev => ({ ...prev, isGenerating: false }))
      toast.success('今日主題生成完成！', { id: 'generate-today-complete' })
    } else if (currentCount < 30) {
      // 重置標記，如果主題數量減少
      hasShownCompleteToast.current = false
      if (currentCount === 0 && !isGenerating) {
        setIsGenerating(false)
      }
    }
  }, [todayTopicsCount, isGenerating]) // 只依賴 todayTopicsCount 和 isGenerating，不依賴 topics

  // 計算統計資料
  const pendingCount = topics.filter((t) => t.status === 'pending').length
  const confirmedCount = topics.filter((t) => t.status === 'confirmed').length
  const totalTopics = topics.length
  // todayTopics 已在上面定義，使用統一的計算邏輯

  return (
    <div className="p-4 sm:p-6">
      {/* 錯誤警告（如果有連接錯誤） */}
      {shouldShowError && (
        <div className="mb-4">
          <ConnectionErrorDisplay 
            error={topicsError || schedulesError || new Error('無法連接到後端服務')} 
            onRetry={handleRetry} 
          />
        </div>
      )}
      
      {/* 速率限制警告 */}
      {(topicsError as any)?.status === 429 || (schedulesError as any)?.status === 429 ? (
        <div className="mb-4 bg-orange-50 border border-orange-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <div className="flex-1">
              <h3 className="font-semibold text-orange-800 mb-1">
                ⚠️ 請求過於頻繁
              </h3>
              <p className="text-sm text-orange-700 mb-3">
                後端服務限制了請求頻率，請稍後再試。
                {(topicsError as any)?.details?.retryAfter && (
                  <span className="block mt-1">
                    建議等待 {(topicsError as any).details.retryAfter} 秒後再試。
                  </span>
                )}
              </p>
              <button
                onClick={handleRetry}
                className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors text-sm"
              >
                重試
              </button>
            </div>
          </div>
        </div>
      ) : null}
      
      {/* 載入超時提示 */}
      {isLoading && !hasError && (
        <div className="mb-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-sm text-yellow-800">
            ⚠️ 載入時間較長，請檢查後端服務是否正常運行
          </p>
          <button
            onClick={handleRetry}
            className="mt-2 text-sm text-yellow-700 hover:text-yellow-900 underline"
          >
            重試
          </button>
        </div>
      )}
      
      {/* 生成進度提示 */}
      {generationProgress.isGenerating && (
        <div className="mb-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
              <h3 className="font-semibold text-blue-800">
                正在生成今日主題...
              </h3>
            </div>
            <span className="text-sm text-blue-600 font-medium">
              {generationProgress.current}/{generationProgress.total}
            </span>
          </div>
          <div className="w-full bg-blue-100 rounded-full h-2.5 mb-2">
            <div 
              className="bg-blue-600 h-2.5 rounded-full transition-all duration-500"
              style={{ width: `${generationProgress.percentage}%` }}
            ></div>
          </div>
          <p className="text-xs text-blue-600">
            {generationProgress.percentage < 33 
              ? '🔄 正在生成時尚趨勢主題（0-10個）...' 
              : generationProgress.percentage < 66
              ? '🔄 正在生成美食推薦主題（10-20個）...'
              : '🔄 正在生成社會趨勢主題（20-30個）...'}
          </p>
        </div>
      )}
      
      {/* 進度卡片區 - 六個功能並列 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2 mb-6">
        <div className="relative">
          <ProgressCard
            title="今日主題"
            value={`${todayTopics}/30`}
            percentage={Math.round((todayTopics / 30) * 100)}
            message={todayTopics >= 30 ? "已完成！" : "好的開始！"}
            color="orange"
          />
          <div className="absolute bottom-1 right-1 flex gap-1 z-10">
            {/* 調試：顯示 todayTopics 值（開發環境） */}
            {!import.meta.env.PROD && (
              <span className="text-[8px] text-gray-400 px-1">
                {todayTopics}
              </span>
            )}
            {/* 如果有主題數據，顯示刪除按鈕（不依賴 todayTopics，因為日期過濾可能有問題） */}
            {topics.length > 0 && (
              <button
                onClick={handleDeleteToday}
                disabled={deleteTodayMutation.isPending}
                className="px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
                title={`刪除今日主題（當前：${todayTopics}個）`}
              >
                {deleteTodayMutation.isPending ? '刪除中...' : '🗑️ 刪除'}
              </button>
            )}
            {todayTopics < 30 && (
              <button
                onClick={handleGenerateToday}
                disabled={isGenerating}
                className="px-2 py-1 text-xs bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
                title="立即生成"
              >
                {isGenerating ? '生成中...' : '立即生成'}
              </button>
            )}
          </div>
        </div>
        <ProgressCard
          title="待審核"
          value={`${pendingCount}/${totalTopics}`}
          percentage={totalTopics > 0 ? Math.round((pendingCount / totalTopics) * 100) : 0}
          message="進度良好！"
          color="primary"
        />
        <ProgressCard
          title="已確認"
          value={`${confirmedCount}/${totalTopics}`}
          percentage={totalTopics > 0 ? Math.round((confirmedCount / totalTopics) * 100) : 0}
          message="繼續保持！"
          color="secondary"
        />
        <ProgressCard
          title="內容評分"
          value={topics.length > 0 ? `${Math.round(topics.reduce((sum, t) => sum + (t.wordCount || 0), 0) / topics.length)}/100` : "0/100"}
          percentage={topics.length > 0 ? Math.min(100, Math.round(topics.reduce((sum, t) => sum + (t.wordCount || 0), 0) / topics.length)) : 0}
          message={topics.length > 0 ? "不錯的進展！" : "等待數據..."}
          color="green"
        />
        <UpcomingEvents />
        <RecentActivities />
      </div>

      {/* 中間區域：日曆 + 主題列表 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <Calendar />
        <TodayTopics topics={topics} />
      </div>

      {/* 底部區域：主題卡片 + 右側資訊欄 */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* 主題卡片網格 - 顯示所有今日主題 */}
        <div className="lg:col-span-8">
          {isLoading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
              <p className="mt-4 text-gray-500">載入中...</p>
            </div>
          ) : (
            <>
              <h3 className="text-lg font-bold text-gray-800 mb-4">主題卡片</h3>
              {(() => {
                // 顯示主題：優先今日 → 最近 → 全部
                const now = new Date()
                const todayUTC = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()))
                const today = todayUTC.toISOString().split('T')[0]
                
                // 先嘗試獲取今日主題
                const todayTopicsList = topics.filter((t) => {
                  try {
                    const dateValue = (t as any).generated_at || (t as any).generatedAt || 
                                     (t as any).created_at || (t as any).createdAt
                    if (!dateValue) return false
                    
                    let date: Date
                    if (typeof dateValue === 'string') {
                      date = new Date(dateValue)
                    } else if (dateValue instanceof Date) {
                      date = dateValue
                    } else {
                      date = new Date(dateValue)
                    }
                    
                    if (isNaN(date.getTime())) return false
                    
                    const topicDateUTC = new Date(Date.UTC(
                      date.getUTCFullYear(),
                      date.getUTCMonth(),
                      date.getUTCDate()
                    ))
                    const topicDate = topicDateUTC.toISOString().split('T')[0]
                    return topicDate === today
                  } catch {
                    return false
                  }
                })
                
                // 決定顯示哪些主題
                let displayTopics = todayTopicsList
                let displayTitle = '今日熱門主題'
                let showNotice = false
                
                if (todayTopicsList.length === 0) {
                  // 沒有今日主題，顯示所有主題（按日期排序）
                  displayTopics = [...topics].sort((a, b) => {
                    const dateA = (a as any).generated_at || (a as any).generatedAt || 
                                 (a as any).created_at || (a as any).createdAt
                    const dateB = (b as any).generated_at || (b as any).generatedAt || 
                                 (b as any).created_at || (b as any).createdAt
                    if (!dateA || !dateB) return 0
                    return new Date(dateB).getTime() - new Date(dateA).getTime()
                  })
                  displayTitle = '最新熱門主題'
                  showNotice = true
                }
                
                // 如果完全沒有主題，顯示 Agent 收集中
                if (displayTopics.length === 0) {
                  return (
                    <div className="text-center py-16 bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl">
                      <div className="inline-flex items-center justify-center w-20 h-20 bg-white rounded-full shadow-lg mb-6">
                        <svg className="w-10 h-10 text-blue-500 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                        </svg>
                      </div>
                      <h4 className="text-xl font-semibold text-gray-800 mb-3">🤖 AI Agent 正在收集熱門話題</h4>
                      <p className="text-gray-500 mb-2">系統每 6 小時自動更新三大類別主題</p>
                      <p className="text-gray-400 text-sm">時尚趨勢 · 美食推薦 · 社會趨勢</p>
                      <div className="mt-6 flex justify-center gap-2">
                        <span className="inline-block w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                        <span className="inline-block w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                        <span className="inline-block w-2 h-2 bg-pink-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                      </div>
                    </div>
                  )
                }
                
                // 按分類分組
                const categories = [
                  { key: 'fashion', label: '時尚趨勢', color: 'purple' },
                  { key: 'food', label: '美食推薦', color: 'orange' },
                  { key: 'trend', label: '社會趨勢', color: 'green' }
                ]
                
                const topicsByCategory = categories.map(cat => ({
                  ...cat,
                  topics: displayTopics.filter(t => t.category === cat.key)
                }))
                
                return (
                  <>
                    <div className="flex items-center justify-between mb-4">
                      <p className="text-sm text-gray-600">{displayTitle}（共 {displayTopics.length} 個）</p>
                      {showNotice && (
                        <span className="text-xs text-amber-600 bg-amber-50 px-2 py-1 rounded">
                          🤖 Agent 將於下次更新時收集今日主題
                        </span>
                      )}
                    </div>
                    <div className="space-y-6">
                      {topicsByCategory.map((category) => (
                        <div key={category.key}>
                          <div className="flex items-center justify-between mb-3">
                            <h4 className="text-base font-semibold text-gray-800">
                              {category.label}
                            </h4>
                            <span className="text-sm text-gray-500">
                              {category.topics.length} 個主題
                            </span>
                          </div>
                          {category.topics.length > 0 ? (
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                              {category.topics.map((topic) => (
                                <div key={topic.id} className="h-full">
                                  <TopicCard topic={topic} />
                                </div>
                              ))}
                            </div>
                          ) : (
                            <div className="text-center py-6 text-gray-400 text-sm bg-gray-50 rounded-lg">
                              🤖 Agent 正在收集 {category.label}...
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </>
                )
              })()}
            </>
          )}
        </div>

        {/* 右側資訊欄 */}
        <div className="lg:col-span-4 space-y-6">
          {/* 推薦主題 */}
          {recommendations && recommendations.recommendations.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="font-bold text-gray-800 mb-4">為您推薦</h3>
              <div className="space-y-3">
                {recommendations.recommendations.slice(0, 3).map((rec) => (
                  <div
                    key={rec.id}
                    className="p-3 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="font-semibold text-gray-800 text-sm mb-1">{rec.keyword}</p>
                        <p className="text-xs text-gray-600 mb-2">{rec.reason}</p>
                        <div className="flex items-center gap-2">
                          <span className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded text-xs">
                            {rec.category}
                          </span>
                          <span className="text-xs text-gray-500">
                            信心度: {Math.round(rec.confidence_score * 100)}%
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

