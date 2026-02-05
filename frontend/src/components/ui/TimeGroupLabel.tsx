/**
 * TimeGroupLabel Component
 * Phase 1: 時間分隔顯示元件
 * 
 * 功能：
 * - 顯示「今天」、「昨天」、「本週」、「更早」等時間分組標籤
 * - 智慧判斷日期屬於哪個時間分組
 * - 支援多語言
 */

import { useMemo } from 'react'
import { useTranslation } from '@/i18n'

export type TimeGroup = 'today' | 'yesterday' | 'thisWeek' | 'earlier'

interface TimeGroupLabelProps {
  /** 時間分組 */
  group: TimeGroup
  /** 顯示的項目數量（可選） */
  count?: number
  /** 自定義 className */
  className?: string
}

/**
 * 時間分組對應的翻譯 key
 */
const timeGroupKeys: Record<TimeGroup, string> = {
  today: 'topics.today',
  yesterday: 'topics.yesterday',
  thisWeek: 'topics.thisWeek',
  earlier: 'topics.older',
}

/**
 * 根據日期判斷時間分組
 */
export function getTimeGroup(date: Date | string): TimeGroup {
  const targetDate = typeof date === 'string' ? new Date(date) : date
  const now = new Date()
  
  // 取得今天的開始時間（00:00:00）
  const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  // 取得昨天的開始時間
  const yesterdayStart = new Date(todayStart.getTime() - 24 * 60 * 60 * 1000)
  // 取得本週開始（週一）
  const dayOfWeek = now.getDay()
  const daysToMonday = dayOfWeek === 0 ? 6 : dayOfWeek - 1 // 週日是0，需要特殊處理
  const thisWeekStart = new Date(todayStart.getTime() - daysToMonday * 24 * 60 * 60 * 1000)
  
  // 判斷時間分組
  if (targetDate >= todayStart) {
    return 'today'
  } else if (targetDate >= yesterdayStart) {
    return 'yesterday'
  } else if (targetDate >= thisWeekStart) {
    return 'thisWeek'
  } else {
    return 'earlier'
  }
}

/**
 * 將主題列表按時間分組
 */
export function groupByTime<T extends { generatedAt?: string; generated_at?: string }>(
  items: T[]
): Map<TimeGroup, T[]> {
  const groups = new Map<TimeGroup, T[]>([
    ['today', []],
    ['yesterday', []],
    ['thisWeek', []],
    ['earlier', []],
  ])
  
  for (const item of items) {
    const dateStr = item.generatedAt || item.generated_at
    if (dateStr) {
      const group = getTimeGroup(dateStr)
      groups.get(group)?.push(item)
    } else {
      groups.get('earlier')?.push(item)
    }
  }
  
  return groups
}

/**
 * 時間分組標籤元件
 */
export default function TimeGroupLabel({
  group,
  count,
  className = '',
}: TimeGroupLabelProps) {
  const { t } = useTranslation()
  const label = useMemo(() => t(timeGroupKeys[group] as any) || group, [group, t])
  
  // 根據分組選擇不同的樣式
  const groupStyles: Record<TimeGroup, string> = {
    today: 'bg-emerald-100 text-emerald-800 border-emerald-200',
    yesterday: 'bg-blue-100 text-blue-800 border-blue-200',
    thisWeek: 'bg-purple-100 text-purple-800 border-purple-200',
    earlier: 'bg-gray-100 text-gray-600 border-gray-200',
  }
  
  const iconStyles: Record<TimeGroup, string> = {
    today: '🌟',
    yesterday: '📅',
    thisWeek: '📆',
    earlier: '📁',
  }

  return (
    <div
      className={`flex items-center gap-3 py-4 px-2 ${className}`}
    >
      {/* 左側分隔線 */}
      <div className="flex-grow h-px bg-gradient-to-r from-transparent to-gray-200" />
      
      {/* 標籤 */}
      <div
        className={`
          flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-medium
          border ${groupStyles[group]}
          transition-all duration-200 hover:shadow-sm
        `}
      >
        <span>{iconStyles[group]}</span>
        <span>{label}</span>
        {typeof count === 'number' && count > 0 && (
          <span className="ml-1 px-1.5 py-0.5 text-xs rounded-full bg-white/50">
            {count}
          </span>
        )}
      </div>
      
      {/* 右側分隔線 */}
      <div className="flex-grow h-px bg-gradient-to-l from-transparent to-gray-200" />
    </div>
  )
}

