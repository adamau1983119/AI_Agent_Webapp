/**
 * 社交平台 API
 * Phase 5: 分發與整合
 */
import { fetchAPI } from './client';

// 類型定義
export type SocialPlatform = 'instagram' | 'facebook' | 'threads' | 'tiktok' | 'twitter';
export type ConnectionStatus = 'connected' | 'disconnected' | 'expired' | 'error';
export type PublishStatus = 'pending' | 'publishing' | 'published' | 'failed' | 'retry';

export interface SocialConnection {
  id: string;
  user_id: string;
  platform: SocialPlatform;
  platform_user_id: string;
  platform_username: string;
  platform_name?: string;
  profile_image_url?: string;
  status: ConnectionStatus;
  token_expires_at?: string;
  last_used_at?: string;
  created_at: string;
  updated_at: string;
}

export interface PlatformInfo {
  value: SocialPlatform;
  name: string;
  icon: string;
  max_caption_length: number;
  max_hashtags: number;
  image_required: boolean;
  note?: string;
}

export interface PublishRequest {
  content_id: string;
  content: string;
  platforms: SocialPlatform[];
  hashtags?: string[];
  image_urls?: string[];
  scheduled_at?: string;
}

export interface PublishResult {
  platform: SocialPlatform;
  status: PublishStatus;
  post_id?: string;
  post_url?: string;
  error_message?: string;
  published_at?: string;
}

export interface PublishResponse {
  publish_id: string;
  content_id: string;
  total_platforms: number;
  successful: number;
  failed: number;
  results: PublishResult[];
  created_at: string;
}

export interface PublishHistoryItem {
  id: string;
  content_id: string;
  content_preview: string;
  platforms: SocialPlatform[];
  status: PublishStatus;
  results: PublishResult[];
  created_at: string;
  published_at?: string;
}

export interface OptimizedContent {
  content: string;
  full_content: string;
  hashtags: string[];
  hashtag_string: string;
  character_count: number;
  platform: string;
}

// API 函數
export const socialApi = {
  /**
   * 取得我的社交連接
   */
  getMyConnections: async (): Promise<{ connections: SocialConnection[]; total: number }> => {
    return fetchAPI('/social/connections');
  },

  /**
   * 取得可用平台列表
   */
  getPlatforms: async (): Promise<{ platforms: PlatformInfo[] }> => {
    return fetchAPI('/social/platforms');
  },

  /**
   * 斷開平台連接
   */
  disconnectPlatform: async (platform: SocialPlatform): Promise<{ message: string }> => {
    return fetchAPI(`/social/connections/${platform}`, {
      method: 'DELETE',
    });
  },

  /**
   * 取得 Meta OAuth URL
   */
  getMetaOAuthUrl: async (): Promise<{ oauth_url: string; state: string; platforms: string[] }> => {
    return fetchAPI('/social/meta/connect');
  },

  /**
   * 取得 TikTok OAuth URL
   */
  getTikTokOAuthUrl: async (): Promise<{ oauth_url: string; state: string; platforms: string[] }> => {
    return fetchAPI('/social/tiktok/connect');
  },

  /**
   * 發布內容
   */
  publishContent: async (data: PublishRequest): Promise<PublishResponse> => {
    return fetchAPI<PublishResponse>('/social/publish', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * 預覽內容最佳化
   */
  previewOptimization: async (
    content: string,
    hashtags: string[],
    platform: SocialPlatform
  ): Promise<{ original_content: string; optimized: OptimizedContent; platform: PlatformInfo }> => {
    const params = new URLSearchParams({
      content,
      platform,
    });
    hashtags.forEach((tag) => params.append('hashtags', tag));
    return fetchAPI(`/social/preview-optimize?${params.toString()}`);
  },

  /**
   * 取得發布歷史
   */
  getPublishHistory: async (
    page = 1,
    limit = 20
  ): Promise<{ items: PublishHistoryItem[]; total: number; page: number; limit: number }> => {
    return fetchAPI(`/social/publish/history?page=${page}&limit=${limit}`);
  },

  /**
   * 取得發布狀態
   */
  getPublishStatus: async (publishId: string): Promise<PublishHistoryItem> => {
    return fetchAPI(`/social/publish/${publishId}`);
  },
};

// 平台標籤
export const platformLabels: Record<SocialPlatform, string> = {
  instagram: 'Instagram',
  facebook: 'Facebook',
  threads: 'Threads',
  tiktok: 'TikTok',
  twitter: 'Twitter/X',
};

// 平台圖標
export const platformIcons: Record<SocialPlatform, string> = {
  instagram: '📸',
  facebook: '👤',
  threads: '🧵',
  tiktok: '🎵',
  twitter: '🐦',
};

// 發布狀態標籤
export const publishStatusI18nKeys: Record<PublishStatus, string> = {
  pending: 'publish.status.pending',
  publishing: 'publish.status.publishing',
  published: 'publish.status.published',
  failed: 'publish.status.failed',
  retry: 'publish.status.retry',
};

// 發布狀態顏色
export const publishStatusColors: Record<PublishStatus, string> = {
  pending: 'bg-gray-100 text-gray-600',
  publishing: 'bg-blue-100 text-blue-600',
  published: 'bg-green-100 text-green-600',
  failed: 'bg-red-100 text-red-600',
  retry: 'bg-yellow-100 text-yellow-600',
};

