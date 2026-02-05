/**
 * 頁面標題 Hook
 * 根據當前路由動態設定頁面標題
 * 支援多語言
 */
import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { useTranslation } from '@/i18n'

const BRAND_NAME = 'Influencers AI'

export function usePageTitle(customTitle?: string) {
  const location = useLocation()
  const { t } = useTranslation()

  useEffect(() => {
    // 根據路由取得對應的翻譯 key
    const pageTitleKeys: Record<string, string> = {
      '/': 'nav.dashboard',
      '/topics': 'nav.topics',
      '/channels': 'nav.channels',
      '/inspiration': 'nav.inspiration',
      '/style-profile': 'nav.styleProfile',
      '/publish': 'nav.publish',
      '/social-connect': 'nav.socialConnect',
      '/preferences': 'nav.settings',
      '/schedule': 'nav.schedule',
      '/settings': 'nav.settings',
      '/login': 'nav.login',
      '/register': 'nav.register',
    }

    const titleKey = pageTitleKeys[location.pathname]
    const pageTitle = titleKey ? t(titleKey as any) : ''
    
    const title = customTitle 
      ? `${customTitle} - ${BRAND_NAME}`
      : pageTitle 
        ? `${pageTitle} - ${BRAND_NAME}`
        : BRAND_NAME
        
    document.title = title
  }, [location.pathname, customTitle, t])
}


