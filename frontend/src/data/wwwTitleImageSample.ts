/**
 * Canned Who What Wear topic for title-image Sample UI.
 * Source: https://www.whowhatwear.com/fashion/celebrity/tom-bateman-the-love-hypothesis-interview-2026
 * Demo only — no live extract / no credits.
 */
export type SampleLang = 'zh-TW' | 'en' | 'ja'

export type SamplePhoto = {
  id: string
  /** Display URL (local Sample copy of article photo) */
  url: string
  /** Original CDN URL from the article */
  sourceUrl: string
  credit: string
}

export type WwwTitleImageSample = {
  sourceUrl: string
  category: 'fashion'
  title: string
  summary: string
  headings: string[]
  body: string
  hashtags: string[]
  photos: SamplePhoto[]
  styles: { id: 'a' | 'b' | 'c'; labelKey: string }[]
}

const PHOTOS: SamplePhoto[] = [
  {
    id: 'www-tb-1',
    // Hero portrait from article CDN (saved under public for Sample match grid)
    url: '/sample/www-tb/www-tb-1.jpg',
    sourceUrl: 'https://cdn.mos.cms.futurecdn.net/sYduMSbLpMzcwj7YoycL5i-1280-80.jpg',
    credit: 'Graham Dunn / Who What Wear',
  },
  {
    id: 'www-tb-2',
    url: '/sample/www-tb/www-tb-2.jpg',
    sourceUrl: 'https://cdn.mos.cms.futurecdn.net/LcsY5oUd5Hd342ZWsPbXCi.jpg',
    credit: 'Graham Dunn / Who What Wear',
  },
  {
    id: 'www-tb-3',
    url: '/sample/www-tb/www-tb-3.jpg',
    sourceUrl: 'https://cdn.mos.cms.futurecdn.net/XW5dMN24ksqdARr3DDdNem.jpg',
    credit: 'Graham Dunn / Who What Wear',
  },
  {
    id: 'www-tb-4',
    url: '/sample/www-tb/www-tb-4.jpg',
    sourceUrl: 'https://cdn.mos.cms.futurecdn.net/HH53krKMnU94VqY3gUXrnW.jpg',
    credit: 'Graham Dunn / Who What Wear',
  },
]

const STYLES = [
  { id: 'a' as const, labelKey: 'titleImage.styleA' },
  { id: 'b' as const, labelKey: 'titleImage.styleB' },
  { id: 'c' as const, labelKey: 'titleImage.styleC' },
]

const BY_LANG: Record<SampleLang, Omit<WwwTitleImageSample, 'photos' | 'styles' | 'sourceUrl' | 'category'>> = {
  'zh-TW': {
    title: 'Tom Bateman 談浪漫喜劇、Lili Reinhart 與拍 TikTok',
    summary:
      '《The Love Hypothesis》訪談：Bateman 與 Lili Reinhart 的對手戲化學、BookTok／TikTok 宣傳，以及他最愛的經典浪漫喜劇。',
    headings: [
      '八十萬次觀看之後：Bateman 怎麼看 TikTok 宣傳',
      '假交往到真心：The Love Hypothesis 的對立吸引',
      '離線演員×網路巨星：Olive 與 Adam 的化学反应',
    ],
    body:
      'Bateman 說，若有八千萬人看這部片「太好了」。他本偏離線，卻在 Reinhart 帶領下拍 TikTok；兩人來自不同世界，正好呼應片中對立吸引。\n\n' +
      '改編自 Ali Hazelwood 暢銷書，假交往 Trope 放進實驗室與博士生日常——重點不只在一起，而是跨越差異去聽懂對方。',
    hashtags: ['#TheLoveHypothesis', '#TomBateman', '#LiliReinhart', '#BookTok', '#浪漫喜劇'],
  },
  en: {
    title: 'Tom Bateman on Favorite Rom-Coms, Lili Reinhart, and Making TikToks',
    summary:
      'Who What Wear interview on The Love Hypothesis: chemistry with Lili Reinhart, BookTok/TikTok press, and classic rom-coms he loves.',
    headings: [
      'After 80M views: Bateman on going TikTok for Love Hypothesis',
      'Fake dating to real spark: opposites attract on screen',
      'Offline actor × online star: Olive and Adam chemistry',
    ],
    body:
      'Bateman says if 80 million people watch the movie, “fucking great.” Usually offline, he let Reinhart guide him into TikTok—two worlds meeting, much like the film’s opposites-attract story.\n\n' +
      'Based on Ali Hazelwood’s bestseller, the fake-dating trope lands in labs and PhD life. It’s not only about getting together—it’s reaching across a divide and learning to hear each other.',
    hashtags: ['#TheLoveHypothesis', '#TomBateman', '#LiliReinhart', '#BookTok', '#RomCom'],
  },
  ja: {
    title: 'トム・ベイトマン、ロマコメとLili Reinhart、TikTok撮影を語る',
    summary:
      'Who What Wearインタビュー。『The Love Hypothesis』、Reinhartとのケミストリー、BookTok／TikTok宣伝、好きなロマコメ。',
    headings: [
      '8000万回再生の先：ベイトマンが語るTikTok宣伝',
      '偽デートから本気へ：対極が惹かれ合う物語',
      'オフライン俳優×ネットスター：OliveとAdamの化学反応',
    ],
    body:
      'ベイトマンは「8000万人が観たら最高」と語る。普段はオフライン寄りだが、Reinhartに手を引かれTikTokへ。異なる世界の出会いが、作品の「対極の恋」と重なる。\n\n' +
      'Ali Hazelwoodのベストセラーが原作。偽デートの定番を研究室と博士課程に置く。付き合うだけでなく、違いを越えて相手の声を聴く話でもある。',
    hashtags: ['#TheLoveHypothesis', '#TomBateman', '#LiliReinhart', '#BookTok', '#ロマコメ'],
  },
}

export function getWwwTitleImageSample(lang: string): WwwTitleImageSample {
  const key: SampleLang = lang.startsWith('ja') ? 'ja' : lang.startsWith('en') ? 'en' : 'zh-TW'
  const pack = BY_LANG[key]
  return {
    sourceUrl:
      'https://www.whowhatwear.com/fashion/celebrity/tom-bateman-the-love-hypothesis-interview-2026',
    category: 'fashion',
    photos: PHOTOS,
    styles: STYLES,
    ...pack,
  }
}
