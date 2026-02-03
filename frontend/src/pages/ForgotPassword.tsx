/**
 * 忘記密碼頁面
 * Phase 2: 會員系統
 * Style: Lane Crawford 風格 - 高端極簡、黑白為主
 * Font: Cormorant Garamond (display) + Montserrat (sans)
 */
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation, Language } from '../i18n';
import { authApi } from '../api/auth';

// 統一品牌設定
const BRAND = {
  name: 'INFLUENCERS',
  slogan: 'AI-POWERED CONTENT CREATION',
};

export default function ForgotPassword() {
  const { t, language, setLanguage } = useTranslation();
  const navigate = useNavigate();
  
  const [email, setEmail] = useState('');
  const [emailError, setEmailError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState('');
  
  // Email 驗證
  const validateEmail = (value: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!value) {
      setEmailError('');
      return false;
    }
    if (!emailRegex.test(value)) {
      setEmailError('請輸入有效的 Email 地址');
      return false;
    }
    setEmailError('');
    return true;
  };
  
  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setEmail(value);
    validateEmail(value);
    setError('');
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (!validateEmail(email)) {
      return;
    }
    
    setIsLoading(true);
    try {
      await authApi.forgotPassword(email);
      setIsSuccess(true);
    } catch (err: any) {
      setError(err.message || '發送失敗，請稍後再試');
    } finally {
      setIsLoading(false);
    }
  };
  
  // 語言選項
  const languageLabels: Record<Language, string> = {
    'zh-TW': '繁中',
    'en': 'EN',
    'ja': '日本語'
  };
  
  // 成功畫面
  if (isSuccess) {
    return (
      <div className="min-h-screen bg-[#FAF9F7] flex items-center justify-center font-sans">
        <div className="w-full max-w-md px-8 py-16 text-center">
          {/* 成功圖標 */}
          <div className="w-20 h-20 mx-auto mb-8 border border-black flex items-center justify-center">
            <svg className="w-8 h-8 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          
          <h2 className="font-display text-2xl tracking-[0.15em] uppercase font-light text-black mb-4">
            {t('auth.forgot.success')}
          </h2>
          
          <div className="w-12 h-px bg-black mx-auto mb-6"></div>
          
          <p className="text-gray-500 text-sm font-light mb-2">
            我們已發送重設連結到
          </p>
          <p className="text-black font-light mb-6 tracking-wide">
            {email}
          </p>
          <p className="text-[10px] text-gray-400 mb-10 tracking-[0.1em] uppercase">
            請在 24 小時內完成密碼重設
          </p>
          
          <Link
            to="/login"
            className="inline-block px-12 py-4 bg-black text-white text-[11px] tracking-[0.2em] uppercase hover:bg-gray-900 transition-colors duration-300"
          >
            BACK TO LOGIN
          </Link>
          
          <p className="mt-8 text-[10px] text-gray-400 tracking-wide">
            沒收到郵件？請檢查垃圾郵件資料夾
          </p>
        </div>
      </div>
    );
  }
  
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
          <button
            onClick={() => navigate('/login')}
            className="text-gray-400 hover:text-black transition-colors text-[10px] tracking-[0.15em] uppercase"
          >
            ← {t('common.back')}
          </button>
          <button
            onClick={() => {
              const langs: Language[] = ['zh-TW', 'en', 'ja'];
              const currentIndex = langs.indexOf(language);
              const nextLang = langs[(currentIndex + 1) % langs.length];
              setLanguage(nextLang);
            }}
            className="text-gray-400 hover:text-black transition-colors text-[10px] tracking-[0.15em] uppercase"
          >
            {languageLabels[language]}
          </button>
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
                {t('auth.forgot.title')}
              </h2>
              <p className="text-gray-400 text-xs font-light tracking-[0.1em] uppercase">
                RESET YOUR PASSWORD
              </p>
            </div>
            
            {/* 說明文字 */}
            <p className="text-center text-gray-500 text-sm font-light mb-8">
              {t('auth.forgot.subtitle')}
            </p>
            
            {/* 錯誤訊息 */}
            {error && (
              <div className="mb-8 p-4 border border-red-200 bg-red-50/50">
                <p className="text-red-500 text-xs text-center font-light tracking-wide">{error}</p>
              </div>
            )}
            
            {/* 表單 */}
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Email 輸入框 */}
              <div>
                <label htmlFor="email" className="block text-[10px] tracking-[0.15em] uppercase text-gray-500 mb-3">
                  EMAIL
                </label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={handleEmailChange}
                  onBlur={() => validateEmail(email)}
                  required
                  className={`w-full px-0 py-3 bg-transparent border-0 border-b text-black placeholder-gray-300 focus:outline-none transition-colors duration-300 text-sm tracking-wide ${
                    emailError
                      ? 'border-red-300 focus:border-red-500'
                      : 'border-gray-200 focus:border-black'
                  }`}
                  placeholder="example@email.com"
                />
                {emailError && (
                  <p className="mt-2 text-[10px] text-red-500 font-light tracking-wide">{emailError}</p>
                )}
              </div>
              
              {/* 提交按鈕 */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-4 bg-black text-white text-[11px] tracking-[0.2em] uppercase hover:bg-gray-900 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors duration-300"
              >
                {isLoading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    SENDING...
                  </span>
                ) : (
                  'SEND RESET LINK'
                )}
              </button>
            </form>
            
            {/* 分隔線 */}
            <div className="w-full h-px bg-gray-200 my-8"></div>
            
            {/* 返回登入連結 */}
            <p className="text-center text-gray-400 text-xs font-light tracking-wide">
              {t('auth.forgot.backToLogin')}{' '}
              <Link
                to="/login"
                className="text-black underline hover:no-underline transition-all"
              >
                Sign In
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
