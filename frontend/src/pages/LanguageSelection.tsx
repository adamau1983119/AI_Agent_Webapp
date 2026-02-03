/**
 * 語言選擇頁
 * Language Selection Page
 * 
 * 設計風格：Lane Crawford 高端時尚風格
 * Mobile First 設計
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation, languageOptions, Language } from '../i18n';

export default function LanguageSelection() {
  const navigate = useNavigate();
  const { setLanguage } = useTranslation();
  const [selectedLang, setSelectedLang] = useState<Language | null>(null);

  const handleLanguageSelect = (lang: Language) => {
    setSelectedLang(lang);
    setLanguage(lang);
    
    // 儲存到 localStorage
    localStorage.setItem('preferred-language', lang);
    
    // 短暫延遲後跳轉到登入頁
    setTimeout(() => {
      navigate('/login');
    }, 300);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-white">
      {/* 手機版：垂直排列 */}
      <div className="w-full max-w-md px-6 py-12 md:hidden">
        {/* Logo */}
        <div className="text-center mb-12">
          <div className="w-24 h-24 mx-auto mb-6 bg-black rounded-full flex items-center justify-center">
            <span className="text-white text-3xl font-serif">IA</span>
          </div>
          <h1 className="text-3xl font-serif text-black mb-2">
            Influencers AI
          </h1>
          <p className="text-lg font-serif text-gray-600">
            Agents
          </p>
        </div>

        {/* 分隔線 */}
        <div className="w-24 h-px bg-gray-300 mx-auto mb-12"></div>

        {/* 標題 */}
        <div className="text-center mb-12">
          <h2 className="text-xl font-medium text-black mb-2">
            選擇您的語言
          </h2>
          <p className="text-sm text-gray-500">
            Select Your Language
          </p>
        </div>

        {/* 語言按鈕（垂直排列） */}
        <div className="space-y-4 mb-12">
          {languageOptions.map((option) => (
            <button
              key={option.code}
              onClick={() => handleLanguageSelect(option.code)}
              className={`w-full px-6 py-4 border-2 rounded-none transition-all duration-200 ${
                selectedLang === option.code
                  ? 'border-black bg-black text-white'
                  : 'border-black bg-white text-black hover:bg-gray-50'
              }`}
            >
              <div className="text-left flex items-center gap-3">
                <span className="text-2xl font-bold">{option.icon}</span>
                <div>
                  <div className="text-lg font-medium">
                    {option.name}
                  </div>
                  {option.code === 'zh-TW' && (
                    <div className="text-sm text-gray-500 mt-0.5">
                      Traditional Chinese
                    </div>
                  )}
                  {option.code === 'ja' && (
                    <div className="text-sm text-gray-500 mt-0.5">
                      Japanese
                    </div>
                  )}
                </div>
              </div>
            </button>
          ))}
        </div>

        {/* 版權資訊 */}
        <div className="text-center text-xs text-gray-400">
          © 2026 Influencers AI
        </div>
      </div>

      {/* 平板/桌面版：水平排列 */}
      <div className="hidden md:flex flex-col items-center justify-center min-h-screen px-8">
        {/* Logo */}
        <div className="text-center mb-16">
          <div className="w-32 h-32 mx-auto mb-8 bg-black rounded-full flex items-center justify-center">
            <span className="text-white text-5xl font-serif">IA</span>
          </div>
          <h1 className="text-5xl font-serif text-black mb-3">
            Influencers AI
          </h1>
          <p className="text-2xl font-serif text-gray-600">
            Agents
          </p>
        </div>

        {/* 分隔線 */}
        <div className="w-32 h-px bg-gray-300 mb-16"></div>

        {/* 標題 */}
        <div className="text-center mb-16">
          <h2 className="text-2xl font-medium text-black mb-2">
            選擇您的語言
          </h2>
          <p className="text-base text-gray-500">
            Select Your Language
          </p>
        </div>

        {/* 語言按鈕（水平排列） */}
        <div className="flex gap-6 mb-16">
          {languageOptions.map((option) => (
            <button
              key={option.code}
              onClick={() => handleLanguageSelect(option.code)}
              className={`px-8 py-6 border-2 rounded-none transition-all duration-200 min-w-[180px] ${
                selectedLang === option.code
                  ? 'border-black bg-black text-white'
                  : 'border-black bg-white text-black hover:bg-gray-50'
              }`}
            >
              <div className="text-center">
                <span className="text-3xl font-bold block mb-2">{option.icon}</span>
                <div className="text-xl font-medium">
                  {option.name}
                </div>
                {option.code === 'zh-TW' && (
                  <div className="text-sm text-gray-500 mt-2">
                    Traditional Chinese
                  </div>
                )}
                {option.code === 'ja' && (
                  <div className="text-sm text-gray-500 mt-2">
                    Japanese
                  </div>
                )}
              </div>
            </button>
          ))}
        </div>

        {/* 版權資訊 */}
        <div className="text-center text-sm text-gray-400 mb-4">
          © 2026 Influencers AI
        </div>
        
        {/* 測試用：清除語言偏好按鈕（僅開發環境） */}
        {import.meta.env.DEV && (
          <div className="text-center mt-4">
            <button
              onClick={() => {
                localStorage.removeItem('preferred-language');
                localStorage.removeItem('i18n-storage');
                window.location.reload();
              }}
              className="text-xs text-gray-400 hover:text-gray-600 underline"
            >
              [測試] 清除語言偏好
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

