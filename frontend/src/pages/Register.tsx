/**
 * 註冊頁面
 * Phase 2: 會員系統
 * Style: Lane Crawford 風格 - 高端極簡、黑白為主
 * Font: Cormorant Garamond (display) + Montserrat (sans)
 */
import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation, languageOptions } from '../i18n';
import { useAuthStore } from '../stores/authStore';
import { authApi } from '../api/auth';

// 統一品牌設定
const BRAND = {
  name: 'INFLUENCERS',
  slogan: 'AI-POWERED CONTENT CREATION',
};

export default function Register() {
  const { t, language } = useTranslation();
  const navigate = useNavigate();
  
  const { register, isLoading, error, clearError, isAuthenticated } = useAuthStore();
  
  const [formData, setFormData] = useState({
    surname: '',
    givenName: '',
    email: '',
    password: '',
    confirmPassword: '',
    language: language,
    agreeTerms: false,
  });
  
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
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
      errors.agreeTerms = t('error.validation');
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
      name: `${formData.surname} ${formData.givenName}`.trim(),
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
      <div className="min-h-screen flex items-center justify-center bg-[#FAF9F7] font-sans">
        <div className="w-full max-w-md px-8 py-16 text-center">
          {/* 成功圖標 */}
          <div className="w-20 h-20 mx-auto mb-8 border border-black flex items-center justify-center">
            <svg className="w-8 h-8 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          
          <h2 className="font-display text-2xl tracking-[0.15em] uppercase font-light text-black mb-4">
            {t('auth.verify.title')}
          </h2>
          
          <div className="w-12 h-px bg-black mx-auto mb-6"></div>
          
          <p className="text-gray-500 font-light text-sm leading-relaxed mb-4">
            {t('auth.verify.subtitle')}
          </p>
          <p className="text-gray-400 text-xs font-light mb-10 tracking-wide">
            {t('auth.verify.checkEmail')}
          </p>
          
          <Link
            to="/login"
            className="inline-block px-12 py-4 bg-black text-white text-[11px] tracking-[0.2em] uppercase hover:bg-gray-900 transition-colors duration-300"
          >
            BACK TO LOGIN
          </Link>
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
      <div className="w-full lg:w-1/2 flex items-center justify-center px-6 py-12 lg:py-0 overflow-y-auto">
        <div className="w-full max-w-md">
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
              {t('auth.register.title')}
            </h2>
            <p className="text-gray-400 text-xs font-light tracking-[0.1em] uppercase">
              CREATE YOUR ACCOUNT
            </p>
          </div>
          
          {/* 錯誤訊息 */}
          {error && (
            <div className="mb-8 p-4 border border-red-200 bg-red-50/50">
              <p className="text-red-500 text-xs text-center font-light tracking-wide">{error}</p>
            </div>
          )}
          
          {/* Google 註冊 */}
          <button
            type="button"
            data-testid="btn-register-google"
            onClick={handleGoogleRegister}
            className="w-full flex items-center justify-center gap-3 px-6 py-4 border border-gray-200 hover:border-black text-black text-[11px] tracking-[0.15em] uppercase transition-all duration-300 mb-8"
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
            CONTINUE WITH GOOGLE
          </button>
          
          {/* 分隔線 */}
          <div className="relative mb-8">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200"></div>
            </div>
            <div className="relative flex justify-center">
              <span className="px-6 bg-[#FAF9F7] text-gray-400 text-[10px] tracking-[0.15em] uppercase">
                OR
              </span>
            </div>
          </div>
          
          {/* Email 註冊表單 */}
          <form data-testid="form-register" onSubmit={handleSubmit} className="space-y-6">
            {/* 姓名欄位 - 分開姓和名 */}
            <div className="grid grid-cols-2 gap-4">
              {/* 姓 Surname */}
              <div>
                <label htmlFor="surname" className="block text-[10px] tracking-[0.15em] uppercase text-gray-500 mb-3">
                  SURNAME
                </label>
                <input
                  id="surname"
                  data-testid="input-register-surname"
                  type="text"
                  value={formData.surname}
                  onChange={(e) => handleChange('surname', e.target.value)}
                  className="w-full px-0 py-3 bg-transparent border-0 border-b border-gray-200 text-black placeholder-gray-300 focus:outline-none focus:border-black transition-colors duration-300 text-sm tracking-wide"
                  placeholder={t('auth.register.surname')}
                />
              </div>
              
              {/* 名 Given Name */}
              <div>
                <label htmlFor="givenName" className="block text-[10px] tracking-[0.15em] uppercase text-gray-500 mb-3">
                  GIVEN NAME
                </label>
                <input
                  id="givenName"
                  data-testid="input-register-given-name"
                  type="text"
                  value={formData.givenName}
                  onChange={(e) => handleChange('givenName', e.target.value)}
                  className="w-full px-0 py-3 bg-transparent border-0 border-b border-gray-200 text-black placeholder-gray-300 focus:outline-none focus:border-black transition-colors duration-300 text-sm tracking-wide"
                  placeholder={t('auth.register.givenName')}
                />
              </div>
            </div>
            
            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-[10px] tracking-[0.15em] uppercase text-gray-500 mb-3">
                EMAIL
              </label>
              <input
                id="email"
                data-testid="input-register-email"
                type="email"
                value={formData.email}
                onChange={(e) => handleChange('email', e.target.value)}
                required
                className="w-full px-0 py-3 bg-transparent border-0 border-b border-gray-200 text-black placeholder-gray-300 focus:outline-none focus:border-black transition-colors duration-300 text-sm tracking-wide"
                placeholder={t('auth.register.emailPlaceholder')}
              />
            </div>
            
            {/* 密碼 */}
            <div>
              <label htmlFor="password" className="block text-[10px] tracking-[0.15em] uppercase text-gray-500 mb-3">
                PASSWORD
              </label>
              <div className="relative">
                <input
                  id="password"
                  data-testid="input-register-password"
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={(e) => handleChange('password', e.target.value)}
                  required
                  className={`w-full px-0 py-3 pr-10 bg-transparent border-0 border-b text-black placeholder-gray-300 focus:outline-none transition-colors duration-300 text-sm tracking-wide ${
                    validationErrors.password ? 'border-red-300 focus:border-red-500' : 'border-gray-200 focus:border-black'
                  }`}
                  placeholder={t('auth.register.passwordPlaceholder')}
                />
                {/* 密碼顯示/隱藏按鈕 */}
                <button
                  type="button"
                  data-testid="btn-register-toggle-password"
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
              {validationErrors.password && (
                <p className="mt-2 text-[10px] text-red-500 font-light tracking-wide">{validationErrors.password}</p>
              )}
              {/* 密碼強度指示器 */}
              {formData.password && (
                <div className="mt-3 space-y-1">
                  <div className="flex items-center gap-2 text-[10px] font-light tracking-wide">
                    <span className={formData.password.length >= 8 ? 'text-green-600' : 'text-gray-400'}>
                      {formData.password.length >= 8 ? '✓' : '○'} {t('auth.password.minLength')}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-[10px] font-light tracking-wide">
                    <span className={/[A-Z]/.test(formData.password) ? 'text-green-600' : 'text-gray-400'}>
                      {/[A-Z]/.test(formData.password) ? '✓' : '○'} {t('auth.password.uppercase')}
                    </span>
                  </div>
                </div>
              )}
            </div>
            
            {/* 確認密碼 */}
            <div>
              <label htmlFor="confirmPassword" className="block text-[10px] tracking-[0.15em] uppercase text-gray-500 mb-3">
                CONFIRM PASSWORD
              </label>
              <div className="relative">
                <input
                  id="confirmPassword"
                  data-testid="input-register-confirm"
                  type={showConfirmPassword ? 'text' : 'password'}
                  value={formData.confirmPassword}
                  onChange={(e) => handleChange('confirmPassword', e.target.value)}
                  required
                  className={`w-full px-0 py-3 pr-10 bg-transparent border-0 border-b text-black placeholder-gray-300 focus:outline-none transition-colors duration-300 text-sm tracking-wide ${
                    validationErrors.confirmPassword ? 'border-red-300 focus:border-red-500' : 'border-gray-200 focus:border-black'
                  }`}
                  placeholder={t('auth.register.confirmPasswordPlaceholder')}
                />
                {/* 確認密碼顯示/隱藏按鈕 */}
                <button
                  type="button"
                  data-testid="btn-register-toggle-confirm-password"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-0 top-1/2 -translate-y-1/2 p-2 text-gray-400 hover:text-black transition-colors"
                >
                  {showConfirmPassword ? (
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
              {validationErrors.confirmPassword && (
                <p className="mt-2 text-[10px] text-red-500 font-light tracking-wide">{validationErrors.confirmPassword}</p>
              )}
            </div>
            
            {/* 語言偏好 */}
            <div>
              <label htmlFor="language" className="block text-[10px] tracking-[0.15em] uppercase text-gray-500 mb-3">
                LANGUAGE PREFERENCE
              </label>
              <select
                id="language"
                data-testid="select-register-lang"
                value={formData.language}
                onChange={(e) => handleChange('language', e.target.value)}
                className="w-full px-0 py-3 bg-transparent border-0 border-b border-gray-200 text-black focus:outline-none focus:border-black transition-colors duration-300 text-sm tracking-wide appearance-none cursor-pointer"
                style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%23999'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='1' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E")`, backgroundRepeat: 'no-repeat', backgroundPosition: 'right center', backgroundSize: '16px' }}
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
                    data-testid="checkbox-register-terms"
                    checked={formData.agreeTerms}
                    onChange={(e) => handleChange('agreeTerms', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-4 h-4 border border-gray-300 peer-checked:border-black peer-checked:bg-black transition-all duration-200"></div>
                  <svg 
                    className="absolute top-0.5 left-0.5 w-3 h-3 text-white opacity-0 peer-checked:opacity-100 transition-opacity duration-200" 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span className="text-[10px] text-gray-500 font-light leading-relaxed tracking-wide">
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
                <p className="mt-2 text-[10px] text-red-500 font-light tracking-wide">{validationErrors.agreeTerms}</p>
              )}
            </div>
            
            {/* 提交按鈕 */}
            <button
              type="submit"
              data-testid="btn-register-submit"
              disabled={isLoading}
              className="w-full py-4 mt-4 bg-black text-white text-[11px] tracking-[0.2em] uppercase hover:bg-gray-900 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors duration-300"
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  CREATING...
                </span>
              ) : (
                'CREATE ACCOUNT'
              )}
            </button>
          </form>
          
          {/* 登入連結 */}
          <p className="mt-10 text-center text-gray-400 text-xs font-light tracking-wide">
            {t('auth.register.hasAccount')}{' '}
            <Link
              to="/login"
              data-testid="link-register-login"
              className="text-black underline hover:no-underline transition-all"
            >
              {t('auth.register.loginLink')}
            </Link>
          </p>
          
          {/* 底部裝飾線 */}
          <div className="mt-12 flex justify-center">
            <div className="w-16 h-px bg-gray-200"></div>
          </div>
        </div>
      </div>
    </div>
  );
}
