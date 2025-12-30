/**
 * 排程相關 API
 * 只使用真實後端 API，不使用 Mock 數據
 */

import { fetchAPI } from './client'
import type { Schedule } from '@/types'

/**
 * 排程 API
 */
export const schedulesAPI = {
  /**
   * 取得排程列表
   */
  getSchedules: async (date?: string): Promise<Schedule[]> => {
    const params = date ? `?date=${date}` : ''
    const schedules = await fetchAPI<Schedule[]>(`/schedules${params}`)
    return schedules
  },

  /**
   * 手動觸發主題生成
   */
  manualGenerateTopics: async (
    category: 'fashion' | 'food' | 'trend',
    count: number = 3
  ): Promise<{ message: string; category: string; count: number }> => {
    return await fetchAPI<{ message: string; category: string; count: number }>(
      '/schedules/generate',
      {
        method: 'POST',
        body: JSON.stringify({ category, count }),
      }
    )
  },

  /**
   * 啟動排程服務
   */
  startScheduler: async (): Promise<{ message: string; status: string }> => {
    return await fetchAPI<{ message: string; status: string }>(
      '/schedules/start',
      {
        method: 'POST',
      }
    )
  },

  /**
   * 停止排程服務
   */
  stopScheduler: async (): Promise<{ message: string; status: string }> => {
    return await fetchAPI<{ message: string; status: string }>(
      '/schedules/stop',
      {
        method: 'POST',
      }
    )
  },

  /**
   * 取得排程服務狀態
   */
  getSchedulerStatus: async (): Promise<{
    status: string
    jobs: Array<{ id: string; next_run_time: string | null }>
  }> => {
    return await fetchAPI<{
      status: string
      jobs: Array<{ id: string; next_run_time: string | null }>
    }>('/schedules/status')
  },

  /**
   * 立即生成今日所有主題
   */
  generateTodayAllTopics: async (force: boolean = false): Promise<{
    message: string
    categories: string[]
    expected_count: number
    existing_count: number
  }> => {
    return await fetchAPI<{
      message: string
      categories: string[]
      expected_count: number
      existing_count: number
    }>('/schedules/generate-today', {
      method: 'POST',
      body: JSON.stringify({ force: force }),
      headers: {
        'Content-Type': 'application/json',
      },
    })
  },
}
