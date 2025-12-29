import { create } from 'zustand'

interface UIState {
  sidebarOpen: boolean
  currentPage: string
  setSidebarOpen: (open: boolean) => void
  toggleSidebar: () => void
  setCurrentPage: (page: string) => void
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  currentPage: 'dashboard',
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setCurrentPage: (page) => set({ currentPage: page }),
}))

