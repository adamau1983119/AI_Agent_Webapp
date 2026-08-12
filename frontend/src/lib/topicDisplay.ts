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

function sourceNeedsDescription(topic: Topic): boolean {
  return Boolean((topic.description || '').trim())
}

export function getTopicI18nMaps(topic: Topic) {
  const rawTitles = (topic.titlesI18n || topic.titles_i18n || {}) as Record<string, string>
  const rawDescs = (topic.descriptionI18n || topic.description_i18n || {}) as Record<string, string>
  const titles: Record<string, string> = {}
  const descriptions: Record<string, string> = {}
  for (const [k, v] of Object.entries(rawTitles)) {
    const ok = usableCachedTitle(v)
    if (ok) titles[k] = ok
  }
  for (const [k, v] of Object.entries(rawDescs)) {
    const ok = usableCachedTitle(v)
    if (ok) descriptions[k] = ok
  }
  return { titles, descriptions }
}

/** 一語一包：有源摘要則 title+desc 皆須齊；否則僅 title。 */
export function hasCompleteDisplayPack(
  topic: Topic,
  uiLanguage: string,
  override?: TopicDisplayOverride | null
): boolean {
  const ui = normalizeUiLanguage(uiLanguage)
  const needDesc = sourceNeedsDescription(topic)
  if (override && usableCachedTitle(override.title)) {
    if (!needDesc) return true
    return Boolean(usableCachedTitle(override.description))
  }
  const { titles, descriptions } = getTopicI18nMaps(topic)
  if (!usableCachedTitle(titles[ui])) return false
  if (needDesc && !usableCachedTitle(descriptions[ui])) return false
  return true
}

export {
  collectionTitleMatchesUi,
  getCollectionLanguage,
  normalizeUiLanguage,
  topicTitleScriptMismatch,
}

export function isServerLocaleResolved(topic: Topic, uiLanguage: string): boolean {
  const ui = normalizeUiLanguage(uiLanguage)
  const loc = topic.contentLocale || topic.content_locale
  const resolved = topic.localeResolved ?? topic.locale_resolved
  if (!resolved || !loc) return false
  return normalizeUiLanguage(loc) === ui
}

/** 是否顯示「譯為目前語言」／觸發自動補齊 */
export function needsTranslateToCurrentLanguage(topic: Topic, uiLanguage: string): boolean {
  if (isServerLocaleResolved(topic, uiLanguage)) return false
  const ui = normalizeUiLanguage(uiLanguage)
  const collectionLang = getCollectionLanguage(topic)
  if (hasCompleteDisplayPack(topic, ui)) {
    if (ui === collectionLang) return topicTitleScriptMismatch(topic)
    return false
  }
  if (ui !== collectionLang) return true
  return topicTitleScriptMismatch(topic)
}

/** 方案 C：成套齊才用譯文；否則整卡回落收集語言（禁止半包混語） */
export function resolveTopicDisplayCopy(
  topic: Topic,
  uiLanguage: string,
  override?: TopicDisplayOverride | null
) {
  const ui = normalizeUiLanguage(uiLanguage)
  const collectionLang = getCollectionLanguage(topic)
  const { titles, descriptions } = getTopicI18nMaps(topic)
  const needDesc = sourceNeedsDescription(topic)

  if (isServerLocaleResolved(topic, uiLanguage)) {
    return {
      title: topic.title || '',
      description: topic.description,
      usingTranslation: ui !== collectionLang || topicTitleScriptMismatch(topic),
      fromCache: true,
      localePending: false,
    }
  }

  if (override && usableCachedTitle(override.title)) {
    const descOk = !needDesc || Boolean(usableCachedTitle(override.description))
    if (descOk) {
      return {
        title: override.title,
        description: needDesc ? (override.description || '') : topic.description,
        usingTranslation: true,
        fromCache: Boolean(override.cached),
        localePending: false,
      }
    }
  }

  if (hasCompleteDisplayPack(topic, ui)) {
    const cached = usableCachedTitle(titles[ui])!
    return {
      title: cached,
      description: needDesc ? descriptions[ui] : topic.description,
      usingTranslation: ui !== collectionLang || topicTitleScriptMismatch(topic),
      fromCache: true,
      localePending: false,
    }
  }

  if (ui !== collectionLang) {
    return {
      title: '',
      description: '',
      usingTranslation: true,
      fromCache: false,
      localePending: true,
    }
  }

  const rawTitle = topic.title || ''
  return {
    title: usableCachedTitle(rawTitle) || rawTitle,
    description: topic.description,
    usingTranslation: false,
    fromCache: false,
    localePending: false,
  }
}

export function isLocaleDisplayPending(
  topic: Topic,
  uiLanguage: string,
  override?: TopicDisplayOverride | null
): boolean {
  return resolveTopicDisplayCopy(topic, uiLanguage, override).localePending === true
}

export function getOriginalTitleLine(topic: Topic, displayTitle: string): string | null {
  const original = (topic.originalTitle || topic.original_title || '').trim()
  if (!original) return null
  if (original === displayTitle.trim()) return null
  return original
}
