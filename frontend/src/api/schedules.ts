/**
 * 排程相關 API
 */

import { fetchAPI, USE_MOCK, delay } from './client'
import { mockSchedules } from './mockData'
import type { Schedule } from '@/types'

/**
 * 排程 API
 */
export const schedulesAPI = {
  /**
   * 取得排程列表
   */
  getSchedules: async (date?: string): Promise<Schedule[]> => {
    if (USE_MOCK) {
      await delay(300)
      return mockSchedules
    }

    try {
      const params = date ? `?date=${date}` : ''
      const schedules = await fetchAPI<Schedule[]>(`/schedules${params}`)
      return schedules
    } catch (error) {
      console.error('Failed to fetch schedules, falling back to mock data', error)
      await delay(300)
      return mockSchedules
    }
  },

  /**
   * 手動觸發主題生成
   */
  manualGenerateTopics: async (
    category: 'fashion' | 'food' | 'trend',
    count: number = 3
  ): Promise<{ message: string; category: string; count: number }> => {
    if (USE_MOCK) {
      await delay(1000)
      return {
        message: '主題生成任務已啟動',
        category,
        count,
      }
    }

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
    if (USE_MOCK) {
      await delay(300)
      return { message: '排程服務已啟動', status: 'running' }
    }

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
    if (USE_MOCK) {
      await delay(300)
      return { message: '排程服務已停止', status: 'stopped' }
    }

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
    if (USE_MOCK) {
      await delay(300)
      return {
        status: 'running',
        jobs: [
          { id: 'fashion_topics_07:00', next_run_time: '2025-12-30T07:00:00Z' },
          { id: 'food_topics_12:00', next_run_time: '2025-12-30T12:00:00Z' },
          { id: 'trend_topics_18:00', next_run_time: '2025-12-30T18:00:00Z' },
        ],
      }
    }

    return await fetchAPI<{
      status: string
      jobs: Array<{ id: string; next_run_time: string | null }>
    }>('/schedules/status')
  },
}

