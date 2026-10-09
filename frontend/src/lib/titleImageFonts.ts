/** Open webfonts for the title-image canvas. Five faces per UI language. */

export type TitleFontId =
  | 'noto-sans-tc'
  | 'noto-serif-tc'
  | 'noto-sans-hk'
  | 'lxgw-wenkai-tc'
  | 'huninn'
  | 'noto-sans-jp'
  | 'noto-serif-jp'
  | 'biz-udp-gothic'
  | 'biz-udp-mincho'
  | 'm-plus-1'
  | 'inter'
  | 'roboto'
  | 'open-sans'
  | 'poppins'
  | 'montserrat'

type Lang = 'zh-TW' | 'en' | 'ja'

const FAMILY: Record<TitleFontId, string> = {
  'noto-sans-tc': 'Noto Sans TC',
  'noto-serif-tc': 'Noto Serif TC',
  'noto-sans-hk': 'Noto Sans HK',
  'lxgw-wenkai-tc': 'LXGW WenKai TC',
  'huninn': 'Huninn',
  'noto-sans-jp': 'Noto Sans JP',
  'noto-serif-jp': 'Noto Serif JP',
  'biz-udp-gothic': 'BIZ UDPGothic',
  'biz-udp-mincho': 'BIZ UDPMincho',
  'm-plus-1': 'M PLUS 1',
  inter: 'Inter',
  roboto: 'Roboto',
  'open-sans': 'Open Sans',
  poppins: 'Poppins',
  montserrat: 'Montserrat',
}

const GOOGLE: Record<TitleFontId, string> = {
  'noto-sans-tc': 'Noto+Sans+TC',
  'noto-serif-tc': 'Noto+Serif+TC',
  'noto-sans-hk': 'Noto+Sans+HK',
  'lxgw-wenkai-tc': 'LXGW+WenKai+TC',
  huninn: 'Huninn',
  'noto-sans-jp': 'Noto+Sans+JP',
  'noto-serif-jp': 'Noto+Serif+JP',
  'biz-udp-gothic': 'BIZ+UDPGothic',
  'biz-udp-mincho': 'BIZ+UDPMincho',
  'm-plus-1': 'M+PLUS+1',
  inter: 'Inter',
  roboto: 'Roboto',
  'open-sans': 'Open+Sans',
  poppins: 'Poppins',
  montserrat: 'Montserrat',
}

const BY_LANG: Record<Lang, TitleFontId[]> = {
  'zh-TW': ['noto-sans-tc', 'noto-serif-tc', 'noto-sans-hk', 'lxgw-wenkai-tc', 'huninn'],
  ja: ['noto-sans-jp', 'noto-serif-jp', 'biz-udp-gothic', 'biz-udp-mincho', 'm-plus-1'],
  en: ['inter', 'roboto', 'open-sans', 'poppins', 'montserrat'],
}

const LABEL_KEY: Record<TitleFontId, string> = {
  'noto-sans-tc': 'titleImage.face.notoSansTc',
  'noto-serif-tc': 'titleImage.face.notoSerifTc',
  'noto-sans-hk': 'titleImage.face.notoSansHk',
  'lxgw-wenkai-tc': 'titleImage.face.lxgwWenkaiTc',
  huninn: 'titleImage.face.huninn',
  'noto-sans-jp': 'titleImage.face.notoSansJp',
  'noto-serif-jp': 'titleImage.face.notoSerifJp',
  'biz-udp-gothic': 'titleImage.face.bizUdpGothic',
  'biz-udp-mincho': 'titleImage.face.bizUdpMincho',
  'm-plus-1': 'titleImage.face.mPlus1',
  inter: 'titleImage.face.inter',
  roboto: 'titleImage.face.roboto',
  'open-sans': 'titleImage.face.openSans',
  poppins: 'titleImage.face.poppins',
  montserrat: 'titleImage.face.montserrat',
}

export function facesForLanguage(language: string): TitleFontId[] {
  if (language === 'en' || language === 'ja') return BY_LANG[language]
  return BY_LANG['zh-TW']
}

export function faceLabelKey(id: TitleFontId): string {
  return LABEL_KEY[id]
}

export function canvasFontFamily(id: TitleFontId): string {
  const name = FAMILY[id]
  return `"${name}", "PingFang TC", "Microsoft JhengHei", "Hiragino Sans", sans-serif`
}

function sampleText(text: string): string {
  const chars = Array.from(new Set(Array.from(text))).join('')
  return (chars || 'A').slice(0, 80)
}

export async function ensureTitleFont(id: TitleFontId, text: string): Promise<void> {
  const sample = sampleText(text)
  const linkId = `title-font-${id}`
  let link = document.getElementById(linkId) as HTMLLinkElement | null
  if (!link || link.dataset.sample !== sample) {
    link?.remove()
    link = document.createElement('link')
    link.id = linkId
    link.rel = 'stylesheet'
    link.dataset.sample = sample
    link.href =
      `https://fonts.googleapis.com/css2?family=${GOOGLE[id]}:wght@600` +
      `&text=${encodeURIComponent(sample)}&display=swap`
    const ready = new Promise<void>((resolve) => {
      link!.onload = () => resolve()
      link!.onerror = () => resolve()
    })
    document.head.appendChild(link)
    await ready
  }
  try {
    await document.fonts.load(`600 32px "${FAMILY[id]}"`)
  } catch {
    /* canvas falls back to the next family */
  }
}
