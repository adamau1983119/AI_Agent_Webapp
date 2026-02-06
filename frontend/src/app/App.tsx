import { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import MainLayout from '@/components/layout/MainLayout'
import Dashboard from '@/pages/Dashboard'
import Topics from '@/pages/Topics'
import TopicDetail from '@/pages/TopicDetail'
import Preferences from '@/pages/Preferences'
import Schedule from '@/pages/Schedule'
// Phase 1: 登入/註冊頁面
import LanguageSelection from '@/pages/LanguageSelection'
import Login from '@/pages/Login'
import Register from '@/pages/Register'
import ForgotPassword from '@/pages/ForgotPassword'
import OAuthCallback from '@/pages/OAuthCallback'
import VerifyEmail from '@/pages/VerifyEmail'
import Terms from '@/pages/Terms'
import Privacy from '@/pages/Privacy'
// Phase 2: 會員系統頁面
import Settings from '@/pages/Settings'
// Phase 3: 內容功能頁面
import Channels from '@/pages/Channels'
import CreateChannel from '@/pages/CreateChannel'
import ChannelDetail from '@/pages/ChannelDetail'
import ChannelEdit from '@/pages/ChannelEdit'
import Inspiration from '@/pages/Inspiration'
// Phase 4: AI 個人化頁面
import StyleProfile from '@/pages/StyleProfile'
// Phase 5: 分發與整合頁面
import SocialConnect from '@/pages/SocialConnect'
import Publish from '@/pages/Publish'
import { initializeAuth } from '@/stores/authStore'

// 根路徑重定向：已登入 → 主題列表，新用戶 → 語言選擇，已選語言 → 登入
function RootRedirect() {
  const hasLanguage = localStorage.getItem('preferred-language');
  const token = localStorage.getItem('auth_token');
  
  // 已登入用戶直接進入主題列表（與訪客模式相同的內容，但有完整功能）
  if (token) {
    return <Navigate to="/topics" replace />;
  }
  
  // 新用戶（未選語言）→ 語言選擇
  if (!hasLanguage) {
    return <Navigate to="/language" replace />;
  }
  
  // 已選語言但未登入 → 登入頁
  return <Navigate to="/login" replace />;
}

function App() {
  // 初始化認證狀態
  useEffect(() => {
    initializeAuth()
  }, [])

  return (
    <>
      <Routes>
        {/* 根路徑：重定向到語言選擇或登入頁 */}
        <Route path="/" element={<RootRedirect />} />
        
        {/* Phase 1: 認證頁面（無 Layout） */}
        <Route path="/language" element={<LanguageSelection />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/oauth-callback" element={<OAuthCallback />} />
        <Route path="/verify-email" element={<VerifyEmail />} />
        <Route path="/terms" element={<Terms />} />
        <Route path="/privacy" element={<Privacy />} />
        
        {/* 主要頁面（有 Layout） */}
        <Route
          path="/*"
          element={
            <MainLayout>
              <Routes>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/topics" element={<Topics />} />
                <Route path="/topics/:id" element={<TopicDetail />} />
                <Route path="/preferences" element={<Preferences />} />
                <Route path="/schedule" element={<Schedule />} />
                <Route path="/settings" element={<Settings />} />
                {/* Phase 3: 內容功能 */}
                <Route path="/channels" element={<Channels />} />
                <Route path="/channels/create" element={<CreateChannel />} />
                <Route path="/channels/:id" element={<ChannelDetail />} />
                <Route path="/channels/:id/edit" element={<ChannelEdit />} />
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
