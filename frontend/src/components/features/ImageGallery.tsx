/**
 * 圖片畫廊元件
 */

import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { imagesAPI } from '@/api/client'
import { showSuccess, showError } from '@/utils/toast'
import type { Image } from '@/types'
import type { ImageReorderItem } from '@/api/images'
import ImagePreview from './ImagePreview'

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
  const queryClient = useQueryClient()
  const [previewImage, setPreviewImage] = useState<Image | null>(null)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [isReordering, setIsReordering] = useState(false)
  const [reorderedImages, setReorderedImages] = useState<Image[]>([])

  // 刪除圖片
  const deleteMutation = useMutation({
    mutationFn: (imageId: string) => imagesAPI.deleteImage(topicId, imageId),
    onSuccess: () => {
      queryClient.invalidateQueries(['images', topicId])
      showSuccess('圖片已成功刪除')
      onImageUpdate?.()
      setDeletingId(null)
    },
    onError: (error) => {
      showError('刪除圖片失敗，請稍後再試')
      setDeletingId(null)
      console.error('Failed to delete image:', error)
    },
  })

  // 重新排序圖片
  const reorderMutation = useMutation({
    mutationFn: (orders: ImageReorderItem[]) =>
      imagesAPI.reorderImages(topicId, orders),
    onSuccess: () => {
      queryClient.invalidateQueries(['images', topicId])
      showSuccess('圖片順序已更新')
      setIsReordering(false)
      setReorderedImages([])
      onImageUpdate?.()
    },
    onError: (error) => {
      showError('更新圖片順序失敗，請稍後再試')
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
      <div className="mb-4 flex justify-end">
        {!isReordering ? (
          <button
            onClick={handleStartReorder}
            className="px-3 py-1 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
          >
            🔄 重新排序
          </button>
        ) : (
          <div className="flex gap-2">
            <button
              onClick={handleCancelReorder}
              className="px-3 py-1 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
            >
              取消
            </button>
            <button
              onClick={handleSaveReorder}
              disabled={reorderMutation.isPending}
              className="px-3 py-1 text-sm font-medium text-white bg-primary rounded-md hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {reorderMutation.isPending ? '儲存中...' : '儲存順序'}
            </button>
          </div>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4">
        {sortedImages.map((image, index) => (
          <div
            key={image.id}
            className="relative group aspect-square rounded-lg overflow-hidden bg-gray-100 cursor-pointer"
            onClick={() => !isReordering && setPreviewImage(image)}
          >
            {/* 圖片 */}
            <img
              src={image.url}
              alt={`Image ${image.order}`}
              className="w-full h-full object-cover pointer-events-none"
              onError={(e) => {
                e.currentTarget.src =
                  'https://via.placeholder.com/400x400?text=Image'
              }}
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
                    handleMoveUp(index)
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
                    handleMoveDown(index)
                  }}
                  disabled={index === sortedImages.length - 1}
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
                    setPreviewImage(image)
                  }}
                  onMouseDown={(e) => e.stopPropagation()}
                  className="px-3 py-1 bg-white/90 text-gray-800 rounded text-xs font-medium hover:bg-white transition-colors pointer-events-auto"
                >
                  預覽
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleDelete(image.id)
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
