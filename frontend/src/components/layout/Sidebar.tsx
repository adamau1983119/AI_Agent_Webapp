import { Link, useLocation } from 'react-router-dom'
import { useUIStore } from '@/stores/uiStore'
import { useAuthStore } from '@/stores/authStore'
import { useTranslation } from '@/i18n'

/** v7 導航可見性（對齊 專案完整架構表_v7.md 「前端路由」） */
type V7NavVisibility = 'show' | 'hide' | 'beta'

const menuItemsConfig: Array<{
  path: string
  labelKey: string
  icon: string
  testId: string
  v7Nav: V7NavVisibility
}> = [
  { path: '/dashboard', labelKey: 'nav.dashboard', icon: 'home', testId: 'link-sidebar-dashboard', v7Nav: 'show' },
  { path: '/topics', labelKey: 'nav.topics', icon: 'document', testId: 'link-sidebar-topics', v7Nav: 'show' },
  { path: '/discover', labelKey: 'nav.discover', icon: 'compass', testId: 'link-sidebar-discover', v7Nav: 'show' },
  { path: '/my-channel', labelKey: 'nav.channels', icon: 'channel', testId: 'link-sidebar-my-channel', v7Nav: 'show' },
  { path: '/channels', labelKey: 'nav.channelList', icon: 'channel', testId: 'link-sidebar-channels', v7Nav: 'show' },
  { path: '/inspiration', labelKey: 'nav.inspiration', icon: 'lightbulb', testId: 'link-sidebar-inspiration', v7Nav: 'show' },
  { path: '/style-profile', labelKey: 'nav.styleProfile', icon: 'sparkles', testId: 'link-sidebar-style', v7Nav: 'hide' },
  { path: '/publish', labelKey: 'nav.publish', icon: 'rocket', testId: 'link-sidebar-publish', v7Nav: 'beta' },
  { path: '/social-connect', labelKey: 'nav.socialConnect', icon: 'link', testId: 'link-sidebar-social', v7Nav: 'beta' },
  { path: '/preferences', labelKey: 'nav.preferences', icon: 'settings', testId: 'link-sidebar-preferences', v7Nav: 'show' },
  { path: '/schedule', labelKey: 'nav.schedule', icon: 'calendar', testId: 'link-sidebar-schedule', v7Nav: 'hide' },
]

const visibleMenuItems = menuItemsConfig.filter((item) => item.v7Nav !== 'hide')

export default function Sidebar() {
  const location = useLocation()
  const { t } = useTranslation()
  const { setCurrentPage, sidebarOpen, setSidebarOpen } = useUIStore()
  const { logout, isAuthenticated } = useAuthStore()

  const handleClick = (path: string) => {
    setCurrentPage(path === '/dashboard' ? 'dashboard' : path.slice(1))
    // 移動端點擊後關閉側邊欄
    if (window.innerWidth < 1024) {
      setSidebarOpen(false)
    }
  }

  const handleLogout = () => {
    logout()
    window.location.href = '/login'
  }

  return (
    <aside
      className={`fixed lg:static inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 flex flex-col transform transition-transform duration-300 ease-in-out ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
      }`}
    >
      {/* Logo - Influencers AI */}
      <div className="p-6 border-b border-gray-200">
        <Link to="/dashboard" data-testid="link-sidebar-logo" className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-cyan-500 rounded-xl flex items-center justify-center shadow-lg">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
            </svg>
          </div>
          <div className="flex flex-col">
            <span className="text-lg font-bold bg-gradient-to-r from-purple-600 to-cyan-600 bg-clip-text text-transparent">
              {t('brand.name')}
            </span>
            <span className="text-[10px] text-gray-500 -mt-0.5">{t('brand.tagline')}</span>
          </div>
        </Link>
      </div>

      {/* 導航選單 */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {visibleMenuItems.map((item) => {
            const isActive = location.pathname === item.path
            return (
              <li key={item.path}>
                <Link
                  to={item.path}
                  data-testid={item.testId}
                  onClick={() => handleClick(item.path)}
                  className={`sidebar-item ${isActive ? 'active' : ''}`}
                >
                  <Icon name={item.icon} />
                  <span className="flex-1 min-w-0">{t(item.labelKey as any)}</span>
                  {item.v7Nav === 'beta' && (
                    <span className="shrink-0 text-[10px] font-medium text-amber-700 bg-amber-50 border border-amber-200 px-1.5 py-0.5 rounded">
                      {t('feature.beta')}
                    </span>
                  )}
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>

      {/* 登出 */}
      {isAuthenticated && (
        <div className="p-4 border-t border-gray-200">
          <button data-testid="btn-sidebar-logout" onClick={handleLogout} className="sidebar-item w-full text-red-600 hover:bg-red-50">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
            </svg>
            <span>{t('nav.logout')}</span>
          </button>
        </div>
      )}
    </aside>
  )
}

// 圖示元件
function Icon({ name }: { name: string }) {
  const icons: Record<string, JSX.Element> = {
    home: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
      </svg>
    ),
    document: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
      </svg>
    ),
    settings: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"></path>
      </svg>
    ),
    calendar: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
      </svg>
    ),
    channel: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
      </svg>
    ),
    lightbulb: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
      </svg>
    ),
    sparkles: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"></path>
      </svg>
    ),
    rocket: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
      </svg>
    ),
    link: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path>
      </svg>
    ),
    compass: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 2a10 10 0 100 20 10 10 0 000-20zm0 4l1.5 5.5L19 13l-5.5 1.5L12 20l-1.5-5.5L5 13l5.5-1.5L12 6z"></path>
      </svg>
    ),
  }
  return icons[name] || icons.home
}

