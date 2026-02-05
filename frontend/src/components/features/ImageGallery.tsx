/**
 * 圖片畫廊元件
 */

import { useState, useMemo } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { imagesAPI, API_BASE_URL } from '@/api/client'
import { showSuccess, showError } from '@/utils/toast'
import type { Image } from '@/types'
import type { ImageReorderItem } from '@/api/images'
import ImagePreview from './ImagePreview'
import { useTranslation } from '@/i18n'

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

/**
 * 占位符 SVG（用於圖片載入失敗時）
 */
const PlaceholderSVG = ({ className }: { className?: string }) => (
  <svg
    className={className || 'w-full h-full'}
    viewBox="0 0 400 400"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <rect width="400" height="400" fill="#F3F4F6" />
    <path
      d="M150 150L200 200L250 150L300 200V300H100V200L150 150Z"
      stroke="#9CA3AF"
      strokeWidth="2"
      fill="none"
    />
    <circle cx="150" cy="150" r="20" fill="#9CA3AF" />
    <text
      x="200"
      y="250"
      textAnchor="middle"
      fill="#9CA3AF"
      fontSize="16"
      fontFamily="Arial, sans-serif"
    >
      圖片無法載入
    </text>
  </svg>
)

/**
 * 圖片畫廊項目組件（處理單個圖片的載入狀態）
 */
function ImageGalleryItem({
  image,
  index,
  isReordering,
  deletingId,
  onPreview,
  onDelete,
  onMoveUp,
  onMoveDown,
  isLast,
}: {
  image: Image
  index: number
  isReordering: boolean
  deletingId: string | null
  onPreview: () => void
  onDelete: (id: string) => void
  onMoveUp: (index: number) => void
  onMoveDown: (index: number) => void
  isLast: boolean
}) {
  const [imageError, setImageError] = useState(false)
  const [imageLoading, setImageLoading] = useState(true)
  const proxyUrl = useMemo(() => getProxyImageUrl(image.url), [image.url])

  return (
    <div
      className="relative group aspect-square rounded-lg overflow-hidden bg-gray-100 cursor-pointer"
      onClick={() => !isReordering && onPreview()}
    >
      {/* 載入指示器 */}
      {imageLoading && !imageError && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-200 z-10">
          <div className="w-6 h-6 border-3 border-primary border-t-transparent rounded-full animate-spin"></div>
        </div>
      )}

      {/* 錯誤狀態 */}
      {imageError && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-200 z-10">
          <div className="w-16 h-16">
            <PlaceholderSVG />
          </div>
        </div>
      )}

      {/* 圖片 */}
      <img
        src={proxyUrl}
        alt={`Image ${image.order}`}
        className="w-full h-full object-cover pointer-events-none"
        onLoad={() => {
          setImageLoading(false)
          setImageError(false)
        }}
        onError={(e) => {
          setImageLoading(false)
          setImageError(true)
          console.warn('圖片載入失敗:', {
            id: image.id,
            url: image.url,
            proxyUrl: proxyUrl
          })
        }}
        loading="lazy"
      />

      {/* 排序模式下的控制按鈕 */}
      {isReordering && (
        <div 
          className="absolute inset-0 bg-black/50 flex items-center justify-center gap-2 z-10"
          onClick={(e) => e.stopPropagation()}
        >
          <button
            onClick={(e) => {
              e.stopPropagation()
              onMoveUp(index)
            }}
            disabled={index === 0}
            className="px-3 py-1 bg-white/90 text-gray-800 rounded text-xs font-medium hover:bg-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ↑
          </button>
          <span className="px-3 py-1 bg-white/90 text-gray-800 rounded text-xs font-medium">
            {index + 1}
          </span>
          <button
            onClick={(e) => {
              e.stopPropagation()
              onMoveDown(index)
            }}
            disabled={isLast}
            className="px-3 py-1 bg-white/90 text-gray-800 rounded text-xs font-medium hover:bg-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ↓
          </button>
        </div>
      )}

      {/* 懸停時顯示的操作按鈕（非排序模式） */}
      {!isReordering && (
        <div 
          className="absolute inset-0 bg-black/0 group-hover:bg-black/50 transition-all duration-200 flex items-center justify-center gap-2 opacity-0 group-hover:opacity-100 pointer-events-none"
        >
          <button
            onClick={(e) => {
              e.stopPropagation()
              onPreview()
            }}
            onMouseDown={(e) => e.stopPropagation()}
            className="px-3 py-1 bg-white/90 text-gray-800 rounded text-xs font-medium hover:bg-white transition-colors pointer-events-auto"
          >
            預覽
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation()
              onDelete(image.id)
            }}
            onMouseDown={(e) => e.stopPropagation()}
            disabled={deletingId === image.id}
            className="px-3 py-1 bg-red-500/90 text-white rounded text-xs font-medium hover:bg-red-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed pointer-events-auto"
          >
            {deletingId === image.id ? '刪除中...' : '刪除'}
          </button>
        </div>
      )}

      {/* 底部資訊 */}
      <div 
        className="absolute bottom-0 left-0 right-0 bg-black/50 text-white text-xs p-2 pointer-events-none"
      >
        <div className="flex justify-between items-center">
          <span>{image.source}</span>
          <span>#{image.order + 1}</span>
        </div>
      </div>
    </div>
  )
}

interface ImageGalleryProps {
  images: Image[]
  topicId: string
  onImageUpdate?: () => void
}

