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

// 類別標籤映射
// 注意：這個映射現在應該使用 i18n，但為了向後兼容保留
// 實際使用時應該通過 i18n 系統獲取翻譯
export const categoryLabels: Record<ChannelCategory, string> = {
  fashion: '時尚',
  food: '美食',
  trend: '趨勢',
  finance: '財經',
  sports: '運動',
  tech: '科技',
  entertainment: '娛樂',
  other: '其他（自定義）', // 這個會被 i18n 替換
};

// 地區標籤映射
export const regionLabels: Record<ChannelRegion, string> = {
  hong_kong: '香港',
  taiwan: '台灣',
  japan: '日本',
  korea: '韓國',
  china: '中國大陸',
  usa: '美國',
  uk: '英國',
  global: '全球',
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

