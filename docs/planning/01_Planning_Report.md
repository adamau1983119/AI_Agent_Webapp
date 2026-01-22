# TopicCollector Planning Report
# TopicCollector 改良規劃報告

Version: v1.2
Date: 2026-01-22
Project: AI Agent Webapp for Social Media Content Generation

---

## Executive Summary / 執行摘要

This project is a social media content generation platform. After adding 72 RSS Feed sources, the system experiences:
1. **Startup blocking** and **API timeout** issues
2. **No photo display** on topic cards (cards show blank before content generation)

本專案是社群媒體內容生成平台。新增 72 個 RSS Feed 後，系統出現：
1. 啟動阻塞和 API 超時問題
2. 主題卡片無照片顯示（內容生成前卡片空白）

---

## Proposed Solutions / 解決方案

### Solution A: TopicCollector Improvements
- Lazy loading mechanism
- Article scoring algorithm (Score = 0.4T + 0.3S + 0.2C + 0.1R)
- Caching and throttling control
- Health monitoring API

### Solution B: Image Matching Logic (NEW)
- **Phase 5A**: Immediate preview from article source images
- **Phase 5B**: Smart matching after content generation

---

## Article Scoring Algorithm / 文章評分演算法

**Formula**: Score = 0.4T + 0.3S + 0.2C + 0.1R

| Dimension | Weight | Description |
|-----------|--------|-------------|
| T (Time) | 40% | Newer articles score higher |
| S (Source) | 30% | Trusted sources score higher |
| C (Completeness) | 20% | Has image/summary scores higher |
| R (Relevance) | 10% | Keyword match |

---

## Image Matching Algorithm / 圖片匹配演算法 (NEW)

**Formula**: ImageScore = 0.5K + 0.3T + 0.2Q

| Dimension | Weight | Description |
|-----------|--------|-------------|
| K (Keyword) | 50% | alt/caption keyword match |
| T (Trust) | 30% | Source credibility tier |
| Q (Quality) | 20% | Resolution >= 800px |

### Two-Phase Design / 兩階段設計

```
Phase 5A: Article → Preview Images (Immediate)
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ RSS Article │ ──▶ │ Extractor   │ ──▶ │ preview[]   │
│ og:image    │     │ Extract img │     │ Card shows  │
│ <img> tags  │     │             │     │ photo NOW   │
└─────────────┘     └─────────────┘     └─────────────┘

Phase 5B: Content → Matched Images (After Generation)
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Generated   │ ──▶ │ Matcher     │ ──▶ │ matched[]   │
│ Content     │     │ Score+Rank  │     │ 8-10 best   │
│ Keywords    │     │             │     │ images      │
└─────────────┘     └─────────────┘     └─────────────┘
```

---

## Implementation Phases / 實施階段

| Phase | Name | Est. Hours | Priority |
|-------|------|------------|----------|
| 1 | Core Scoring | 4 hours | 🔴 High |
| 2 | Cache and Persistence | 3 hours | 🔴 High |
| 3 | Health Monitoring API | 2 hours | 🟡 Medium |
| 4 | Config Externalization | 2 hours | 🟢 Optional |
| **5A** | **Immediate Preview** | **1 hour** | **🔴 High** |
| **5B** | **Smart Matching** | **3 hours** | **🟡 Medium** |

---

## Acceptance Criteria / 驗收標準

### TopicCollector
- [ ] Service startup < 10 seconds
- [ ] Each article has score field
- [ ] Each category returns top 10 articles
- [ ] Health API returns correct status
- [ ] Emergency rollback available

### Image Matching (NEW)
- [ ] Every topic card has at least 1 preview image
- [ ] 8-10 matched images after content generation
- [ ] Each matched image has score and caption
- [ ] External search fallback when preview < 8

---

## Expected Results / 預期效果

| Metric | Before | After |
|--------|--------|-------|
| Service startup | Blocking | < 10s |
| API timeout | Frequent | Rare |
| Cards with images | ~30% | **100%** |
| Image relevance | Low | **High** |

---

## Document References / 文件參考

- `02_Implementation_Checklist.md` - 完整檢查清單
- `03_Technical_Specification.md` - 技術規格
- `04_Image_Matching_Logic.md` - 圖片匹配邏輯詳細規格

---

End of Planning Report