export default function ImageGallery({
  images,
  topicId,
  onImageUpdate,
}: ImageGalleryProps) {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [isMatching, setIsMatching] = useState(false)

  // 智能匹配照片
  const matchMutation = useMutation({
    mutationFn: (minCount: number) => imagesAPI.matchPhotos(topicId, minCount),
    onMutate: () => {
      setIsMatching(true)
      showSuccess(t('common.loading'))
    },
    onSuccess: async (data) => {
      setIsMatching(false)
      // 立即重新獲取圖片列表，確保UI更新
      await queryClient.refetchQueries({ queryKey: ['images', topicId] })
      showSuccess(t('common.success'))
    },
    onError: (error: any) => {
      setIsMatching(false)
      showError(error?.message || t('common.failed'))
    },
  })

  // 驗證匹配度
  const validateMutation = useMutation({
    mutationFn: () => imagesAPI.validateMatch(topicId),
    onSuccess: (data) => {
      if (data.overall_match) {
        showSuccess(t('common.success'))
      } else {
        showError(t('common.failed'))
        console.warn('匹配問題:', data.warnings)
      }
    },
    onError: (error: any) => {
      showError(error?.message || t('common.failed'))
    },
  })
  const [previewImage, setPreviewImage] = useState<Image | null>(null)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [isReordering, setIsReordering] = useState(false)
  const [reorderedImages, setReorderedImages] = useState<Image[]>([])

  // 刪除圖片
  const deleteMutation = useMutation({
    mutationFn: (imageId: string) => imagesAPI.deleteImage(topicId, imageId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['images', topicId] })
      showSuccess(t('common.success'))
      onImageUpdate?.()
      setDeletingId(null)
    },
    onError: (error) => {
      showError(t('common.failed'))
      setDeletingId(null)
      console.error('Failed to delete image:', error)
    },
  })

  // 重新排序圖片
  const reorderMutation = useMutation({
    mutationFn: (orders: ImageReorderItem[]) =>
      imagesAPI.reorderImages(topicId, orders),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['images', topicId] })
      showSuccess(t('common.success'))
      setIsReordering(false)
      setReorderedImages([])
      onImageUpdate?.()
    },
    onError: (error) => {
      showError(t('common.failed'))
      setIsReordering(false)
      setReorderedImages([])
      console.error('Failed to reorder images:', error)
    },
  })

  const handleDelete = (imageId: string) => {
    if (confirm('確定要刪除這張圖片嗎？')) {
      setDeletingId(imageId)
      deleteMutation.mutate(imageId)
    }
  }

  const handleStartReorder = () => {
    setIsReordering(true)
    setReorderedImages([...images].sort((a, b) => a.order - b.order))
  }

  const handleCancelReorder = () => {
    setIsReordering(false)
    setReorderedImages([])
  }

  const handleMoveUp = (index: number) => {
    if (index === 0) return
    const newImages = [...reorderedImages]
    ;[newImages[index - 1], newImages[index]] = [
      newImages[index],
      newImages[index - 1],
    ]
    setReorderedImages(newImages)
  }

  const handleMoveDown = (index: number) => {
    if (index === reorderedImages.length - 1) return
    const newImages = [...reorderedImages]
    ;[newImages[index], newImages[index + 1]] = [
      newImages[index + 1],
      newImages[index],
    ]
    setReorderedImages(newImages)
  }

  const handleSaveReorder = () => {
    const orders: ImageReorderItem[] = reorderedImages.map((image, index) => ({
      image_id: image.id,
      order: index,
    }))
    reorderMutation.mutate(orders)
  }

  // 按 order 排序
  const sortedImages = isReordering
    ? reorderedImages
    : [...images].sort((a, b) => a.order - b.order)

  return (
    <>
      {/* 排序控制按鈕 */}
      <div className="mb-4 flex justify-between items-center">
        <div className="flex gap-2">
          <button
            onClick={() => validateMutation.mutate()}
            disabled={validateMutation.isPending}
            className="px-3 py-1 text-sm font-medium text-blue-700 bg-blue-100 rounded-md hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {validateMutation.isPending ? t('common.loading') : `✓ ${t('images.validateMatch')}`}
          </button>
          {images.length < 8 && (
            <button
              onClick={() => matchMutation.mutate(8)}
              disabled={isMatching}
              className="px-3 py-1 text-sm font-medium text-primary bg-primary/10 rounded-md hover:bg-primary/20 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isMatching ? t('common.loading') : `🔍 ${t('images.smartMatch')}`}
            </button>
          )}
        </div>
        {!isReordering ? (
          <button
            onClick={handleStartReorder}
            className="px-3 py-1 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
          >
            🔄 {t('images.reorder')}
          </button>
        ) : (
          <div className="flex gap-2">
            <button
              onClick={handleCancelReorder}
              className="px-3 py-1 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
            >
              {t('common.cancel')}
            </button>
            <button
              onClick={handleSaveReorder}
              disabled={reorderMutation.isPending}
              className="px-3 py-1 text-sm font-medium text-white bg-primary rounded-md hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {reorderMutation.isPending ? t('common.loading') : t('common.save')}
            </button>
          </div>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4">
        {sortedImages.map((image, index) => (
          <ImageGalleryItem
            key={image.id}
            image={image}
            index={index}
            isReordering={isReordering}
            deletingId={deletingId}
            onPreview={() => setPreviewImage(image)}
            onDelete={handleDelete}
            onMoveUp={handleMoveUp}
            onMoveDown={handleMoveDown}
            isLast={index === sortedImages.length - 1}
          />
        ))}
      </div>

      {/* 圖片預覽 */}
      {previewImage && (
        <ImagePreview
          image={previewImage}
          onClose={() => setPreviewImage(null)}
        />
      )}
    </>
  )
}
