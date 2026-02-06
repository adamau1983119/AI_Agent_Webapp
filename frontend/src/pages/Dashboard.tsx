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
import { useTranslation } from '@/i18n'

export default function Dashboard() {
  usePageTitle()
  const { t } = useTranslation()
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
      toast.loading(t('dashboard.generating'), { id: 'generate-today' })
    },
    onSuccess: async (data) => {
      // 不立即設置 isGenerating 為 false，讓進度顯示繼續運行
      // setIsGenerating(false) 將在 useEffect 中根據主題數量自動更新
      toast.success(data.message || t('dashboard.generateStarted'), { id: 'generate-today' })
      
      // 立即刷新數據
      // React Query 的 refetchInterval 會自動處理後續的輪詢
      refetchTopics()
      refetchSchedules()
    },
    onError: (error: any) => {
      setIsGenerating(false)
      // 根據錯誤狀態碼顯示不同的錯誤訊息
      let errorMessage = t('dashboard.generateFailed')
      if (error?.status === 400) {
        // 400 錯誤：通常是資料庫未連接
        errorMessage = error?.message || t('dashboard.dbNotConnected')
        if (error?.details?.suggestion) {
          errorMessage = `${errorMessage}\n${error.details.suggestion}`
        }
      } else if (error?.status === 500) {
        // 500 錯誤：系統內部錯誤
        errorMessage = error?.message || t('dashboard.serverError')
      } else {
        errorMessage = error?.message || t('dashboard.generateFailed')
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
      const errorMessage = error?.message || t('dashboard.deleteFailed')
      toast.error(errorMessage, { id: 'delete-today', duration: 5000 })
    },
  })

  const handleDeleteToday = () => {
    if (!confirm(t('dashboard.confirmDelete'))) {
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
      toast.success(t('dashboard.generateSuccess'), { id: 'generate-today-complete' })
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
    <div className="min-h-screen bg-[#FAF9F7] p-6 sm:p-8 font-sans">
      {/* 頁面標題 */}
      <div className="mb-8">
        <h1 className="text-2xl font-light tracking-[0.1em] text-black mb-2 uppercase">{t('nav.dashboard')}</h1>
        <div className="w-12 h-px bg-black"></div>
      </div>

      {/* 錯誤警告（如果有連接錯誤） */}
      {shouldShowError && (
        <div className="mb-6">
          <ConnectionErrorDisplay 
            error={topicsError || schedulesError || new Error(t('dashboard.cannotConnect'))} 
            onRetry={handleRetry} 
          />
        </div>
      )}
      
      {/* 速率限制警告 - Lane Crawford Style */}
      {(topicsError as any)?.status === 429 || (schedulesError as any)?.status === 429 ? (
        <div className="mb-6 bg-white border border-gray-200 p-6">
          <div className="flex items-start gap-4">
            <div className="flex-1">
              <h3 className="text-[11px] tracking-[0.15em] uppercase text-gray-800 mb-2">
                REQUEST LIMIT REACHED
              </h3>
              <p className="text-sm text-gray-500 font-light mb-4">
                後端服務限制了請求頻率，請稍後再試。
                {(topicsError as any)?.details?.retryAfter && (
                  <span className="block mt-1">
                    建議等待 {(topicsError as any).details.retryAfter} 秒後再試。
                  </span>
                )}
              </p>
              <button
                onClick={handleRetry}
                className="px-6 py-3 bg-black text-white text-[11px] tracking-[0.2em] uppercase hover:bg-gray-900 transition-colors"
              >
                RETRY
              </button>
            </div>
          </div>
        </div>
      ) : null}
      
      {/* 載入超時提示 - Lane Crawford Style */}
      {isLoading && !hasError && (
        <div className="mb-6 bg-white border border-gray-200 p-6">
          <p className="text-[11px] tracking-[0.1em] uppercase text-gray-600 mb-3">
            ⏳ LOADING — PLEASE WAIT
          </p>
          <button
            onClick={handleRetry}
            className="text-[10px] text-black underline hover:no-underline tracking-[0.1em] uppercase"
          >
            RETRY
          </button>
        </div>
      )}
      
      {/* 生成進度提示 - Lane Crawford Style */}
      {generationProgress.isGenerating && (
        <div className="mb-6 bg-white border border-black p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="animate-spin rounded-full h-4 w-4 border-b border-black"></div>
              <h3 className="text-[11px] tracking-[0.15em] uppercase text-black">
                GENERATING TOPICS
              </h3>
            </div>
            <span className="text-sm text-gray-600 font-light">
              {generationProgress.current}/{generationProgress.total}
            </span>
          </div>
          <div className="w-full h-px bg-gray-200 mb-3">
            <div 
              className="h-full bg-black transition-all duration-500"
              style={{ width: `${generationProgress.percentage}%` }}
            ></div>
          </div>
          <p className="text-[10px] text-gray-500 font-light tracking-wide">
            {generationProgress.percentage < 33 
              ? 'Generating fashion trends (0-10)...' 
              : generationProgress.percentage < 66
              ? 'Generating food recommendations (10-20)...'
              : 'Generating social trends (20-30)...'}
          </p>
        </div>
      )}
      
      {/* 統計卡片區 - Lane Crawford Style */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        {/* 今日主題卡片 - 特殊處理 */}
        <div className="relative bg-white border border-gray-100 p-4 hover:border-gray-300 transition-all">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-[10px] tracking-[0.15em] uppercase text-gray-500 font-light">
              TODAY'S TOPICS
            </h3>
            <span className="text-[10px] text-gray-400 font-light">
              {Math.round((todayTopics / 30) * 100)}%
            </span>
          </div>
          <div className="w-full h-px bg-gray-100 mb-3">
            <div 
              className="h-full bg-black transition-all duration-500"
              style={{ width: `${Math.round((todayTopics / 30) * 100)}%` }}
          />
          </div>
          <p className="text-xl font-light tracking-wide text-black mb-1">{todayTopics}/30</p>
          <p className="text-[10px] text-gray-400 font-light tracking-wide mb-3">
            {todayTopics >= 30 ? 'COMPLETED' : 'IN PROGRESS'}
          </p>
          
          {/* 操作按鈕 */}
          <div className="flex gap-2 mt-2">
            {topics.length > 0 && (
              <button
                data-testid="btn-dashboard-delete"
                onClick={handleDeleteToday}
                disabled={deleteTodayMutation.isPending}
                className="flex-1 py-1.5 text-[10px] tracking-[0.15em] uppercase border border-gray-200 text-gray-600 hover:border-black hover:text-black disabled:opacity-50 transition-all"
              >
                {deleteTodayMutation.isPending ? '...' : 'DELETE'}
              </button>
            )}
            {todayTopics < 30 && (
              <button
                data-testid="btn-dashboard-generate"
                onClick={handleGenerateToday}
                disabled={isGenerating}
                className="flex-1 py-1.5 text-[10px] tracking-[0.2em] uppercase bg-black text-white hover:bg-gray-900 disabled:bg-gray-300 transition-all"
              >
                {isGenerating ? '...' : 'GENERATE'}
              </button>
            )}
          </div>
        </div>

        <ProgressCard
          title="PENDING"
          value={`${pendingCount}/${totalTopics}`}
          percentage={totalTopics > 0 ? Math.round((pendingCount / totalTopics) * 100) : 0}
          message="REVIEWING"
        />
        <ProgressCard
          title="CONFIRMED"
          value={`${confirmedCount}/${totalTopics}`}
          percentage={totalTopics > 0 ? Math.round((confirmedCount / totalTopics) * 100) : 0}
          message="APPROVED"
        />
        <ProgressCard
          title="QUALITY"
          value={topics.length > 0 ? `${Math.round(topics.reduce((sum, t) => sum + (t.wordCount || 0), 0) / topics.length)}/100` : "0/100"}
          percentage={topics.length > 0 ? Math.min(100, Math.round(topics.reduce((sum, t) => sum + (t.wordCount || 0), 0) / topics.length)) : 0}
          message={topics.length > 0 ? "GOOD PROGRESS" : "AWAITING DATA"}
        />
        <UpcomingEvents />
        <RecentActivities />
      </div>

      {/* 快速操作區 - Lane Crawford Style */}
      <div className="mb-8">
        <h2 className="text-[11px] tracking-[0.15em] uppercase text-gray-500 mb-4">QUICK ACTIONS</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <a href="/topics" data-testid="link-dashboard-topics" className="group bg-white border border-gray-100 p-6 text-center hover:border-black transition-all">
            <div className="w-10 h-10 mx-auto mb-3 border border-gray-200 flex items-center justify-center group-hover:border-black transition-all">
              <svg className="w-5 h-5 text-gray-400 group-hover:text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
              </svg>
            </div>
            <p className="text-[10px] tracking-[0.15em] uppercase text-gray-600 group-hover:text-black">BROWSE TOPICS</p>
          </a>
          <a href="/channels" data-testid="link-dashboard-channels" className="group bg-white border border-gray-100 p-6 text-center hover:border-black transition-all">
            <div className="w-10 h-10 mx-auto mb-3 border border-gray-200 flex items-center justify-center group-hover:border-black transition-all">
              <svg className="w-5 h-5 text-gray-400 group-hover:text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M7 4V2m0 2v2m0-2H5m2 0h2m6 0V2m0 2v2m0-2h-2m2 0h2M5 8h14M5 12h14M5 16h14M5 20h14" />
              </svg>
            </div>
            <p className="text-[10px] tracking-[0.15em] uppercase text-gray-600 group-hover:text-black">MY CHANNELS</p>
          </a>
          <a href="/inspiration" data-testid="link-dashboard-inspiration" className="group bg-white border border-gray-100 p-6 text-center hover:border-black transition-all">
            <div className="w-10 h-10 mx-auto mb-3 border border-gray-200 flex items-center justify-center group-hover:border-black transition-all">
              <svg className="w-5 h-5 text-gray-400 group-hover:text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <p className="text-[10px] tracking-[0.15em] uppercase text-gray-600 group-hover:text-black">INSPIRATION</p>
          </a>
          <a href="/style-profile" data-testid="link-dashboard-style" className="group bg-white border border-gray-100 p-6 text-center hover:border-black transition-all">
            <div className="w-10 h-10 mx-auto mb-3 border border-gray-200 flex items-center justify-center group-hover:border-black transition-all">
              <svg className="w-5 h-5 text-gray-400 group-hover:text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <p className="text-[10px] tracking-[0.15em] uppercase text-gray-600 group-hover:text-black">STYLE PROFILE</p>
          </a>
        </div>
      </div>

      {/* 中間區域：日曆 + 主題列表 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <Calendar />
        <TodayTopics topics={topics} />
      </div>

      {/* 底部區域：主題卡片 + 右側資訊欄 */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* 主題卡片網格 - 顯示所有今日主題 */}
        <div className="lg:col-span-8">
          {isLoading ? (
            <div className="text-center py-16">
              <div className="inline-block animate-spin rounded-full h-6 w-6 border-b border-black"></div>
              <p className="mt-4 text-[11px] tracking-[0.1em] uppercase text-gray-500">LOADING...</p>
            </div>
          ) : (
            <>
              <h3 className="text-[11px] tracking-[0.15em] uppercase text-gray-500 mb-4">TOPIC CARDS</h3>
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
                let displayTitle = t('dashboard.todayTopics')
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
                  displayTitle = t('dashboard.latestTopics')
                  showNotice = true
                }
                
                // 如果完全沒有主題，顯示 Agent 收集中 - Lane Crawford Style
                if (displayTopics.length === 0) {
                  return (
                    <div className="text-center py-20 bg-white border border-gray-100">
                      <div className="inline-flex items-center justify-center w-16 h-16 border border-gray-200 mb-8">
                        <svg className="w-8 h-8 text-gray-400 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                        </svg>
                      </div>
                      <h4 className="text-sm tracking-[0.15em] uppercase text-black mb-4">AI AGENT COLLECTING</h4>
                      <div className="w-12 h-px bg-gray-300 mx-auto mb-4"></div>
                      <p className="text-gray-500 font-light text-sm mb-2">System updates every 6 hours</p>
                      <p className="text-[10px] tracking-[0.1em] uppercase text-gray-400">FASHION · FOOD · TRENDS</p>
                      <div className="mt-8 flex justify-center gap-3">
                        <span className="inline-block w-1.5 h-1.5 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                        <span className="inline-block w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                        <span className="inline-block w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                      </div>
                    </div>
                  )
                }
                
                // 按分類分組
                const categories = [
                  { key: 'fashion', label: 'FASHION TRENDS' },
                  { key: 'food', label: 'FOOD & DINING' },
                  { key: 'trend', label: 'SOCIAL TRENDS' }
                ]
                
                const topicsByCategory = categories.map(cat => ({
                  ...cat,
                  topics: displayTopics.filter(t => t.category === cat.key)
                }))
                
                return (
                  <>
                    <div className="flex items-center justify-between mb-6">
                      <p className="text-sm text-gray-500 font-light">{displayTitle} — {displayTopics.length} items</p>
                      {showNotice && (
                        <span className="text-[10px] tracking-[0.1em] uppercase text-gray-500 border border-gray-200 px-3 py-1">
                          NEXT UPDATE PENDING
                        </span>
                      )}
                    </div>
                    <div className="space-y-8">
                      {topicsByCategory.map((category) => (
                        <div key={category.key}>
                          <div className="flex items-center justify-between mb-4">
                            <h4 className="text-[11px] tracking-[0.15em] uppercase text-black">
                              {category.label}
                            </h4>
                            <span className="text-[10px] text-gray-400 font-light">
                              {category.topics.length} topics
                            </span>
                          </div>
                          {category.topics.length > 0 ? (
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                              {category.topics.map((topic) => (
                                <div key={topic.id} className="h-full">
                                  <TopicCard topic={topic} />
                                </div>
                              ))}
                            </div>
                          ) : (
                            <div className="text-center py-8 text-[10px] tracking-[0.1em] uppercase text-gray-400 bg-white border border-gray-100">
                              COLLECTING {category.label}...
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

        {/* 右側資訊欄 - Lane Crawford Style */}
        <div className="lg:col-span-4 space-y-6">
          {/* 推薦主題 */}
          {recommendations && recommendations.recommendations.length > 0 && (
            <div className="bg-white border border-gray-100 p-6">
              <h3 className="text-[11px] tracking-[0.15em] uppercase text-gray-500 mb-4">RECOMMENDED FOR YOU</h3>
              <div className="w-8 h-px bg-black mb-6"></div>
              <div className="space-y-4">
                {recommendations.recommendations.slice(0, 3).map((rec) => (
                  <div
                    key={rec.id}
                    className="p-4 border border-gray-100 hover:border-gray-300 transition-all"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="text-sm font-light text-black mb-2">{rec.keyword}</p>
                        <p className="text-[10px] text-gray-500 font-light mb-3">{rec.reason}</p>
                        <div className="flex items-center gap-3">
                          <span className="text-[9px] tracking-[0.1em] uppercase text-gray-600 border border-gray-200 px-2 py-0.5">
                            {rec.category}
                          </span>
                          <span className="text-[9px] text-gray-400">
                            {Math.round(rec.confidence_score * 100)}%
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

