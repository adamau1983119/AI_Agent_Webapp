/**
 * 靈感策劃頁面
 * Phase 3: 內容功能
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from '../i18n';
import { useAuthStore } from '../stores/authStore';
import { 
  inspirationApi, 
  InspirationItem,
  AssistantStartResponse,
  AssistantGenerateResponse,
  QuestionOption
} from '../api/inspiration';
import toast from 'react-hot-toast';

export default function Inspiration() {
  const { t } = useTranslation();
  
  const categories = [
    { value: 'general', label: t('filters.all'), icon: '✨' },
    { value: 'fashion', label: t('filters.fashion'), icon: '👗' },
    { value: 'food', label: t('filters.food'), icon: '🍽️' },
    { value: 'tech', label: t('filters.tech'), icon: '💻' },
    { value: 'finance', label: t('filters.finance'), icon: '💰' },
    { value: 'sports', label: t('filters.sports'), icon: '⚽' },
    { value: 'entertainment', label: t('filters.entertainment'), icon: '🎬' },
  ];
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuthStore();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('general');
  const [results, setResults] = useState<InspirationItem[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  
  // AI 助手狀態
  const [mode, setMode] = useState<'search' | 'assistant'>('search');
  const [assistantTopic, setAssistantTopic] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [questions, setQuestions] = useState<QuestionOption[]>([]);
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState<AssistantGenerateResponse | null>(null);
  
  // 載入熱門趨勢
  useEffect(() => {
    loadTrending();
  }, [selectedCategory]);
  
  // 搜尋建議
  useEffect(() => {
    if (searchQuery.length >= 2) {
      const timer = setTimeout(async () => {
        try {
          const response = await inspirationApi.getSuggestions(searchQuery);
          setSuggestions(response.suggestions);
          setShowSuggestions(true);
        } catch (err) {
          console.error('Failed to get suggestions:', err);
        }
      }, 300);
      
      return () => clearTimeout(timer);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, [searchQuery]);
  
  const loadTrending = async () => {
    setIsSearching(true);
    try {
      const response = await inspirationApi.getTrending({
        category: selectedCategory,
        language: user?.language || 'zh-TW',
        limit: 10,
      });
      setResults(response.topics);
    } catch (err: any) {
      console.error('Failed to load trending:', err);
      // 顯示錯誤提示給用戶
      const errorMessage = err?.message || t('common.failed');
      toast.error(errorMessage);
      // 如果 API 失敗，清空結果列表
      setResults([]);
    } finally {
      setIsSearching(false);
    }
  };
  
  const handleSearch = async (query?: string) => {
    const q = query || searchQuery;
    if (!q.trim()) return;
    
    setShowSuggestions(false);
    setIsSearching(true);
    
    try {
      const response = await inspirationApi.search(q, {
        language: user?.language || 'zh-TW',
        limit: 10,
      });
      setResults(response.results);
    } catch (err: any) {
      toast.error(t('common.failed'));
    } finally {
      setIsSearching(false);
    }
  };
  
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };
  
  const handleSuggestionClick = (suggestion: string) => {
    setSearchQuery(suggestion);
    setShowSuggestions(false);
    handleSearch(suggestion);
  };
  
  const handleUseInspiration = (item: InspirationItem) => {
    // 導航到 AI 頻道助手頁面，傳遞靈感資訊作為初始輸入
    // 如果沒有 AI 頻道助手頁面，則導航到主題列表頁面並顯示提示
    if (isAuthenticated) {
      // 已登入：導航到 AI 頻道助手（如果有的話）或主題列表
      // 暫時導航到主題列表，並在 localStorage 中保存靈感資訊供後續使用
      const inspirationData = {
        title: item.title,
        description: item.description,
        url: item.url,
        source: item.source,
      };
      localStorage.setItem('pendingInspiration', JSON.stringify(inspirationData));
      navigate('/topics');
      toast.success(t('inspiration.inspirationSaved'));
    } else {
      // 未登入：提示用戶登入
      toast.error(t('auth.loginRequired'));
      navigate('/login');
    }
  };
  
  // AI 助手功能
  const handleStartAssistant = async () => {
    if (!assistantTopic.trim()) {
      toast.error(t('inspiration.assistant.topicRequired'));
      return;
    }
    
    if (!isAuthenticated) {
      toast.error(t('auth.loginRequired'));
      navigate('/login');
      return;
    }
    
    try {
      setIsSearching(true);
      const response = await inspirationApi.assistantStart(
        assistantTopic,
        user?.language || 'zh-TW'
      );
      
      setSessionId(response.session_id);
      setQuestions(response.questions);
      setCurrentQuestionIndex(0);
      setAnswers({});
      setGeneratedContent(null);
      setMode('assistant');
    } catch (err: any) {
      toast.error(err?.message || t('inspiration.assistant.startFailed'));
    } finally {
      setIsSearching(false);
    }
  };
  
  const handleAnswerQuestion = (questionId: string, answer: string) => {
    setAnswers({ ...answers, [questionId]: answer });
  };
  
  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      handleGenerateContent();
    }
  };
  
  const handleGenerateContent = async () => {
    if (!sessionId) return;
    
    try {
      setIsGenerating(true);
      const response = await inspirationApi.assistantGenerate(sessionId, answers);
      setGeneratedContent(response);
    } catch (err: any) {
      toast.error(err?.message || t('inspiration.assistant.generateFailed'));
    } finally {
      setIsGenerating(false);
    }
  };
  
  const handleResetAssistant = () => {
    setMode('search');
    setAssistantTopic('');
    setSessionId(null);
    setQuestions([]);
    setAnswers({});
    setCurrentQuestionIndex(0);
    setGeneratedContent(null);
  };
  
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 標題 */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            {t('inspiration.title')}
          </h1>
          <p className="text-gray-500 dark:text-gray-400">
            {t('nav.inspiration')}
          </p>
        </div>
        
        {/* 模式切換 */}
        <div className="flex gap-4 mb-8 justify-center">
          <button
            onClick={() => setMode('search')}
            className={`px-6 py-3 rounded-full font-medium transition-all ${
              mode === 'search'
                ? 'bg-purple-500 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
            data-testid="btn-inspiration-mode-search"
          >
            🔍 {t('common.search')}
          </button>
          {isAuthenticated && (
            <button
              onClick={() => {
                setMode('assistant');
                if (!sessionId) {
                  setAssistantTopic('');
                }
              }}
              className={`px-6 py-3 rounded-full font-medium transition-all ${
                mode === 'assistant'
                  ? 'bg-purple-500 text-white'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
              data-testid="btn-inspiration-mode-assistant"
            >
              🤖 {t('inspiration.assistant.title')}
            </button>
          )}
        </div>
        
        {/* AI 助手模式 */}
        {mode === 'assistant' && (
          <div className="mb-8">
            {!sessionId ? (
              // 開始對話
              <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                  {t('inspiration.assistant.title')}
                </h2>
                <p className="text-gray-500 dark:text-gray-400 mb-6">
                  {t('inspiration.assistant.subtitle')}
                </p>
                <div className="flex gap-4">
                  <input
                    type="text"
                    value={assistantTopic}
                    onChange={(e) => setAssistantTopic(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleStartAssistant()}
                    placeholder={t('inspiration.assistant.topicPlaceholder')}
                    className="flex-1 px-5 py-4 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    data-testid="input-assistant-topic"
                  />
                  <button
                    onClick={handleStartAssistant}
                    disabled={!assistantTopic.trim() || isSearching}
                    className="px-8 py-4 bg-gradient-to-r from-purple-500 to-cyan-500 text-white font-medium rounded-xl hover:from-purple-600 hover:to-cyan-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                    data-testid="btn-assistant-start"
                  >
                    {t('inspiration.assistant.startConversation')}
                  </button>
                </div>
              </div>
            ) : generatedContent ? (
              // 顯示生成的內容
              <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                    {t('inspiration.assistant.contentReady')}
                  </h2>
                  <button
                    onClick={handleResetAssistant}
                    className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                  >
                    {t('common.close')}
                  </button>
                </div>
                
                {/* 驗證狀態 */}
                {generatedContent.verification_status && (
                  <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-xl">
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                        generatedContent.verification_status.status === 'verified'
                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                          : generatedContent.verification_status.status === 'partially_verified'
                          ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                          : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                      }`}>
                        {generatedContent.verification_status.status === 'verified' && '✅ '}
                        {generatedContent.verification_status.status === 'partially_verified' && '⚠️ '}
                        {generatedContent.verification_status.status === 'unverified' && '❌ '}
                        {t(`inspiration.verification.${generatedContent.verification_status.status}`)}
                      </span>
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        {Math.round(generatedContent.verification_status.confidence * 100)}% 可信度
                      </span>
                    </div>
                  </div>
                )}
                
                {/* 內容 */}
                <div className="mb-6 p-6 bg-gray-50 dark:bg-gray-700 rounded-xl">
                  <pre className="whitespace-pre-wrap text-gray-900 dark:text-white font-sans">
                    {generatedContent.content}
                  </pre>
                </div>
                
                {/* 來源 */}
                {generatedContent.sources && generatedContent.sources.length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                      參考來源
                    </h3>
                    <div className="space-y-2">
                      {generatedContent.sources.map((source, index) => (
                        <a
                          key={index}
                          href={source.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="block p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                        >
                          <div className="font-medium text-gray-900 dark:text-white">
                            {source.title}
                          </div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            {source.url}
                          </div>
                        </a>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* 操作按鈕 */}
                <div className="flex gap-4">
                  <button
                    onClick={() => {
                      // 使用此內容（可以導航到內容生成頁面）
                      toast.success(t('inspiration.assistant.contentSavedToast'));
                      handleResetAssistant();
                    }}
                    className="flex-1 px-6 py-3 bg-gradient-to-r from-purple-500 to-cyan-500 text-white font-medium rounded-xl hover:from-purple-600 hover:to-cyan-600 transition-all"
                    data-testid="btn-assistant-use-content"
                  >
                    {t('inspiration.assistant.useContent')}
                  </button>
                  <button
                    onClick={handleGenerateContent}
                    disabled={isGenerating}
                    className="px-6 py-3 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-200 font-medium rounded-xl hover:bg-gray-50 dark:hover:bg-gray-600 transition-all disabled:opacity-50"
                    data-testid="btn-assistant-regenerate"
                  >
                    {t('inspiration.assistant.regenerate')}
                  </button>
                </div>
              </div>
            ) : (
              // 問答流程
              <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
                  {t('inspiration.assistant.askQuestion')}
                </h2>
                
                {questions.length > 0 && currentQuestionIndex < questions.length && (
                  <div>
                    <div className="mb-6">
                      <div className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                        問題 {currentQuestionIndex + 1} / {questions.length}
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                        {questions[currentQuestionIndex].question}
                      </h3>
                      
                      {/* 快速選擇選項 */}
                      {questions[currentQuestionIndex].options && questions[currentQuestionIndex].options.length > 0 && (
                        <div className="grid grid-cols-2 gap-3 mb-4">
                          {questions[currentQuestionIndex].options.map((option, idx) => (
                            <button
                              key={idx}
                              onClick={() => handleAnswerQuestion(
                                questions[currentQuestionIndex].question_id,
                                option
                              )}
                              className={`p-4 rounded-xl border-2 transition-all ${
                                answers[questions[currentQuestionIndex].question_id] === option
                                  ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300'
                                  : 'border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 hover:border-purple-300 dark:hover:border-purple-600'
                              }`}
                              data-testid={`btn-assistant-option-${idx}`}
                            >
                              {option}
                            </button>
                          ))}
                        </div>
                      )}
                      
                      {/* 自定義輸入 */}
                      {questions[currentQuestionIndex].options && questions[currentQuestionIndex].options.length === 0 && (
                        <input
                          type="text"
                          value={answers[questions[currentQuestionIndex].question_id] || ''}
                          onChange={(e) => handleAnswerQuestion(
                            questions[currentQuestionIndex].question_id,
                            e.target.value
                          )}
                          onKeyDown={(e) => e.key === 'Enter' && handleNextQuestion()}
                          placeholder={t('inspiration.assistant.answer')}
                          className="w-full px-5 py-4 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                          data-testid="input-assistant-answer"
                        />
                      )}
                    </div>
                    
                    <div className="flex gap-4">
                      {currentQuestionIndex > 0 && (
                        <button
                          onClick={() => setCurrentQuestionIndex(currentQuestionIndex - 1)}
                          className="px-6 py-3 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-200 font-medium rounded-xl hover:bg-gray-50 dark:hover:bg-gray-600 transition-all"
                        >
                          {t('common.back')}
                        </button>
                      )}
                      <button
                        onClick={handleNextQuestion}
                        disabled={
                          !answers[questions[currentQuestionIndex].question_id] ||
                          (currentQuestionIndex === questions.length - 1 && isGenerating)
                        }
                        className="flex-1 px-6 py-3 bg-gradient-to-r from-purple-500 to-cyan-500 text-white font-medium rounded-xl hover:from-purple-600 hover:to-cyan-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                        data-testid="btn-assistant-next"
                      >
                        {currentQuestionIndex === questions.length - 1
                          ? (isGenerating ? t('inspiration.assistant.generating') : t('inspiration.assistant.generate'))
                          : t('inspiration.assistant.next')}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
        
        {/* 搜尋欄 */}
        <div className="relative mb-8">
          <div className="flex gap-4">
            <div className="relative flex-1">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
                placeholder={t('inspiration.searchPlaceholder')}
                data-testid="input-inspiration-search"
                className="w-full px-5 py-4 pl-12 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
              <svg
                className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              
              {/* 搜尋建議 */}
              {showSuggestions && suggestions.length > 0 && (
                <>
                  <div
                    className="fixed inset-0 z-10"
                    onClick={() => setShowSuggestions(false)}
                  />
                  <div className="absolute top-full left-0 right-0 mt-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-lg z-20 overflow-hidden">
                    {suggestions.map((suggestion, index) => (
                      <button
                        key={index}
                        onClick={() => handleSuggestionClick(suggestion)}
                        data-testid={`btn-inspiration-suggestion-${index}`}
                        className="w-full px-4 py-3 text-left text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                      >
                        <span className="flex items-center gap-2">
                          <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                          </svg>
                          {suggestion}
                        </span>
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>
            
            <button
              onClick={() => handleSearch()}
              disabled={!searchQuery.trim() || isSearching}
              data-testid="btn-inspiration-search"
              className="px-8 py-4 bg-gradient-to-r from-purple-500 to-cyan-500 text-white font-medium rounded-2xl hover:from-purple-600 hover:to-cyan-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {t('common.search')}
            </button>
          </div>
        </div>
        
        {/* 類別選擇 */}
        <div className="flex flex-wrap gap-2 mb-8 justify-center">
          {categories.map((cat) => (
            <button
              key={cat.value}
              onClick={() => {
                setSelectedCategory(cat.value);
                setSearchQuery('');
              }}
              data-testid={`btn-inspiration-category-${cat.value}`}
              className={`px-4 py-2 rounded-full font-medium transition-all ${
                selectedCategory === cat.value
                  ? 'bg-purple-500 text-white'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              <span className="mr-1">{cat.icon}</span>
              {cat.label}
            </button>
          ))}
        </div>
        
        {/* 結果列表 */}
        {isSearching ? (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <svg className="animate-spin h-12 w-12 text-purple-500 mx-auto mb-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <p className="text-gray-500">{t('common.searching')}</p>
            </div>
          </div>
        ) : results.length === 0 ? (
          <div className="text-center py-20">
            <div className="w-20 h-20 mx-auto mb-4 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
              <svg className="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <p className="text-gray-500 dark:text-gray-400">
              {t('common.noData')}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {results.map((item, index) => (
              <InspirationCard
                key={index}
                item={item}
                onUseInspiration={handleUseInspiration}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// 靈感卡片組件
function InspirationCard({
  item,
  onUseInspiration,
}: {
  item: InspirationItem;
  onUseInspiration: (item: InspirationItem) => void;
}) {
  const { t } = useTranslation();
  
  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-shadow duration-200">
      <div className="flex gap-4">
        {/* 圖片 */}
        {item.image_url && (
          <div className="flex-shrink-0 w-24 h-24 rounded-xl overflow-hidden bg-gray-100 dark:bg-gray-700">
            <img
              src={item.image_url}
              alt={item.title}
              className="w-full h-full object-cover"
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = 'none';
              }}
            />
          </div>
        )}
        
        {/* 內容 */}
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2">
            {item.title}
          </h3>
          
          {item.description && (
            <p className="text-gray-600 dark:text-gray-300 text-sm mb-3 line-clamp-2">
              {item.description}
            </p>
          )}
          
          <div className="flex items-center gap-4">
            {/* 來源 */}
            <span className={`text-xs px-2 py-1 rounded-full ${
              item.source === 'google'
                ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
                : 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400'
            }`}>
              {item.source === 'google' ? `🔍 ${t('inspiration.searchResult')}` : `✨ ${t('inspiration.aiGenerated')}`}
            </span>
            
            {/* 連結 */}
            {item.url && (
              <a
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-purple-500 hover:text-purple-600 flex items-center gap-1"
              >
                {t('inspiration.viewOriginal')}
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            )}
          </div>
        </div>
        
        {/* 操作按鈕 */}
        <div className="flex-shrink-0">
          <button
            type="button"
            data-testid="btn-inspiration-use-this"
            onClick={() => onUseInspiration(item)}
            className="p-2 text-gray-400 hover:text-purple-500 hover:bg-purple-50 dark:hover:bg-purple-900/20 rounded-lg transition-colors"
            title={t('inspiration.useThis')}
            aria-label={t('inspiration.useThis')}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}

