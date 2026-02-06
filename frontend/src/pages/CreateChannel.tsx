/**
 * 建立頻道頁面
 * Phase 3: 內容功能
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from '../i18n';
import { useAuthStore } from '../stores/authStore';
import {
  channelsApi,
  ChannelCategory,
  ChannelRegion,
  ChannelCreateRequest,
  categoryLabels,
  regionLabels,
  categoryIcons,
} from '../api/channels';
import toast from 'react-hot-toast';

const categories: { value: ChannelCategory; label: string; icon: string }[] = [
  { value: 'fashion', label: categoryLabels.fashion, icon: categoryIcons.fashion },
  { value: 'food', label: categoryLabels.food, icon: categoryIcons.food },
  { value: 'trend', label: categoryLabels.trend, icon: categoryIcons.trend },
  { value: 'finance', label: categoryLabels.finance, icon: categoryIcons.finance },
  { value: 'sports', label: categoryLabels.sports, icon: categoryIcons.sports },
  { value: 'tech', label: categoryLabels.tech, icon: categoryIcons.tech },
  { value: 'entertainment', label: categoryLabels.entertainment, icon: categoryIcons.entertainment },
  { value: 'other', label: categoryLabels.other, icon: categoryIcons.other },
];

const regions: { value: ChannelRegion; label: string }[] = [
  { value: 'global', label: regionLabels.global },
  { value: 'hong_kong', label: regionLabels.hong_kong },
  { value: 'taiwan', label: regionLabels.taiwan },
  { value: 'japan', label: regionLabels.japan },
  { value: 'korea', label: regionLabels.korea },
  { value: 'china', label: regionLabels.china },
  { value: 'usa', label: regionLabels.usa },
  { value: 'uk', label: regionLabels.uk },
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
  
  // AI 助手：處理用戶輸入
  const handleAssistSubmit = async () => {
    if (!assistInput.trim()) {
      toast.error(t('channels.assist.inputRequired'));
      return;
    }
    
    setIsAssisting(true);
    setAssistResult(null);
    
    try {
      const userLanguage = localStorage.getItem('language') || 'zh-TW';
      const result = await channelsApi.assistChannel(assistInput.trim(), userLanguage);
      setAssistResult(result);
      
      // 如果解析成功且信心度高，自動填入表單
      if (result.confidence >= 0.7 && result.category && result.region) {
        setCategory(result.category as ChannelCategory);
        setRegion(result.region as ChannelRegion);
        if (result.keywords.length > 0) {
          setCustomKeywords(result.keywords);
        }
        toast.success(t('channels.assist.autoFilled'));
      }
    } catch (err: any) {
      toast.error(err.message || t('channels.assist.failed'));
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
          <div className="mb-8 bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg border-2 border-purple-200 dark:border-purple-800">
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
            
            {/* 輸入區域 */}
            <div className="mb-4">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                {t('channels.assist.prompt')}
              </p>
              <div className="flex gap-2">
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
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent disabled:opacity-50"
                />
                <button
                  onClick={handleAssistSubmit}
                  disabled={!assistInput.trim() || isAssisting}
                  data-testid="btn-channels-assist-submit"
                  className="px-6 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                >
                  {isAssisting ? (
                    <>
                      <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      {t('common.loading')}
                    </>
                  ) : (
                    t('channels.assist.submit')
                  )}
                </button>
              </div>
            </div>
            
            {/* 結果顯示 */}
            {assistResult && (
              <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                {assistResult.clarification_needed ? (
                  <div>
                    <p className="text-sm text-gray-700 dark:text-gray-300 mb-2">
                      {assistResult.clarification_question}
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">{t('channels.assist.category')}</p>
                      <p className="font-medium text-gray-900 dark:text-white">
                        {assistResult.category ? categoryLabels[assistResult.category as ChannelCategory] : '-'}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">{t('channels.assist.region')}</p>
                      <p className="font-medium text-gray-900 dark:text-white">
                        {assistResult.region ? regionLabels[assistResult.region as ChannelRegion] : '-'}
                      </p>
                    </div>
                    {assistResult.keywords.length > 0 && (
                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">{t('channels.assist.keywords')}</p>
                        <div className="flex flex-wrap gap-2">
                          {assistResult.keywords.map((kw, idx) => (
                            <span key={idx} className="px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded text-sm">
                              {kw}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {assistResult.recommended_sources.length > 0 && (
                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">{t('channels.assist.sources')}</p>
                        <div className="space-y-1">
                          {assistResult.recommended_sources.slice(0, 3).map((source, idx) => (
                            <p key={idx} className="text-sm text-gray-700 dark:text-gray-300">
                              • {source.name}
                            </p>
                          ))}
                        </div>
                      </div>
                    )}
                    <div className="flex gap-2 pt-2">
                      <button
                        onClick={handleAssistConfirm}
                        data-testid="btn-channels-assist-confirm"
                        className="flex-1 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
                      >
                        {t('channels.assist.confirm')}
                      </button>
                      <button
                        onClick={() => {
                          setAssistInput('');
                          setAssistResult(null);
                        }}
                        data-testid="btn-channels-assist-modify"
                        className="flex-1 px-4 py-2 bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors"
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
                      {cat.label}
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
                      {reg.label}
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
                      {category && categoryLabels[category]} · {regionLabels[region]}
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

