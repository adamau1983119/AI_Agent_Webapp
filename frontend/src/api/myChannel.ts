/**
 * MyChannel API（v7.1 · MC-2～MC-6）
 * 使用 fetchAPIEnvelope：後端 envelope 含 data + balance/empty，不可被 interceptor 拆掉。
 */
import { fetchAPIEnvelope } from './client';

export interface MyChannelFeedCard {
  id: string;
  heading: string;
  intro: string;
  category?: string;
  image_url?: string | null;
}

export interface MyChannelFeedResponse {
  data: MyChannelFeedCard[];
  balance: number;
  lang: string;
  cached: boolean;
  rate_limited: boolean;
  empty: boolean;
  has_channels: boolean;
}

export interface UnlockResponse {
  topic_id: string;
  source_url: string;
  digest_300: string;
  balance: number;
}

export interface ChannelTemplate {
  id: string;
  category: string;
  region: string;
  name_key: string;
  desc_key: string;
  suggested_name: string;
}

export const myChannelApi = {
  getFeed: (lang: string) =>
    fetchAPIEnvelope<MyChannelFeedResponse>(
      `/my-channel/feed?lang=${encodeURIComponent(lang)}`
    ),

  unlock: (topicId: string, idempotencyKey: string) =>
    fetchAPIEnvelope<UnlockResponse>(`/my-channel/topics/${topicId}/unlock`, {
      method: 'POST',
      body: JSON.stringify({ idempotency_key: idempotencyKey }),
    }),

  getChannelTemplates: () =>
    fetchAPIEnvelope<{ data: ChannelTemplate[] }>('/my-channel/channel-templates'),
};
