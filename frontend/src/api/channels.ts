/**
 * 頻道 API
 * Phase 3: 內容功能
 */
import { fetchAPI, fetchAPIWithPagination } from './client';
import { convertTopic } from './topics';
import type { Topic } from '@/types';
import type { PaginatedResponse } from './topics';

// 類型定義
export interface ChannelFeedEntry {
  name: string;
  url: string;
  role: string;
}

export interface Channel {
  id: string;
  user_id: string;
  name: string;
  category: ChannelCategory;
  region: ChannelRegion;
  custom_keywords: string[];
  description?: string;
  selected_feeds?: ChannelFeedEntry[];
  status: 'active' | 'paused' | 'deleted';
  topic_count: number;
  last_collected_at?: string;
  collection_status: 'idle' | 'collecting' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
}

export type ChannelCategory =
  | 'fashion'
  | 'food'
  | 'trend'
  | 'finance'
  | 'sports'
  | 'tech'
  | 'entertainment'
  | 'other';

export type ChannelRegion =
  | 'hong_kong'
  | 'taiwan'
  | 'japan'
  | 'korea'
  | 'china'
  | 'usa'
  | 'uk'
  | 'global';

export interface ChannelCreateRequest {
  name: string;
  category: ChannelCategory;
  region?: ChannelRegion;
  custom_keywords?: string[];
  description?: string;
  /** Step 2 選取之來源（≤10）；省略或空陣列表示使用後端預設 RSS 池 */
  selected_feeds?: ChannelFeedEntry[];
}

export interface ChannelUpdateRequest {
  name?: string;
  custom_keywords?: string[];
  description?: string;
  status?: 'active' | 'paused';
}

export interface ChannelListResponse {
  channels: Channel[];
  total: number;
  max_channels: number;
}

export interface CategoryOption {
  value: ChannelCategory;
  label: string;
}

export interface RegionOption {
  value: ChannelRegion;
  label: string;
}

