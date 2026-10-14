/** 建立頻道第三步：名稱用字典組出，描述固定一行。不呼叫模型。 */

const TAILS: Record<'zh-TW' | 'en' | 'ja', string[]> = {
  'zh-TW': ['', '筆記', '頻道', '情報', '地圖', '日誌', '見聞', '路線', '手帖', '日報', '精選', '速報', '觀測', '札記', '週報', '導覽', '聚焦', '現場', '專線', '櫥窗'],
  en: ['', 'Notes', 'Channel', 'News', 'Map', 'Journal', 'Stories', 'Route', 'Handbook', 'Brief', 'Picks', 'Flash', 'Watch', 'Log', 'Weekly', 'Guide', 'Focus', 'Desk', 'Line', 'Window'],
  ja: ['', 'ノート', 'チャンネル', '情報', 'マップ', '日誌', '見聞', 'ルート', '手帖', '日報', '精選', '速報', '観測', '札記', '週報', '案内', '焦点', '現場', '専線', '展示'],
}

export interface ChannelNameChoice {
  name: string
  description: string
}

function clip(value: string, max: number): string {
  return value.trim().slice(0, max)
}

function oneLineDescription(lang: 'zh-TW' | 'en' | 'ja', region: string, category: string): string {
  if (lang === 'en') return clip(`${region} ${category} updates.`, 80)
  if (lang === 'ja') return clip(`${region}の${category}公開情報。`, 80)
  return clip(`整理${region}${category}的公開消息。`, 80)
}

/** 只出 3 個：前面、後面、再加詞庫第二個尾詞。20 個尾詞留在詞庫。 */
export function buildChannelNameChoices(
  lang: 'zh-TW' | 'en' | 'ja',
  displayName: string,
  regionLabel: string,
  categoryLabel: string,
): ChannelNameChoice[] {
  const who = clip(displayName, 24)
  const region = regionLabel.trim()
  const category = categoryLabel.trim()
  const tail = TAILS[lang][1] || ''
  const description = oneLineDescription(lang, region, category)
  const names =
    lang === 'en'
      ? [`${who}'s ${region} ${category}`, `${region} ${category} by ${who}`, `${who} ${region} ${category} ${tail}`]
      : lang === 'ja'
        ? [`${who}の${region}${category}`, `${region}${category}の${who}`, `${who}${region}${category}${tail}`]
        : [`${who}的${region}${category}`, `${region}${category} ${who}`, `${who}${region}${category}${tail}`]
  return names.map((name) => ({ name: clip(name.replace(/\s+/g, ' '), 50), description }))
}
