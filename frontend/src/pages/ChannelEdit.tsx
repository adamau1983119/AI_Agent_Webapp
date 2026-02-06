/**
 * 頻道設定頁
 * Phase 3: 內容功能
 */
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from '../i18n';
import { useAuthStore } from '../stores/authStore';
import {
  channelsApi,
  Channel,
  ChannelUpdateRequest,
  ChannelCategory,
  ChannelRegion,
  categoryLabels,
  regionLabels,
  categoryIcons,
} from '../api/channels';
import toast from 'react-hot-toast';

export default function ChannelEdit() {
  const { id } = useParams<{ id: string }>();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();
  
  const [channel, setChannel] = useState<Channel | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  
  // 表單狀態
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [customKeywords, setCustomKeywords] = useState<string[]>([]);
  const [keywordInput, setKeywordInput] = useState('');
  const [status, setStatus] = useState<'active' | 'paused'>('active');
  
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    
    if (id) {
      loadChannel();
    }
  }, [id, isAuthenticated, navigate]);
  
  const loadChannel = async () => {
    if (!id) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await channelsApi.getChannel(id);
      setChannel(data);
      setName(data.name);
      setDescription(data.description || '');
      setCustomKeywords(data.custom_keywords || []);
      setStatus(data.status === 'active' ? 'active' : 'paused');
    } catch (err: any) {
      setError(err.message || t('channels.loadFailed'));
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleAddKeyword = () => {
    if (keywordInput.trim() && !customKeywords.includes(keywordInput.trim())) {
      setCustomKeywords([...customKeywords, keywordInput.trim()]);
      setKeywordInput('');
    }
  };
  
  const handleRemoveKeyword = (keyword: string) => {
    setCustomKeywords(customKeywords.filter(k => k !== keyword));
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id) return;
    
    setIsSubmitting(true);
    
    try {
      const updateData: ChannelUpdateRequest = {
        name: name.trim(),
        description: description.trim() || undefined,
        custom_keywords: customKeywords.length > 0 ? customKeywords : undefined,
        status,
      };
      
      await channelsApi.updateChannel(id, updateData);
      toast.success(t('channels.updateSuccess'));
      navigate(`/channels/${id}`);
    } catch (err: any) {
      toast.error(err.message || t('channels.updateFailed'));
    } finally {
      setIsSubmitting(false);
    }
  };
  
  const handleDelete = async () => {
    if (!id) return;
    
    setIsDeleting(true);
    try {
      await channelsApi.deleteChannel(id);
      toast.success(t('channels.deleted'));
      navigate('/channels');
    } catch (err: any) {
      toast.error(err.message || t('channels.deleteFailed'));
    } finally {
      setIsDeleting(false);
      setShowDeleteConfirm(false);
    }
  };
  
  // 未登入
  if (!isAuthenticated) {
    return null;
  }
  
  // 載入中
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
          </div>
        </div>
      </div>
    );
  }
  
  // 錯誤
  if (error || !channel) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <p className="text-red-800 dark:text-red-200">{error || t('channels.notFound')}</p>
            <button
              onClick={() => navigate('/channels')}
              data-testid="btn-channel-edit-back"
              className="mt-4 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
            >
              {t('common.back')}
            </button>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 返回按鈕 */}
        <button
          onClick={() => navigate(`/channels/${channel.id}`)}
          data-testid="btn-channel-edit-back"
          className="mb-6 flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          {t('common.back')}
        </button>
        
        {/* 標題 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            {t('channels.editChannel')}
          </h1>
          <p className="text-gray-500 dark:text-gray-400">
            {t('channels.editDescription')}
          </p>
        </div>
        
        {/* 頻道資訊顯示（只讀） */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg mb-6">
          <div className="flex items-center gap-4 mb-4">
            <span className="text-4xl">
              {categoryIcons[channel.category as ChannelCategory]}
            </span>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">{t('channels.category')}</p>
              <p className="font-medium text-gray-900 dark:text-white">
                {categoryLabels[channel.category as ChannelCategory]}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">{t('channels.region')}</p>
              <p className="font-medium text-gray-900 dark:text-white">
                {regionLabels[channel.region as ChannelRegion]}
              </p>
            </div>
          </div>
          <p className="text-xs text-gray-400 dark:text-gray-500">
            {t('channels.categoryRegionNote')}
          </p>
        </div>
        
        {/* 表單 */}
        <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg space-y-6">
          {/* 頻道名稱 */}
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('channels.name')} <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              data-testid="input-channel-edit-name"
              className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent min-h-[44px]"
            />
          </div>
          
          {/* 描述 */}
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('channels.description')}
            </label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={4}
              data-testid="input-channel-edit-description"
              className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>
          
          {/* 自定義關鍵字 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('channels.keywords')}
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={keywordInput}
                onChange={(e) => setKeywordInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddKeyword();
                  }
                }}
                placeholder={t('channels.keywordPlaceholder')}
                data-testid="input-channel-edit-keyword"
                className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent min-h-[44px]"
              />
              <button
                type="button"
                onClick={handleAddKeyword}
                disabled={!keywordInput.trim()}
                data-testid="btn-channel-edit-add-keyword"
                className="px-4 py-2 bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed min-h-[44px]"
              >
                {t('common.add')}
              </button>
            </div>
            {customKeywords.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {customKeywords.map((keyword, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded-full text-sm flex items-center gap-2"
                  >
                    {keyword}
                    <button
                      type="button"
                      onClick={() => handleRemoveKeyword(keyword)}
                      data-testid={`btn-channel-edit-remove-keyword-${index}`}
                      className="text-purple-600 dark:text-purple-400 hover:text-purple-800 dark:hover:text-purple-200"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>
          
          {/* 狀態切換 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('channels.status')}
            </label>
            <div className="flex gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="status"
                  value="active"
                  checked={status === 'active'}
                  onChange={(e) => setStatus(e.target.value as 'active' | 'paused')}
                  data-testid="radio-channel-edit-status-active"
                  className="w-4 h-4 text-purple-600 focus:ring-purple-500"
                />
                <span className="text-gray-700 dark:text-gray-300">{t('channels.statusActive')}</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="status"
                  value="paused"
                  checked={status === 'paused'}
                  onChange={(e) => setStatus(e.target.value as 'active' | 'paused')}
                  data-testid="radio-channel-edit-status-paused"
                  className="w-4 h-4 text-purple-600 focus:ring-purple-500"
                />
                <span className="text-gray-700 dark:text-gray-300">{t('channels.statusPaused')}</span>
              </label>
            </div>
          </div>
          
          {/* 提交按鈕 */}
          <div className="flex flex-col sm:flex-row gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              type="submit"
              disabled={isSubmitting || !name.trim()}
              data-testid="btn-channel-edit-submit"
              className="flex-1 px-6 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed min-h-[44px] font-medium"
            >
              {isSubmitting ? t('common.saving') : t('common.save')}
            </button>
            <button
              type="button"
              onClick={() => setShowDeleteConfirm(true)}
              data-testid="btn-channel-edit-delete"
              className="px-6 py-3 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors min-h-[44px] font-medium"
            >
              {t('channels.deleteChannel')}
            </button>
          </div>
        </form>
        
        {/* 刪除確認對話框 */}
        {showDeleteConfirm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-md w-full">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                {t('channels.deleteConfirm')}
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                {t('channels.deleteWarning', { name: channel.name })}
              </p>
              <div className="flex gap-3">
                <button
                  onClick={() => setShowDeleteConfirm(false)}
                  data-testid="btn-channel-edit-delete-cancel"
                  className="flex-1 px-4 py-2 bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors min-h-[44px]"
                >
                  {t('common.cancel')}
                </button>
                <button
                  onClick={handleDelete}
                  disabled={isDeleting}
                  data-testid="btn-channel-edit-delete-confirm"
                  className="flex-1 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed min-h-[44px]"
                >
                  {isDeleting ? t('common.deleting') : t('common.delete')}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

