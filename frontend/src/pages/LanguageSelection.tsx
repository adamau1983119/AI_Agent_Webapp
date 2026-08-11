/**
 * 語言選擇頁
 * Language Selection Page
 * 
 * Style: Lane Crawford 風格 - 高端極簡、黑白為主
 * Font: Cormorant Garamond (display) + Montserrat (sans)
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation, languageOptions, Language } from '../i18n';
import { BRAND } from '@/lib/brand';

export default function LanguageSelection() {
  const navigate = useNavigate();
  const { t, setLanguage } = useTranslation();
  const [selectedLang, setSelectedLang] = useState<Language | null>(null);

  const handleLanguageSelect = (lang: Language) => {
    setSelectedLang(lang);
    setLanguage(lang);
    
    // 儲存到 localStorage
    localStorage.setItem('preferred-language', lang);
    
    setTimeout(() => {
      navigate('/welcome');
    }, 300);
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
      
      {/* 右側內容區 */}
      <div className="w-full lg:w-1/2 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          {/* 移動端 Logo */}
          <div className="lg:hidden text-center mb-16">
            <h1 className="font-display text-4xl font-light tracking-[0.3em] uppercase text-black">
              {BRAND.name}
            </h1>
            <div className="w-20 h-px bg-black mx-auto mt-6 mb-6"></div>
            <p className="text-gray-400 text-[10px] tracking-[0.2em] uppercase font-light">
              {BRAND.slogan}
            </p>
          </div>

          {/* 桌面版分隔線 */}
          <div className="hidden lg:block text-center mb-16">
            <div className="w-16 h-px bg-gray-300 mx-auto"></div>
          </div>

          {/* 標題 */}
          <div className="text-center mb-12">
            <h2 className="font-display text-2xl tracking-[0.1em] font-light text-black mb-3">
              {t('language.selectTitle')}
            </h2>
            <p className="text-gray-400 text-xs font-light tracking-[0.1em]">
              {t('language.selectSubtitle')}
            </p>
          </div>

          {/* 語言選項 */}
          <div className="space-y-4 mb-12">
            {languageOptions.map((option) => (
              <button
                key={option.code}
                onClick={() => handleLanguageSelect(option.code)}
                className={`w-full px-6 py-5 border transition-all duration-300 group ${
                  selectedLang === option.code
                    ? 'border-black bg-black text-white'
                    : 'border-gray-200 bg-transparent text-black hover:border-black'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <span className={`text-xl font-light ${
                      selectedLang === option.code ? 'text-white' : 'text-black'
                    }`}>
                      {option.icon}
                    </span>
                    <div className="text-left">
                      <div className="text-sm tracking-[0.15em] uppercase font-light">
                        {option.name}
                      </div>
                      <div className={`text-[10px] mt-1 tracking-[0.1em] uppercase ${
                        selectedLang === option.code ? 'text-white/60' : 'text-gray-400'
                      }`}>
                        {t(`language.${option.code}.english`)}
                      </div>
                    </div>
                  </div>
                  <svg 
                    className={`w-5 h-5 transition-all duration-300 ${
                      selectedLang === option.code 
                        ? 'text-white translate-x-0 opacity-100' 
                        : 'text-gray-300 -translate-x-2 opacity-0 group-hover:translate-x-0 group-hover:opacity-100 group-hover:text-black'
                    }`} 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                  </svg>
                </div>
              </button>
            ))}
          </div>

          {/* 底部裝飾線 */}
          <div className="flex justify-center mb-8">
            <div className="w-16 h-px bg-gray-200"></div>
          </div>

          {/* 版權資訊 */}
          <div className="text-center text-[10px] text-gray-400 tracking-[0.15em] uppercase">
            © 2026 {BRAND.name}
          </div>
          
          {/* 測試用：清除語言偏好按鈕（僅開發環境） */}
          {import.meta.env.DEV && (
            <div className="text-center mt-8">
              <button
                onClick={() => {
                  localStorage.removeItem('preferred-language');
                  localStorage.removeItem('i18n-storage');
                  window.location.reload();
                }}
                className="text-[10px] text-gray-400 hover:text-black underline tracking-[0.1em] uppercase transition-colors"
              >
                [DEV] Reset Language
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
