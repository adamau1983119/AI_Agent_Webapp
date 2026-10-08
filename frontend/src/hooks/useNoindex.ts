import { useEffect } from 'react'

const MARK = 'data-ae-noindex'

export function useNoindex() {
  useEffect(() => {
    const meta = document.createElement('meta')
    meta.name = 'robots'
    meta.content = 'noindex'
    meta.setAttribute(MARK, '1')
    document.head.appendChild(meta)
    return () => {
      meta.remove()
    }
  }, [])
}
