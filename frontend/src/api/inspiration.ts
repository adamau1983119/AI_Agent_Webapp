/**
 * 靈感策劃 API
 * Phase 3: 內容功能
 */
import { fetchAPI } from './client';

// 類型定義
export interface InspirationItem {
  title: string;
  description?: string;
  url?: string;
  source: string;
  image_url?: string;
  published_date?: string;
}

export interface InspirationSearchResponse {
  query: string;
  results: InspirationItem[];
  total: number;
}

export interface KeywordExtractionResponse {
  keywords: string[];
  count: number;
}

export interface TrendingTopicsResponse {
  category: string;
  region: string;
  topics: InspirationItem[];
  total: number;
}

export interface SearchSuggestionsResponse {
  query: string;
  suggestions: string[];
}

// API 函數
export const inspirationApi = {
  /**
   * 搜尋靈感
   */
  search: async (
    query: string,
    options?: {
      language?: string;
      limit?: number;
    }
  ): Promise<InspirationSearchResponse> => {
    const params = new URLSearchParams();
    params.set('q', query);
    if (options?.language) params.set('language', options.language);
    if (options?.limit) params.set('limit', options.limit.toString());
    
    return fetchAPI<InspirationSearchResponse>(`/inspiration/search?${params.toString()}`);
  },

  /**
   * 提取關鍵字
   */
  extractKeywords: async (
    text: string,
    options?: {
      language?: string;
      limit?: number;
    }
  ): Promise<KeywordExtractionResponse> => {
    const params = new URLSearchParams();
    if (options?.language) params.set('language', options.language);
    if (options?.limit) params.set('limit', options.limit.toString());
    
    return fetchAPI<KeywordExtractionResponse>(`/inspiration/extract-keywords?${params.toString()}`, {
      method: 'POST',
      body: JSON.stringify({ text }),
    });
  },

  /**
   * 取得熱門趨勢主題
   */
  getTrending: async (
    options?: {
      category?: string;
      region?: string;
      language?: string;
      limit?: number;
    }
  ): Promise<TrendingTopicsResponse> => {
    const params = new URLSearchParams();
    if (options?.category) params.set('category', options.category);
    if (options?.region) params.set('region', options.region);
    if (options?.language) params.set('language', options.language);
    if (options?.limit) params.set('limit', options.limit.toString());
    
    return fetchAPI<TrendingTopicsResponse>(`/inspiration/trending?${params.toString()}`);
  },

  /**
   * 取得搜尋建議
   */
  getSuggestions: async (query: string, language?: string): Promise<SearchSuggestionsResponse> => {
    const params = new URLSearchParams({ q: query });
    if (language) params.set('language', language);
    return fetchAPI<SearchSuggestionsResponse>(`/inspiration/suggestions?${params.toString()}`);
  },

  /**
   * AI 助手：開始對話
   */
  assistantStart: async (topic: string, language?: string): Promise<AssistantStartResponse> => {
    return fetchAPI<AssistantStartResponse>('/inspiration/assistant/start', {
      method: 'POST',
      body: JSON.stringify({ topic, language: language || 'zh-TW' }),
    });
  },

  /**
   * AI 助手：生成內容
   */
  assistantGenerate: async (sessionId: string, answers: Record<string, any>): Promise<AssistantGenerateResponse> => {
    return fetchAPI<AssistantGenerateResponse>('/inspiration/assistant/generate', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, answers }),
    });
  },

  /**
   * 取得偏好
   */
  getPreferences: async (): Promise<any> => {
    return fetchAPI<any>('/inspiration/preferences');
  },

  /**
   * 更新偏好
   */
  updatePreferences: async (preferences: Record<string, any>): Promise<any> => {
    return fetchAPI<any>('/inspiration/preferences', {
      method: 'PUT',
      body: JSON.stringify(preferences),
    });
  },
};

// AI 助手相關類型
export interface QuestionOption {
  question_id: string;
  question: string;
  type: string;
  options: string[];
  required: boolean;
}

export interface AssistantStartResponse {
  session_id: string;
  conversation_id: string;
  questions: QuestionOption[];
  preferences_applied?: Record<string, any>;
}

export interface AssistantGenerateResponse {
  state: string;
  content: string;
  verification_status?: {
    status: string;
    confidence: number;
    sources: Array<{
      url: string;
      credibility_score: number;
      verification_status: string;
    }>;
  };
  modules_included: string[];
  sources: Array<{
    url: string;
    title: string;
    type: string;
  }>;
}

