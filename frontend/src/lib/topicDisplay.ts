import type { Topic } from '@/types'
import type { TopicDisplayOverride } from '@/components/ui/TopicTranslateDisplayButton'

export type UiLanguage = 'zh-TW' | 'en' | 'ja'

export function normalizeUiLanguage(lang?: string): UiLanguage {
  if (!lang) return 'zh-TW'
  const low = lang.toLowerCase()
  if (low.startsWith('en')) return 'en'
  if (low === 'ja' || low.startsWith('ja')) return 'ja'
  return 'zh-TW'
}

export function getTopicI18nMaps(topic: Topic) {
  return {
    titles: (topic.titlesI18n || topic.titles_i18n || {}) as Record<string, string>,
    descriptions: (topic.descriptionI18n || topic.description_i18n || {}) as Record<string, string>,
  }
}

export function getCollectionLanguage(topic: Topic): UiLanguage {
  return normalizeUiLanguage(topic.displayLanguage || topic.display_language)
}

export function titleHasCjk(text: string): boolean {
  return /[\u4e00-\u9fff]/.test(text)
}

/** 收集語言與標題實際文字是否一致（避免 display_language=zh-TW 但 RSS 英文） */
export function collectionTitleMatchesUi(topic: Topic, ui: UiLanguage): boolean {
  const collectionLang = getCollectionLanguage(topic)
  if (ui !== collectionLang) return false
  const title = (topic.title || '').trim()
  if (ui === 'zh-TW') return titleHasCjk(title)
  if (ui === 'en') return /[A-Za-z]/.test(title)
  return true
}

/** 是否顯示「譯為目前語言」按鈕 */
export function needsTranslateToCurrentLanguage(topic: Topic, uiLanguage: string): boolean {
  const ui = normalizeUiLanguage(uiLanguage)
  const collectionLang = getCollectionLanguage(topic)
  const { titles } = getTopicI18nMaps(topic)
  if (titles[ui]?.trim()) return false
  if (ui !== collectionLang) return true
  return !collectionTitleMatchesUi(topic, ui)
}

/** 方案 C：預設顯示收集時標題；若已有目前語言快取則優先顯示譯文 */
export function resolveTopicDisplayCopy(
  topic: Topic,
  uiLanguage: string,
  override?: TopicDisplayOverride | null
) {
  const ui = normalizeUiLanguage(uiLanguage)
  const collectionLang = getCollectionLanguage(topic)
  const { titles, descriptions } = getTopicI18nMaps(topic)

  if (override) {
    return {
      title: override.title,
      description: override.description ?? topic.description,
      usingTranslation: true,
      fromCache: Boolean(override.cached),
    }
  }

  if (titles[ui]?.trim()) {
    return {
      title: titles[ui],
      description: descriptions[ui] ?? topic.description,
      usingTranslation: ui !== collectionLang || !collectionTitleMatchesUi(topic, ui),
      fromCache: true,
    }
  }

  return {
    title: topic.title,
    description: topic.description,
    usingTranslation: false,
    fromCache: false,
  }
}

export function getOriginalTitleLine(topic: Topic, displayTitle: string): string | null {
  const original = (topic.originalTitle || topic.original_title || '').trim()
  if (!original) return null
  if (original === displayTitle.trim()) return null
  return original
}
