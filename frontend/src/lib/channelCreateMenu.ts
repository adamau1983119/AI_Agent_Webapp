import type { ChannelCategory } from '../api/channels';

const hiddenCreateCategories = new Set<ChannelCategory>(['lego', 'cosplay', 'other']);

export function isHiddenCreateCategory(value: string): boolean {
  return hiddenCreateCategories.has(value as ChannelCategory);
}

export function visibleCreateCategories<T extends { value: ChannelCategory }>(rows: T[]): T[] {
  return rows.filter((row) => !hiddenCreateCategories.has(row.value));
}
