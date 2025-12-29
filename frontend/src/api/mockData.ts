import type { Topic, Content, Image, Schedule } from '@/types'

// Mock 主題資料
export const mockTopics: Topic[] = [
  // ⚠️ 已刪除錯誤的 Dior sample（見「錯誤修正記錄_Sample生成.md」）
  // ✅ 待 AI Agent 模組完成後，使用模組實際生成
  {
    id: 'topic_001',
    title: '2025 春夏時尚趨勢',
    category: 'fashion',
    status: 'pending',
    source: 'Vogue',
    generatedAt: '2025-12-19T07:00:00Z',
    updatedAt: '2025-12-19T07:00:00Z',
    imageCount: 8,
    wordCount: 485,
  },
  {
    id: 'topic_002',
    title: '台北必吃美食推薦',
    category: 'food',
    status: 'pending',
    source: 'CNN',
    generatedAt: '2025-12-19T12:00:00Z',
    updatedAt: '2025-12-19T12:00:00Z',
    imageCount: 8,
    wordCount: 420,
  },
  {
    id: 'topic_003',
    title: 'AI 技術發展趨勢',
    category: 'trend',
    status: 'confirmed',
    source: 'YouTube',
    generatedAt: '2025-12-19T18:00:00Z',
    updatedAt: '2025-12-19T18:00:00Z',
    imageCount: 8,
    wordCount: 500,
  },
]

// Mock 內容資料
export const mockContents: Record<string, Content> = {
  // ⚠️ 已刪除錯誤的 Dior sample（見「錯誤修正記錄_Sample生成.md」）
  // ✅ 待 AI Agent 模組完成後，使用模組實際生成
  topic_001: {
    id: 'content_001',
    topicId: 'topic_001',
    article: '2025 年春夏時尚趨勢展現了對可持續性和創新的關注...',
    script: '歡迎來到時尚趨勢分析。今天我們要探討 2025 年春夏的時尚趨勢...',
    wordCount: 485,
    estimatedDuration: 28,
    modelUsed: 'qwen-turbo',
    version: 1,
  },
}

// Mock 圖片資料
export const mockImages: Record<string, Image[]> = {
  // ⚠️ 已刪除錯誤的 Dior sample（見「錯誤修正記錄_Sample生成.md」）
  // ✅ 待圖片搜尋服務完成後，使用服務實際搜尋
  topic_001: [
    {
      id: 'image_001',
      topicId: 'topic_001',
      url: 'https://images.unsplash.com/photo-1445205170230-053b83016050',
      source: 'Unsplash',
      photographer: 'John Doe',
      license: 'Unsplash License',
      order: 1,
    },
  ],
}

// Mock 排程資料
export const mockSchedules: Schedule[] = [
  {
    date: '2025-12-19',
    timeSlot: '07:00',
    status: 'completed',
    topicsCount: 3,
    completedAt: '2025-12-19T07:15:00Z',
  },
  {
    date: '2025-12-19',
    timeSlot: '12:00',
    status: 'processing',
    topicsCount: 2,
  },
  {
    date: '2025-12-19',
    timeSlot: '18:00',
    status: 'pending',
    topicsCount: 0,
  },
]

