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
  if (profile === 'latin') return hasLatin(trimmed) && !(hasCjk(trimmed) && !hasLatin(trimmed))
  if (profile === 'japanese') {
    if (hasKana(trimmed)) return true
    if (hasCjk(trimmed) && !mostlyAsciiLatin(trimmed)) return true
    return false
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
