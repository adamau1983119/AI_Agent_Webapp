import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './app/App.tsx'
import './index.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      refetchOnMount: false, // 避免組件掛載時自動重試
      retry: (failureCount, error: any) => {
        // 429 錯誤不重試
        if (error?.status === 429) {
          return false
        }
        // 其他錯誤最多重試 1 次
        return failureCount < 1
      },
      retryDelay: (attemptIndex) => {
        // 指數退避：2秒、4秒
        return Math.min(1000 * 2 ** attemptIndex, 4000)
      },
      staleTime: 30000, // 30 秒內認為數據新鮮
      gcTime: 5 * 60 * 1000, // 5 分鐘緩存（React Query v5）
      // 啟用查詢去重（默認已啟用，但明確設定）
      structuralSharing: true,
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>,
)

