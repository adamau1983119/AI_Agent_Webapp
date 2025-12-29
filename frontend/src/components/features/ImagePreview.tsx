/**
 * 圖片預覽元件
 */

import type { Image } from '@/types'

interface ImagePreviewProps {
  image: Image
  onClose: () => void
}

export default function ImagePreview({
  image,
  onClose,
}: ImagePreviewProps) {
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
          <img
            src={image.url}
            alt={`Preview ${image.id}`}
            className="max-w-full max-h-[80vh] object-contain"
            onError={(e) => {
              e.currentTarget.src =
                'https://via.placeholder.com/800x600?text=Image+Not+Found'
            }}
          />

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
