/**
 * 圖片預覽元件
 */

import { useMemo, useState } from 'react'
import { API_BASE_URL } from '@/api/client'
import type { Image } from '@/types'

/**
 * 生成圖片代理 URL
 */
function getProxyImageUrl(imageUrl: string): string {
  if (!imageUrl) return ''
  // 如果 URL 已經是代理 URL，直接返回
  if (imageUrl.includes('/images/proxy')) return imageUrl
  // 構建代理 URL
  return `${API_BASE_URL}/images/proxy?url=${encodeURIComponent(imageUrl)}`
}

interface ImagePreviewProps {
  image: Image
  onClose: () => void
}

export default function ImagePreview({
  image,
  onClose,
}: ImagePreviewProps) {
  const proxyUrl = useMemo(() => getProxyImageUrl(image.url), [image.url])
  const [imageError, setImageError] = useState(false)
  const [imageLoading, setImageLoading] = useState(true)

  return (
    <div
      className="fixed inset-0 bg-black/90 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="relative max-w-7xl max-h-full"
        onClick={(e) => e.stopPropagation()}
      >
        {/* 關閉按鈕 */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-10 text-white hover:text-gray-300 text-3xl font-bold bg-black/50 rounded-full w-10 h-10 flex items-center justify-center"
        >
          ×
        </button>

        {/* 圖片 */}
        <div className="bg-white rounded-lg overflow-hidden">
          {imageLoading && !imageError && (
            <div className="flex items-center justify-center h-[80vh] bg-gray-100">
              <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
            </div>
          )}
          {imageError && (
            <div className="flex flex-col items-center justify-center h-[80vh] bg-gray-100 p-8">
              <div className="text-gray-500 text-lg mb-2">⚠️ 圖片無法載入</div>
              <div className="text-gray-400 text-sm text-center max-w-md">
                無法載入圖片預覽。可能是網路問題或圖片 URL 無效。
              </div>
            </div>
          )}
          {!imageError && (
            <img
              src={proxyUrl}
              alt={`Preview ${image.id}`}
              className="max-w-full max-h-[80vh] object-contain"
              onLoad={() => {
                setImageLoading(false)
                setImageError(false)
              }}
              onError={(e) => {
                setImageLoading(false)
                setImageError(true)
                console.warn('圖片預覽載入失敗:', {
                  id: image.id,
                  url: image.url,
                  proxyUrl: proxyUrl
                })
              }}
            />
          )}

          {/* 圖片資訊 */}
          <div className="bg-white p-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-gray-500">來源</span>
                <p className="font-medium text-gray-900">{image.source}</p>
              </div>
              {image.photographer && (
                <div>
                  <span className="text-gray-500">攝影師</span>
                  <p className="font-medium text-gray-900">
                    {image.photographer}
                  </p>
                </div>
              )}
              <div>
                <span className="text-gray-500">授權</span>
                <p className="font-medium text-gray-900">{image.license}</p>
              </div>
              <div>
                <span className="text-gray-500">順序</span>
                <p className="font-medium text-gray-900">#{image.order + 1}</p>
              </div>
            </div>

            {/* 圖片 URL */}
            <div className="mt-4 pt-4 border-t border-gray-200">
              <span className="text-gray-500 text-sm">圖片 URL</span>
              <p className="text-xs text-gray-600 break-all mt-1">{image.url}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
