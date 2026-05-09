/**
 * 登入頁面
 * Phase 2: 會員系統
 * Style: Lane Crawford 風格 - 高端極簡、黑白為主
 * Font: Cormorant Garamond (display) + Montserrat (sans)
 */
import { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useTranslation } from '../i18n';
import { useAuthStore } from '../stores/authStore';
import { authApi } from '../api/auth';

// 統一品牌設定
const BRAND = {
  name: 'INFLUENCERS',
  slogan: 'AI-POWERED CONTENT CREATION',
};

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
  
  // 如果已登入，重定向到 Dashboard
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
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
      navigate('/dashboard');
    }
  };
  
  const handleGoogleLogin = () => {
    window.location.href = authApi.getGoogleLoginUrl();
  };

  const handleGuestMode = () => {
    navigate('/topics');
  };
  
  return (
    <div className="min-h-screen bg-[#FAF9F7] flex font-sans">
      {/* 左側裝飾區 - 桌面版顯示 */}
      <div className="hidden lg:flex lg:w-1/2 bg-black items-center justify-center relative overflow-hidden">
        {/* 優雅的幾何裝飾 */}
        <div className="absolute inset-0 opacity-[0.08]">
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] border border-white rotate-45"></div>
        </div>
        
        <div className="relative z-10 text-center px-12">
          <h1 className="text-white font-display text-6xl font-light tracking-[0.4em] uppercase mb-8">
            {BRAND.name}
          </h1>
          <div className="w-24 h-px bg-white/50 mx-auto mb-8"></div>
          <p className="text-white/60 font-sans text-xs tracking-[0.25em] uppercase font-light">
            {BRAND.slogan}
          </p>
        </div>
      </div>
      
      {/* 右側表單區 */}
      <div className="w-full lg:w-1/2 flex flex-col">
        {/* 頂部導航 */}
        <header className="flex items-center justify-between px-8 py-6">
          <Link 
            to="/language" 
            data-testid="btn-login-back"
            className="text-gray-400 hover:text-black transition-colors text-[10px] tracking-[0.15em] uppercase"
          >
            ← {t('common.back')}
          </Link>
          <Link 
            to="/language" 
            data-testid="btn-login-lang"
            className="text-gray-400 hover:text-black transition-colors text-[10px] tracking-[0.15em] uppercase"
          >
            {t('common.language')}
          </Link>
        </header>

        {/* 主要內容區 */}
        <main className="flex-1 flex items-center justify-center px-8 py-8">
          <div className="w-full max-w-sm">
            {/* 移動端 Logo */}
            <div className="lg:hidden text-center mb-12">
              <h1 className="font-display text-3xl font-light tracking-[0.3em] uppercase text-black">
                {BRAND.name}
              </h1>
              <div className="w-16 h-px bg-black mx-auto mt-4 mb-4"></div>
              <p className="text-gray-400 text-[10px] tracking-[0.2em] uppercase font-light">
                {BRAND.slogan}
              </p>
            </div>

            {/* 標題 */}
            <div className="text-center mb-10">
              <h2 className="font-display text-2xl tracking-[0.1em] font-light text-black mb-3">
                {t('auth.login.title')}
              </h2>
              <p className="text-gray-400 text-xs font-light tracking-[0.1em] uppercase">
                {t('auth.login.welcomeBack')}
              </p>
            </div>
            
            {/* 錯誤訊息 */}
            {(error || oauthError) && (
              <div className="mb-8 p-4 border border-red-200 bg-red-50/50">
                <p className="text-red-500 text-xs text-center font-light tracking-wide">
                  {error || getOAuthErrorMessage(oauthError, t)}
                </p>
              </div>
            )}
            
            {/* 登入表單 */}
            <form data-testid="form-login" onSubmit={handleSubmit} className="space-y-6">
              {/* Email 輸入框 */}
              <div>
                <label 
                  htmlFor="email" 
                  className="block text-[10px] tracking-[0.15em] uppercase text-gray-500 mb-3"
                >
                  {t('common.email')}
                </label>
                <input
                  id="email"
                  data-testid="input-login-email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full px-0 py-3 bg-transparent border-0 border-b border-gray-200 text-black placeholder-gray-300 focus:outline-none focus:border-black transition-colors duration-300 text-sm tracking-wide"
                  placeholder="example@email.com"
                />
              </div>
              
              {/* 密碼輸入框 */}
              <div>
                <label 
                  htmlFor="password" 
                  className="block text-[10px] tracking-[0.15em] uppercase text-gray-500 mb-3"
                >
                  {t('auth.login.password').toUpperCase()}
                </label>
                <div className="relative">
                  <input
                    id="password"
                    data-testid="input-login-password"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="w-full px-0 py-3 bg-transparent border-0 border-b border-gray-200 text-black placeholder-gray-300 focus:outline-none focus:border-black transition-colors duration-300 pr-16 text-sm tracking-wide"
                    placeholder="••••••••"
                  />
                  <button
                    type="button"
                    data-testid="btn-login-toggle-password"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-0 top-1/2 -translate-y-1/2 p-2 text-gray-400 hover:text-black transition-colors"
                  >
                    {showPassword ? (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                      </svg>
                    ) : (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    )}
                  </button>
                </div>
              </div>

              {/* 忘記密碼 */}
              <div className="text-right pt-1">
                <Link
                  to="/forgot-password"
                  data-testid="link-login-forgot"
                  className="text-[10px] text-gray-400 hover:text-black transition-colors tracking-[0.1em] uppercase"
                >
                  {t('auth.login.forgotPassword')}
                </Link>
              </div>
              
              {/* 登入按鈕 */}
              <button
                type="submit"
                data-testid="btn-login-submit"
                disabled={isLoading}
                className="w-full py-4 bg-black text-white text-[11px] tracking-[0.2em] uppercase hover:bg-gray-900 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors duration-300"
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
                <span className="px-6 bg-[#FAF9F7] text-gray-400 text-[10px] tracking-[0.15em] uppercase">
                  {t('common.or')}
                </span>
              </div>
            </div>
            
            {/* Google 登入 */}
            <button
              type="button"
              data-testid="btn-login-google"
              onClick={handleGoogleLogin}
              className="w-full flex items-center justify-center gap-3 px-6 py-4 border border-gray-200 hover:border-black text-black text-[11px] tracking-[0.15em] uppercase transition-all duration-300"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24">
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
              data-testid="btn-login-guest"
              onClick={handleGuestMode}
              className="w-full mt-4 py-3 text-gray-400 hover:text-black text-[10px] tracking-[0.15em] uppercase transition-colors duration-300"
            >
              {t('auth.login.guestMode')}
            </button>
            
            {/* 分隔線 */}
            <div className="w-full h-px bg-gray-200 my-8"></div>
            
            {/* 註冊連結 */}
            <p className="text-center text-gray-400 text-xs font-light tracking-wide">
              {t('auth.login.noAccount')}{' '}
              <Link
                to="/register"
                data-testid="link-login-register"
                className="text-black underline hover:no-underline transition-all"
              >
                {t('auth.login.registerLink')}
              </Link>
            </p>

            {/* 底部裝飾線 */}
            <div className="mt-12 flex justify-center">
              <div className="w-16 h-px bg-gray-200"></div>
            </div>
          </div>
        </main>

        {/* 底部版權 - 僅移動端顯示 */}
        <footer className="lg:hidden py-6 text-center">
          <p className="text-gray-400 text-[10px] tracking-[0.15em] uppercase">© 2026 {BRAND.name}</p>
        </footer>
      </div>
    </div>
  );
}

// OAuth 錯誤訊息對照
function getOAuthErrorMessage(error: string | null, t: (key: string) => string): string {
  if (!error) return '';
  
  const errorMessages: Record<string, string> = {
    'access_denied': t('error.oauth.accessDenied'),
    'no_code': t('error.oauth.noCode'),
    'token_exchange_failed': t('error.oauth.tokenFailed'),
    'user_info_failed': t('error.oauth.userInfoFailed'),
    'database_unavailable': t('error.oauth.databaseUnavailable'),
    'max_users_reached': t('error.maxUsers'),
    'oauth_failed': t('error.oauth.failed'),
  };
  
  return errorMessages[error] || t('error.oauth.failed');
}
