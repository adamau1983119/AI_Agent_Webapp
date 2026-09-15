/** Convert a proxied image to sRGB JPEG (longest edge 1440) and download. */

const JPEG_MAX_EDGE = 1440
const JPEG_QUALITY = 0.9

export async function downloadImageAsJpeg(
  proxyUrl: string,
  filename: string
): Promise<void> {
  if (!proxyUrl) {
    throw new Error('missing_url')
  }
  const res = await fetch(proxyUrl)
  if (!res.ok) {
    throw new Error('fetch_failed')
  }
  const blob = await res.blob()
  const type = (blob.type || '').toLowerCase()
  if (!type.startsWith('image/') || type.includes('svg')) {
    throw new Error('unsupported')
  }
  const bitmap = await createImageBitmap(blob)
  const scale = Math.min(1, JPEG_MAX_EDGE / Math.max(bitmap.width, bitmap.height, 1))
  const width = Math.max(1, Math.round(bitmap.width * scale))
  const height = Math.max(1, Math.round(bitmap.height * scale))
  const canvas = document.createElement('canvas')
  canvas.width = width
  canvas.height = height
  const ctx = canvas.getContext('2d')
  if (!ctx) {
    bitmap.close()
    throw new Error('canvas')
  }
  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, width, height)
  ctx.drawImage(bitmap, 0, 0, width, height)
  bitmap.close()
  const jpeg = await new Promise<Blob | null>((resolve) => {
    canvas.toBlob(resolve, 'image/jpeg', JPEG_QUALITY)
  })
  if (!jpeg) {
    throw new Error('encode')
  }
  const href = URL.createObjectURL(jpeg)
  const link = document.createElement('a')
  link.href = href
  link.download = filename.toLowerCase().endsWith('.jpg') ? filename : `${filename}.jpg`
  link.click()
  URL.revokeObjectURL(href)
}
