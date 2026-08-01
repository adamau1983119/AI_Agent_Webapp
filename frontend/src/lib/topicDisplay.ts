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

function hasHan(text: string): boolean {
  return /[\u4e00-\u9fff]/.test(text)
}

function hasKana(text: string): boolean {
  return /[\u3040-\u30ff\uff66-\uff9d]/.test(text)
}

/** Drop mis-tagged slots (Chinese under en, etc.). */
export function pickI18nText(
  map: Record<string, string>,
  ui: UiLanguage
): string | undefined {
  const candidates = [map[ui]]
  if (ui === 'en') candidates.push(map['en-US'], map['EN'])
  if (ui === 'ja') candidates.push(map['ja-JP'], map['JA'])
  if (ui === 'zh-TW') candidates.push(map['zh'], map['zh-Hant'])

  for (const raw of candidates) {
    const text = (raw || '').trim()
    if (!text) continue
    if (ui === 'en' && (hasHan(text) || hasKana(text))) continue
    if (ui === 'ja' && !hasHan(text) && !hasKana(text)) continue
    if (ui === 'zh-TW' && !hasHan(text)) continue
    return text
  }
  return undefined
}

/** Prefer script truth when display_language was mis-tagged at collect. */
export function getCollectionLanguage(topic: Topic): UiLanguage {
  const declared = normalizeUiLanguage(topic.displayLanguage || topic.display_language)
  const title = (topic.title || '').trim()
  if (hasKana(title)) return 'ja'
  if (hasHan(title) && declared === 'en') return 'zh-TW'
  return declared
}

export function needsTranslateToCurrentLanguage(topic: Topic, uiLanguage: string): boolean {
  const ui = normalizeUiLanguage(uiLanguage)
  const { titles } = getTopicI18nMaps(topic)
  if (pickI18nText(titles, ui)) return false
  return ui !== getCollectionLanguage(topic)
}

/** Prefer titles_i18n / description_i18n for fluent language switch. */
export function resolveTopicDisplayCopy(
  topic: Topic,
  uiLanguage: string,
  override?: TopicDisplayOverride | null
) {
  const ui = normalizeUiLanguage(uiLanguage)
  const { titles, descriptions } = getTopicI18nMaps(topic)

  if (override) {
    return {
      title: override.title,
      description: override.description ?? topic.description,
      usingTranslation: true,
      fromCache: Boolean(override.cached),
    }
  }

  const title = pickI18nText(titles, ui) || topic.title
  const description = pickI18nText(descriptions, ui) || topic.description
  const fromPrefetch = Boolean(pickI18nText(titles, ui) || pickI18nText(descriptions, ui))

  return {
    title,
    description,
    usingTranslation: fromPrefetch && ui !== getCollectionLanguage(topic),
    fromCache: fromPrefetch,
  }
}

export function getOriginalTitleLine(topic: Topic, displayTitle: string): string | null {
  const original = (topic.originalTitle || topic.original_title || '').trim()
  if (!original) return null
  if (original === displayTitle.trim()) return null
  return original
}
