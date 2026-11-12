import type { Language } from '@/i18n'

export function mapGuestLanguage(raw: string | null | undefined): Language {
  const value = (raw || '').trim()
  if (value === 'zh-TW' || value === 'en' || value === 'ja') return value
  const lower = value.toLowerCase()
  if (lower.startsWith('ja')) return 'ja'
  if (lower.startsWith('en')) return 'en'
  if (lower === 'zh-tw' || lower === 'zh-hk' || lower.startsWith('zh-hant')) return 'zh-TW'
  return 'zh-TW'
}
