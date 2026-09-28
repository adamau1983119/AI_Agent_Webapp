/**
 * /compose-sample thin wrapper around TitleImageEditPanel (canned photos + headings).
 */
import TitleImageEditPanel from '@/components/features/TitleImageEditPanel'

const PHOTOS = [
  { id: 'p1', url: '/sample/www-tb/www-tb-1.jpg' },
  { id: 'p2', url: '/sample/www-tb/www-tb-2.jpg' },
  { id: 'p3', url: '/sample/www-tb/www-tb-3.jpg' },
]

const HEADINGS_ZH = [
  'Tom Bateman 聊最愛浪漫喜劇與 TikTok',
  '莉莉與他的幕後默契',
  '愛情假設到螢幕化學',
]

export default function TitleImageEditDemo() {
  return (
    <TitleImageEditPanel
      photos={PHOTOS}
      headings={HEADINGS_ZH}
      testPrefix="demo"
      titleKey="titleImage.editDemoTitle"
      hintKey="titleImage.editDemoHint"
      filename="title-edit-demo.jpg"
    />
  )
}
