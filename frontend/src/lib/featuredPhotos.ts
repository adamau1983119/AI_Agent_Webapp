export const FEATURED_PHOTO_CAP = 4

export function featuredSlots(existingCount: number, cap = FEATURED_PHOTO_CAP): number {
  return Math.max(0, cap - Math.max(0, existingCount))
}
