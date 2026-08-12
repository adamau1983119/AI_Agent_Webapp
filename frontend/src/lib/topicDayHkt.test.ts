import { describe, expect, it } from 'vitest'
import { dedupeTopicsByTitle, normalizeTopicTitle } from './topicDayHkt'

describe('normalizeTopicTitle', () => {
  it('strips punctuation and lowercases', () => {
    expect(normalizeTopicTitle('Hello, World!')).toBe('hello world')
  })
})

describe('dedupeTopicsByTitle', () => {
  it('keeps first occurrence of duplicate titles', () => {
    const topics = [
      { id: 'a', title: 'Nike 新鞋發表' },
      { id: 'b', title: 'Nike 新鞋發表！！' },
      { id: 'c', title: '另一則' },
    ]
    const result = dedupeTopicsByTitle(topics)
    expect(result.map((t) => t.id)).toEqual(['a', 'c'])
  })
})
