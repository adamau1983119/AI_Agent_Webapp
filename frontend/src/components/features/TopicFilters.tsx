/**
 * 主題篩選元件
 * 支援多語言
 */

import { useState, useEffect, useRef, useCallback } from 'react'
import type { TopicFilters as TopicFiltersType } from '@/api/topics'
import { useTranslation } from '@/i18n'
import { todayHktDateString } from '@/lib/topicDayHkt'

interface TopicFiltersProps {
  onFilterChange: (filters: TopicFiltersType) => void
  className?: string
  initialCategory?: string
}

export default function TopicFilters({
  onFilterChange,
  className = '',
  initialCategory = '',
}: TopicFiltersProps) {
  const { t } = useTranslation()
  const [category, setCategory] = useState<string>(initialCategory)
  const [status, setStatus] = useState<string>('')
  const [date, setDate] = useState<string>('')
  const [searchQuery, setSearchQuery] = useState<string>('')
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  const handleFilterChange = useCallback(() => {
    const filters: TopicFiltersType = {
      page: 1,
      limit: 10,
    }

    if (category) filters.category = category as 'fashion' | 'food' | 'trend'
    if (status) filters.status = status as 'pending' | 'confirmed' | 'deleted'
    if (date) filters.date = date
    if (searchQuery && searchQuery.trim()) filters.search = searchQuery.trim()

    onFilterChange(filters)
  }, [category, status, date, searchQuery, onFilterChange])

  // 防抖處理搜尋
  useEffect(() => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current)
    }

    searchTimeoutRef.current = setTimeout(() => {
      handleFilterChange()
    }, 500)

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current)
      }
    }
  }, [searchQuery, handleFilterChange])

  // 當其他篩選條件變更時立即觸發
  useEffect(() => {
    handleFilterChange()
  }, [category, status, date, handleFilterChange])

  const handleReset = () => {
    setCategory('')
    setStatus('')
    setDate('')
    setSearchQuery('')
    onFilterChange({ page: 1, limit: 10 })
  }

  return (
    <div className={`bg-white rounded-lg shadow p-6 ${className}`}>
      <h3 className="text-lg font-semibold text-gray-800 mb-4">{t('filters.title')}</h3>

      <div className="space-y-4">
        {/* 搜尋框 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('filters.search')}
          </label>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault()
                // 清除防抖計時器，立即執行搜尋
                if (searchTimeoutRef.current) {
                  clearTimeout(searchTimeoutRef.current)
                }
                handleFilterChange()
              }
            }}
            placeholder={t('filters.searchPlaceholder')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
          />
        </div>

        {/* 分類篩選 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('filters.category')}
          </label>
          <select
            value={category}
            onChange={(e) => {
              setCategory(e.target.value)
              handleFilterChange()
            }}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
          >
            <option value="">{t('filters.all')}</option>
            <option value="fashion">{t('filters.fashion')}</option>
            <option value="food">{t('filters.food')}</option>
            <option value="trend">{t('filters.trend')}</option>
          </select>
        </div>

        {/* 狀態篩選 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('filters.status')}
          </label>
          <select
            value={status}
            onChange={(e) => {
              setStatus(e.target.value)
              handleFilterChange()
            }}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
          >
            <option value="">{t('filters.all')}</option>
            <option value="pending">{t('filters.pending')}</option>
            <option value="confirmed">{t('filters.confirmed')}</option>
            <option value="deleted">{t('filters.deleted')}</option>
          </select>
        </div>

        {/* 日期篩選 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('filters.date')}
          </label>
          <input
            type="date"
            value={date}
            max={todayHktDateString()}
            onChange={(e) => {
              const today = todayHktDateString()
              const next = e.target.value
              setDate(next && next > today ? today : next)
              handleFilterChange()
            }}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
          />
        </div>

        {/* 操作按鈕 */}
        <div className="flex gap-2 pt-2">
          <button
            onClick={handleReset}
            className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
          >
            {t('filters.reset')}
          </button>
        </div>
      </div>
    </div>
  )
}
