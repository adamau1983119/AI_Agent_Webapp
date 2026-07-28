/**
 * 圖片代理工具函數
 * 將原始圖片 URL 轉換為後端代理 URL，避免 CORS 問題
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

/** 本機 data URI 佔位（勿用 via.placeholder.com，該域常掛並刷 Console 紅錯） */
export const IMAGE_PLACEHOLDER_DATA_URI =
  'data:image/svg+xml,' +
  encodeURIComponent(
    '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="80" viewBox="0 0 120 80">' +
      '<rect fill="#e5e7eb" width="120" height="80"/>' +
      '</svg>'
  )

/**
 * 獲取圖片代理 URL
 *
 * @param originalUrl 原始圖片 URL
 * @returns 代理 URL 或本機佔位圖
 */
export function getProxyUrl(originalUrl: string): string {
  if (!originalUrl) {
    return IMAGE_PLACEHOLDER_DATA_URI
  }

  if (originalUrl.startsWith('data:')) {
    return originalUrl
  }

  // 如果已經是代理 URL，直接返回
  if (originalUrl.includes('/images/proxy')) {
    return originalUrl
  }

  // 舊佔位網址改走本機 data URI，避免外網失敗
  if (originalUrl.includes('via.placeholder.com')) {
    return IMAGE_PLACEHOLDER_DATA_URI
  }

  return `${API_BASE_URL}/images/proxy?url=${encodeURIComponent(originalUrl)}`
}

/**
 * 檢查 URL 是否為有效的圖片 URL
 */
export function isValidImageUrl(url: string): boolean {
  if (!url) return false
  if (url.startsWith('data:image/')) return true

  try {
    const urlObj = new URL(url)
    return urlObj.protocol === 'http:' || urlObj.protocol === 'https:'
  } catch {
    return false
  }
}
