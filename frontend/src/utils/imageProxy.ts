/**
 * 圖片代理工具函數
 * 將原始圖片 URL 轉換為後端代理 URL，避免 CORS 問題
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

/**
 * 獲取圖片代理 URL
 * 
 * @param originalUrl 原始圖片 URL
 * @returns 代理 URL
 */
export function getProxyUrl(originalUrl: string): string {
  if (!originalUrl) {
    // 如果沒有原始 URL，返回佔位圖
    return `https://via.placeholder.com/120x80/e5e7eb/6b7280?text=No+Image`
  }
  
  // 如果已經是代理 URL，直接返回
  if (originalUrl.includes('/images/proxy')) {
    return originalUrl
  }
  
  // 如果是佔位圖 URL，直接返回
  if (originalUrl.includes('via.placeholder.com')) {
    return originalUrl
  }
  
  // 轉換為代理 URL
  return `${API_BASE_URL}/images/proxy?url=${encodeURIComponent(originalUrl)}`
}

/**
 * 檢查 URL 是否為有效的圖片 URL
 * 
 * @param url 要檢查的 URL
 * @returns 是否為有效的圖片 URL
 */
export function isValidImageUrl(url: string): boolean {
  if (!url) return false
  
  // 檢查是否為有效的 HTTP/HTTPS URL
  try {
    const urlObj = new URL(url)
    return urlObj.protocol === 'http:' || urlObj.protocol === 'https:'
  } catch {
    return false
  }
}

