// 主題類型
export interface Topic {
  id: string
  title: string
  category: 'fashion' | 'food' | 'trend'
  status: 'pending' | 'confirmed' | 'deleted'
  source: string
  generatedAt?: string  // 可選，後端可能使用 generated_at
  generated_at?: string  // 後端格式
  createdAt?: string  // 可選，後端可能使用 created_at
  created_at?: string  // 後端格式
  updatedAt?: string
  updated_at?: string  // 後端格式
  imageCount?: number
  wordCount?: number
  // 階段 1 新增欄位
  previewImages?: string[]  // 預覽圖片 URL 列表（前端格式）
  preview_images?: string[]  // 預覽圖片 URL 列表（後端格式）
  isExpanded?: boolean      // 是否已展開
  description?: string      // 主題內容摘要（約30字）
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

// 圖片來源類型
export type ImageSource = 
  | 'unsplash'
  | 'pexels'
  | 'pixabay'
  | 'google_custom_search'
  | 'duckduckgo'

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

