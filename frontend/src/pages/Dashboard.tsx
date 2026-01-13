import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
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
  const queryClient = useQueryClient()
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
    queryFn: () => topicsAPI.getTopics(),
    retry: (failureCount, error: any) => {
      // 429 錯誤不重試，等待用戶手動重試
      if (error?.status === 429) {
        return false
      }
      // 其他錯誤最多重試 1 次
      return failureCount < 1
    },
    retryDelay: (attemptIndex) => {
      // 指數退避：2秒、4秒
      return Math.min(1000 * 2 ** attemptIndex, 4000)
    },
    staleTime: 30000, // 30 秒內認為數據新鮮
    gcTime: 5 * 60 * 1000, // 5 分鐘緩存
    enabled: true,
    refetchOnWindowFocus: false, // 避免視窗聚焦時自動重試
    refetchOnMount: false, // 避免組件掛載時自動重試
  })

  const {
    data: schedules = [],
    isLoading: schedulesLoading,
    error: schedulesError,
    refetch: refetchSchedules,
  } = useQuery({
    queryKey: ['schedules'],
    queryFn: () => api.getSchedules(),
    retry: (failureCount, error: any) => {
      // 429 錯誤不重試，等待用戶手動重試
      if (error?.status === 429) {
        return false
      }
      // 其他錯誤最多重試 1 次
      return failureCount < 1
    },
    retryDelay: (attemptIndex) => {
      // 指數退避：2秒、4秒
      return Math.min(1000 * 2 ** attemptIndex, 4000)
    },
    staleTime: 30000, // 30 秒內認為數據新鮮
    gcTime: 5 * 60 * 1000, // 5 分鐘緩存
    enabled: true,
    refetchOnWindowFocus: false, // 避免視窗聚焦時自動重試
    refetchOnMount: false, // 避免組件掛載時自動重試
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

  // 生成今日主題的 mutation
  const generateTodayMutation = useMutation({
    mutationFn: (force: boolean) => schedulesAPI.generateTodayAllTopics(force),
    onMutate: () => {
      setIsGenerating(true)
      toast.loading('正在生成今日主題...', { id: 'generate-today' })
    },
    onSuccess: (data) => {
      setIsGenerating(false)
      toast.success(data.message || '今日主題生成任務已啟動', { id: 'generate-today' })
      // 重新獲取數據
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ['topics'] })
        queryClient.invalidateQueries({ queryKey: ['schedules'] })
      }, 3000) // 3秒後刷新，給後端時間生成
    },
    onError: (error: any) => {
      setIsGenerating(false)
      toast.error(error?.message || '生成今日主題失敗', { id: 'generate-today' })
    },
  })

  const handleGenerateToday = () => {
    if (isGenerating) return
    generateTodayMutation.mutate(false)
  }

  // 從分頁響應中提取 topics 數組
  // 重要：如果有錯誤，不使用緩存數據，返回空數組
  const topics = (topicsError || schedulesError) ? [] : (topicsResponse?.data || [])

  // 計算統計資料
  const pendingCount = topics.filter((t) => t.status === 'pending').length
  const confirmedCount = topics.filter((t) => t.status === 'confirmed').length
  const totalTopics = topics.length
  const todayTopics = topics.filter((t) => {
    const today = new Date().toISOString().split('T')[0]
    return t.generatedAt?.startsWith(today) || false
  }).length

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
      
      {/* 進度卡片區 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2 mb-6">
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
        <div className="relative">
          <ProgressCard
            title="今日主題"
            value={`${todayTopics}/9`}
            percentage={Math.round((todayTopics / 9) * 100)}
            message={todayTopics >= 9 ? "已完成！" : "好的開始！"}
            color="orange"
          />
          {todayTopics < 9 && (
            <button
              onClick={handleGenerateToday}
              disabled={isGenerating}
              className="absolute top-1 right-1 px-1.5 py-0.5 text-[10px] bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isGenerating ? '生成中...' : '立即生成'}
            </button>
          )}
        </div>
      </div>

      {/* 中間區域：日曆 + 主題列表 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <Calendar />
        <TodayTopics schedules={schedules} />
      </div>

      {/* 底部區域：主題卡片 + 右側資訊欄 */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* 主題卡片網格 */}
        <div className="lg:col-span-8">
          {isLoading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
              <p className="mt-4 text-gray-500">載入中...</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {topics.slice(0, 3).map((topic) => (
                <TopicCard key={topic.id} topic={topic} />
              ))}
            </div>
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
          <UpcomingEvents />
          <RecentActivities />
        </div>
      </div>
    </div>
  )
}

