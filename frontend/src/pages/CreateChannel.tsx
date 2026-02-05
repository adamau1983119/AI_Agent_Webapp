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
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            {t('channels.create')}
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-2">
            {t('channels.createDescription')}
          </p>
        </div>
        
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

