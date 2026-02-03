/**
 * 登入頁面
 * Phase 2: 會員系統
 * Style: Lane Crawford 風格 - 高端極簡、黑白為主
 */
import { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useTranslation } from '../i18n';
import { useAuthStore } from '../stores/authStore';
import { authApi } from '../api/auth';

export default function Login() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  
  const { login, isLoading, error, clearError, isAuthenticated } = useAuthStore();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  
  // 處理 OAuth 錯誤
  const oauthError = searchParams.get('error');
  
  // 如果已登入，重定向到首頁
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);
  
  // 清除錯誤
  useEffect(() => {
    return () => clearError();
  }, [clearError]);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    
    const success = await login({ email, password });
    if (success) {
      navigate('/');
    }
  };
  
  const handleGoogleLogin = () => {
    window.location.href = authApi.getGoogleLoginUrl();
  };

  const handleGuestMode = () => {
    navigate('/topics');
  };
  
  return (
    <div className="min-h-screen bg-[#FAF9F7] flex">
      {/* 左側裝飾區 - 桌面版顯示 */}
      <div className="hidden lg:flex lg:w-1/2 bg-black items-center justify-center relative overflow-hidden">
        {/* 優雅的幾何裝飾 */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-20 w-40 h-40 border border-white"></div>
          <div className="absolute bottom-20 right-20 w-60 h-60 border border-white"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 border border-white rotate-45"></div>
        </div>
        
        <div className="relative z-10 text-center px-12">
          <h1 className="text-white text-5xl font-light tracking-[0.3em] uppercase mb-6">
            Influencers
          </h1>
          <div className="w-24 h-px bg-white mx-auto mb-6"></div>
          <p className="text-white/70 text-sm tracking-[0.15em] uppercase font-light">
            AI-Powered Content Creation
          </p>
        </div>
      </div>
      
      {/* 右側表單區 */}
      <div className="w-full lg:w-1/2 flex flex-col">
        {/* 頂部導航 */}
        <header className="flex items-center justify-between px-8 py-6">
          <Link 
            to="/language" 
            className="text-gray-500 hover:text-black transition-colors text-xs tracking-[0.1em] uppercase"
          >
            ← {t('common.back')}
          </Link>
          <Link 
            to="/language" 
            className="text-gray-500 hover:text-black transition-colors text-xs tracking-[0.1em] uppercase"
          >
            {t('common.language')}
          </Link>
        </header>

        {/* 主要內容區 */}
        <main className="flex-1 flex items-center justify-center px-8 py-8">
          <div className="w-full max-w-sm">
            {/* 移動端 Logo */}
            <div className="lg:hidden text-center mb-12">
              <h1 className="text-3xl font-light tracking-[0.2em] uppercase text-black">
                Influencers
              </h1>
              <div className="w-16 h-px bg-black mx-auto mt-4"></div>
            </div>

            {/* 標題 */}
            <div className="text-center mb-10">
              <h2 className="text-xl tracking-[0.15em] uppercase font-light text-black mb-3">
                {t('auth.login.title')}
              </h2>
              <p className="text-gray-500 text-sm font-light">
                {t('auth.login.welcome')}
              </p>
            </div>
            
            {/* 錯誤訊息 */}
            {(error || oauthError) && (
              <div className="mb-8 p-4 border border-red-200 bg-red-50">
                <p className="text-red-600 text-sm text-center font-light">
                  {error || getOAuthErrorMessage(oauthError, t)}
                </p>
              </div>
            )}
            
            {/* 登入表單 */}
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Email 輸入框 */}
              <div>
                <label 
                  htmlFor="email" 
                  className="block text-xs tracking-[0.1em] uppercase text-gray-600 mb-3"
                >
                  Email
                </label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full px-0 py-3 bg-transparent border-0 border-b border-gray-300 text-black placeholder-gray-400 focus:outline-none focus:border-black transition-colors duration-300 text-sm"
                  placeholder="example@email.com"
                />
              </div>
              
              {/* 密碼輸入框 */}
              <div>
                <label 
                  htmlFor="password" 
                  className="block text-xs tracking-[0.1em] uppercase text-gray-600 mb-3"
                >
                  {t('auth.login.password')}
                </label>
                <div className="relative">
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="w-full px-0 py-3 bg-transparent border-0 border-b border-gray-300 text-black placeholder-gray-400 focus:outline-none focus:border-black transition-colors duration-300 pr-16 text-sm"
                    placeholder="••••••••"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-0 top-1/2 -translate-y-1/2 text-gray-400 hover:text-black text-xs tracking-wide uppercase transition-colors"
                  >
                    {showPassword ? t('common.hide') : t('common.show')}
                  </button>
                </div>
              </div>

              {/* 忘記密碼 */}
              <div className="text-right pt-1">
                <Link
                  to="/forgot-password"
                  className="text-xs text-gray-500 hover:text-black transition-colors tracking-wide"
                >
                  {t('auth.login.forgotPassword')}
                </Link>
              </div>
              
              {/* 登入按鈕 */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-4 bg-black text-white text-xs tracking-[0.2em] uppercase hover:bg-gray-900 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors duration-300"
              >
                {isLoading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    {t('common.loading')}
                  </span>
                ) : (
                  t('auth.login.submit')
                )}
              </button>
            </form>
            
            {/* 分隔線 */}
            <div className="relative my-8">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-200"></div>
              </div>
              <div className="relative flex justify-center">
                <span className="px-6 bg-[#FAF9F7] text-gray-400 text-xs tracking-[0.1em] uppercase">
                  {t('common.or')}
                </span>
              </div>
            </div>
            
            {/* Google 登入 */}
            <button
              type="button"
              onClick={handleGoogleLogin}
              className="w-full flex items-center justify-center gap-3 px-6 py-4 border border-gray-300 hover:border-black text-black text-xs tracking-[0.1em] uppercase transition-all duration-300"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              {t('auth.login.googleLogin')}
            </button>

            {/* 訪客瀏覽 */}
            <button
              type="button"
              onClick={handleGuestMode}
              className="w-full mt-4 py-3 text-gray-400 hover:text-black text-xs tracking-[0.1em] uppercase transition-colors duration-300"
            >
              {t('auth.login.guestMode')}
            </button>
            
            {/* 分隔線 */}
            <div className="w-full h-px bg-gray-200 my-8"></div>
            
            {/* 註冊連結 */}
            <p className="text-center text-gray-500 text-sm font-light">
              {t('auth.login.noAccount')}{' '}
              <Link
                to="/register"
                className="text-black underline hover:no-underline transition-all"
              >
                {t('auth.login.registerLink')}
              </Link>
            </p>

            {/* 底部裝飾線 */}
            <div className="mt-12 flex justify-center">
              <div className="w-16 h-px bg-gray-300"></div>
            </div>
          </div>
        </main>

        {/* 底部版權 - 僅移動端顯示 */}
        <footer className="lg:hidden py-6 text-center">
          <p className="text-gray-400 text-xs tracking-wide">© 2026 Influencers AI</p>
        </footer>
      </div>
    </div>
  );
}

// OAuth 錯誤訊息對照
function getOAuthErrorMessage(error: string | null, t: (key: string) => string): string {
  if (!error) return '';
  
  const errorMessages: Record<string, string> = {
    'access_denied': '您已取消 Google 登入',
    'no_code': '無法取得授權碼',
    'token_exchange_failed': 'Google 授權失敗，請重試',
    'user_info_failed': '無法取得 Google 帳號資訊',
    'max_users_reached': t('error.maxUsers'),
    'oauth_failed': 'Google 登入失敗，請重試',
  };
  
  return errorMessages[error] || 'Google 登入失敗';
}
