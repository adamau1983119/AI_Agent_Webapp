/**
 * 評分 API
 * Phase 4: AI 個人化
 */
import { fetchAPI } from './client';
import { RatingValue } from './styleProfile';

// 類型定義
export type RatingReason =
  | 'tone_good'
  | 'content_relevant'
  | 'creative'
  | 'professional'
  | 'engaging'
  | 'length_perfect'
  | 'tone_bad'
  | 'content_irrelevant'
  | 'too_generic'
  | 'too_long'
  | 'too_short'
  | 'boring'
  | 'inaccurate'
  | 'other';

export interface RatingCreateRequest {
  content_id: string;
  topic_id: string;
  value: RatingValue;
  reasons?: RatingReason[];
  comment?: string;
  content_format?: string;
  content_length?: number;
  topic_category?: string;
}

export interface Rating {
  id: string;
  user_id: string;
  content_id: string;
  topic_id: string;
  value: RatingValue;
  reasons: RatingReason[];
  comment?: string;
  content_format?: string;
  content_length?: number;
  topic_category?: string;
  created_at: string;
}

export interface RatingStats {
  total_ratings: number;
  positive_ratings: number;
  negative_ratings: number;
  positive_ratio: number;
  top_like_reasons: Array<{ reason: string; count: number }>;
  top_dislike_reasons: Array<{ reason: string; count: number }>;
  ratings_by_format: Record<string, { like: number; dislike: number }>;
  ratings_by_category: Record<string, { like: number; dislike: number }>;
}

export interface RatingReasonOption {
  value: RatingReason;
  label: string;
  sentiment: 'positive' | 'negative' | 'neutral';
}

// API 函數
export const ratingsApi = {
  /**
   * 提交評分
   */
  submitRating: async (data: RatingCreateRequest): Promise<Rating> => {
    return fetchAPI<Rating>('/ratings', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * 取得評分原因選項
   */
  getReasons: async (type?: 'like' | 'dislike'): Promise<{ reasons: RatingReasonOption[] }> => {
    const params = type ? `?rating_type=${type}` : '';
    return fetchAPI(`/ratings/reasons${params}`);
  },

  /**
   * 取得我的評分統計
   */
  getMyStats: async (): Promise<RatingStats> => {
    return fetchAPI<RatingStats>('/ratings/stats');
  },

  /**
   * 取得我的評分歷史
   */
  getMyHistory: async (page = 1, limit = 20): Promise<{ ratings: Rating[]; total: number; page: number; limit: number }> => {
    return fetchAPI(`/ratings/history?page=${page}&limit=${limit}`);
  },

  /**
   * 取得對特定內容的評分
   */
  getRatingForContent: async (contentId: string): Promise<{ rated: boolean; rating?: Rating }> => {
    return fetchAPI(`/ratings/content/${contentId}`);
  },
};

// 評分原因 i18n 鍵映射（使用 t() 渲染）
export const ratingReasonI18nKeys: Record<RatingReason, string> = {
  tone_good: 'rating.reason.tone_good',
  content_relevant: 'rating.reason.content_relevant',
  creative: 'rating.reason.creative',
  professional: 'rating.reason.professional',
  engaging: 'rating.reason.engaging',
  length_perfect: 'rating.reason.length_perfect',
  tone_bad: 'rating.reason.tone_bad',
  content_irrelevant: 'rating.reason.content_irrelevant',
  too_generic: 'rating.reason.too_generic',
  too_long: 'rating.reason.too_long',
  too_short: 'rating.reason.too_short',
  boring: 'rating.reason.boring',
  inaccurate: 'rating.reason.inaccurate',
  other: 'rating.reason.other',
};

// 正面原因
export const positiveReasons: RatingReason[] = [
  'tone_good',
  'content_relevant',
  'creative',
  'professional',
  'engaging',
  'length_perfect',
];

// 負面原因
export const negativeReasons: RatingReason[] = [
  'tone_bad',
  'content_irrelevant',
  'too_generic',
  'too_long',
  'too_short',
  'boring',
  'inaccurate',
];