// API 函數
export const channelsApi = {
  /**
   * 取得我的頻道列表
   */
  getMyChannels: async (): Promise<ChannelListResponse> => {
    return fetchAPI<ChannelListResponse>('/channels');
  },

  /**
   * 建立頻道
   */
  createChannel: async (data: ChannelCreateRequest): Promise<Channel> => {
    return fetchAPI<Channel>('/channels', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * 取得單一頻道
   */
  getChannel: async (channelId: string): Promise<Channel> => {
    return fetchAPI<Channel>(`/channels/${channelId}`);
  },

  /**
   * 更新頻道
   */
  updateChannel: async (channelId: string, data: ChannelUpdateRequest): Promise<Channel> => {
    return fetchAPI<Channel>(`/channels/${channelId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /**
   * 刪除頻道
   */
  deleteChannel: async (channelId: string): Promise<{ message: string }> => {
    return fetchAPI<{ message: string }>(`/channels/${channelId}`, {
      method: 'DELETE',
    });
  },

  /**
   * 取得可用類別
   */
  getCategories: async (): Promise<{ categories: CategoryOption[] }> => {
    return fetchAPI<{ categories: CategoryOption[] }>('/channels/categories');
  },

  /**
   * 取得可用地區
   */
  getRegions: async (): Promise<{ regions: RegionOption[] }> => {
    return fetchAPI<{ regions: RegionOption[] }>('/channels/regions');
  },

  /**
   * 建立頻道 Step 2：該類別＋地區之系統預設 RSS 候選（需登入）
   */
  getDefaultRssSources: async (
    category: ChannelCategory,
    region: ChannelRegion
  ): Promise<{ sources: ChannelFeedEntry[] }> => {
    const q = new URLSearchParams({ category, region });
    return fetchAPI<{ sources: ChannelFeedEntry[] }>(
      `/channels/defaults/rss-sources?${q.toString()}`
    );
  },

  /**
   * 取得頻道 RSS 來源
   */
  getChannelSources: async (channelId: string): Promise<any> => {
    return fetchAPI(`/channels/${channelId}/sources`);
  },

  /**
   * 手動觸發頻道收集
   */
  triggerCollection: async (channelId: string): Promise<any> => {
    return fetchAPI(`/channels/${channelId}/collect`, {
      method: 'POST',
    });
  },

  /**
   * 取得頻道底下已寫入資料庫的主題（依 channel_id，非僅統計數字）
   */
  getChannelTopics: async (
    channelId: string,
    page: number = 1,
    limit: number = 50
  ): Promise<PaginatedResponse<Topic>> => {
    const params = new URLSearchParams({
      page: String(page),
      limit: String(limit),
    });
    const response = await fetchAPIWithPagination<any>(
      `/channels/${channelId}/topics?${params.toString()}`
    );
    const pagination = response.pagination || {
      page,
      limit,
      total: response.data.length,
      totalPages: Math.ceil(response.data.length / limit) || 0,
    };
    const total = pagination.total ?? response.data.length;
    const pageLimit = pagination.limit ?? limit;
    const computedPages =
      Math.ceil(total / pageLimit) || 0;

    return {
      data: response.data.map(convertTopic),
      pagination: {
        page: pagination.page ?? page,
        limit: pageLimit,
        total,
        totalPages:
          pagination.totalPages ??
          pagination.total_pages ??
          computedPages,
      },
    };
  },

  /**
   * AI 頻道助手 - 解析用戶自然語言輸入
   * @param conversationHistory 先前對話（由舊到新，不含本次 userInput）
   */
  assistChannel: async (
    userInput: string,
    language: string = 'zh-TW',
    conversationHistory: { role: 'user' | 'assistant'; content: string }[] = [],
    excludeUrls: string[] = []
  ): Promise<{
    category: string | null;
    region: string | null;
    keywords: string[];
    confidence: number;
    clarification_needed: boolean;
    clarification_question: string | null;
    recommended_sources: Array<{ name: string; url: string; role: string }>;
    suggested_channel_name: string | null;
    suggested_channel_description: string | null;
  }> => {
    return fetchAPI('/channels/assist', {
      method: 'POST',
      body: JSON.stringify({
        user_input: userInput,
        language,
        conversation_history: conversationHistory,
        exclude_urls: excludeUrls.slice(0, 50),
      }),
      skipErrorHandler: true,
    });
  },

  /**
   * 驗證使用者貼上之 Feed URL（SSRF 防護 + RSS 粗判）
   */
  validateFeedUrl: async (
    url: string
  ): Promise<{
    valid: boolean;
    title: string | null;
    suggested_name: string | null;
    error_code: string | null;
  }> => {
    return fetchAPI('/channels/feeds/validate', {
      method: 'POST',
      body: JSON.stringify({ url: url.trim() }),
    });
  },

  /**
   * 建立頻道精靈：後端結構化選項（檢索 MVP＝站內 RSS 白名單）
   * @see docs/channel_create_ai_guided_spec.md
   */
  getAssistWizardOptions: async (params: {
    step: 1 | 2 | 3;
    category?: ChannelCategory;
    region?: ChannelRegion;
    excludeUrls?: string[];
    language?: string;
    customKeywords?: string[];
  }): Promise<{
    step: number;
    retrieval_mvp: string;
    quick_options: Array<{ kind: 'category' | 'region'; value: string; label_key: string }>;
    feed_options: Array<{ kind: 'feed'; name: string; url: string; role: string }>;
    suggested_channel_name: string | null;
    suggested_channel_description: string | null;
  }> => {
    return fetchAPI('/channels/assist/wizard-options', {
      method: 'POST',
      body: JSON.stringify({
        step: params.step,
        category: params.category,
        region: params.region,
        exclude_urls: params.excludeUrls ?? [],
        language: params.language ?? 'zh-TW',
        custom_keywords: params.customKeywords ?? [],
      }),
      skipErrorHandler: true,
    });
  },

  /**
   * 站內 RSS 白名單關鍵字搜尋
   */
  searchWhitelistFeeds: async (
    q: string,
    limit: number = 30
  ): Promise<{
    query: string;
    results: Array<{ name: string; url: string; role: string; category: string; region: string }>;
  }> => {
    const params = new URLSearchParams({ q: q.trim(), limit: String(limit) });
    return fetchAPI(`/channels/feeds/search?${params.toString()}`);
  },
};

// 類別 i18n 鍵映射（使用 t() 渲染）
export const categoryI18nKeys: Record<ChannelCategory, string> = {
  fashion: 'channels.category.fashion',
  food: 'channels.category.food',
  trend: 'channels.category.trend',
  finance: 'channels.category.finance',
  sports: 'channels.category.sports',
  tech: 'channels.category.tech',
  entertainment: 'channels.category.entertainment',
  other: 'channels.category.other',
};

// 地區 i18n 鍵映射（使用 t() 渲染）
export const regionI18nKeys: Record<ChannelRegion, string> = {
  hong_kong: 'channels.region.hong_kong',
  taiwan: 'channels.region.taiwan',
  japan: 'channels.region.japan',
  korea: 'channels.region.korea',
  china: 'channels.region.china',
  usa: 'channels.region.usa',
  uk: 'channels.region.uk',
  global: 'channels.region.global',
};

// 類別圖標映射
export const categoryIcons: Record<ChannelCategory, string> = {
  fashion: '👗',
  food: '🍽️',
  trend: '📈',
  finance: '💰',
  sports: '⚽',
  tech: '💻',
  entertainment: '🎬',
  other: '📝',
};

