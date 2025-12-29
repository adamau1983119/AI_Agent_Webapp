import { ReactNode, useEffect } from 'react'
import Sidebar from './Sidebar'
import Header from './Header'
import { useUIStore } from '@/stores/uiStore'

interface MainLayoutProps {
  children: ReactNode
}

export default function MainLayout({ children }: MainLayoutProps) {
  const { sidebarOpen, setSidebarOpen } = useUIStore()

  // 移動端：側邊欄打開時禁止背景滾動
  useEffect(() => {
    if (sidebarOpen && window.innerWidth < 1024) {
      document.body.classList.add('sidebar-open')
    } else {
      document.body.classList.remove('sidebar-open')
    }
    return () => {
      document.body.classList.remove('sidebar-open')
    }
  }, [sidebarOpen])

  return (
    <div className="flex h-screen bg-gray-50">
      {/* 移動端遮罩層 */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* 側邊欄 */}
      <Sidebar />

      {/* 主內容區 */}
      <div className="flex-1 flex flex-col overflow-hidden min-w-0 w-full lg:w-auto">
        <Header />
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  )
}

