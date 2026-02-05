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
  getSuggestions: async (query: string): Promise<SearchSuggestionsResponse> => {
    return fetchAPI<SearchSuggestionsResponse>(`/inspiration/suggestions?q=${encodeURIComponent(query)}`);
  },
};

