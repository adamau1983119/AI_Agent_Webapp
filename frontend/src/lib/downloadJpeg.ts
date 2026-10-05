/** Convert loaded <img> (or URL) to sRGB JPEG and trigger download in gesture. */

const JPEG_MAX_EDGE = 1440
const JPEG_QUALITY = 0.92

function canvasToJpegBlob(canvas: HTMLCanvasElement): Promise<Blob> {
  return new Promise((resolve, reject) => {
    canvas.toBlob(
      (b) => (b ? resolve(b) : reject(new Error('encode'))),
      'image/jpeg',
      JPEG_QUALITY
    )
  })
}

function triggerDownload(blob: Blob, filename: string): void {
  const href = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = href
  a.download = filename.toLowerCase().endsWith('.jpg') ? filename : `${filename}.jpg`
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(href)
}

/** Prefer already-decoded DOM image (avoids second proxy fetch / gesture issues). */
export async function downloadImageElementAsJpeg(
  img: HTMLImageElement,
  filename: string
): Promise<void> {
  if (!img || !img.naturalWidth) throw new Error('missing_img')
  const scale = Math.min(1, JPEG_MAX_EDGE / Math.max(img.naturalWidth, img.naturalHeight, 1))
  const width = Math.max(1, Math.round(img.naturalWidth * scale))
  const height = Math.max(1, Math.round(img.naturalHeight * scale))
  const canvas = document.createElement('canvas')
  canvas.width = width
  canvas.height = height
  const ctx = canvas.getContext('2d')
  if (!ctx) throw new Error('canvas')
  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, width, height)
  ctx.drawImage(img, 0, 0, width, height)
  const jpeg = await canvasToJpegBlob(canvas)
  triggerDownload(jpeg, filename)
}

export async function downloadImageAsJpeg(
  proxyUrl: string,
  filename: string
): Promise<void> {
  if (!proxyUrl) throw new Error('missing_url')
  const res = await fetch(proxyUrl)
  if (!res.ok) throw new Error('fetch_failed')
  const blob = await res.blob()
  const type = (blob.type || '').toLowerCase()
  if (!type.startsWith('image/') || type.includes('svg')) throw new Error('unsupported')
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
  const jpeg = await canvasToJpegBlob(canvas)
  triggerDownload(jpeg, filename)
}

/** Save the photo already on screen as JPEG, with no heading. Same canvas path as title images. */
export async function downloadShownPhotoAsJpeg(
  img: HTMLImageElement | null,
  proxyUrl: string,
  filename: string
): Promise<void> {
  if (img && img.naturalWidth > 0) {
    try {
      await downloadImageElementAsJpeg(img, filename)
      return
    } catch {
      // A tainted canvas cannot be read. Reload through the proxy instead.
    }
  }
  await downloadImageAsJpeg(proxyUrl, filename)
}
