/** Demo editor: photo + heading + align + font face/size + writing + bg → JPEG. */

import { canvasFontFamily, ensureTitleFont, type TitleFontId } from '@/lib/titleImageFonts'

export type { TitleFontId as FontFace } from '@/lib/titleImageFonts'
export type VAlign = 'top' | 'middle' | 'bottom'
export type HAlign = 'left' | 'center' | 'right'
export type FontScale = 'sm' | 'md' | 'lg'
/** h = 橫排；v = 直書（字由上而下，欄由右而左） */
export type WritingMode = 'h' | 'v'
/** 標題底色 10 選 */
export type TitleBg =
  | 'black'
  | 'white'
  | 'navy'
  | 'crimson'
  | 'forest'
  | 'purple'
  | 'amber'
  | 'teal'
  | 'slate'
  | 'rose'

const MAX_EDGE = 1080
const JPEG_Q = 0.9
const SCALE: Record<FontScale, number> = { sm: 0.04, md: 0.055, lg: 0.078 }

/** fill = 底條色；ink = 文字色（淺底用深字）；swatch = UI 色塊 */
export const TITLE_BG_PALETTE: Record<TitleBg, { fill: string; ink: string; swatch: string }> = {
  black: { fill: 'rgba(0,0,0,0.55)', ink: '#ffffff', swatch: '#111827' },
  white: { fill: 'rgba(255,255,255,0.82)', ink: '#111827', swatch: '#f8fafc' },
  navy: { fill: 'rgba(15,23,42,0.72)', ink: '#f8fafc', swatch: '#0f172a' },
  crimson: { fill: 'rgba(153,27,27,0.72)', ink: '#ffffff', swatch: '#991b1b' },
  forest: { fill: 'rgba(20,83,45,0.72)', ink: '#ecfdf5', swatch: '#14532d' },
  purple: { fill: 'rgba(88,28,135,0.72)', ink: '#faf5ff', swatch: '#581c87' },
  amber: { fill: 'rgba(245,158,11,0.85)', ink: '#1c1917', swatch: '#f59e0b' },
  teal: { fill: 'rgba(15,118,110,0.72)', ink: '#f0fdfa', swatch: '#0f766e' },
  slate: { fill: 'rgba(71,85,105,0.75)', ink: '#f8fafc', swatch: '#475569' },
  rose: { fill: 'rgba(190,24,93,0.72)', ink: '#fff1f2', swatch: '#be185d' },
}

export const TITLE_BG_OPTS: TitleBg[] = [
  'black',
  'white',
  'navy',
  'crimson',
  'forest',
  'purple',
  'amber',
  'teal',
  'slate',
  'rose',
]

