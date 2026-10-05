const STORAGE_KEY = 'ae_tour_public_v1'
export const TOUR_SAMPLE_QUERY = 'tourSample'
export const TOUR_STEPS = 5

export type PublicTourStatus = 'idle' | 'active' | 'skipped' | 'done'
export type PublicTourState = {
  status: PublicTourStatus
  step: number
  topicId: string
}

const idle: PublicTourState = { status: 'idle', step: 1, topicId: '' }

function readRaw(): PublicTourState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return idle
    const parsed = JSON.parse(raw) as Partial<PublicTourState>
    const step = Number(parsed.step)
    return {
      status: parsed.status === 'active' || parsed.status === 'skipped' || parsed.status === 'done'
        ? parsed.status
        : 'idle',
      step: step >= 1 && step <= TOUR_STEPS ? step : 1,
      topicId: typeof parsed.topicId === 'string' ? parsed.topicId : '',
    }
  } catch {
    return idle
  }
}

export function readPublicTour(): PublicTourState {
  return readRaw()
}

export function writePublicTour(next: PublicTourState): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
}

export function shouldForceSample(search: string): boolean {
  const q = new URLSearchParams(search.startsWith('?') ? search.slice(1) : search)
  return q.get(TOUR_SAMPLE_QUERY) === '1'
}

export type TourTopicPick = {
  id: string
  title?: string
  category?: string
  description?: string
  summaryFlash?: string
  summary_flash?: string
  previewImages?: string[]
  preview_images?: string[]
}

function factLen(t: TourTopicPick): number {
  return (t.summaryFlash || t.summary_flash || t.description || '').trim().length
}

function hasPreview(t: TourTopicPick): boolean {
  const imgs = t.previewImages || t.preview_images || []
  return Array.isArray(imgs) && imgs.length > 0
}

const CAT_RANK: Record<string, number> = { fashion: 0, food: 1, trend: 2 }

export function pickPublicTourTopic(topics: TourTopicPick[]): TourTopicPick | null {
  const ok = topics.filter((t) => {
    const cat = t.category || ''
    if (!t.id || !(cat in CAT_RANK)) return false
    if (!(t.title || '').trim()) return false
    return factLen(t) >= 8
  })
  if (!ok.length) return null
  ok.sort((a, b) => {
    const img = Number(hasPreview(b)) - Number(hasPreview(a))
    if (img) return img
    const cat = (CAT_RANK[a.category || ''] ?? 9) - (CAT_RANK[b.category || ''] ?? 9)
    if (cat) return cat
    return factLen(b) - factLen(a)
  })
  return ok[0]
}
