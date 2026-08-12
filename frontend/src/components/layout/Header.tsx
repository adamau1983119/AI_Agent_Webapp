import { format } from 'date-fns'
import { zhTW, enUS, ja } from 'date-fns/locale'
import { useState, FormEvent, useRef, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import { useUIStore } from '@/stores/uiStore'
import { useAuthStore } from '@/stores/authStore'
import { useTranslation, languageOptions, Language } from '@/i18n'

export default function Header() {
  const { t, language, setLanguage } = useTranslation()
  const queryClient = useQueryClient()
  const today = new Date()
  
  // 根據語言選擇日期格式和地區
  // 注意：日期格式字符串中的中文/日文字符是格式符號的一部分，不是用戶可見文字
  // 這些格式字符串是 date-fns 庫使用的格式模板，不需要 i18n
  const dateLocales = { 'zh-TW': zhTW, 'en': enUS, 'ja': ja }
  const dateFormats = { 
    'zh-TW': 'yyyy年M月d日 EEEE', // 格式模板，不是用戶可見文字
    'en': 'EEEE, MMMM d', 
    'ja': 'yyyy年M月d日(EEEE)' // 格式模板，不是用戶可見文字
  }
  const dateStr = format(today, dateFormats[language] || dateFormats['en'], { 
    locale: dateLocales[language] || dateLocales['en'] 
  })
  const { toggleSidebar } = useUIStore()
  const { user, isAuthenticated, logout } = useAuthStore()
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState('')
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [showLangMenu, setShowLangMenu] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)
  const langMenuRef = useRef<HTMLDivElement>(null)

  // 點擊外部關閉選單
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setShowUserMenu(false)
      }
      if (langMenuRef.current && !langMenuRef.current.contains(event.target as Node)) {
        setShowLangMenu(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // 處理語言切換
  const handleLanguageChange = (lang: Language) => {
    setLanguage(lang)
    localStorage.setItem('preferred-language', lang)
    setShowLangMenu(false)
    void queryClient.invalidateQueries({ queryKey: ['publicFeed'] })
    void queryClient.invalidateQueries({ queryKey: ['topics'] })
    void queryClient.invalidateQueries({ queryKey: ['topic'] })
    void queryClient.invalidateQueries({ queryKey: ['content'] })
  }

  // 當前語言的顯示信息
  const currentLangOption = languageOptions.find(opt => opt.code === language) || languageOptions[0]

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

  const handleLogout = () => {
    logout()
    setShowUserMenu(false)
    navigate('/login')
  }

  // 取得顯示名稱和問候語
  const displayName = user?.name || user?.email?.split('@')[0] || t('greeting.guest')
  const greeting = isAuthenticated 
    ? `${t('greeting.hello')}, ${displayName}!` 
    : `${t('greeting.hello')}, ${t('greeting.guest')}!`

  return (
    <header className="bg-white border-b border-gray-200 px-4 sm:px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          {/* 移動端漢堡菜單按鈕 */}
          <button
            data-testid="btn-header-menu"
            onClick={toggleSidebar}
            className="lg:hidden p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg"
            aria-label={t('common.toggleSidebar')}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16"></path>
            </svg>
          </button>

          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-gray-800">{greeting}</h1>
            <p className="text-gray-500 text-xs sm:text-sm">{dateStr}</p>
          </div>
        </div>

        <div className="flex items-center gap-2 sm:gap-4">
          {/* 搜索框 - 移動端隱藏 */}
          <form data-testid="form-header-search" onSubmit={handleSearch} className="hidden md:block relative">
            <input
              data-testid="input-header-search"
              type="text"
              placeholder={t('topics.searchPlaceholder')}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary w-48 lg:w-64"
              aria-label={t('topics.searchPlaceholder')}
              autoComplete="off"
            />
            {searchQuery && (
              <button
                data-testid="btn-header-search-clear"
                type="button"
                onClick={() => setSearchQuery('')}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                aria-label={t('common.clearSearch')}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            )}
          </form>

          {/* 通知按鈕 */}
          <button data-testid="btn-header-notification" className="relative p-2 text-gray-600 hover:text-gray-800">
            <svg className="w-5 h-5 sm:w-6 sm:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
            </svg>
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>

          {/* 語言選擇器 */}
          <div className="relative" ref={langMenuRef}>
            <button
              data-testid="btn-header-lang"
              onClick={() => setShowLangMenu(!showLangMenu)}
              className="flex items-center gap-1.5 px-2 py-1.5 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
              title={t('common.changeLanguage')}
            >
              <span className="text-lg font-medium">{currentLangOption.icon}</span>
              <span className="hidden sm:inline text-sm font-medium">{currentLangOption.shortName}</span>
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
              </svg>
            </button>

            {/* 語言下拉選單 */}
            {showLangMenu && (
              <div data-testid="menu-header-lang" className="absolute right-0 mt-2 w-44 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase border-b border-gray-100">
                  {t('common.language')}
                </div>
                {languageOptions.map((option) => (
                  <button
                    key={option.code}
                    data-testid={`btn-header-lang-${option.code === 'zh-TW' ? 'zh' : option.code}`}
                    onClick={() => handleLanguageChange(option.code)}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 text-sm hover:bg-gray-50 transition-colors ${
                      language === option.code ? 'bg-purple-50 text-purple-700' : 'text-gray-700'
                    }`}
                  >
                    <span className="text-lg font-medium">{option.icon}</span>
                    <span className="flex-1 text-left">{option.name}</span>
                    {language === option.code && (
                      <svg className="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                      </svg>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* 用戶信息 */}
          {isAuthenticated ? (
            <div className="relative" ref={menuRef}>
              <button
                data-testid="btn-header-user"
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center gap-2 hover:opacity-80 transition-opacity"
              >
                {/* 頭像 */}
                {user?.avatar_url ? (
                  <img
                    src={user.avatar_url}
                    alt={displayName}
                    className="w-8 h-8 sm:w-10 sm:h-10 rounded-full object-cover"
                  />
                ) : (
                  <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-purple-500 to-cyan-500 rounded-full flex items-center justify-center text-white font-bold">
                    {displayName.charAt(0).toUpperCase()}
                  </div>
                )}
                <span className="hidden sm:inline text-gray-700 font-medium max-w-[120px] truncate">
                  {displayName}
                </span>
                <svg className="hidden sm:block w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
                </svg>
              </button>

              {/* 下拉選單 */}
              {showUserMenu && (
                <div data-testid="menu-header-user" className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                  <div className="px-4 py-2 border-b border-gray-100">
                    <p className="text-sm font-medium text-gray-800 truncate">{displayName}</p>
                    <p className="text-xs text-gray-500 truncate">{user?.email}</p>
                  </div>
                  <Link
                    to="/settings"
                    data-testid="link-header-settings"
                    onClick={() => setShowUserMenu(false)}
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    {t('nav.settings')}
                  </Link>
                  <button
                    data-testid="btn-header-logout"
                    onClick={handleLogout}
                    className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                  >
                    {t('nav.logout')}
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                to="/login"
                data-testid="link-header-login"
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
              >
                {t('nav.login')}
              </Link>
              <Link
                to="/register"
                data-testid="link-header-register"
                className="px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-purple-500 to-cyan-500 rounded-lg hover:opacity-90"
              >
                {t('nav.register')}
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
