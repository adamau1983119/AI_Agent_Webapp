/**
 * 評分面板組件
 * Phase 4: AI 個人化
 */
import { useState, useEffect } from 'react';
import {
  ratingsApi,
  RatingReason,
  ratingReasonLabels,
  positiveReasons,
  negativeReasons,
} from '../../api/ratings';
import { RatingValue } from '../../api/styleProfile';
import { useTranslation } from '../../i18n';
import toast from 'react-hot-toast';

interface RatingPanelProps {
  contentId: string;
  topicId: string;
  contentFormat?: string;
  contentLength?: number;
  topicCategory?: string;
  onRatingSubmitted?: (value: RatingValue) => void;
}

export default function RatingPanel({
  contentId,
  topicId,
  contentFormat,
  contentLength,
  topicCategory,
  onRatingSubmitted,
}: RatingPanelProps) {
  const { t } = useTranslation();
  const [selectedValue, setSelectedValue] = useState<RatingValue | null>(null);
  const [selectedReasons, setSelectedReasons] = useState<RatingReason[]>([]);
  const [comment, setComment] = useState('');
  const [showReasons, setShowReasons] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [hasRated, setHasRated] = useState(false);

  // 檢查是否已評分
  useEffect(() => {
    checkExistingRating();
  }, [contentId]);

  const checkExistingRating = async () => {
    try {
      const result = await ratingsApi.getRatingForContent(contentId);
      if (result.rated && result.rating) {
        setHasRated(true);
        setSelectedValue(result.rating.value);
      }
    } catch (err) {
      // 忽略錯誤
    }
  };

  const handleRatingClick = (value: RatingValue) => {
    if (hasRated) return;
    setSelectedValue(value);
    setShowReasons(true);
    setSelectedReasons([]);
  };

  const toggleReason = (reason: RatingReason) => {
    setSelectedReasons((prev) =>
      prev.includes(reason)
        ? prev.filter((r) => r !== reason)
        : [...prev, reason]
    );
  };

  const handleSubmit = async () => {
    if (!selectedValue) return;

    setIsSubmitting(true);
    try {
      await ratingsApi.submitRating({
        content_id: contentId,
        topic_id: topicId,
        value: selectedValue,
        reasons: selectedReasons,
        comment: comment.trim() || undefined,
        content_format: contentFormat,
        content_length: contentLength,
        topic_category: topicCategory,
      });

      setHasRated(true);
      setShowReasons(false);
      toast.success(t('common.success'));
      onRatingSubmitted?.(selectedValue);
    } catch (err: any) {
      toast.error(err.message || t('common.failed'));
    } finally {
      setIsSubmitting(false);
    }
  };

  const reasons = selectedValue === 'like' ? positiveReasons : negativeReasons;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
      {/* 評分標題 */}
      <div className="flex items-center justify-between mb-4">
        <span className="text-sm font-medium text-gray-700 dark:text-gray-200">
          這個內容對您有幫助嗎？
        </span>
        {hasRated && (
          <span className="text-xs text-green-600 dark:text-green-400 flex items-center gap-1">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            已評分
          </span>
        )}
      </div>

      {/* 評分按鈕 */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => handleRatingClick('like')}
          disabled={hasRated}
          className={`flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-all ${
            selectedValue === 'like'
              ? 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 ring-2 ring-green-500'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-green-50 dark:hover:bg-green-900/20'
          } ${hasRated ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <span className="text-2xl">👍</span>
          <span>喜歡</span>
        </button>

        <button
          onClick={() => handleRatingClick('dislike')}
          disabled={hasRated}
          className={`flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-all ${
            selectedValue === 'dislike'
              ? 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 ring-2 ring-red-500'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-red-50 dark:hover:bg-red-900/20'
          } ${hasRated ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <span className="text-2xl">👎</span>
          <span>不喜歡</span>
        </button>
      </div>

      {/* 原因選擇 */}
      {showReasons && !hasRated && (
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
            告訴我們原因（可選多個）
          </p>

          <div className="flex flex-wrap gap-2 mb-4">
            {reasons.map((reason) => (
              <button
                key={reason}
                onClick={() => toggleReason(reason)}
                className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                  selectedReasons.includes(reason)
                    ? selectedValue === 'like'
                      ? 'bg-green-500 text-white'
                      : 'bg-red-500 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
              >
                {ratingReasonLabels[reason]}
              </button>
            ))}
          </div>

          {/* 評論 */}
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="還有其他想說的嗎？（選填）"
            rows={2}
            maxLength={500}
            className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-700 dark:text-gray-200 placeholder-gray-400 resize-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />

          {/* 提交按鈕 */}
          <div className="flex justify-end mt-3">
            <button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="px-6 py-2 bg-gradient-to-r from-purple-500 to-cyan-500 text-white font-medium rounded-lg hover:from-purple-600 hover:to-cyan-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  {t('common.loading')}
                </>
              ) : (
                t('common.submit')
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

