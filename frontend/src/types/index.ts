// 主題類型
export interface Topic {
  id: string
  title: string
  category: 'fashion' | 'food' | 'trend'
  status: 'pending' | 'confirmed' | 'deleted'
  source: string
  generatedAt: string
  updatedAt: string
  imageCount: number
  wordCount: number
}

// 內容類型
export interface Content {
  id: string
  topicId: string
  article: string
  script: string
  wordCount: number
  estimatedDuration: number
  modelUsed: string
  version: number
}

// 圖片類型
export interface Image {
  id: string
  topicId: string
  url: string
  source: string
  photographer: string
  license: string
  order: number
}

// 使用者偏好類型
export interface UserPreferences {
  fashionWeight: number
  foodWeight: number
  trendWeight: number
  keywords: string[]
  excludedKeywords: string[]
}

// 排程類型
export interface Schedule {
  date: string
  timeSlot: string
  status: 'completed' | 'processing' | 'pending'
  topicsCount: number
  completedAt?: string
}

