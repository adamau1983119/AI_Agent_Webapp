/**
 * 使用者內容偏好 API（主題權重／關鍵字）
 * 對齊 backend GET/PUT /api/v1/user/preferences
 */

import { fetchAPI } from './client'

export interface UserPreferencesData {
  id: string
  fashion_weight: number
  food_weight: number
  trend_weight: number
  keywords: string[]
  excluded_keywords: string[]
  source_preferences?: {
    fashion: string[]
    food: string[]
    trend: string[]
  }
  updated_at?: string
}

export interface UserPreferencesUpdate {
  fashion_weight?: number
  food_weight?: number
  trend_weight?: number
  keywords?: string[]
  excluded_keywords?: string[]
}

export const userPreferencesAPI = {
  getPreferences: async (): Promise<UserPreferencesData> => {
    return fetchAPI<UserPreferencesData>('/user/preferences')
  },

  updatePreferences: async (data: UserPreferencesUpdate): Promise<UserPreferencesData> => {
    return fetchAPI<UserPreferencesData>('/user/preferences', {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },
}
