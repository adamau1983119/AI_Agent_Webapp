/**
 * 頻道 API
 * Phase 3: 內容功能
 */
import { fetchAPI } from './client';

// 類型定義
export interface Channel {
  id: string;
  user_id: string;
  name: string;
  category: ChannelCategory;
  region: ChannelRegion;
  custom_keywords: string[];
  description?: string;
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
   * AI 頻道助手 - 解析用戶自然語言輸入
   */
  assistChannel: async (userInput: string, language: string = 'zh-TW'): Promise<{
    category: string | null;
    region: string | null;
    keywords: string[];
    confidence: number;
    clarification_needed: boolean;
    clarification_question: string | null;
    recommended_sources: Array<{ name: string; url: string; role: string }>;
  }> => {
    return fetchAPI('/channels/assist', {
      method: 'POST',
      body: JSON.stringify({ user_input: userInput, language }),
    });
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

