import { useEffect } from 'react'

const ORIGIN = 'https://www.ai-alterego.com'
const HOME = `${ORIGIN}/`

function upsertLink(rel: string, href: string) {
  let link = document.querySelector<HTMLLinkElement>(`link[rel="${rel}"]`)
  if (!link) {
    link = document.createElement('link')
    link.rel = rel
    document.head.appendChild(link)
  }
  link.href = href
}

function upsertMeta(attr: 'name' | 'property', key: string, content: string) {
  let meta = document.querySelector<HTMLMetaElement>(`meta[${attr}="${key}"]`)
  if (!meta) {
    meta = document.createElement('meta')
    meta.setAttribute(attr, key)
    document.head.appendChild(meta)
  }
  meta.content = content
}

/** 公開頁自有 canonical。不寫 noindex，離開頁面時把 canonical 還回首頁。 */
export function usePublicPageSeo(title: string, description: string) {
  useEffect(() => {
    const path = window.location.pathname.replace(/\/$/, '') || '/'
    const url = `${ORIGIN}${path}`
    document.title = title
    upsertLink('canonical', url)
    upsertMeta('name', 'description', description)
    upsertMeta('property', 'og:title', title)
    upsertMeta('property', 'og:description', description)
    upsertMeta('property', 'og:url', url)
    return () => {
      upsertLink('canonical', HOME)
      upsertMeta('property', 'og:url', HOME)
    }
  }, [title, description])
}
