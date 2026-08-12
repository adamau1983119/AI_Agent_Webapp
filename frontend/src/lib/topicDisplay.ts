import type { Topic } from '@/types'
import type { TopicDisplayOverride } from '@/components/ui/TopicTranslateDisplayButton'
import {
  collectionTitleMatchesUi,
  getCollectionLanguage,
  normalizeUiLanguage,
  topicTitleScriptMismatch,
  usableCachedTitle,
  type UiLanguage,
} from '@/lib/topicLanguages'

export type { UiLanguage }

export function getTopicI18nMaps(topic: Topic) {
  const rawTitles = (topic.titlesI18n || topic.titles_i18n || {}) as Record<string, string>
  const titles: Record<string, string> = {}
  for (const [k, v] of Object.entries(rawTitles)) {
    const ok = usableCachedTitle(v)
    if (ok) titles[k] = ok
  }
  return {
    titles,
    descriptions: (topic.descriptionI18n || topic.description_i18n || {}) as Record<string, string>,
  }
}

export {
  collectionTitleMatchesUi,
  getCollectionLanguage,
  normalizeUiLanguage,
  topicTitleScriptMismatch,
}

/** 是否顯示「譯為目前語言」按鈕 */
export function needsTranslateToCurrentLanguage(topic: Topic, uiLanguage: string): boolean {
  const ui = normalizeUiLanguage(uiLanguage)
  const collectionLang = getCollectionLanguage(topic)
  const { titles } = getTopicI18nMaps(topic)
  if (usableCachedTitle(titles[ui])) return false
  if (ui !== collectionLang) return true
  return topicTitleScriptMismatch(topic)
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

  if (override && usableCachedTitle(override.title)) {
    return {
      title: override.title,
      description: override.description ?? topic.description,
      usingTranslation: true,
      fromCache: Boolean(override.cached),
    }
  }

  const cached = usableCachedTitle(titles[ui])
  if (cached) {
    return {
      title: cached,
      description: descriptions[ui] ?? topic.description,
      usingTranslation: ui !== collectionLang || topicTitleScriptMismatch(topic),
      fromCache: true,
    }
  }

  const rawTitle = topic.title || ''
  return {
    title: usableCachedTitle(rawTitle) || rawTitle,
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
