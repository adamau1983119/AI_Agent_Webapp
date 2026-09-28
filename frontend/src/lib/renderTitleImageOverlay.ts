/** Demo title-image overlay: photo + heading → JPEG download. Sample only. */

export type OverlayStyleId = 'a' | 'b' | 'c'

const MAX_EDGE = 1080
const JPEG_Q = 0.9

const FALLBACK_COLORS = ['#1e293b', '#0f172a', '#292524', '#1c1917']

function paintFallback(ctx: CanvasRenderingContext2D, w: number, h: number, seed: string) {
  const n = Math.abs([...seed].reduce((a, c) => a + c.charCodeAt(0), 0)) % FALLBACK_COLORS.length
  ctx.fillStyle = FALLBACK_COLORS[n]
  ctx.fillRect(0, 0, w, h)
  ctx.fillStyle = 'rgba(255,255,255,0.08)'
  ctx.fillRect(0, h * 0.55, w, h * 0.45)
}

function loadImage(url: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    // Only set CORS for absolute http(s) remote URLs
    if (/^https?:\/\//i.test(url)) img.crossOrigin = 'anonymous'
    const timer = window.setTimeout(() => reject(new Error('image_timeout')), 8000)
    img.onload = () => {
      window.clearTimeout(timer)
      resolve(img)
    }
    img.onerror = () => {
      window.clearTimeout(timer)
      reject(new Error('image_load'))
    }
    img.src = url
  })
}

function drawHeading(
  ctx: CanvasRenderingContext2D,
  heading: string,
  style: OverlayStyleId,
  w: number,
  h: number
) {
  const pad = Math.round(w * 0.06)
  const fontSize = Math.max(28, Math.round(w * 0.055))
  ctx.font = `700 ${fontSize}px Georgia, "Times New Roman", serif`
  ctx.textBaseline = 'top'

  const wrap = (text: string, maxWidth: number): string[] => {
    const lines: string[] = []
    let line = ''
    const push = () => {
      if (line) lines.push(line)
      line = ''
    }
    const tokens = text.match(/[^\s]+|\s+/g) || [text]
    for (const token of tokens) {
      if (/^\s+$/.test(token)) {
        const trial = line + token
        if (ctx.measureText(trial).width > maxWidth && line.trim()) push()
        else line = trial
        continue
      }
      for (const ch of Array.from(token)) {
        const trial = line + ch
        if (ctx.measureText(trial).width > maxWidth && line) {
          push()
          line = ch
        } else {
          line = trial
        }
      }
    }
    push()
    return lines.filter((l) => l.trim()).slice(0, 4)
  }

  const lines = wrap(heading, w - pad * 2)
  const lineH = fontSize * 1.25
  const blockH = lines.length * lineH

  if (style === 'a') {
    const y0 = (h - blockH) / 2
    ctx.fillStyle = 'rgba(0,0,0,0.35)'
    ctx.fillRect(0, y0 - pad * 0.5, w, blockH + pad)
    ctx.fillStyle = '#ffffff'
    ctx.textAlign = 'center'
    lines.forEach((ln, i) => {
      ctx.shadowColor = 'rgba(0,0,0,0.6)'
      ctx.shadowBlur = 8
      ctx.fillText(ln, w / 2, y0 + i * lineH)
    })
    ctx.shadowBlur = 0
    return
  }

  if (style === 'b') {
    const y0 = h - blockH - pad * 1.5
    ctx.fillStyle = 'rgba(0,0,0,0.55)'
    ctx.fillRect(0, y0 - pad * 0.4, w, blockH + pad * 1.2)
    ctx.fillStyle = '#ffffff'
    ctx.textAlign = 'left'
    lines.forEach((ln, i) => {
      ctx.fillText(ln, pad, y0 + i * lineH)
    })
    return
  }

  ctx.fillStyle = '#111111'
  ctx.fillRect(0, 0, w, blockH + pad * 1.4)
  ctx.fillStyle = '#f5f5f0'
  ctx.textAlign = 'left'
  lines.forEach((ln, i) => {
    ctx.fillText(ln, pad, pad * 0.6 + i * lineH)
  })
}

async function paintBase(
  ctx: CanvasRenderingContext2D,
  photoUrl: string,
  w: number,
  h: number
): Promise<void> {
  try {
    const img = await loadImage(photoUrl)
    const scale = Math.max(w / Math.max(img.naturalWidth, 1), h / Math.max(img.naturalHeight, 1))
    const dw = img.naturalWidth * scale
    const dh = img.naturalHeight * scale
    ctx.drawImage(img, (w - dw) / 2, (h - dh) / 2, dw, dh)
  } catch {
    paintFallback(ctx, w, h, photoUrl.slice(0, 40))
  }
}

export async function renderAndDownloadTitleImage(opts: {
  photoUrl: string
  heading: string
  style: OverlayStyleId
  filename: string
}): Promise<void> {
  const w = MAX_EDGE
  const h = MAX_EDGE
  const canvas = document.createElement('canvas')
  canvas.width = w
  canvas.height = h
  const ctx = canvas.getContext('2d')
  if (!ctx) throw new Error('canvas')
  await paintBase(ctx, opts.photoUrl, w, h)
  drawHeading(ctx, opts.heading.trim(), opts.style, w, h)

  const blob = await new Promise<Blob | null>((resolve) => {
    canvas.toBlob(resolve, 'image/jpeg', JPEG_Q)
  })
  if (!blob) throw new Error('encode')

  const href = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = href
  a.download = opts.filename.toLowerCase().endsWith('.jpg') ? opts.filename : `${opts.filename}.jpg`
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(href)
}

export async function renderTitleImagePreviewDataUrl(opts: {
  photoUrl: string
  heading: string
  style: OverlayStyleId
}): Promise<string> {
  const w = 640
  const h = 640
  const canvas = document.createElement('canvas')
  canvas.width = w
  canvas.height = h
  const ctx = canvas.getContext('2d')
  if (!ctx) throw new Error('canvas')
  await paintBase(ctx, opts.photoUrl, w, h)
  drawHeading(ctx, opts.heading.trim(), opts.style, w, h)
  return canvas.toDataURL('image/jpeg', 0.85)
}
