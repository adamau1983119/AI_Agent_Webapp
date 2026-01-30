import { useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import MainLayout from '@/components/layout/MainLayout'
import Dashboard from '@/pages/Dashboard'
import Topics from '@/pages/Topics'
import TopicDetail from '@/pages/TopicDetail'
import Preferences from '@/pages/Preferences'
import Schedule from '@/pages/Schedule'
// Phase 2: 會員系統頁面
import Login from '@/pages/Login'
import Register from '@/pages/Register'
import Settings from '@/pages/Settings'
import OAuthCallback from '@/pages/OAuthCallback'
// Phase 3: 內容功能頁面
import Channels from '@/pages/Channels'
import CreateChannel from '@/pages/CreateChannel'
import Inspiration from '@/pages/Inspiration'
// Phase 4: AI 個人化頁面
import StyleProfile from '@/pages/StyleProfile'
// Phase 5: 分發與整合頁面
import SocialConnect from '@/pages/SocialConnect'
import Publish from '@/pages/Publish'
import { initializeAuth } from '@/stores/authStore'

function App() {
  // 初始化認證狀態
  useEffect(() => {
    initializeAuth()
  }, [])

  return (
    <>
      <Routes>
        {/* 認證頁面（無 Layout） */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/oauth-callback" element={<OAuthCallback />} />
        
        {/* 主要頁面（有 Layout） */}
        <Route
          path="/*"
          element={
            <MainLayout>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/topics" element={<Topics />} />
                <Route path="/topics/:id" element={<TopicDetail />} />
                <Route path="/preferences" element={<Preferences />} />
                <Route path="/schedule" element={<Schedule />} />
                <Route path="/settings" element={<Settings />} />
                {/* Phase 3: 內容功能 */}
                <Route path="/channels" element={<Channels />} />
                <Route path="/channels/create" element={<CreateChannel />} />
                <Route path="/inspiration" element={<Inspiration />} />
                {/* Phase 4: AI 個人化 */}
                <Route path="/style-profile" element={<StyleProfile />} />
                {/* Phase 5: 分發與整合 */}
                <Route path="/social-connect" element={<SocialConnect />} />
                <Route path="/publish" element={<Publish />} />
              </Routes>
            </MainLayout>
          }
        />
      </Routes>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#363636',
            color: '#fff',
            borderRadius: '8px',
            padding: '12px 16px',
          },
          success: {
            duration: 3000,
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
          error: {
            duration: 4000,
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
    </>
  )
}

export default App
