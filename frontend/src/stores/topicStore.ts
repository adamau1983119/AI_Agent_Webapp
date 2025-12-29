import { create } from 'zustand'
import type { Topic } from '@/types'

interface TopicState {
  selectedTopic: Topic | null
  filters: {
    category: 'fashion' | 'food' | 'trend' | null
    status: 'pending' | 'confirmed' | 'deleted' | null
    date: string | null
  }
  setSelectedTopic: (topic: Topic | null) => void
  updateFilters: (filters: Partial<TopicState['filters']>) => void
  resetFilters: () => void
}

export const useTopicStore = create<TopicState>((set) => ({
  selectedTopic: null,
  filters: {
    category: null,
    status: null,
    date: null,
  },
  setSelectedTopic: (topic) => set({ selectedTopic: topic }),
  updateFilters: (filters) =>
    set((state) => ({
      filters: { ...state.filters, ...filters },
    })),
  resetFilters: () =>
    set({
      filters: {
        category: null,
        status: null,
        date: null,
      },
    }),
}))

