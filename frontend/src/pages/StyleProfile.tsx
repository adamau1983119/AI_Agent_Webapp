/**
 * 風格檔案頁面
 * Phase 4: AI 個人化
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { useTranslation } from '../i18n';
import {
  styleProfileApi,
  StyleAnalysis,
  PresetStyle,
  presetStyleLabels,
  learningStageLabels,
  getLearningProgress,
} from '../api/styleProfile';
import toast from 'react-hot-toast';

const presetStyles: { value: PresetStyle; icon: string; description: string }[] = [
  { value: 'professional', icon: '💼', description: '適合商業、財經、科技等專業內容' },
  { value: 'casual', icon: '😊', description: '適合生活、旅遊、美食等日常內容' },
  { value: 'humorous', icon: '😂', description: '適合娛樂、趣聞、創意內容' },
  { value: 'inspiring', icon: '✨', description: '適合勵志、成長、心靈雞湯內容' },
  { value: 'storytelling', icon: '📖', description: '適合分享經歷、教學、深度內容' },
];

export default function StyleProfile() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuthStore();
  const [analysis, setAnalysis] = useState<StyleAnalysis | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedStyle, setSelectedStyle] = useState<PresetStyle | null>(null);
  const [isUpdating, setIsUpdating] = useState(false);
  const [showResetConfirm, setShowResetConfirm] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    loadAnalysis();
  }, [isAuthenticated, navigate]);

  const loadAnalysis = async () => {
    setIsLoading(true);
    try {
      const data = await styleProfileApi.getAnalysis();
      setAnalysis(data);
      setSelectedStyle(data.preset_style);
    } catch (err: any) {
      toast.error(t('common.failed'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleStyleChange = async (style: PresetStyle) => {
    if (style === selectedStyle) return;
    
    setIsUpdating(true);
    try {
      await styleProfileApi.setPresetStyle(style);
      setSelectedStyle(style);
      toast.success(`已切換為「${presetStyleLabels[style]}」風格`);
      loadAnalysis();
    } catch (err: any) {
      toast.error(err.message || t('common.failed'));
    } finally {
      setIsUpdating(false);
    }
  };

  const handleReset = async () => {
    try {
      await styleProfileApi.reset();
      toast.success(t('common.success'));
      setShowResetConfirm(false);
      loadAnalysis();
    } catch (err: any) {
      toast.error(err.message || t('common.failed'));
    }
  };

  if (!isAuthenticated) return null;

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <svg className="animate-spin h-12 w-12 text-purple-500 mx-auto mb-4" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          <p className="text-gray-500">{t('common.loading')}</p>
        </div>
      </div>
    );
  }

  const progress = analysis ? getLearningProgress(analysis.learning_stage, analysis.total_ratings) : 0;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 標題 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">{t('style.title')}</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-2">
            {t('nav.styleProfile')}
          </p>
        </div>

        {/* 學習進度卡片 */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                學習進度
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {analysis?.learning_stage_label || '冷啟動'} · 已評分 {analysis?.total_ratings || 0} 次
              </p>
            </div>
            <div className={`px-4 py-2 rounded-full text-sm font-medium ${
              analysis?.learning_stage === 'mature'
                ? 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400'
                : analysis?.learning_stage === 'learning'
                ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-400'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
            }`}>
              {learningStageLabels[analysis?.learning_stage || 'cold_start']}
            </div>
          </div>

          {/* 進度條 */}
          <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-purple-500 to-cyan-500 transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>

          {/* 里程碑 */}
          <div className="flex justify-between mt-2 text-xs text-gray-500 dark:text-gray-400">
            <span>{t('style.coldStart')} (0)</span>
            <span>{t('style.learning')} (20)</span>
            <span>{t('style.mature')} (100)</span>
          </div>

          {/* 建議 */}
          {analysis?.recommendations && analysis.recommendations.length > 0 && (
            <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              {analysis.recommendations.map((rec, index) => (
                <p key={index} className="text-sm text-gray-600 dark:text-gray-300 flex items-start gap-2">
                  <span className="text-purple-500">💡</span>
                  {rec}
                </p>
              ))}
            </div>
          )}
        </div>

        {/* 信心分數 */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <StatCard
            label="信心分數"
            value={`${Math.round((analysis?.confidence_score || 0) * 100)}%`}
            icon="🎯"
          />
          <StatCard
            label="總評分數"
            value={analysis?.total_ratings?.toString() || '0'}
            icon="📊"
          />
          <StatCard
            label="正面比例"
            value={`${Math.round((analysis?.positive_ratio || 0) * 100)}%`}
            icon="👍"
          />
          <StatCard
            label="風格特徵"
            value={analysis?.style_traits?.length?.toString() || '0'}
            icon="✨"
          />
        </div>

        {/* 風格特徵 */}
        {analysis?.style_traits && analysis.style_traits.length > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg mb-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              您的風格特徵
            </h2>
            <div className="flex flex-wrap gap-2">
              {analysis.style_traits.map((trait, index) => (
                <span
                  key={index}
                  className="px-4 py-2 bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded-full text-sm font-medium"
                >
                  {trait}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* 預設風格選擇 */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg mb-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            預設風格
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
            選擇一個基礎風格，系統會在此基礎上學習您的偏好
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {presetStyles.map((style) => (
              <button
                key={style.value}
                onClick={() => handleStyleChange(style.value)}
                disabled={isUpdating}
                className={`p-4 rounded-xl border-2 transition-all text-left ${
                  selectedStyle === style.value
                    ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
                    : 'border-gray-200 dark:border-gray-600 hover:border-purple-300 dark:hover:border-purple-700'
                } ${isUpdating ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-2xl">{style.icon}</span>
                  <span className={`font-medium ${
                    selectedStyle === style.value
                      ? 'text-purple-600 dark:text-purple-400'
                      : 'text-gray-700 dark:text-gray-200'
                  }`}>
                    {presetStyleLabels[style.value]}
                  </span>
                </div>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {style.description}
                </p>
              </button>
            ))}
          </div>
        </div>

        {/* 語氣偏好 */}
        {analysis?.tone && (
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg mb-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              語氣偏好
            </h2>
            <div className="space-y-4">
              <ToneBar label="正式程度" value={analysis.tone.formal_score} />
              <ToneBar label="幽默程度" value={analysis.tone.humor_score} />
              <ToneBar label="情感表達" value={analysis.tone.emotion_score} />
              <ToneBar label="直接程度" value={analysis.tone.directness_score} />
            </div>
          </div>
        )}

        {/* 重置按鈕 */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            重置風格檔案
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
            清除所有學習記錄，重新開始。此操作無法復原。
          </p>
          <button
            onClick={() => setShowResetConfirm(true)}
            className="px-4 py-2 text-red-600 dark:text-red-400 border border-red-300 dark:border-red-700 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
          >
            重置風格檔案
          </button>
        </div>

        {/* 重置確認對話框 */}
        {showResetConfirm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-md mx-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                確認重置？
              </h3>
              <p className="text-gray-500 dark:text-gray-400 mb-6">
                這將清除所有學習記錄和評分歷史。您的預設風格將被保留。
              </p>
              <div className="flex gap-4">
                <button
                  onClick={() => setShowResetConfirm(false)}
                  className="flex-1 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600"
                >
                  {t('common.cancel')}
                </button>
                <button
                  onClick={handleReset}
                  className="flex-1 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
                >
                  {t('common.confirm')}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// 統計卡片組件
function StatCard({ label, value, icon }: { label: string; value: string; icon: string }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow">
      <div className="flex items-center gap-2 mb-1">
        <span>{icon}</span>
        <span className="text-sm text-gray-500 dark:text-gray-400">{label}</span>
      </div>
      <p className="text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
    </div>
  );
}

// 語氣條組件
function ToneBar({ label, value }: { label: string; value: number }) {
  const percentage = Math.round(value * 100);
  
  return (
    <div>
      <div className="flex justify-between mb-1">
        <span className="text-sm text-gray-600 dark:text-gray-300">{label}</span>
        <span className="text-sm text-gray-500 dark:text-gray-400">{percentage}%</span>
      </div>
      <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <div
          className="h-full bg-purple-500 transition-all duration-500"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

