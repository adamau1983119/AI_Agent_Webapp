import { format } from 'date-fns'
import { useState, FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { useUIStore } from '@/stores/uiStore'

export default function Header() {
  const today = new Date()
  const dateStr = format(today, 'EEEE, MMMM d')
  const { toggleSidebar } = useUIStore()
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState('')

  const handleSearch = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      // 導航到 Topics 頁面並帶上搜索參數
      navigate(`/topics?search=${encodeURIComponent(searchQuery.trim())}`)
      setSearchQuery('') // 清空搜索框
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      if (searchQuery.trim()) {
        navigate(`/topics?search=${encodeURIComponent(searchQuery.trim())}`)
        setSearchQuery('')
      }
    }
  }

  return (
    <header className="bg-white border-b border-gray-200 px-4 sm:px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          {/* 移動端漢堡菜單按鈕 */}
          <button
            onClick={toggleSidebar}
            className="lg:hidden p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg"
            aria-label="Toggle sidebar"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16"></path>
            </svg>
          </button>

          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-gray-800">Hello, User!</h1>
            <p className="text-gray-500 text-xs sm:text-sm">{dateStr}</p>
          </div>
        </div>

        <div className="flex items-center gap-2 sm:gap-4">
          {/* 搜索框 - 移動端隱藏 */}
          <form onSubmit={handleSearch} className="hidden md:block relative">
            <input
              type="text"
              placeholder="搜尋主題..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary w-48 lg:w-64"
              aria-label="搜尋主題"
              autoComplete="off"
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery('')}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                aria-label="清除搜索"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            )}
          </form>

          {/* 通知按鈕 */}
          <button className="relative p-2 text-gray-600 hover:text-gray-800">
            <svg className="w-5 h-5 sm:w-6 sm:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
            </svg>
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>

          {/* 用戶信息 - 移動端簡化 */}
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-primary to-secondary rounded-full"></div>
            <span className="hidden sm:inline text-gray-700 font-medium">User</span>
            <svg className="hidden sm:block w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
            </svg>
          </div>
        </div>
      </div>
    </header>
  )
}

