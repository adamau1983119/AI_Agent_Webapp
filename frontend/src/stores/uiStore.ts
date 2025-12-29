import { create } from 'zustand'

interface UIState {
  sidebarOpen: boolean
  currentPage: string
  setSidebarOpen: (open: boolean) => void
  toggleSidebar: () => void
  setCurrentPage: (page: string) => void
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: false, // 移動端默認關閉
  currentPage: 'dashboard',
  setSidebarOpen: (open: boolean) => set({ sidebarOpen: open }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setCurrentPage: (page) => set({ currentPage: page }),
}))

