/**
 * 註冊頁面
 * Phase 2: 會員系統
 * Style: Lane Crawford 風格 - 高端極簡、黑白為主
 */
import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation, languageOptions } from '../i18n';
import { useAuthStore } from '../stores/authStore';
import { authApi } from '../api/auth';

export default function Register() {
  const { t, language } = useTranslation();
  const navigate = useNavigate();
  
  const { register, isLoading, error, clearError, isAuthenticated } = useAuthStore();
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    language: language,
    agreeTerms: false,
  });
  
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [isSuccess, setIsSuccess] = useState(false);
  
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
  
  // 密碼驗證
  const validatePassword = (password: string): string[] => {
    const errors: string[] = [];
    if (password.length < 8) {
      errors.push(t('auth.password.minLength'));
    }
    if (!/[A-Z]/.test(password)) {
      errors.push(t('auth.password.uppercase'));
    }
    return errors;
  };
  
  // 表單驗證
  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};
    
    // 密碼驗證
    const passwordErrors = validatePassword(formData.password);
    if (passwordErrors.length > 0) {
      errors.password = passwordErrors.join('、');
    }
    
    // 確認密碼
    if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = t('auth.password.match');
    }
    
    // 同意條款
    if (!formData.agreeTerms) {
      errors.agreeTerms = '請同意服務條款';
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    
    if (!validateForm()) {
      return;
    }
    
    const success = await register({
      name: formData.name,
      email: formData.email,
      password: formData.password,
      language: formData.language,
    });
    
    if (success) {
      setIsSuccess(true);
    }
  };
  
  const handleGoogleRegister = () => {
    window.location.href = authApi.getGoogleLoginUrl();
  };
  
  const handleChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // 清除該欄位的驗證錯誤
    if (validationErrors[field]) {
      setValidationErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };
  
  // 註冊成功畫面 - Lane Crawford Style
  if (isSuccess) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#FAF9F7]">
        <div className="w-full max-w-md px-8 py-16 text-center">
          {/* 成功圖標 */}
          <div className="w-20 h-20 mx-auto mb-8 border border-black rounded-full flex items-center justify-center">
            <svg className="w-10 h-10 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          
          <h2 className="text-2xl tracking-[0.2em] uppercase font-light text-black mb-4">
            {t('auth.verify.title')}
          </h2>
          
          <div className="w-12 h-px bg-black mx-auto mb-6"></div>
          
          <p className="text-gray-600 font-light leading-relaxed mb-4">
            {t('auth.verify.subtitle')}
          </p>
          <p className="text-gray-500 text-sm font-light mb-10">
            {t('auth.verify.checkEmail')}
          </p>
          
          <Link
            to="/login"
            className="inline-block px-12 py-4 bg-black text-white text-xs tracking-[0.2em] uppercase hover:bg-gray-900 transition-colors duration-300"
          >
            {t('auth.forgot.backToLogin')}
          </Link>
        </div>
      </div>
    );
  }
  
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
      <div className="w-full lg:w-1/2 flex items-center justify-center px-6 py-12 lg:py-0">
        <div className="w-full max-w-md">
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
              {t('auth.register.title')}
            </h2>
            <p className="text-gray-500 text-sm font-light">
              {t('auth.register.subtitle')}
            </p>
          </div>
          
          {/* 錯誤訊息 */}
          {error && (
            <div className="mb-8 p-4 border border-red-200 bg-red-50">
              <p className="text-red-600 text-sm text-center font-light">{error}</p>
            </div>
          )}
          
          {/* Google 註冊 */}
          <button
            type="button"
            onClick={handleGoogleRegister}
            className="w-full flex items-center justify-center gap-3 px-6 py-4 border border-gray-300 hover:border-black text-black text-xs tracking-[0.1em] uppercase transition-all duration-300 mb-8"
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
            {t('auth.register.googleRegister')}
          </button>
          
          {/* 分隔線 */}
          <div className="relative mb-8">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200"></div>
            </div>
            <div className="relative flex justify-center">
              <span className="px-6 bg-[#FAF9F7] text-gray-400 text-xs tracking-[0.1em] uppercase">
                {t('common.or')}
              </span>
            </div>
          </div>
          
          {/* Email 註冊表單 */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 名稱 */}
            <div>
              <label htmlFor="name" className="block text-xs tracking-[0.1em] uppercase text-gray-600 mb-3">
                {t('auth.register.name')}
              </label>
              <input
                id="name"
                type="text"
                value={formData.name}
                onChange={(e) => handleChange('name', e.target.value)}
                className="w-full px-0 py-3 bg-transparent border-0 border-b border-gray-300 text-black placeholder-gray-400 focus:outline-none focus:border-black transition-colors duration-300 text-sm"
                placeholder={t('auth.register.namePlaceholder')}
              />
            </div>
            
            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-xs tracking-[0.1em] uppercase text-gray-600 mb-3">
                {t('auth.register.email')}
              </label>
              <input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => handleChange('email', e.target.value)}
                required
                className="w-full px-0 py-3 bg-transparent border-0 border-b border-gray-300 text-black placeholder-gray-400 focus:outline-none focus:border-black transition-colors duration-300 text-sm"
                placeholder={t('auth.register.emailPlaceholder')}
              />
            </div>
            
            {/* 密碼 */}
            <div>
              <label htmlFor="password" className="block text-xs tracking-[0.1em] uppercase text-gray-600 mb-3">
                {t('auth.register.password')}
              </label>
              <input
                id="password"
                type="password"
                value={formData.password}
                onChange={(e) => handleChange('password', e.target.value)}
                required
                className={`w-full px-0 py-3 bg-transparent border-0 border-b text-black placeholder-gray-400 focus:outline-none transition-colors duration-300 text-sm ${
                  validationErrors.password ? 'border-red-400 focus:border-red-500' : 'border-gray-300 focus:border-black'
                }`}
                placeholder={t('auth.register.passwordPlaceholder')}
              />
              {validationErrors.password && (
                <p className="mt-2 text-xs text-red-500 font-light">{validationErrors.password}</p>
              )}
              {/* 密碼強度指示器 */}
              {formData.password && (
                <div className="mt-3 space-y-1">
                  <div className="flex items-center gap-2 text-xs font-light">
                    <span className={formData.password.length >= 8 ? 'text-green-600' : 'text-gray-400'}>
                      {formData.password.length >= 8 ? '✓' : '○'} {t('auth.password.minLength')}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-xs font-light">
                    <span className={/[A-Z]/.test(formData.password) ? 'text-green-600' : 'text-gray-400'}>
                      {/[A-Z]/.test(formData.password) ? '✓' : '○'} {t('auth.password.uppercase')}
                    </span>
                  </div>
                </div>
              )}
            </div>
            
            {/* 確認密碼 */}
            <div>
              <label htmlFor="confirmPassword" className="block text-xs tracking-[0.1em] uppercase text-gray-600 mb-3">
                {t('auth.register.confirmPassword')}
              </label>
              <input
                id="confirmPassword"
                type="password"
                value={formData.confirmPassword}
                onChange={(e) => handleChange('confirmPassword', e.target.value)}
                required
                className={`w-full px-0 py-3 bg-transparent border-0 border-b text-black placeholder-gray-400 focus:outline-none transition-colors duration-300 text-sm ${
                  validationErrors.confirmPassword ? 'border-red-400 focus:border-red-500' : 'border-gray-300 focus:border-black'
                }`}
                placeholder={t('auth.register.confirmPasswordPlaceholder')}
              />
              {validationErrors.confirmPassword && (
                <p className="mt-2 text-xs text-red-500 font-light">{validationErrors.confirmPassword}</p>
              )}
            </div>
            
            {/* 語言偏好 */}
            <div>
              <label htmlFor="language" className="block text-xs tracking-[0.1em] uppercase text-gray-600 mb-3">
                {t('auth.register.language')}
              </label>
              <select
                id="language"
                value={formData.language}
                onChange={(e) => handleChange('language', e.target.value)}
                className="w-full px-0 py-3 bg-transparent border-0 border-b border-gray-300 text-black focus:outline-none focus:border-black transition-colors duration-300 text-sm appearance-none cursor-pointer"
                style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%23999'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E")`, backgroundRepeat: 'no-repeat', backgroundPosition: 'right center', backgroundSize: '20px' }}
              >
                {languageOptions.map(option => (
                  <option key={option.code} value={option.code}>
                    {option.icon} {option.name}
                  </option>
                ))}
              </select>
            </div>
            
            {/* 同意條款 */}
            <div className="pt-2">
              <label className="flex items-start gap-3 cursor-pointer group">
                <div className="relative mt-0.5">
                  <input
                    type="checkbox"
                    checked={formData.agreeTerms}
                    onChange={(e) => handleChange('agreeTerms', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-4 h-4 border border-gray-400 peer-checked:border-black peer-checked:bg-black transition-all duration-200"></div>
                  <svg 
                    className="absolute top-0.5 left-0.5 w-3 h-3 text-white opacity-0 peer-checked:opacity-100 transition-opacity duration-200" 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span className="text-xs text-gray-600 font-light leading-relaxed">
                  {t('auth.register.terms')}{' '}
                  <a href="/terms" className="text-black underline hover:no-underline">
                    {t('auth.register.termsLink')}
                  </a>{' '}
                  {t('auth.register.and')}{' '}
                  <a href="/privacy" className="text-black underline hover:no-underline">
                    {t('auth.register.privacyLink')}
                  </a>
                </span>
              </label>
              {validationErrors.agreeTerms && (
                <p className="mt-2 text-xs text-red-500 font-light">{validationErrors.agreeTerms}</p>
              )}
            </div>
            
            {/* 提交按鈕 */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-4 mt-4 bg-black text-white text-xs tracking-[0.2em] uppercase hover:bg-gray-900 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors duration-300"
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
                t('auth.register.submit')
              )}
            </button>
          </form>
          
          {/* 登入連結 */}
          <p className="mt-10 text-center text-gray-500 text-sm font-light">
            {t('auth.register.hasAccount')}{' '}
            <Link
              to="/login"
              className="text-black underline hover:no-underline transition-all"
            >
              {t('auth.register.loginLink')}
            </Link>
          </p>
          
          {/* 底部裝飾線 */}
          <div className="mt-12 flex justify-center">
            <div className="w-16 h-px bg-gray-300"></div>
          </div>
        </div>
      </div>
    </div>
  );
}
