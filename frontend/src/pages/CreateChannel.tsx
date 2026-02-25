/**
 * 建立頻道頁面
 * Phase 3: 內容功能
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from '../i18n';
import { useAuthStore } from '../stores/authStore';
import {
  channelsApi,
  ChannelCategory,
  ChannelRegion,
  ChannelCreateRequest,
  categoryI18nKeys,
  regionI18nKeys,
  categoryIcons,
} from '../api/channels';
import toast from 'react-hot-toast';
import { useTypewriter } from '../hooks/useTypewriter';

const categories: { value: ChannelCategory; label: string; icon: string }[] = [
  { value: 'fashion', label: categoryI18nKeys.fashion, icon: categoryIcons.fashion },
  { value: 'food', label: categoryI18nKeys.food, icon: categoryIcons.food },
  { value: 'trend', label: categoryI18nKeys.trend, icon: categoryIcons.trend },
  { value: 'finance', label: categoryI18nKeys.finance, icon: categoryIcons.finance },
  { value: 'sports', label: categoryI18nKeys.sports, icon: categoryIcons.sports },
  { value: 'tech', label: categoryI18nKeys.tech, icon: categoryIcons.tech },
  { value: 'entertainment', label: categoryI18nKeys.entertainment, icon: categoryIcons.entertainment },
  { value: 'other', label: categoryI18nKeys.other, icon: categoryIcons.other },
];

const regions: { value: ChannelRegion; label: string }[] = [
  { value: 'global', label: regionI18nKeys.global },
  { value: 'hong_kong', label: regionI18nKeys.hong_kong },
  { value: 'taiwan', label: regionI18nKeys.taiwan },
  { value: 'japan', label: regionI18nKeys.japan },
  { value: 'korea', label: regionI18nKeys.korea },
  { value: 'china', label: regionI18nKeys.china },
  { value: 'usa', label: regionI18nKeys.usa },
  { value: 'uk', label: regionI18nKeys.uk },
];

// 常見組合預設（對應 i18n channels.assist.preset.* 鍵）
const quickPresets: { key: string; category: ChannelCategory; region: ChannelRegion; icon: string }[] = [
  { key: 'japanFashion', category: 'fashion', region: 'japan', icon: '👘' },
  { key: 'hkFood', category: 'food', region: 'hong_kong', icon: '🍜' },
  { key: 'globalTrend', category: 'trend', region: 'global', icon: '🌐' },
  { key: 'taiwanTech', category: 'tech', region: 'taiwan', icon: '💻' },
  { key: 'koreaEntertainment', category: 'entertainment', region: 'korea', icon: '🎬' },
];

export default function CreateChannel() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();
  
  // 表單狀態
  const [step, setStep] = useState(1);
  const [name, setName] = useState('');
  const [category, setCategory] = useState<ChannelCategory | null>(null);
  const [region, setRegion] = useState<ChannelRegion>('global');
  const [customKeywords, setCustomKeywords] = useState<string[]>([]);
  const [keywordInput, setKeywordInput] = useState('');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // AI 助手狀態
  const [showAssist, setShowAssist] = useState(false);
  const [assistInput, setAssistInput] = useState('');
  const [isAssisting, setIsAssisting] = useState(false);
  const [assistResult, setAssistResult] = useState<{
    category: string | null;
    region: string | null;
    keywords: string[];
    confidence: number;
    clarification_needed: boolean;
    clarification_question: string | null;
    recommended_sources: Array<{ name: string; url: string; role: string }>;
  } | null>(null);
  const [assistMessage, setAssistMessage] = useState<string>('');
  
  // 打字效果
  const { displayedText: typedMessage, isTyping } = useTypewriter({
    text: assistMessage,
    speed: 30,
  });
  
  // 未登入
  if (!isAuthenticated) {
    navigate('/login');
    return null;
  }
  
  // 添加關鍵字
  const addKeyword = () => {
    const keyword = keywordInput.trim();
    if (keyword && !customKeywords.includes(keyword) && customKeywords.length < 5) {
      setCustomKeywords([...customKeywords, keyword]);
      setKeywordInput('');
    }
  };
  
  // 移除關鍵字
  const removeKeyword = (index: number) => {
    setCustomKeywords(customKeywords.filter((_, i) => i !== index));
  };
  
  // 處理按 Enter
  const handleKeywordKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addKeyword();
    }
  };
  
  // AI 助手：快捷按鈕點擊（類別）
  const handleQuickCategoryClick = (cat: ChannelCategory) => {
    setCategory(cat);
    // 先翻譯 i18n 鍵，再傳入模板
    const categoryText = t(categoryI18nKeys[cat]);
    const text = t('channels.assist.quickCategory', { category: categoryText });
    setAssistInput(text);
  };
  
  // AI 助手：快捷按鈕點擊（地區）
  const handleQuickRegionClick = (reg: ChannelRegion) => {
    setRegion(reg);
    // 先翻譯 i18n 鍵，再傳入模板
    const regionText = t(regionI18nKeys[reg]);
    const text = t('channels.assist.quickRegion', { region: regionText });
    setAssistInput(text);
  };

  // AI 助手：預設組合快捷按鈕
  const quickPresets = [
    { key: 'japanFashion', category: 'fashion' as ChannelCategory, region: 'japan' as ChannelRegion, icon: '🇯🇵👗' },
    { key: 'hkFood', category: 'food' as ChannelCategory, region: 'hong_kong' as ChannelRegion, icon: '🇭🇰🍜' },
    { key: 'globalTrend', category: 'trend' as ChannelCategory, region: 'global' as ChannelRegion, icon: '🌍📊' },
    { key: 'taiwanTech', category: 'tech' as ChannelCategory, region: 'taiwan' as ChannelRegion, icon: '🇹🇼💻' },
    { key: 'koreaEntertainment', category: 'entertainment' as ChannelCategory, region: 'korea' as ChannelRegion, icon: '🇰🇷🎬' },
  ];

  // AI 助手：預設組合點擊
  const handlePresetClick = (preset: typeof quickPresets[0]) => {
    setCategory(preset.category);
    setRegion(preset.region);
    const label = t(`channels.assist.preset.${preset.key}` as any);
    setAssistInput(label);
  };

  // 從 URL 提取網域名
  const extractDomain = (url: string): string => {
    try {
      const u = new URL(url);
      return u.hostname.replace(/^www\./, '');
    } catch {
      return url;
    }
  };
  
  // AI 助手：處理用戶輸入
  const handleAssistSubmit = async () => {
    if (!assistInput.trim()) {
      toast.error(t('channels.assist.inputRequired'));
      return;
    }
    
    setIsAssisting(true);
    setAssistResult(null);
    setAssistMessage('');
    
    try {
      const userLanguage = localStorage.getItem('language') || 'zh-TW';
      const result = await channelsApi.assistChannel(assistInput.trim(), userLanguage);
      setAssistResult(result);
      
      // 生成 AI 回覆訊息（打字效果）
      if (result.clarification_needed) {
        setAssistMessage(result.clarification_question || t('channels.assist.clarificationDefault'));
      } else if (result.confidence >= 0.7 && result.category && result.region) {
        const categoryName = categoryI18nKeys[result.category as ChannelCategory];
        const regionName = regionI18nKeys[result.region as ChannelRegion];
        const keywordsText = result.keywords.length > 0 
          ? t('channels.assist.responseWithKeywords', { 
              category: categoryName, 
              region: regionName,
              keywords: result.keywords.join(', ')
            })
          : t('channels.assist.responseWithoutKeywords', { 
              category: categoryName, 
              region: regionName
            });
        setAssistMessage(keywordsText);
        
        // 自動填入表單
        setCategory(result.category as ChannelCategory);
        setRegion(result.region as ChannelRegion);
        if (result.keywords.length > 0) {
          setCustomKeywords(result.keywords);
        }
        toast.success(t('channels.assist.autoFilled'));
      } else if (result.confidence >= 0.5) {
        // 中等信心度：顯示結果但提示可能需要更多資訊
        const categoryName = result.category ? categoryI18nKeys[result.category as ChannelCategory] : '-';
        const regionName = result.region ? regionI18nKeys[result.region as ChannelRegion] : '-';
        setAssistMessage(t('channels.assist.responseWithoutKeywords', { 
          category: categoryName, 
          region: regionName
        }));
      } else {
        // 低信心度
        setAssistMessage(t('channels.assist.lowConfidence'));
      }
    } catch (err: any) {
      // 錯誤處理
      const errorMessage = err?.response?.data?.detail || err?.message || t('channels.assist.failed');
      toast.error(errorMessage);
      setAssistMessage(t('channels.assist.errorMessage'));
      
      // 記錄錯誤（開發環境）
      if (process.env.NODE_ENV === 'development') {
        console.error('AI Assistant Error:', err);
      }
    } finally {
      setIsAssisting(false);
    }
  };
  
  // AI 助手：確認並應用結果
  const handleAssistConfirm = () => {
    if (assistResult && assistResult.category && assistResult.region) {
      setCategory(assistResult.category as ChannelCategory);
      setRegion(assistResult.region as ChannelRegion);
      if (assistResult.keywords.length > 0) {
        setCustomKeywords(assistResult.keywords);
      }
      setShowAssist(false);
      setAssistInput('');
      setAssistResult(null);
      toast.success(t('channels.assist.applied'));
    }
  };
  
  // AI 助手：關閉
  const handleAssistClose = () => {
    setShowAssist(false);
    setAssistInput('');
    setAssistResult(null);
    setAssistMessage('');
  };
  
  // AI 助手：重置對話
  const handleAssistReset = () => {
    setAssistInput('');
    setAssistResult(null);
    setAssistMessage('');
  };
  
  // 提交表單
  const handleSubmit = async () => {
    if (!name.trim()) {
      toast.error(t('channels.validation.nameRequired'));
      return;
    }
    
    if (!category) {
      toast.error(t('channels.validation.categoryRequired'));
      return;
    }
    
    if (category === 'other' && customKeywords.length === 0) {
      toast.error(t('channels.validation.keywordsRequired'));
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      const data: ChannelCreateRequest = {
        name: name.trim(),
        category,
        region,
        custom_keywords: customKeywords,
        description: description.trim() || undefined,
      };
      
      await channelsApi.createChannel(data);
      toast.success(t('channels.createSuccess'));
      navigate('/channels');
    } catch (err: any) {
      toast.error(err.message || t('common.failed'));
    } finally {
      setIsSubmitting(false);
    }
  };
  
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 返回按鈕 */}
        <button
          onClick={() => navigate('/channels')}
          className="flex items-center gap-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 mb-6"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          {t('channels.backToList')}
        </button>
        
        {/* 標題 */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            {t('channels.create')}
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-2">
            {t('channels.createDescription')}
          </p>
        </div>
            {/* AI 助手按鈕 */}
            {step === 1 && (
              <button
                onClick={() => setShowAssist(true)}
                data-testid="btn-channels-assist"
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-500 to-cyan-500 text-white rounded-lg hover:from-purple-600 hover:to-cyan-600 transition-all shadow-lg"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                <span className="font-medium">{t('channels.assist.title')}</span>
              </button>
            )}
          </div>
        </div>
        
        {/* AI 助手對話框 */}
        {showAssist && (
          <div className="mb-8 bg-white dark:bg-gray-800 rounded-2xl p-4 sm:p-6 shadow-lg border-2 border-purple-200 dark:border-purple-800">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                <svg className="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                {t('channels.assist.title')}
              </h3>
              <button
                onClick={handleAssistClose}
                data-testid="btn-channels-assist-close"
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            {/* 快捷按鈕區域 */}
            <div className="mb-4">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                {t('channels.assist.quickButtons')}
              </p>
              <div className="space-y-3">
                {/* 常見組合預設 */}
                <div>
                  <p className="text-xs text-gray-400 dark:text-gray-500 mb-1.5">
                    {t('channels.assist.presets')}
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {quickPresets.map((preset) => (
                      <button
                        key={preset.key}
                        onClick={() => handlePresetClick(preset)}
                        data-testid={`btn-channels-assist-preset-${preset.key}`}
                        disabled={isAssisting}
                        className={`px-3 py-1.5 sm:px-4 sm:py-2 text-xs sm:text-sm rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1.5 min-h-[44px] border ${
                          category === preset.category && region === preset.region
                            ? 'bg-purple-100 dark:bg-purple-900/30 border-purple-400 dark:border-purple-600 text-purple-700 dark:text-purple-300 ring-1 ring-purple-300 dark:ring-purple-700'
                            : 'bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-600 border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:border-purple-300 dark:hover:border-purple-600 hover:shadow-sm'
                        }`}
                      >
                        <span className="text-sm">{preset.icon}</span>
                        <span>{t(`channels.assist.preset.${preset.key}` as any)}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* 類別快捷按鈕 - 顯示其他類型（非時尚/美食/趨勢） */}
                <div>
                  <p className="text-xs text-gray-400 dark:text-gray-500 mb-1.5">
                    {t('channels.assist.quickCategoryLabel')}
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {categories
                      .filter((cat) => !['fashion', 'food', 'trend'].includes(cat.value))
                      .map((cat) => (
                        <button
                          key={cat.value}
                          onClick={() => handleQuickCategoryClick(cat.value)}
                          data-testid={`btn-channels-assist-quick-category-${cat.value}`}
                          disabled={isAssisting}
                          className={`px-3 py-1.5 sm:px-4 sm:py-2 text-xs sm:text-sm rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1 min-h-[44px] border ${
                            category === cat.value
                              ? 'bg-purple-100 dark:bg-purple-900/30 border-purple-400 dark:border-purple-600 text-purple-700 dark:text-purple-300 ring-1 ring-purple-300 dark:ring-purple-700'
                              : 'bg-gray-100 dark:bg-gray-700 border-transparent text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                          }`}
                        >
                          <span className="text-base sm:text-lg">{cat.icon}</span>
                          <span className="hidden sm:inline">{t(cat.label)}</span>
                          <span className="sm:hidden">{t(cat.label).substring(0, 2)}</span>
                        </button>
                      ))}
                  </div>
                  <p className="text-xs text-gray-400 dark:text-gray-500 mt-2 px-1">
                    {t('channels.assist.quickCategoryNote')}
                  </p>
                </div>

                {/* 地區快捷按鈕 - 顯示全部 8 個地區 */}
                <div>
                  <p className="text-xs text-gray-400 dark:text-gray-500 mb-1.5">
                    {t('channels.assist.quickRegionLabel')}
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {regions.map((reg) => (
                      <button
                        key={reg.value}
                        onClick={() => handleQuickRegionClick(reg.value)}
                        data-testid={`btn-channels-assist-quick-region-${reg.value}`}
                        disabled={isAssisting}
                        className={`px-3 py-1.5 sm:px-4 sm:py-2 text-xs sm:text-sm rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed min-h-[44px] border ${
                          region === reg.value
                            ? 'bg-purple-100 dark:bg-purple-900/30 border-purple-400 dark:border-purple-600 text-purple-700 dark:text-purple-300 ring-1 ring-purple-300 dark:ring-purple-700'
                            : 'bg-gray-100 dark:bg-gray-700 border-transparent text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                        }`}
                      >
                        {t(reg.label)}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
            
            {/* 輸入區域 */}
            <div className="mb-4">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                {t('channels.assist.prompt')}
              </p>
              <div className="flex flex-col sm:flex-row gap-2">
                <input
                  type="text"
                  value={assistInput}
                  onChange={(e) => setAssistInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleAssistSubmit();
                    }
                  }}
                  placeholder={t('channels.assist.placeholder')}
                  data-testid="input-channels-assist"
                  disabled={isAssisting}
                  className="flex-1 px-4 py-3 sm:py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent disabled:opacity-50 text-sm sm:text-base min-h-[44px]"
                />
                <button
                  onClick={handleAssistSubmit}
                  disabled={!assistInput.trim() || isAssisting}
                  data-testid="btn-channels-assist-submit"
                  className="px-6 py-3 sm:py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2 min-h-[44px] text-sm sm:text-base font-medium"
                >
                  {isAssisting ? (
                    <>
                      <svg className="animate-spin h-4 w-4 sm:h-5 sm:w-5" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      <span className="hidden sm:inline">{t('common.loading')}</span>
                    </>
                  ) : (
                    t('channels.assist.submit')
                  )}
                </button>
              </div>
            </div>
            
            {/* AI 回覆訊息（打字效果） */}
            {typedMessage && (
              <div className="mb-4 p-3 sm:p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                <div className="flex items-start gap-2 sm:gap-3">
                  <svg className="w-5 h-5 sm:w-6 sm:h-6 text-purple-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm sm:text-base text-gray-700 dark:text-gray-300 whitespace-pre-line break-words">
                      {typedMessage}
                      {isTyping && (
                        <span className="inline-block w-2 h-4 bg-purple-500 ml-1 animate-pulse" />
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {/* 錯誤訊息顯示 */}
            {!isAssisting && assistResult && assistResult.confidence < 0.5 && !assistResult.clarification_needed && (
              <div className="mb-4 p-3 sm:p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                <div className="flex items-start gap-2">
                  <svg className="w-5 h-5 text-yellow-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <div className="flex-1">
                    <p className="text-sm sm:text-base text-yellow-800 dark:text-yellow-200">
                      {t('channels.assist.lowConfidenceWarning')}
                    </p>
                  </div>
                </div>
              </div>
            )}
            
            {/* 結果顯示 */}
            {assistResult && (
              <div className="mt-4 p-3 sm:p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                {assistResult.clarification_needed ? (
                  <div>
                    <p className="text-sm sm:text-base text-gray-700 dark:text-gray-300 mb-2 break-words">
                      {assistResult.clarification_question}
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3 sm:space-y-4">
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">{t('channels.assist.category')}</p>
                      <p className="font-medium text-sm sm:text-base text-gray-900 dark:text-white">
                        {assistResult.category ? categoryI18nKeys[assistResult.category as ChannelCategory] : '-'}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">{t('channels.assist.region')}</p>
                      <p className="font-medium text-sm sm:text-base text-gray-900 dark:text-white">
                        {assistResult.region ? regionI18nKeys[assistResult.region as ChannelRegion] : '-'}
                      </p>
                    </div>
                    {assistResult.keywords.length > 0 && (
                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">{t('channels.assist.keywords')}</p>
                        <div className="flex flex-wrap gap-2">
                          {assistResult.keywords.map((kw, idx) => (
                            <span key={idx} className="px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded text-xs sm:text-sm">
                              {kw}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {assistResult.recommended_sources.length > 0 && (
                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">{t('channels.assist.sources')}</p>
                        <div className="space-y-2">
                          {assistResult.recommended_sources.slice(0, 5).map((source, idx) => {
                            // 從 URL 解析網域與 favicon
                            let domain = '';
                            let faviconUrl = '';
                            let sourceType: 'rss' | 'web' | 'api' = 'web';
                            let websiteUrl = source.url; // 預設使用原始 URL
                            
                            try {
                              const urlObj = new URL(source.url);
                              domain = urlObj.hostname.replace(/^www\./, '');
                              faviconUrl = `https://www.google.com/s2/favicons?domain=${domain}&sz=32`;
                              
                              // 猜測來源類型
                              if (source.url.includes('/rss') || source.url.includes('/feed') || source.url.endsWith('.xml')) {
                                sourceType = 'rss';
                                // 如果是 RSS feed URL，提取網站首頁 URL
                                websiteUrl = `${urlObj.protocol}//${urlObj.hostname}`;
                              } else if (source.url.includes('/api') || source.url.includes('api.')) {
                                sourceType = 'api';
                              }
                            } catch {
                              domain = source.url;
                            }

                            const sourceTypeColors = {
                              rss: 'bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400',
                              web: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400',
                              api: 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400',
                            };

                            return (
                              <div 
                                key={idx} 
                                className="group p-3 sm:p-4 bg-white dark:bg-gray-600 rounded-xl border border-gray-200 dark:border-gray-500 hover:border-purple-300 dark:hover:border-purple-600 hover:shadow-md transition-all duration-200"
                                data-testid={`source-preview-${idx}`}
                              >
                                <div className="flex items-start gap-3">
                                  {/* Favicon */}
                                  <div className="flex-shrink-0 w-8 h-8 sm:w-10 sm:h-10 rounded-lg bg-gray-100 dark:bg-gray-500 flex items-center justify-center overflow-hidden">
                                    {faviconUrl ? (
                                      <img 
                                        src={faviconUrl} 
                                        alt="" 
                                        className="w-5 h-5 sm:w-6 sm:h-6"
                                        onError={(e) => {
                                          (e.target as HTMLImageElement).style.display = 'none';
                                          (e.target as HTMLImageElement).nextElementSibling?.classList.remove('hidden');
                                        }}
                                      />
                                    ) : null}
                                    <svg className={`w-4 h-4 sm:w-5 sm:h-5 text-gray-400 ${faviconUrl ? 'hidden' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                                    </svg>
                                  </div>

                                  {/* 來源資訊 */}
                                  <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-1">
                                      <p className="text-sm sm:text-base font-medium text-gray-900 dark:text-white truncate">
                                        {source.name}
                                      </p>
                                      {/* 來源類型標籤 */}
                                      <span className={`flex-shrink-0 px-1.5 py-0.5 text-[10px] sm:text-xs font-medium rounded ${sourceTypeColors[sourceType]}`}>
                                        {t(`channels.assist.sourceType.${sourceType}` as any)}
                                      </span>
                                    </div>
                                    {/* 網域 */}
                                    {domain && (
                                      <p className="text-xs text-gray-400 dark:text-gray-500 truncate mb-1">
                                        {domain}
                                      </p>
                                    )}
                                    {/* 角色描述 */}
                                    {source.role && (
                                      <p className="text-xs text-gray-500 dark:text-gray-400 break-words line-clamp-2">
                                        {source.role}
                                      </p>
                                    )}
                                  </div>

                                  {/* 訪問按鈕 */}
                                  {websiteUrl && (
                                    <a
                                      href={websiteUrl}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="flex-shrink-0 p-2 text-gray-400 hover:text-purple-500 group-hover:bg-purple-50 dark:group-hover:bg-purple-900/20 rounded-lg transition-all min-w-[44px] min-h-[44px] flex items-center justify-center"
                                      data-testid={`source-link-${idx}`}
                                      onClick={(e) => e.stopPropagation()}
                                      aria-label={t('channels.assist.visitSource')}
                                      title={t('channels.assist.visitSource')}
                                    >
                                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                      </svg>
                                    </a>
                                  )}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                        {assistResult.recommended_sources.length > 5 && (
                          <p className="text-xs text-gray-400 dark:text-gray-500 mt-2 text-center">
                            {t('channels.assist.moreSources', { count: assistResult.recommended_sources.length - 5 })}
                          </p>
                        )}
                      </div>
                    )}
                    <div className="flex flex-col sm:flex-row gap-2 pt-2">
                      <button
                        onClick={handleAssistConfirm}
                        data-testid="btn-channels-assist-confirm"
                        className="flex-1 px-4 py-3 sm:py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors min-h-[44px] text-sm sm:text-base font-medium"
                      >
                        {t('channels.assist.confirm')}
                      </button>
                      <button
                        onClick={handleAssistReset}
                        data-testid="btn-channels-assist-modify"
                        className="flex-1 px-4 py-3 sm:py-2 bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors min-h-[44px] text-sm sm:text-base font-medium"
                      >
                        {t('channels.assist.modify')}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
        
        {/* 步驟指示器 */}
        <div className="flex items-center justify-center mb-8">
          {[1, 2, 3].map((s) => (
            <div key={s} className="flex items-center">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center font-medium transition-all ${
                  s < step
                    ? 'bg-green-500 text-white'
                    : s === step
                    ? 'bg-purple-500 text-white'
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400'
                }`}
              >
                {s < step ? (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  s
                )}
              </div>
              {s < 3 && (
                <div
                  className={`w-20 h-1 ${
                    s < step ? 'bg-green-500' : 'bg-gray-200 dark:bg-gray-700'
                  }`}
                />
              )}
            </div>
          ))}
        </div>
        
        {/* 表單內容 */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg">
          {/* 步驟 1: 選擇類別 */}
          {step === 1 && (
            <div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                {t('channels.step1.title')}
              </h2>
              <p className="text-gray-500 dark:text-gray-400 mb-6">
                {t('channels.step1.description')}
              </p>
              
              <div className="grid grid-cols-2 gap-4">
                {categories.map((cat) => (
                  <button
                    key={cat.value}
                    onClick={() => setCategory(cat.value)}
                    className={`p-4 rounded-xl border-2 transition-all duration-200 flex items-center gap-3 ${
                      category === cat.value
                        ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
                        : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                    }`}
                  >
                    <span className="text-2xl">{cat.icon}</span>
                    <span className={`font-medium ${
                      category === cat.value
                        ? 'text-purple-600 dark:text-purple-400'
                        : 'text-gray-700 dark:text-gray-200'
                    }`}>
                      {t(cat.label)}
                    </span>
                  </button>
                ))}
              </div>
              
              <div className="mt-8 flex justify-end">
                <button
                  onClick={() => category && setStep(2)}
                  disabled={!category}
                  className="px-6 py-3 bg-purple-500 text-white font-medium rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-purple-600 transition-colors"
                >
                  {t('common.next')}
                </button>
              </div>
            </div>
          )}
          
          {/* 步驟 2: 選擇地區 */}
          {step === 2 && (
            <div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                {t('channels.step2.title')}
              </h2>
              <p className="text-gray-500 dark:text-gray-400 mb-6">
                {t('channels.step2.description')}
              </p>
              
              <div className="grid grid-cols-2 gap-4">
                {regions.map((reg) => (
                  <button
                    key={reg.value}
                    onClick={() => setRegion(reg.value)}
                    className={`p-4 rounded-xl border-2 transition-all duration-200 ${
                      region === reg.value
                        ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
                        : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                    }`}
                  >
                    <span className={`font-medium ${
                      region === reg.value
                        ? 'text-purple-600 dark:text-purple-400'
                        : 'text-gray-700 dark:text-gray-200'
                    }`}>
                      {t(reg.label)}
                    </span>
                  </button>
                ))}
              </div>
              
              {/* 自定義關鍵字（當類別為 other 時） */}
              {category === 'other' && (
                <div className="mt-6">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">
                    {t('channels.customKeywords')} <span className="text-red-500">*</span>
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={keywordInput}
                      onChange={(e) => setKeywordInput(e.target.value)}
                      onKeyDown={handleKeywordKeyDown}
                      placeholder={t('channels.keywordPlaceholder')}
                      className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                    <button
                      onClick={addKeyword}
                      disabled={!keywordInput.trim() || customKeywords.length >= 5}
                      className="px-4 py-2 bg-gray-100 dark:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {t('common.add')}
                    </button>
                  </div>
                  
                  {customKeywords.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {customKeywords.map((keyword, index) => (
                        <span
                          key={index}
                          className="inline-flex items-center gap-1 px-3 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded-full"
                        >
                          {keyword}
                          <button
                            onClick={() => removeKeyword(index)}
                            className="hover:text-purple-800 dark:hover:text-purple-200"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                        </span>
                      ))}
                    </div>
                  )}
                  
                  <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                    {t('channels.keywordsMax')} ({customKeywords.length}/5)
                  </p>
                </div>
              )}
              
              <div className="mt-8 flex justify-between">
                <button
                  onClick={() => setStep(1)}
                  className="px-6 py-3 text-gray-600 dark:text-gray-300 font-medium hover:text-gray-800 dark:hover:text-white"
                >
                  {t('common.previous')}
                </button>
                <button
                  onClick={() => setStep(3)}
                  disabled={category === 'other' && customKeywords.length === 0}
                  className="px-6 py-3 bg-purple-500 text-white font-medium rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-purple-600 transition-colors"
                >
                  {t('common.next')}
                </button>
              </div>
            </div>
          )}
          
          {/* 步驟 3: 命名頻道 */}
          {step === 3 && (
            <div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                {t('channels.step3.title')}
              </h2>
              <p className="text-gray-500 dark:text-gray-400 mb-6">
                {t('channels.step3.description')}
              </p>
              
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">
                    {t('channels.channelName')} <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder={t('channels.channelNamePlaceholder')}
                    maxLength={50}
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                  <p className="mt-1 text-sm text-gray-500 dark:text-gray-400 text-right">
                    {name.length}/50
                  </p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">
                    {t('channels.channelDescription')}
                  </label>
                  <textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder={t('channels.channelDescriptionPlaceholder')}
                    maxLength={200}
                    rows={3}
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                  />
                  <p className="mt-1 text-sm text-gray-500 dark:text-gray-400 text-right">
                    {description.length}/200
                  </p>
                </div>
              </div>
              
              {/* 預覽 */}
              <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">
                  {t('channels.preview')}
                </h3>
                <div className="flex items-center gap-3">
                  <span className="text-3xl">
                    {category && categoryIcons[category]}
                  </span>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {name || t('channels.unnamed')}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {category && categoryI18nKeys[category]} · {t(regionI18nKeys[region])}
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="mt-8 flex justify-between">
                <button
                  onClick={() => setStep(2)}
                  className="px-6 py-3 text-gray-600 dark:text-gray-300 font-medium hover:text-gray-800 dark:hover:text-white"
                >
                  {t('common.previous')}
                </button>
                <button
                  onClick={handleSubmit}
                  disabled={!name.trim() || isSubmitting}
                  className="px-8 py-3 bg-gradient-to-r from-purple-500 to-cyan-500 text-white font-medium rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:from-purple-600 hover:to-cyan-600 transition-all flex items-center gap-2"
                >
                  {isSubmitting ? (
                    <>
                      <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      {t('common.loading')}
                    </>
                  ) : (
                    t('channels.create')
                  )}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

