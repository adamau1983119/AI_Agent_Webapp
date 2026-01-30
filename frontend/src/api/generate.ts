/**
 * 內容生成 API
 * Phase 4: AI 個人化
 */
import { fetchAPI } from './client';
import { OutputFormat } from './styleProfile';

// 類型定義
export interface GenerateRequest {
  topic_id: string;
  title: string;
  summary?: string;
  category?: string;
  output_format?: OutputFormat;
  language?: string;
}

export interface GenerateResponse {
  content_id: string;
  topic_id: string;
  content: string;
  output_format: string;
  word_count: number;
  hashtags: string[];
  generation_time_ms: number;
}

export interface QuickGenerateResponse {
  content_id: string;
  content: string;
  output_format: string;
  word_count: number;
  hashtags: string[];
  generation_time_ms: number;
  personalized: boolean;
}

// API 函數
export const generateApi = {
  /**
   * 生成個人化內容
   */
  generate: async (data: GenerateRequest): Promise<GenerateResponse> => {
    return fetchAPI<GenerateResponse>('/generate', {
      method: 'POST',
      body: JSON.stringify({
        ...data,
        output_format: data.output_format || 'social_post',
        language: data.language || 'zh-TW',
      }),
    });
  },

  /**
   * 預覽生成 Prompt
   */
  previewPrompt: async (data: GenerateRequest): Promise<{
    prompt: string;
    output_format: string;
    language: string;
    style_profile_summary: {
      preset_style?: string;
      learning_stage?: string;
      confidence_score?: number;
    };
  }> => {
    return fetchAPI('/generate/preview', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * 快速生成
   */
  quickGenerate: async (
    title: string,
    format: OutputFormat = 'caption',
    language = 'zh-TW'
  ): Promise<QuickGenerateResponse> => {
    const params = new URLSearchParams({
      title,
      format,
      language,
    });
    return fetchAPI<QuickGenerateResponse>(`/generate/quick?${params.toString()}`);
  },
};

