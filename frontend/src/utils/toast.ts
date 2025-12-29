/**
 * Toast 通知工具函數
 * 統一管理所有 Toast 通知
 */

import toast from 'react-hot-toast'

/**
 * 顯示成功訊息
 */
export const showSuccess = (message: string) => {
  toast.success(message, {
    duration: 3000,
    position: 'top-right',
    style: {
      background: '#10b981',
      color: '#fff',
    },
    iconTheme: {
      primary: '#fff',
      secondary: '#10b981',
    },
  })
}

/**
 * 顯示錯誤訊息
 */
export const showError = (message: string) => {
  toast.error(message, {
    duration: 4000,
    position: 'top-right',
    style: {
      background: '#ef4444',
      color: '#fff',
    },
    iconTheme: {
      primary: '#fff',
      secondary: '#ef4444',
    },
  })
}

/**
 * 顯示警告訊息
 */
export const showWarning = (message: string) => {
  toast(message, {
    duration: 3000,
    position: 'top-right',
    icon: '⚠️',
    style: {
      background: '#f59e0b',
      color: '#fff',
    },
  })
}

/**
 * 顯示資訊訊息
 */
export const showInfo = (message: string) => {
  toast(message, {
    duration: 3000,
    position: 'top-right',
    icon: 'ℹ️',
    style: {
      background: '#3b82f6',
      color: '#fff',
    },
  })
}

/**
 * 顯示載入中訊息
 * @returns toast ID，用於後續更新或移除
 */
export const showLoading = (message: string = '處理中...') => {
  return toast.loading(message, {
    position: 'top-right',
  })
}

/**
 * 更新載入中的 Toast
 */
export const updateLoading = (
  toastId: string,
  message: string,
  type: 'success' | 'error' = 'success'
) => {
  if (type === 'success') {
    toast.success(message, {
      id: toastId,
      duration: 3000,
    })
  } else {
    toast.error(message, {
      id: toastId,
      duration: 4000,
    })
  }
}

/**
 * 移除 Toast
 */
export const dismissToast = (toastId: string) => {
  toast.dismiss(toastId)
}