function loadImage(url: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image()
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

function wrapLines(
  ctx: CanvasRenderingContext2D,
  text: string,
  maxWidth: number,
  maxLines: number
): string[] {
  const lines: string[] = []
  let line = ''
  for (const ch of text.replace(/\n/g, ' ')) {
    const trial = line + ch
    if (ctx.measureText(trial).width <= maxWidth || !line) line = trial
    else {
      lines.push(line)
      line = ch
      if (lines.length >= maxLines) break
    }
  }
  if (line && lines.length < maxLines) lines.push(line)
  return lines.length ? lines : [text.slice(0, 40)]
}

/** Split into vertical columns: each column is top→bottom chars; columns right→left. */
function verticalColumns(text: string, maxCharsPerCol: number, maxCols: number): string[][] {
  const chars = Array.from(text.replace(/\s+/g, '').trim())
  if (!chars.length) return [['·']]
  const cols: string[][] = []
  for (let i = 0; i < chars.length && cols.length < maxCols; i += maxCharsPerCol) {
    cols.push(chars.slice(i, i + maxCharsPerCol))
  }
  return cols
}

function drawHorizontal(
  ctx: CanvasRenderingContext2D,
  heading: string,
  w: number,
  h: number,
  vAlign: VAlign,
  hAlign: HAlign,
  fontSize: number,
  pad: number,
  bg: TitleBg
) {
  const { fill, ink } = TITLE_BG_PALETTE[bg]
  ctx.textBaseline = 'top'
  const lines = wrapLines(ctx, heading.trim(), w - pad * 2, 4)
  const lineH = fontSize * 1.25
  const blockH = lines.length * lineH
  let y0 = pad
  if (vAlign === 'middle') y0 = (h - blockH) / 2
  if (vAlign === 'bottom') y0 = h - blockH - pad * 1.4
  ctx.fillStyle = fill
  ctx.fillRect(0, Math.max(0, y0 - pad * 0.35), w, blockH + pad * 0.7)
  ctx.fillStyle = ink
  ctx.textAlign = hAlign === 'left' ? 'left' : hAlign === 'right' ? 'right' : 'center'
  const x = hAlign === 'left' ? pad : hAlign === 'right' ? w - pad : w / 2
  lines.forEach((ln, i) => {
    ctx.shadowColor = ink === '#ffffff' || ink.startsWith('#f') ? 'rgba(0,0,0,0.45)' : 'rgba(255,255,255,0.35)'
    ctx.shadowBlur = 5
    ctx.fillText(ln, x, y0 + i * lineH)
  })
  ctx.shadowBlur = 0
}

function drawVertical(
  ctx: CanvasRenderingContext2D,
  heading: string,
  w: number,
  h: number,
  vAlign: VAlign,
  hAlign: HAlign,
  fontSize: number,
  pad: number,
  bg: TitleBg
) {
  const { fill, ink } = TITLE_BG_PALETTE[bg]
  ctx.textAlign = 'center'
  ctx.textBaseline = 'top'
  const colGap = fontSize * 1.35
  const charH = fontSize * 1.15
  const maxChars = Math.max(4, Math.floor((h - pad * 2) / charH))
  const cols = verticalColumns(heading, maxChars, 4)
  const blockW = cols.length * colGap
  const blockH = Math.max(...cols.map((c) => c.length)) * charH

  let xRight = w - pad - fontSize / 2
  if (hAlign === 'left') xRight = pad + blockW - fontSize / 2
  if (hAlign === 'center') xRight = w / 2 + blockW / 2 - fontSize / 2

  let y0 = pad
  if (vAlign === 'middle') y0 = (h - blockH) / 2
  if (vAlign === 'bottom') y0 = h - blockH - pad

  const barX = Math.min(...cols.map((_, i) => xRight - i * colGap)) - fontSize * 0.55
  const barW = blockW + fontSize * 0.3
  ctx.fillStyle = fill
  ctx.fillRect(Math.max(0, barX), Math.max(0, y0 - pad * 0.25), barW, blockH + pad * 0.5)

  ctx.fillStyle = ink
  cols.forEach((col, ci) => {
    const x = xRight - ci * colGap
    col.forEach((ch, ri) => {
      ctx.shadowColor = ink === '#ffffff' || ink.startsWith('#f') ? 'rgba(0,0,0,0.45)' : 'rgba(255,255,255,0.35)'
      ctx.shadowBlur = 5
      ctx.fillText(ch, x, y0 + ri * charH)
    })
  })
  ctx.shadowBlur = 0
}

function drawEditHeading(
  ctx: CanvasRenderingContext2D,
  heading: string,
  w: number,
  h: number,
  vAlign: VAlign,
  hAlign: HAlign,
  fontScale: FontScale,
  writing: WritingMode,
  fontFace: TitleFontId,
  titleBg: TitleBg
) {
  const pad = Math.round(w * 0.06)
  const fontSize = Math.max(22, Math.round(w * SCALE[fontScale]))
  ctx.font = `600 ${fontSize}px ${canvasFontFamily(fontFace)}`
  if (writing === 'v') {
    drawVertical(ctx, heading, w, h, vAlign, hAlign, fontSize, pad, titleBg)
  } else {
    drawHorizontal(ctx, heading, w, h, vAlign, hAlign, fontSize, pad, titleBg)
  }
}

async function paintBase(
  ctx: CanvasRenderingContext2D,
  photoUrl: string,
  w: number,
  h: number
): Promise<void> {
  ctx.fillStyle = '#0f172a'
  ctx.fillRect(0, 0, w, h)
  const img = await loadImage(photoUrl)
  const scale = Math.max(w / Math.max(img.naturalWidth, 1), h / Math.max(img.naturalHeight, 1))
  const dw = img.naturalWidth * scale
  const dh = img.naturalHeight * scale
  ctx.drawImage(img, (w - dw) / 2, (h - dh) / 2, dw, dh)
}

export type EditRenderOpts = {
  photoUrl: string
  heading: string
  vAlign: VAlign
  hAlign: HAlign
  fontScale: FontScale
  writing: WritingMode
  fontFace: TitleFontId
  titleBg: TitleBg
}

async function renderCanvas(opts: EditRenderOpts, edge: number): Promise<HTMLCanvasElement> {
  const canvas = document.createElement('canvas')
  canvas.width = edge
  canvas.height = edge
  const ctx = canvas.getContext('2d')
  if (!ctx) throw new Error('canvas')
  await ensureTitleFont(opts.fontFace, opts.heading)
  await paintBase(ctx, opts.photoUrl, edge, edge)
  drawEditHeading(
    ctx,
    opts.heading,
    edge,
    edge,
    opts.vAlign,
    opts.hAlign,
    opts.fontScale,
    opts.writing,
    opts.fontFace,
    opts.titleBg
  )
  return canvas
}

export async function renderEditPreviewDataUrl(opts: EditRenderOpts): Promise<string> {
  const canvas = await renderCanvas(opts, 640)
  return canvas.toDataURL('image/jpeg', 0.85)
}

export async function renderEditBlob(opts: EditRenderOpts): Promise<Blob> {
  const canvas = await renderCanvas(opts, MAX_EDGE)
  const blob = await new Promise<Blob | null>((resolve) => {
    canvas.toBlob(resolve, 'image/jpeg', JPEG_Q)
  })
  if (!blob) throw new Error('encode')
  return blob
}

export function downloadEditBlob(blob: Blob, filename: string): void {
  const href = URL.createObjectURL(blob)
  const a = document.createElement('a')
  const name = filename.toLowerCase().endsWith('.jpg') ? filename : `${filename}.jpg`
  a.href = href
  a.download = name
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(href)
}

export async function renderAndDownloadEdit(opts: EditRenderOpts & { filename: string }): Promise<void> {
  const blob = await renderEditBlob(opts)
  downloadEditBlob(blob, opts.filename)
}
