/**
 * 靈感策劃頁面
 * Phase 3: 內容功能
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from '../i18n';
import { useAuthStore } from '../stores/authStore';
import { inspirationApi, InspirationItem } from '../api/inspiration';
import toast from 'react-hot-toast';

const categories = [
  { value: 'general', label: '全部', icon: '✨' },
  { value: 'fashion', label: '時尚', icon: '👗' },
  { value: 'food', label: '美食', icon: '🍽️' },
  { value: 'tech', label: '科技', icon: '💻' },
  { value: 'finance', label: '財經', icon: '💰' },
  { value: 'sports', label: '運動', icon: '⚽' },
  { value: 'entertainment', label: '娛樂', icon: '🎬' },
];

export default function Inspiration() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuthStore();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('general');
  const [results, setResults] = useState<InspirationItem[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  
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
    } catch (err) {
      console.error('Failed to load trending:', err);
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
      toast.error('搜尋失敗');
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
  
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 標題 */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            靈感策劃
          </h1>
          <p className="text-gray-500 dark:text-gray-400">
            探索創作靈感，發現熱門趨勢
          </p>
        </div>
        
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
                placeholder="搜尋靈感主題..."
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
              className="px-8 py-4 bg-gradient-to-r from-purple-500 to-cyan-500 text-white font-medium rounded-2xl hover:from-purple-600 hover:to-cyan-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              搜尋
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
              <p className="text-gray-500">搜尋中...</p>
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
              暫無結果，試試其他關鍵字
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {results.map((item, index) => (
              <InspirationCard key={index} item={item} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// 靈感卡片組件
function InspirationCard({ item }: { item: InspirationItem }) {
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
              {item.source === 'google' ? '🔍 搜尋結果' : '✨ AI 生成'}
            </span>
            
            {/* 連結 */}
            {item.url && (
              <a
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-purple-500 hover:text-purple-600 flex items-center gap-1"
              >
                查看原文
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
            className="p-2 text-gray-400 hover:text-purple-500 hover:bg-purple-50 dark:hover:bg-purple-900/20 rounded-lg transition-colors"
            title="使用此靈感"
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

