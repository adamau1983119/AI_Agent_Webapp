/**
 * Topic UI 語言表（SoT：shared/topic_languages.json）+ 標題腳本檢測。
 */
import langConfig from '@lang-config/topic_languages.json'
import type { Topic } from '@/types'

export type UiLanguage = 'zh-TW' | 'en' | 'ja'

export const SUPPORTED_UI_LANGUAGES = langConfig.supported as readonly UiLanguage[]
export const DEFAULT_UI_LANGUAGE = (langConfig.default || 'zh-TW') as UiLanguage

type ScriptProfile = 'han' | 'latin' | 'japanese'

const scriptProfiles = langConfig.script_profile as Record<UiLanguage, ScriptProfile>

function hasCjk(text: string): boolean {
  return /[\u4e00-\u9fff]/.test(text)
}

function hasKana(text: string): boolean {
  return /[\u3040-\u309f\u30a0-\u30ff]/.test(text)
}

function hasLatin(text: string): boolean {
  return /[A-Za-z]/.test(text)
}

function mostlyAsciiLatin(text: string): boolean {
  const letters = [...text].filter((ch) => /\p{L}/u.test(ch))
  if (!letters.length) return false
  const latin = letters.filter((ch) => ch.charCodeAt(0) < 128).length
  return latin / letters.length >= 0.8
}

function titleMatchesScript(text: string, profile: ScriptProfile): boolean {
  const trimmed = text.trim()
  if (!trimmed) return true
  if (profile === 'han') return hasCjk(trimmed)
  if (profile === 'latin') {
    if (hasKana(trimmed)) return false
    if (hasCjk(trimmed)) return mostlyAsciiLatin(trimmed)
    return hasLatin(trimmed)
  }
  if (profile === 'japanese') {
    if (hasKana(trimmed)) return true
    // 無假名且含中文漢字，絕非有效日語標題
    if (hasCjk(trimmed)) return false
    // 僅短英文/數字品牌詞（如 NASA）允許無假名，長英文句子必須翻譯為日文
    return trimmed.length <= 15 && !(trimmed.includes(' ') && trimmed.split(/\s+/).length > 2)
  }
  return true
}

export function normalizeUiLanguage(lang?: string): UiLanguage {
  if (!lang) return DEFAULT_UI_LANGUAGE
  const low = lang.toLowerCase()
  if (low.startsWith('en')) return 'en'
  if (low === 'ja' || low.startsWith('ja')) return 'ja'
  return 'zh-TW'
}

export function titleMatchesDisplayLanguage(title: string, displayLang?: string): boolean {
  const ui = normalizeUiLanguage(displayLang)
  const profile = scriptProfiles[ui] ?? 'latin'
  return titleMatchesScript(title, profile)
}

export function titleScriptMismatch(title: string, displayLang?: string): boolean {
  return !titleMatchesDisplayLanguage(title, displayLang)
}

export function isFallbackTitle(text?: string | null): boolean {
  const t = (text || '').trim()
  return t.startsWith('[Fallback-') || t.startsWith('[Fallback]')
}

export function usableCachedTitle(text?: string | null, targetLang?: string): string | null {
  const t = (text || '').trim()
  if (!t || isFallbackTitle(t)) return null
  if (targetLang && !titleMatchesDisplayLanguage(t, targetLang)) return null
  return t
}

export function getCollectionLanguage(topic: Topic): UiLanguage {
  return normalizeUiLanguage(topic.displayLanguage || topic.display_language)
}

export function topicTitleScriptMismatch(topic: Topic): boolean {
  if (typeof topic.titleScriptMismatch === 'boolean') {
    return topic.titleScriptMismatch
  }
  if (typeof topic.title_script_mismatch === 'boolean') {
    return topic.title_script_mismatch
  }
  return titleScriptMismatch(topic.title || '', getCollectionLanguage(topic))
}

export function collectionTitleMatchesUi(topic: Topic, ui: UiLanguage): boolean {
  if (ui !== getCollectionLanguage(topic)) return false
  return titleMatchesDisplayLanguage(topic.title || '', ui)
}

export function preloadLanguagesFor(displayLang?: string): UiLanguage[] {
  const lang = normalizeUiLanguage(displayLang)
  return SUPPORTED_UI_LANGUAGES.filter((code) => code !== lang)
}
