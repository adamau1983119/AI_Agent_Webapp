/**
 * 分頁元件
 * 提供完整的分頁控制功能
 */

interface PaginationProps {
  /** 當前頁碼 */
  currentPage: number
  /** 總頁數 */
  totalPages: number
  /** 每頁數量 */
  pageSize?: number
  /** 總資料數 */
  totalItems?: number
  /** 頁碼變更回調 */
  onPageChange: (page: number) => void
  /** 是否顯示總數 */
  showTotal?: boolean
  /** 是否顯示頁碼跳轉 */
  showJump?: boolean
  /** 自訂樣式 */
  className?: string
}

export default function Pagination({
  currentPage,
  totalPages,
  pageSize = 10,
  totalItems,
  onPageChange,
  showTotal = true,
  showJump = true,
  className = '',
}: PaginationProps) {
  // 計算顯示的頁碼範圍
  const getPageNumbers = (): (number | string)[] => {
    const pages: (number | string)[] = []
    const maxVisible = 7 // 最多顯示 7 個頁碼

    if (totalPages <= maxVisible) {
      // 如果總頁數少於等於 7，顯示所有頁碼
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i)
      }
    } else {
      // 如果總頁數大於 7，顯示部分頁碼
      if (currentPage <= 4) {
        // 當前頁在前 4 頁
        for (let i = 1; i <= 5; i++) {
          pages.push(i)
        }
        pages.push('...')
        pages.push(totalPages)
      } else if (currentPage >= totalPages - 3) {
        // 當前頁在後 4 頁
        pages.push(1)
        pages.push('...')
        for (let i = totalPages - 4; i <= totalPages; i++) {
          pages.push(i)
        }
      } else {
        // 當前頁在中間
        pages.push(1)
        pages.push('...')
        for (let i = currentPage - 1; i <= currentPage + 1; i++) {
          pages.push(i)
        }
        pages.push('...')
        pages.push(totalPages)
      }
    }

    return pages
  }

  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= totalPages && page !== currentPage) {
      onPageChange(page)
    }
  }

  const handleJumpToPage = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const pageInput = formData.get('page') as string
    const page = parseInt(pageInput, 10)

    if (page >= 1 && page <= totalPages) {
      handlePageChange(page)
    }
  }

  if (totalPages <= 1) {
    return null // 只有一頁或沒有資料時不顯示分頁
  }

  const pageNumbers = getPageNumbers()

  return (
    <div className={`flex flex-col sm:flex-row items-center justify-between gap-4 ${className}`}>
      {/* 左側：總數資訊 */}
      {showTotal && (
        <div className="text-sm text-gray-600">
          {totalItems !== undefined ? (
            <>
              顯示第{' '}
              <span className="font-medium">
                {(currentPage - 1) * pageSize + 1} -{' '}
                {Math.min(currentPage * pageSize, totalItems)}
              </span>{' '}
              項，共 <span className="font-medium">{totalItems}</span> 項
            </>
          ) : (
            <>
              第 <span className="font-medium">{currentPage}</span> 頁，共{' '}
              <span className="font-medium">{totalPages}</span> 頁
            </>
          )}
        </div>
      )}

      {/* 中間：頁碼控制 */}
      <div className="flex items-center gap-1">
        {/* 上一頁 */}
        <button
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-white"
          aria-label="上一頁"
        >
          ‹
        </button>

        {/* 頁碼 */}
        {pageNumbers.map((page, index) => {
          if (page === '...') {
            return (
              <span
                key={`ellipsis-${index}`}
                className="px-3 py-2 text-sm text-gray-500"
              >
                ...
              </span>
            )
          }

          const pageNum = page as number
          const isActive = pageNum === currentPage

          return (
            <button
              key={pageNum}
              onClick={() => handlePageChange(pageNum)}
              className={`px-3 py-2 text-sm font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary ${
                isActive
                  ? 'bg-primary text-white hover:bg-primary-dark'
                  : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50'
              }`}
              aria-label={`第 ${pageNum} 頁`}
              aria-current={isActive ? 'page' : undefined}
            >
              {pageNum}
            </button>
          )
        })}

        {/* 下一頁 */}
        <button
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-white"
          aria-label="下一頁"
        >
          ›
        </button>
      </div>

      {/* 右側：頁碼跳轉 */}
      {showJump && totalPages > 5 && (
        <form onSubmit={handleJumpToPage} className="flex items-center gap-2">
          <label htmlFor="jump-page" className="text-sm text-gray-600">
            跳轉至
          </label>
          <input
            id="jump-page"
            name="page"
            type="number"
            min={1}
            max={totalPages}
            defaultValue={currentPage}
            className="w-16 px-2 py-1 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            aria-label="跳轉頁碼"
          />
          <button
            type="submit"
            className="px-3 py-1 text-sm font-medium text-white bg-primary rounded-md hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
          >
            前往
          </button>
        </form>
      )}
    </div>
  )
}

