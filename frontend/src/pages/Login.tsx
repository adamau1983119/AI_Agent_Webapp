/**
 * 登入頁面
 * Phase 2: 會員系統
 * 設計風格：Lane Crawford 高端時尚電商
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
  const [emailFocused, setEmailFocused] = useState(false);
  const [passwordFocused, setPasswordFocused] = useState(false);
  
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
    <div className="min-h-screen bg-white flex flex-col">
      {/* 頂部導航 */}
      <header className="flex items-center justify-between px-6 py-4">
        <Link 
          to="/language" 
          className="text-gray-600 hover:text-black transition-colors text-sm"
        >
          ← {t('common.back')}
        </Link>
        <Link 
          to="/language" 
          className="text-gray-600 hover:text-black transition-colors text-sm"
        >
          🌐 {t('common.language')}
        </Link>
      </header>

      {/* 主要內容區 */}
      <main className="flex-1 flex items-center justify-center px-6 py-8">
        <div className="w-full max-w-sm">
          {/* Logo */}
          <div className="text-center mb-12">
            <div className="w-20 h-20 mx-auto mb-6 bg-black rounded-full flex items-center justify-center">
              <span className="text-white text-2xl font-serif">IA</span>
            </div>
            <h1 className="text-3xl font-serif text-black tracking-wide">
              Influencers AI
            </h1>
            <p className="text-gray-500 mt-2 text-sm">Agents</p>
          </div>

          {/* 分隔線 */}
          <div className="w-16 h-px bg-gray-300 mx-auto mb-8"></div>

          {/* 歡迎文字 */}
          <div className="text-center mb-10">
            <h2 className="text-xl text-black mb-1">{t('auth.login.welcome')}</h2>
            <p className="text-gray-500 text-sm">Welcome Back</p>
          </div>
          
          {/* 錯誤訊息 */}
          {(error || oauthError) && (
            <div className="mb-6 p-4 border border-red-300 bg-red-50">
              <p className="text-red-600 text-sm text-center">
                {error || getOAuthErrorMessage(oauthError, t)}
              </p>
            </div>
          )}
          
          {/* 登入表單 */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email 輸入框 - 底線樣式 */}
            <div>
              <label 
                htmlFor="email" 
                className={`block text-sm mb-2 transition-colors ${
                  emailFocused ? 'text-black' : 'text-gray-500'
                }`}
              >
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onFocus={() => setEmailFocused(true)}
                onBlur={() => setEmailFocused(false)}
                required
                className="w-full py-3 bg-transparent border-0 border-b-2 border-gray-300 text-black placeholder-gray-400 focus:outline-none focus:border-black transition-colors"
                placeholder="example@email.com"
              />
            </div>
            
            {/* 密碼輸入框 - 底線樣式 */}
            <div>
              <label 
                htmlFor="password" 
                className={`block text-sm mb-2 transition-colors ${
                  passwordFocused ? 'text-black' : 'text-gray-500'
                }`}
              >
                {t('auth.login.password')} Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  onFocus={() => setPasswordFocused(true)}
                  onBlur={() => setPasswordFocused(false)}
                  required
                  className="w-full py-3 bg-transparent border-0 border-b-2 border-gray-300 text-black placeholder-gray-400 focus:outline-none focus:border-black transition-colors pr-16"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-0 top-1/2 -translate-y-1/2 text-gray-500 hover:text-black text-sm transition-colors"
                >
                  {showPassword ? t('common.hide') : t('common.show')}
                </button>
              </div>
            </div>

            {/* 忘記密碼 */}
            <div className="text-right">
              <Link
                to="/forgot-password"
                className="text-sm text-gray-500 hover:text-black transition-colors"
              >
                {t('auth.login.forgotPassword')}
              </Link>
            </div>
            
            {/* 登入按鈕 - 黑底白字 */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-4 bg-black text-white text-sm font-medium tracking-wider uppercase hover:bg-gray-800 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  {t('common.loading')}
                </span>
              ) : (
                <>登入 LOGIN</>
              )}
            </button>
          </form>
          
          {/* 分隔線 */}
          <div className="flex items-center my-8">
            <div className="flex-1 h-px bg-gray-300"></div>
            <span className="px-4 text-gray-400 text-sm">{t('common.or')} OR</span>
            <div className="flex-1 h-px bg-gray-300"></div>
          </div>
          
          {/* Google 登入 - 白底黑框 */}
          <button
            type="button"
            onClick={handleGoogleLogin}
            className="w-full flex items-center justify-center gap-3 py-4 border-2 border-black text-black text-sm font-medium tracking-wider uppercase hover:bg-black hover:text-white transition-colors"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path
                fill="currentColor"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="currentColor"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="currentColor"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="currentColor"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            {t('auth.login.googleLogin')}
          </button>

          {/* 訪客瀏覽 */}
          <button
            type="button"
            onClick={handleGuestMode}
            className="w-full mt-4 py-3 text-gray-500 hover:text-black text-sm transition-colors"
          >
            👤 {t('auth.login.guestMode')} Guest
          </button>
          
          {/* 分隔線 */}
          <div className="w-full h-px bg-gray-200 my-8"></div>
          
          {/* 註冊連結 */}
          <p className="text-center text-gray-500 text-sm">
            {t('auth.login.noAccount')}{' '}
            <Link
              to="/register"
              className="text-black hover:underline font-medium"
            >
              {t('auth.login.registerLink')} →
            </Link>
          </p>
        </div>
      </main>

      {/* 底部版權 */}
      <footer className="py-6 text-center">
        <p className="text-gray-400 text-xs">© 2026 Influencers AI</p>
      </footer>
    </div>
  );
}

// OAuth 錯誤訊息對照
function getOAuthErrorMessage(error: string | null, t: any): string {
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
