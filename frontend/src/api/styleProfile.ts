/**
 * 風格檔案 API
 * Phase 4: AI 個人化
 */
import { fetchAPI } from './client';

// 類型定義
export type PresetStyle = 'professional' | 'casual' | 'humorous' | 'inspiring' | 'storytelling';
export type OutputFormat = 'full_article' | 'social_post' | 'caption' | 'script';
export type LearningStage = 'cold_start' | 'learning' | 'mature';
export type RatingValue = 'like' | 'dislike';

export interface TonePreference {
  formal_score: number;
  humor_score: number;
  emotion_score: number;
  directness_score: number;
}

export interface ContentPreference {
  preferred_length: string;
  use_emoji: boolean;
  use_hashtags: boolean;
  preferred_hashtag_count: number;
}

export interface TopicPreference {
  liked_topics: string[];
  disliked_topics: string[];
  liked_keywords: string[];
  disliked_keywords: string[];
}

export interface StyleProfile {
  id: string;
  user_id: string;
  preset_style: PresetStyle;
  tone: TonePreference;
  content: ContentPreference;
  topics: TopicPreference;
  learning_stage: LearningStage;
  total_ratings: number;
  positive_ratings: number;
  negative_ratings: number;
  confidence_score: number;
  last_updated_at: string;
  created_at: string;
}

export interface StyleAnalysis {
  user_id: string;
  learning_stage: LearningStage;
  learning_stage_label: string;
  confidence_score: number;
  total_ratings: number;
  positive_ratio: number;
  style_traits: string[];
  preset_style: PresetStyle;
  tone: TonePreference;
  content_preferences: ContentPreference;
  topic_preferences: TopicPreference;
  recommendations: string[];
  top_like_reasons: Array<{ reason: string; count: number }>;
  top_dislike_reasons: Array<{ reason: string; count: number }>;
}

export interface PresetStyleOption {
  value: PresetStyle;
  name: string;
  description: string;
}

export interface OutputFormatOption {
  value: OutputFormat;
  name: string;
  description: string;
  min_length: number;
  max_length: number;
}

// API 函數
export const styleProfileApi = {
  /**
   * 取得我的風格檔案
   */
  getMyProfile: async (): Promise<StyleProfile> => {
    return fetchAPI<StyleProfile>('/style-profile');
  },

  /**
   * 取得風格分析報告
   */
  getAnalysis: async (): Promise<StyleAnalysis> => {
    return fetchAPI<StyleAnalysis>('/style-profile/analysis');
  },

  /**
   * 設定預設風格
   */
  setPresetStyle: async (style: PresetStyle): Promise<{ message: string; profile: StyleProfile }> => {
    return fetchAPI(`/style-profile/preset-style?preset_style=${style}`, {
      method: 'PUT',
    });
  },

  /**
   * 重置風格檔案
   */
  reset: async (): Promise<{ message: string }> => {
    return fetchAPI('/style-profile/reset', {
      method: 'POST',
    });
  },

  /**
   * 取得可用的預設風格
   */
  getAvailableStyles: async (): Promise<{ styles: PresetStyleOption[] }> => {
    return fetchAPI('/style-profile/styles');
  },

  /**
   * 取得可用的輸出格式
   */
  getAvailableFormats: async (): Promise<{ formats: OutputFormatOption[] }> => {
    return fetchAPI('/style-profile/formats');
  },

  /**
   * 預覽風格配置
   */
  previewStyle: async (style: PresetStyle): Promise<any> => {
    return fetchAPI(`/style-profile/preview-style/${style}`);
  },

  /**
   * 預覽格式配置
   */
  previewFormat: async (format: OutputFormat): Promise<any> => {
    return fetchAPI(`/style-profile/preview-format/${format}`);
  },
};

// 預設風格標籤映射
export const presetStyleLabels: Record<PresetStyle, string> = {
  professional: '專業正式',
  casual: '輕鬆隨性',
  humorous: '幽默風趣',
  inspiring: '激勵人心',
  storytelling: '故事敘述',
};

// 輸出格式標籤映射
export const outputFormatLabels: Record<OutputFormat, string> = {
  full_article: '完整文章',
  social_post: '社交貼文',
  caption: 'Caption',
  script: '腳本',
};

// 學習階段標籤映射
export const learningStageLabels: Record<LearningStage, string> = {
  cold_start: '冷啟動',
  learning: '學習中',
  mature: '已成熟',
};

// 學習階段進度
export const getLearningProgress = (stage: LearningStage, totalRatings: number): number => {
  switch (stage) {
    case 'cold_start':
      return Math.min((totalRatings / 20) * 33, 33);
    case 'learning':
      return 33 + Math.min(((totalRatings - 20) / 80) * 33, 33);
    case 'mature':
      return 100;
    default:
      return 0;
  }
};

