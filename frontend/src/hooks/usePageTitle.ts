/**
 * 頁面標題 Hook
 * 根據當前路由動態設定頁面標題
 */
import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

const pageTitles: Record<string, string> = {
  '/': 'AI代理Web應用程式 - 控制面板',
  '/topics': 'AI代理Web應用程式 - 主題列表',
  '/preferences': 'AI代理Web應用程式 - 設定',
  '/schedule': 'AI代理Web應用程式 - 排程',
}

export function usePageTitle(customTitle?: string) {
  const location = useLocation()

  useEffect(() => {
    const title = customTitle || pageTitles[location.pathname] || 'AI代理Web應用程式'
    document.title = title
  }, [location.pathname, customTitle])
}


