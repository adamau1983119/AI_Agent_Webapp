/**
 * HKT 營運日 — 對齊 backend topic_day_hkt（generated_at 為 UTC naive）
 */
const HKT = 'Asia/Hong_Kong'

/** 每日 Cron 產卡上限（對齊 topic_generation.yaml 5×3） */
export const EXPECTED_DAILY_TOPICS = 15

const DATE_FIELDS = ['generated_at', 'generatedAt', 'created_at', 'createdAt'] as const

function formatHktDate(date: Date): string {
  return new Intl.DateTimeFormat('en-CA', { timeZone: HKT }).format(date)
}

export function todayHktDateString(now: Date = new Date()): string {
  return formatHktDate(now)
}

/** 以 HKT 曆日加減（YYYY-MM-DD），避免本機時區把「明天」當今天。 */
export function addHktCalendarDays(hktDay: string, delta: number): string {
  const [y, m, d] = hktDay.split('-').map(Number)
  const utc = new Date(Date.UTC(y, (m || 1) - 1, d || 1))
  utc.setUTCDate(utc.getUTCDate() + delta)
  return utc.toISOString().slice(0, 10)
}

export function yesterdayHktDateString(now: Date = new Date()): string {
  return addHktCalendarDays(todayHktDateString(now), -1)
}

/** 後端 UTC naive ISO → 視為 UTC 再換算 HKT 日 */
export function parseTopicGeneratedAt(value: unknown): Date | null {
  if (value == null || value === '') return null
  if (value instanceof Date) {
    return Number.isNaN(value.getTime()) ? null : value
  }
  if (typeof value === 'string') {
    const hasTz = /[zZ]|[+-]\d{2}:\d{2}$/.test(value)
    const iso = hasTz ? value : `${value}Z`
    const d = new Date(iso)
    return Number.isNaN(d.getTime()) ? null : d
  }
  const d = new Date(value as string | number)
  return Number.isNaN(d.getTime()) ? null : d
}

export function topicHktDateString(topic: Record<string, unknown>): string | null {
  for (const field of DATE_FIELDS) {
    const parsed = parseTopicGeneratedAt(topic[field])
    if (parsed) return formatHktDate(parsed)
  }
  return null
}

export function isTopicOnHktDay(
  topic: Record<string, unknown>,
  hktDay: string = todayHktDateString()
): boolean {
  const day = topicHktDateString(topic)
  return day !== null && day === hktDay
}

export function filterTopicsForHktDay<T extends Record<string, unknown>>(
  topics: T[],
  hktDay: string = todayHktDateString()
): T[] {
  return topics.filter((t) => isTopicOnHktDay(t, hktDay))
}

/** 標準化標題（對齊後端 ContentDeduplicator） */
export function normalizeTopicTitle(title: string): string {
  return title
    .replace(/[^\w\s\u4e00-\u9fff]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase()
}

/** 列表去重：同標題只保留第一張（通常較新） */
export function dedupeTopicsByTitle<T extends { id?: string; title?: string }>(
  topics: T[]
): T[] {
  const seen = new Set<string>()
  const result: T[] = []
  for (const topic of topics) {
    const key = normalizeTopicTitle(topic.title || '')
    if (key.length >= 5) {
      if (seen.has(key)) continue
      seen.add(key)
    }
    result.push(topic)
  }
  return result
}

export function countTopicsForHktDay(
  topics: Record<string, unknown>[],
  hktDay: string = todayHktDateString()
): number {
  return filterTopicsForHktDay(topics, hktDay).length
}
