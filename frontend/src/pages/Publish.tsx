/**
 * 一鍵發布頁面
 * Phase 5: 分發與整合
 */
import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import {
  socialApi,
  SocialConnection,
  SocialPlatform,
  PublishResponse,
  platformLabels,
  platformIcons,
  publishStatusLabels,
  publishStatusColors,
} from '../api/social';
import toast from 'react-hot-toast';

export default function Publish() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { isAuthenticated } = useAuthStore();
  
  const [connections, setConnections] = useState<SocialConnection[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  // 表單狀態
  const [content, setContent] = useState('');
  const [hashtags, setHashtags] = useState<string[]>([]);
  const [hashtagInput, setHashtagInput] = useState('');
  const [selectedPlatforms, setSelectedPlatforms] = useState<SocialPlatform[]>([]);
  const [imageUrls, setImageUrls] = useState<string[]>([]);
  const [imageInput, setImageInput] = useState('');
  
  // 發布狀態
  const [isPublishing, setIsPublishing] = useState(false);
  const [publishResult, setPublishResult] = useState<PublishResponse | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    
    // 從 URL 參數載入內容
    const contentParam = searchParams.get('content');
    if (contentParam) {
      setContent(contentParam);
    }
    
    loadConnections();
  }, [isAuthenticated, navigate, searchParams]);

  const loadConnections = async () => {
    setIsLoading(true);
    try {
      const { connections } = await socialApi.getMyConnections();
      setConnections(connections.filter((c) => c.status === 'connected'));
    } catch (err: any) {
      toast.error('載入連接失敗');
    } finally {
      setIsLoading(false);
    }
  };

  const togglePlatform = (platform: SocialPlatform) => {
    setSelectedPlatforms((prev) =>
      prev.includes(platform)
        ? prev.filter((p) => p !== platform)
        : [...prev, platform]
    );
  };

  const addHashtag = () => {
    const tag = hashtagInput.trim().replace(/^#/, '');
    if (tag && !hashtags.includes(tag) && hashtags.length < 30) {
      setHashtags([...hashtags, tag]);
      setHashtagInput('');
    }
  };

  const removeHashtag = (index: number) => {
    setHashtags(hashtags.filter((_, i) => i !== index));
  };

  const addImageUrl = () => {
    const url = imageInput.trim();
    if (url && !imageUrls.includes(url)) {
      setImageUrls([...imageUrls, url]);
      setImageInput('');
    }
  };

  const removeImageUrl = (index: number) => {
    setImageUrls(imageUrls.filter((_, i) => i !== index));
  };

  const handlePublish = async () => {
    if (!content.trim()) {
      toast.error('請輸入發布內容');
      return;
    }
    
    if (selectedPlatforms.length === 0) {
      toast.error('請選擇至少一個平台');
      return;
    }
    
    // 檢查 Instagram 是否需要圖片
    if (selectedPlatforms.includes('instagram') && imageUrls.length === 0) {
      toast.error('Instagram 發布需要至少一張圖片');
      return;
    }
    
    setIsPublishing(true);
    setPublishResult(null);
    
    try {
      const result = await socialApi.publishContent({
        content_id: `manual_${Date.now()}`,
        content: content.trim(),
        platforms: selectedPlatforms,
        hashtags,
        image_urls: imageUrls,
      });
      
      setPublishResult(result);
      
      if (result.successful === result.total_platforms) {
        toast.success('發布成功！');
      } else if (result.successful > 0) {
        toast.success(`部分發布成功（${result.successful}/${result.total_platforms}）`);
      } else {
        toast.error('發布失敗');
      }
    } catch (err: any) {
      toast.error(err.message || '發布失敗');
    } finally {
      setIsPublishing(false);
    }
  };

  if (!isAuthenticated) return null;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 標題 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            一鍵發布
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-2">
            將內容發布到多個社交平台
          </p>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <svg className="animate-spin h-12 w-12 text-purple-500" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          </div>
        ) : connections.length === 0 ? (
          <div className="text-center py-20">
            <div className="w-20 h-20 mx-auto mb-4 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
              <svg className="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              尚未連接任何平台
            </h3>
            <p className="text-gray-500 dark:text-gray-400 mb-4">
              請先連接您的社交媒體帳號
            </p>
            <button
              onClick={() => navigate('/social-connect')}
              className="px-6 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600"
            >
              連接帳號
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* 左側：內容編輯 */}
            <div className="lg:col-span-2 space-y-6">
              {/* 內容輸入 */}
              <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  發布內容
                </h2>
                <textarea
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="輸入您要發布的內容..."
                  rows={6}
                  className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl text-gray-900 dark:text-white placeholder-gray-400 resize-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
                <p className="mt-2 text-sm text-gray-500 dark:text-gray-400 text-right">
                  {content.length} 字
                </p>
              </div>

              {/* Hashtags */}
              <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Hashtags
                </h2>
                <div className="flex gap-2 mb-4">
                  <input
                    type="text"
                    value={hashtagInput}
                    onChange={(e) => setHashtagInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addHashtag())}
                    placeholder="輸入 hashtag"
                    className="flex-1 px-4 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white"
                  />
                  <button
                    onClick={addHashtag}
                    className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600"
                  >
                    添加
                  </button>
                </div>
                {hashtags.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {hashtags.map((tag, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center gap-1 px-3 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded-full text-sm"
                      >
                        #{tag}
                        <button onClick={() => removeHashtag(index)} className="hover:text-purple-800">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* 圖片 */}
              <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  圖片（Instagram 必須）
                </h2>
                <div className="flex gap-2 mb-4">
                  <input
                    type="text"
                    value={imageInput}
                    onChange={(e) => setImageInput(e.target.value)}
                    placeholder="輸入圖片 URL"
                    className="flex-1 px-4 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white"
                  />
                  <button
                    onClick={addImageUrl}
                    className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600"
                  >
                    添加
                  </button>
                </div>
                {imageUrls.length > 0 && (
                  <div className="grid grid-cols-3 gap-4">
                    {imageUrls.map((url, index) => (
                      <div key={index} className="relative">
                        <img
                          src={url}
                          alt={`圖片 ${index + 1}`}
                          className="w-full h-24 object-cover rounded-lg"
                          onError={(e) => {
                            (e.target as HTMLImageElement).src = 'https://via.placeholder.com/150?text=Invalid';
                          }}
                        />
                        <button
                          onClick={() => removeImageUrl(index)}
                          className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* 右側：平台選擇和發布 */}
            <div className="space-y-6">
              {/* 選擇平台 */}
              <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  選擇平台
                </h2>
                <div className="space-y-3">
                  {connections.map((connection) => {
                    const platform = connection.platform as SocialPlatform;
                    const selected = selectedPlatforms.includes(platform);
                    
                    return (
                      <button
                        key={connection.id}
                        onClick={() => togglePlatform(platform)}
                        className={`w-full flex items-center gap-3 p-3 rounded-xl border-2 transition-all ${
                          selected
                            ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
                            : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                        }`}
                      >
                        <span className="text-2xl">{platformIcons[platform]}</span>
                        <div className="flex-1 text-left">
                          <p className={`font-medium ${
                            selected ? 'text-purple-600 dark:text-purple-400' : 'text-gray-700 dark:text-gray-200'
                          }`}>
                            {platformLabels[platform]}
                          </p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            @{connection.platform_username}
                          </p>
                        </div>
                        {selected && (
                          <svg className="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        )}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* 發布按鈕 */}
              <button
                onClick={handlePublish}
                disabled={isPublishing || !content.trim() || selectedPlatforms.length === 0}
                className="w-full px-6 py-4 bg-gradient-to-r from-purple-500 to-cyan-500 text-white font-medium rounded-xl disabled:opacity-50 disabled:cursor-not-allowed hover:from-purple-600 hover:to-cyan-600 transition-all flex items-center justify-center gap-2"
              >
                {isPublishing ? (
                  <>
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    發布中...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                    發布到 {selectedPlatforms.length} 個平台
                  </>
                )}
              </button>

              {/* 發布結果 */}
              {publishResult && (
                <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    發布結果
                  </h3>
                  <div className="space-y-3">
                    {publishResult.results.map((result, index) => (
                      <div
                        key={index}
                        className={`p-3 rounded-xl ${
                          result.status === 'published'
                            ? 'bg-green-50 dark:bg-green-900/20'
                            : 'bg-red-50 dark:bg-red-900/20'
                        }`}
                      >
                        <div className="flex items-center gap-2">
                          <span>{platformIcons[result.platform as SocialPlatform]}</span>
                          <span className="font-medium text-gray-900 dark:text-white">
                            {platformLabels[result.platform as SocialPlatform]}
                          </span>
                          <span className={`ml-auto text-sm px-2 py-0.5 rounded-full ${publishStatusColors[result.status]}`}>
                            {publishStatusLabels[result.status]}
                          </span>
                        </div>
                        {result.post_url && (
                          <a
                            href={result.post_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm text-purple-500 hover:text-purple-600 mt-1 block"
                          >
                            查看貼文 →
                          </a>
                        )}
                        {result.error_message && (
                          <p className="text-sm text-red-500 mt-1">{result.error_message}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

