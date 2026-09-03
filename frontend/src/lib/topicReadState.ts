const STORAGE_KEY = 'alterego.topicReadIds.v1'
const EVENT_NAME = 'alterego-topic-read'
const MAX_IDS = 400

function readIds(): string[] {
  if (typeof window === 'undefined') return []
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed.filter((id) => typeof id === 'string') : []
  } catch {
    return []
  }
}

function writeIds(ids: string[]): void {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(ids.slice(-MAX_IDS)))
}

export function isTopicRead(topicId: string): boolean {
  if (!topicId) return false
  return readIds().includes(topicId)
}

export function markTopicRead(topicId: string): void {
  if (!topicId || typeof window === 'undefined') return
  const ids = readIds().filter((id) => id !== topicId)
  ids.push(topicId)
  try {
    writeIds(ids)
    window.dispatchEvent(new Event(EVENT_NAME))
  } catch {
    // private mode / quota — skip; unread styling is acceptable
  }
}

export function subscribeTopicRead(onChange: () => void): () => void {
  if (typeof window === 'undefined') return () => undefined
  const handler = () => onChange()
  window.addEventListener(EVENT_NAME, handler)
  window.addEventListener('storage', handler)
  return () => {
    window.removeEventListener(EVENT_NAME, handler)
    window.removeEventListener('storage', handler)
  }
}
