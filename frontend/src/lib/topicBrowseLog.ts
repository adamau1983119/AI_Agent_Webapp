import { interactionsAPI } from '@/api/interactions'

const STORAGE_KEY = 'ae_browse_id'

export function guestBrowseId(): string {
  try {
    const existing = localStorage.getItem(STORAGE_KEY)
    if (existing) return existing
    const created = `guest_${crypto.randomUUID()}`
    localStorage.setItem(STORAGE_KEY, created)
    return created
  } catch {
    return 'guest_local'
  }
}

export function logTopicBrowse(
  kind: 'topic_open' | 'topic_next' | 'topic_back' | 'topic_dwell',
  topicId: string,
  userId?: string | null,
  duration?: number,
): void {
  if (!topicId) return
  interactionsAPI
    .createInteraction({
      user_id: userId || guestBrowseId(),
      topic_id: topicId,
      action: 'view',
      duration: duration ?? 0,
      comment: kind,
    })
    .catch(() => undefined)
}
