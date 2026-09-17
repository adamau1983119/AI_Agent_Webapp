/**
 * Ops Style Trainer API (allowlist).
 */
import { fetchAPI } from './client'

export type TrainerLang = 'zh-TW' | 'en' | 'ja'
export type TrainerDomain = 'fashion' | 'food' | 'trend'
export type TrainerLength = 'short' | 'long'
export type WriteProfile = 'news_recap' | 'hook_gossip'
export type RefType = 'positive' | 'negative'

export interface StructureSlots {
  prefix: string
  fact: string
  quote: string
  context: string
  ending: string
}

export interface AnalyzeResult {
  language: TrainerLang
  domain: TrainerDomain
  length_bucket: TrainerLength
  write_profile: WriteProfile
  ref_type: RefType
  structure: StructureSlots
  body_text: string
  notes: string
}

export interface CoverageLang {
  language: TrainerLang
  filled: number
  target: number
  mode: 'A' | 'B'
}

export const opsTrainerApi = {
  access: () => fetchAPI<{ allowed: boolean }>('/ops/trainer/access'),
  coverage: () =>
    fetchAPI<{ languages: CoverageLang[]; note: string }>('/ops/trainer/coverage', {
      timeout: 30000,
    }),
  analyze: (body: {
    text?: string
    image_data_url?: string
    source_url?: string
    language_hint?: TrainerLang
  }) =>
    fetchAPI<AnalyzeResult>('/ops/trainer/analyze', {
      method: 'POST',
      body: JSON.stringify(body),
      timeout: 120000,
    }),
  confirm: (body: {
    language: TrainerLang
    domain: TrainerDomain
    length_bucket: TrainerLength
    write_profile: WriteProfile
    ref_type: RefType
    structure: StructureSlots
    body_text: string
    source_url?: string
    publish?: boolean
  }) =>
    fetchAPI<{ id: string; status: string }>('/ops/trainer/confirm', {
      method: 'POST',
      body: JSON.stringify(body),
      timeout: 30000,
    }),
}
