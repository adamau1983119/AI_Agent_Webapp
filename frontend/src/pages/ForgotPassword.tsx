/**
 * 忘記密碼頁面
 * Phase 2: 會員系統
 * 設計風格：Lane Crawford 高端時尚風格
 */
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation, Language } from '../i18n';
import { authApi } from '../api/auth';

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
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="w-full max-w-md px-6 py-12">
          <div className="text-center">
            <div className="w-20 h-20 mx-auto mb-6 bg-black rounded-full flex items-center justify-center">
              <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <h2 className="text-2xl font-serif text-black mb-4">
              {t('auth.forgot.success')}
            </h2>
            <p className="text-gray-500 mb-2">
              我們已發送重設連結到
            </p>
            <p className="text-black font-medium mb-8">
              {email}
            </p>
            <p className="text-sm text-gray-400 mb-8">
              請在 24 小時內完成密碼重設
            </p>
            <Link
              to="/login"
              className="inline-block px-6 py-3 bg-black text-white font-medium hover:bg-gray-800 transition-colors"
            >
              {t('auth.forgot.backToLogin')}
            </Link>
            <p className="mt-6 text-xs text-gray-400">
              沒收到郵件？請檢查垃圾郵件資料夾
            </p>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen bg-white">
      {/* 手機版 */}
      <div className="md:hidden">
        {/* 頂部導航 */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <button
            onClick={() => navigate('/login')}
            className="text-black text-sm"
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
            className="text-black text-sm"
          >
            🌐 {languageLabels[language]}
          </button>
        </div>
        
        <div className="px-6 py-8">
          {/* Logo */}
          <div className="text-center mb-12">
            <div className="w-20 h-20 mx-auto mb-4 bg-black rounded-full flex items-center justify-center">
              <span className="text-white text-2xl font-serif">IA</span>
            </div>
            <h1 className="text-2xl font-serif text-black mb-1">
              {t('auth.forgot.title')}
            </h1>
            <p className="text-sm text-gray-500">
              {t('auth.forgot.subtitle')}
            </p>
          </div>
          
          {/* 錯誤訊息 */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500">
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}
          
          {/* 表單 */}
          <form onSubmit={handleSubmit} className="space-y-6 mb-6">
            {/* Email 輸入框（底線樣式） */}
            <div>
              <label htmlFor="email" className="block text-sm text-black mb-1">
                {t('auth.forgot.email')}
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={handleEmailChange}
                onBlur={() => validateEmail(email)}
                required
                className={`w-full py-3 bg-transparent border-0 border-b-2 focus:outline-none focus:ring-0 transition-colors ${
                  emailError
                    ? 'border-red-500 text-red-600'
                    : 'border-gray-300 text-black focus:border-black'
                }`}
                placeholder="example@email.com"
              />
              {emailError && (
                <p className="mt-1 text-xs text-red-500">{emailError}</p>
              )}
            </div>
            
            {/* 提交按鈕（黑底白字） */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-4 bg-black text-white font-medium hover:bg-gray-800 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  {t('common.loading')}
                </span>
              ) : (
                `${t('auth.forgot.submit')} SEND`
              )}
            </button>
          </form>
          
          {/* 分隔線 */}
          <div className="my-6 border-t border-gray-200"></div>
          
          {/* 返回登入連結 */}
          <p className="text-center text-sm text-gray-500">
            {t('auth.forgot.backToLogin')}{' '}
            <Link
              to="/login"
              className="text-black font-medium hover:underline"
            >
              →
            </Link>
          </p>
        </div>
      </div>
      
      {/* 平板/桌面版 */}
      <div className="hidden md:flex min-h-screen">
        {/* 左側圖片區域 */}
        <div className="w-1/2 bg-gray-100 flex items-center justify-center">
          <div className="text-center">
            <div className="w-32 h-32 mx-auto mb-6 bg-black rounded-full flex items-center justify-center">
              <span className="text-white text-5xl font-serif">IA</span>
            </div>
            <h1 className="text-4xl font-serif text-black mb-2">
              Influencers AI
            </h1>
            <p className="text-xl font-serif text-gray-600">
              Agents
            </p>
          </div>
        </div>
        
        {/* 右側表單區域 */}
        <div className="w-1/2 flex items-center justify-center px-12">
          <div className="w-full max-w-md">
            {/* 頂部導航 */}
            <div className="flex items-center justify-between mb-8">
              <button
                onClick={() => navigate('/login')}
                className="text-black text-sm hover:underline"
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
                className="text-black text-sm"
              >
                🌐 {languageLabels[language]}
              </button>
            </div>
            
            <h2 className="text-3xl font-serif text-black mb-2">
              {t('auth.forgot.title')}
            </h2>
            <p className="text-gray-500 mb-8">
              {t('auth.forgot.subtitle')}
            </p>
            
            {/* 錯誤訊息 */}
            {error && (
              <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500">
                <p className="text-red-600 text-sm">{error}</p>
              </div>
            )}
            
            {/* 表單 */}
            <form onSubmit={handleSubmit} className="space-y-6 mb-6">
              {/* Email */}
              <div>
                <label htmlFor="email-desktop" className="block text-sm text-black mb-1">
                  {t('auth.forgot.email')}
                </label>
                <input
                  id="email-desktop"
                  type="email"
                  value={email}
                  onChange={handleEmailChange}
                  onBlur={() => validateEmail(email)}
                  required
                  className={`w-full py-3 bg-transparent border-0 border-b-2 focus:outline-none focus:ring-0 transition-colors ${
                    emailError
                      ? 'border-red-500 text-red-600'
                      : 'border-gray-300 text-black focus:border-black'
                  }`}
                  placeholder="example@email.com"
                />
                {emailError && (
                  <p className="mt-1 text-xs text-red-500">{emailError}</p>
                )}
              </div>
              
              {/* 提交按鈕 */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-4 bg-black text-white font-medium hover:bg-gray-800 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    {t('common.loading')}
                  </span>
                ) : (
                  `${t('auth.forgot.submit')} SEND`
                )}
              </button>
            </form>
            
            {/* 分隔線 */}
            <div className="my-6 border-t border-gray-200"></div>
            
            {/* 返回登入連結 */}
            <p className="text-center text-sm text-gray-500">
              {t('auth.forgot.backToLogin')}{' '}
              <Link
                to="/login"
                className="text-black font-medium hover:underline"
              >
                →
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

