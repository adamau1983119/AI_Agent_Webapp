/** Canned compose demo packs — no API, no credits. */
export type DemoLang = 'zh-TW' | 'en' | 'ja'

export type DemoPack = {
  titles: string[]
  body: string
  hashtag_sets: string[][]
  keepHint: string
}

const ZH: DemoPack = {
  titles: [
    '托特包真正該比的，不是 logo',
    '摸得到的工藝，比開箱濾鏡誠實',
    '通勤托特：能裝、耐背、越用越有味道',
  ],
  body:
    '這只托特不是「貴」那麼簡單：帆布撐得住通勤，皮革邊條越用越有味道。\n\n' +
    '第二段才講重點——縫線密度、內裡分隔、單肩久背仍不變形。想裝筆電＋水壺？量過了，真的進得去。別再只看 logo，摸得到的工藝比較誠實。',
  hashtag_sets: [
    ['#托特包', '#通勤穿搭', '#開箱', '#質感生活', '#工藝'],
    ['#托特包', '#生活風格', '#質感'],
    ['#通勤', '#開箱', '#托特包', '#好物'],
  ],
  keepHint: '這只托特不是「貴」那麼簡單：帆布撐得住通勤，皮革邊條越用越有味道。',
}

const EN: DemoPack = {
  titles: [
    'Judge the tote by craft, not the logo',
    'Touchable quality beats filter hype',
    'Commute tote: fits, lasts, ages well',
  ],
  body:
    'This tote isn’t “expensive” for the logo—canvas that survives commute, leather trim that ages with you.\n\n' +
    'Then the real flex: stitch density, inner pockets, and a strap that won’t punish your shoulder. Laptop + bottle? Measured. Fits. Touch the craft before you trust the name.',
  hashtag_sets: [
    ['#tote', '#commute', '#unboxing', '#quality', '#craft'],
    ['#tote', '#lifestyle', '#style'],
    ['#commute', '#unboxing', '#tote', '#tips'],
  ],
  keepHint:
    'This tote isn’t “expensive” for the logo—canvas that survives commute, leather trim that ages with you.',
}

const JA: DemoPack = {
  titles: [
    'トートはロゴより仕立てを見よう',
    '触れてわかる品質が本音',
    '通勤トート：入る・耐える・育つ',
  ],
  body:
    'このトートはロゴが高いだけじゃない。通勤に耐えるキャンバスと、使うほど味が出るレザー縁。\n\n' +
    '本命はここ——縫い目の密度、内ポケット、肩が痛くなりにくいストラップ。ノートPCとボトル、実寸で入る。触れてわかる仕立てを信じて。',
  hashtag_sets: [
    ['#トート', '#通勤', '#開封', '#質感', '#仕立て'],
    ['#トート', '#ライフスタイル', '#スタイル'],
    ['#通勤', '#開封', '#トート', '#tips'],
  ],
  keepHint:
    'このトートはロゴが高いだけじゃない。通勤に耐えるキャンバスと、使うほど味が出るレザー縁。',
}

const BY_LEN: Record<number, Partial<Record<DemoLang, string>>> = {
  100: {},
  150: {
    'zh-TW':
      ZH.body +
      '\n\n顏色怎麼搭、雨天注意、為什麼「越用越有味道」不是行銷空話——用過一周你就懂。',
    en:
      EN.body +
      '\n\nHow to style the color, rainy-day care, and why “ages with you” is not empty marketing—you’ll know after a week.',
    ja:
      JA.body +
      '\n\n色合わせ、雨の日の注意、「使うほど味が出る」が宣伝文句じゃない理由——一週間使えば分かる。',
  },
}

export function getComposeDemoPack(lang: string, length = 100): DemoPack {
  const key: DemoLang = lang.startsWith('ja') ? 'ja' : lang.startsWith('en') ? 'en' : 'zh-TW'
  const base = key === 'ja' ? JA : key === 'en' ? EN : ZH
  const override = BY_LEN[length]?.[key]
  return override ? { ...base, body: override } : { ...base }
}
