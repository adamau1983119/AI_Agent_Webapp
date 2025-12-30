import { useState } from 'react'
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

  const {
    data: topicsResponse,
    isLoading: topicsLoading,
    error: topicsError,
    refetch: refetchTopics,
  } = useQuery({
    queryKey: ['topics'],
    queryFn: () => topicsAPI.getTopics(),
    retry: 2,
    retryDelay: 1000,
    staleTime: 0, // 不使用過期緩存
    gcTime: 0, // 立即清除緩存（React Query v5）或 cacheTime: 0（v4）
    // 當有錯誤時，不使用緩存數據
    enabled: true,
  })

  const {
    data: schedules = [],
    isLoading: schedulesLoading,
    error: schedulesError,
    refetch: refetchSchedules,
  } = useQuery({
    queryKey: ['schedules'],
    queryFn: () => api.getSchedules(),
    retry: 2,
    retryDelay: 1000,
    staleTime: 0, // 不使用過期緩存
    gcTime: 0, // 立即清除緩存
    // 當有錯誤時，不使用緩存數據
    enabled: true,
  })

  // 取得推薦列表
  const {
    data: recommendations,
  } = useQuery({
    queryKey: ['recommendations', 'user_default'],
    queryFn: () => recommendationsAPI.getRecommendations('user_default', { limit: 5 }),
    retry: 2,
    retryDelay: 1000,
  })

  const isLoading = topicsLoading || schedulesLoading
  const hasError = topicsError || schedulesError

  const handleRetry = () => {
    refetchTopics()
    refetchSchedules()
  }

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
            error={topicsError || schedulesError || undefined} 
            onRetry={handleRetry} 
          />
        </div>
      )}
      
      {/* 進度卡片區 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
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
              className="absolute top-2 right-2 px-3 py-1 text-xs bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
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

