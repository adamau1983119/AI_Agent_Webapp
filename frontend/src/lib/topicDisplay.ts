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

/** 是否顯示「譯為目前語言」按鈕 */
export function needsTranslateToCurrentLanguage(topic: Topic, uiLanguage: string): boolean {
  return normalizeUiLanguage(uiLanguage) !== getCollectionLanguage(topic)
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

  if (ui !== collectionLang && titles[ui]) {
    return {
      title: titles[ui],
      description: descriptions[ui] ?? topic.description,
      usingTranslation: true,
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
