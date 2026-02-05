/**
 * 主題編輯元件
 */

import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { topicsAPI } from '@/api/client'
import { showSuccess, showError } from '@/utils/toast'
import { useTranslation } from '@/i18n'
import type { Topic } from '@/types'
import type { TopicUpdate } from '@/api/topics'

interface TopicEditorProps {
  topic: Topic
  onClose: () => void
  onSuccess?: () => void
}

export default function TopicEditor({
  topic,
  onClose,
  onSuccess,
}: TopicEditorProps) {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState<TopicUpdate>({
    title: topic.title,
    category: topic.category,
    source: topic.source,
  })
  const [errors, setErrors] = useState<Record<string, string>>({})

  const updateMutation = useMutation({
    mutationFn: (data: TopicUpdate) => topicsAPI.updateTopic(topic.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['topic', topic.id])
      queryClient.invalidateQueries(['topics'])
      showSuccess(t('common.success'))
      onSuccess?.()
      onClose()
    },
    onError: (error) => {
      showError(t('common.failed'))
      setErrors({ submit: t('common.failed') })
      console.error('Failed to update topic:', error)
    },
  })

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!formData.title || formData.title.trim() === '') {
      newErrors.title = t('error.validation')
    }

    if (!formData.category) {
      newErrors.category = t('error.validation')
    }

    if (!formData.source || formData.source.trim() === '') {
      newErrors.source = t('error.validation')
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (validate()) {
      updateMutation.mutate(formData)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-2xl">
      <h2 className="text-xl font-bold text-gray-800 mb-6">{t('topics.edit')}</h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* 標題 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('topics.title')} <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={formData.title || ''}
            onChange={(e) =>
              setFormData({ ...formData, title: e.target.value })
            }
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary ${
              errors.title ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder={t('topics.title')}
          />
          {errors.title && (
            <p className="mt-1 text-sm text-red-500">{errors.title}</p>
          )}
        </div>

        {/* 分類 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('filters.category')} <span className="text-red-500">*</span>
          </label>
          <select
            value={formData.category || ''}
            onChange={(e) =>
              setFormData({
                ...formData,
                category: e.target.value as 'fashion' | 'food' | 'trend',
              })
            }
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary ${
              errors.category ? 'border-red-500' : 'border-gray-300'
            }`}
          >
            <option value="">{t('filters.all')}</option>
            <option value="fashion">{t('filters.fashion')}</option>
            <option value="food">{t('filters.food')}</option>
            <option value="trend">{t('filters.trend')}</option>
          </select>
          {errors.category && (
            <p className="mt-1 text-sm text-red-500">{errors.category}</p>
          )}
        </div>

        {/* 來源 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('topics.source')} <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={formData.source || ''}
            onChange={(e) =>
              setFormData({ ...formData, source: e.target.value })
            }
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary ${
              errors.source ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder={t('topics.source')}
          />
          {errors.source && (
            <p className="mt-1 text-sm text-red-500">{errors.source}</p>
          )}
        </div>

        {/* 錯誤訊息 */}
        {errors.submit && (
          <div className="bg-red-50 border border-red-200 rounded-md p-3">
            <p className="text-sm text-red-600">{errors.submit}</p>
          </div>
        )}

        {/* 操作按鈕 */}
        <div className="flex justify-end gap-3 pt-4">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
          >
            {t('common.cancel')}
          </button>
          <button
            type="submit"
            disabled={updateMutation.isPending}
            className="px-4 py-2 text-sm font-medium text-white bg-primary rounded-md hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {updateMutation.isPending ? t('common.loading') : t('common.save')}
          </button>
        </div>
      </form>
    </div>
  )
}
