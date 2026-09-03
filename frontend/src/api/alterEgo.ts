/**
 * Alter Ego API — onboarding / DNA（AE-1d）
 */
import { fetchAPI, fetchAPIEnvelope } from './client';
import { normalizeUiLanguage } from '@/lib/topicLanguages';

export type DnaStatus = 'pending' | 'active' | 'skipped' | 'legacy_only';
export type AlterEgoPlatform = 'facebook' | 'threads' | 'x';
export type ComposePlatform = 'facebook' | 'instagram' | 'threads';
export type ComposeStyle =
  | 'professional'
  | 'casual'
  | 'humorous'
  | 'storytelling'
  | 'educational';
export type ComposePart = 'all' | 'title' | 'body' | 'hashtags';

export interface DnaStatusResponse {
  dna_status: DnaStatus;
  current_dna_version_id?: string | null;
  has_dna: boolean;
}

export interface ExtractResponse {
  dna_json: Record<string, unknown>;
  dna_version_id: string;
  dna_status: 'active';
}

export interface PreviewResponse {
  platform: string;
  preview_text: string;
  soul_text: string;
  shell_constraints: string;
}

export interface ComposeResponse {
  titles: string[];
  body: string;
  hashtag_sets: string[][];
  credits_charged: number;
  balance_after: number;
  max_chars: number;
}

export const alterEgoApi = {
  /** 勿走 unwrap data，避免誤拆壞 dna_status */
  getStatus: () => fetchAPIEnvelope<DnaStatusResponse>('/alter-ego/status'),

  skip: () => fetchAPI<{ dna_status: 'skipped' }>('/alter-ego/skip', { method: 'POST' }),

  /** extract／preview 各含 1～2 次 DeepSeek；預設 10s 會誤殺（Request timeout 10000ms） */
  extract: (exemplars: string[], language: string = 'zh-TW') =>
    fetchAPI<ExtractResponse>('/alter-ego/extract', {
      method: 'POST',
      body: JSON.stringify({ exemplars, language }),
      timeout: 120000,
    }),

  preview: (
    platform: AlterEgoPlatform,
    topicHint: string = '',
    language?: string,
    contextSummary?: string,
    baseContent?: string
  ) =>
    fetchAPI<PreviewResponse>('/alter-ego/preview', {
      method: 'POST',
      body: JSON.stringify({
        platform,
        topic_hint: topicHint,
        ...(language ? { language: normalizeUiLanguage(language) } : {}),
        ...(contextSummary ? { context_summary: contextSummary } : {}),
        ...(baseContent ? { base_content: baseContent } : {}),
      }),
      timeout: 120000,
    }),

  rollback: (snapshotId: string) =>
    fetchAPI<ExtractResponse>('/alter-ego/dna/rollback', {
      method: 'POST',
      body: JSON.stringify({ snapshot_id: snapshotId }),
    }),

  adoptCopy: (payload: { platform: AlterEgoPlatform; topic_id?: string; preview_text: string }) =>
    fetchAPI<{ logged: boolean; event: string }>('/alter-ego/adopt-copy', {
      method: 'POST',
      body: JSON.stringify({
        platform: payload.platform,
        topic_id: payload.topic_id,
        preview_text: payload.preview_text,
      }),
    }),

  compose: (payload: {
    platform: ComposePlatform;
    style: ComposeStyle;
    max_chars: number;
    part?: ComposePart;
    language: string;
    topic_id?: string;
    topic_title?: string;
    context_summary?: string;
  }) =>
    fetchAPI<ComposeResponse>('/alter-ego/compose', {
      method: 'POST',
      body: JSON.stringify({
        platform: payload.platform,
        style: payload.style,
        max_chars: payload.max_chars,
        part: payload.part || 'all',
        language: normalizeUiLanguage(payload.language),
        topic_id: payload.topic_id,
        topic_title: payload.topic_title || '',
        context_summary: payload.context_summary || '',
      }),
      timeout: 120000,
    }),
};
