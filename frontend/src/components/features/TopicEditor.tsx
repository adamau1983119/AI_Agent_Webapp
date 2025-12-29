/**
 * 主題編輯元件
 */

import { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { topicsAPI } from '@/api/client'
import { showSuccess, showError } from '@/utils/toast'
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
      showSuccess('主題已成功更新')
      onSuccess?.()
      onClose()
    },
    onError: (error) => {
      showError('更新主題失敗，請稍後再試')
      setErrors({ submit: '更新失敗，請稍後再試' })
      console.error('Failed to update topic:', error)
    },
  })

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!formData.title || formData.title.trim() === '') {
      newErrors.title = '標題為必填項'
    }

    if (!formData.category) {
      newErrors.category = '分類為必填項'
    }

    if (!formData.source || formData.source.trim() === '') {
      newErrors.source = '來源為必填項'
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
      <h2 className="text-xl font-bold text-gray-800 mb-6">編輯主題</h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* 標題 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            標題 <span className="text-red-500">*</span>
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
            placeholder="輸入主題標題"
          />
          {errors.title && (
            <p className="mt-1 text-sm text-red-500">{errors.title}</p>
          )}
        </div>

        {/* 分類 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            分類 <span className="text-red-500">*</span>
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
            <option value="">選擇分類</option>
            <option value="fashion">時尚</option>
            <option value="food">美食</option>
            <option value="trend">趨勢</option>
          </select>
          {errors.category && (
            <p className="mt-1 text-sm text-red-500">{errors.category}</p>
          )}
        </div>

        {/* 來源 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            來源 <span className="text-red-500">*</span>
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
            placeholder="輸入來源"
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
            取消
          </button>
          <button
            type="submit"
            disabled={updateMutation.isPending}
            className="px-4 py-2 text-sm font-medium text-white bg-primary rounded-md hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {updateMutation.isPending ? '儲存中...' : '儲存'}
          </button>
        </div>
      </form>
    </div>
  )
}
