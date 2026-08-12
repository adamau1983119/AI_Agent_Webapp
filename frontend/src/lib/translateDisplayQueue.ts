/** Dashboard 多卡 translate-display 併發閘門（Content Locale 主路徑下為 fallback）。 */
type Task = () => Promise<void>

const queue: Task[] = []
let active = 0
const MAX_CONCURRENT = 2

function pump(): void {
  while (active < MAX_CONCURRENT && queue.length > 0) {
    const task = queue.shift()!
    active += 1
    void task().finally(() => {
      active -= 1
      pump()
    })
  }
}

/** 排入佇列；回傳 cancel（僅略過尚未開始的工作）。 */
export function enqueueTranslateDisplay(task: Task): () => void {
  let cancelled = false
  const wrapped: Task = async () => {
    if (cancelled) return
    await task()
  }
  queue.push(wrapped)
  pump()
  return () => {
    cancelled = true
  }
}

export function isTranslateRateLimited(): boolean {
  if (typeof sessionStorage === 'undefined') return false
  const until = Number(sessionStorage.getItem('flash_translate_rate_limited_until') || 0)
  return Date.now() < until
}

export function markTranslateRateLimited(ms = 60_000): void {
  if (typeof sessionStorage === 'undefined') return
  try {
    sessionStorage.setItem(
      'flash_translate_rate_limited_until',
      String(Date.now() + ms)
    )
  } catch {
    /* ignore */
  }
}

export function isTranslateHardBlocked(): boolean {
  if (typeof sessionStorage === 'undefined') return false
  return sessionStorage.getItem('flash_translate_unavailable') === '1'
}
