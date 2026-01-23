# TopicCollector Planning Report
# TopicCollector 改良規劃報告

Version: v3.0
Date: 2026-01-23
Project: AI Agent Webapp for Social Media Content Generation
Branch: v3.0.0-development

---

## Executive Summary / 執行摘要

This project is a social media content generation platform. Current issues identified:

1. **RSS Feed Single-Source Monopoly** - All topics from a category come from one source (e.g., Vogue for Fashion)
2. **Lack of Content Diversity** - Critical for influencer content uniqueness
3. **No Source Health Monitoring** - Single feed failure can cause system-wide issues

本專案是社群媒體內容生成平台。當前發現的問題：

1. **RSS Feed 單一來源壟斷** - 同一分類的所有主題來自單一來源（如 Fashion 全來自 Vogue）
2. **內容缺乏多樣性** - 影響網紅內容獨特性
3. **無來源健康監控** - 單一 Feed 失敗可能導致系統問題

---

## Completion Status / 完成狀態

| Phase | Name | Status | Notes |
|-------|------|--------|-------|
| **Phase 5A** | Immediate Preview | ✅ **COMPLETED** | 2026-01-22 |
| Phase 1 | RSS Multi-Source + Core Scoring | ⏳ Pending | Priority: 🔴 High |
| Phase 2 | Health Monitoring + Persistence | ⏳ Pending | Priority: 🔴 High |
| Phase 3 | Health API | ⏳ Pending | Priority: 🟡 Medium |
| Phase 4 | Config Externalization | ⏳ Optional | Priority: 🟢 Low |
| Phase 5B | Smart Image Matching | ⏳ Pending | Priority: 🟡 Medium |

---

## Phase 1: RSS Multi-Source Collection + Core Scoring

### 1.1 RSS Feed Multi-Source Logic (NEW - Priority)

**Problem Identified**:
```python
# Current "First-Come-First-Served" Logic
for feed_url in feeds:
    topics = fetch_from_feed(feed_url)
    if len(topics) >= count:
        break  # ⚠️ Only first successful feed is used
```

**Solution: Role-Based Allocation (Scheme A)**

```
Fashion (10 topics):
├── Authority (2): Vogue, Elle
├── Streetwear (2): Hypebeast, Highsnobiety  
├── Asian (2): Hypebae, SCMP Style
├── Industry (2): BoF, WWD
└── Practical (2): Refinery29, Who What Wear

Food (10 topics):
├── Mainstream (2): Eater, Bon Appétit
├── Professional (2): Food & Wine, Serious Eats
├── Cultural (2): Saveur, Taste Atlas
├── Healthy (2): EatingWell, Cooking Light
└── Casual (2): Delish, Tasty

Trend (10 topics):
├── Tech (2): TechCrunch, The Verge
├── Science (2): Ars Technica, Quanta
├── Culture (2): Vox, The Atlantic
├── Innovation (2): WIRED, MIT Technology Review
└── Lifestyle (2): Fast Company, Curbed
```

**Key Changes**:
- Restructure `self.rss_feeds` to use role-based categorization
- Modify `_collect_from_rss` to collect from each role
- Add configurable role distribution in YAML

### 1.2 Article Scoring Algorithm

**Formula**: Score = 0.4T + 0.3S + 0.2C + 0.1R

| Dimension | Weight | Description |
|-----------|--------|-------------|
| T (Time) | 40% | Newer articles score higher |
| S (Source) | 30% | Trusted sources score higher |
| C (Completeness) | 20% | Has image/summary scores higher |
| R (Relevance) | 10% | Keyword match |

### 1.3 Diversity Score (NEW)

**Formula**: diversity_score = 1 - (max_ratio - avg_ratio)

```python
# Example
topics = [Vogue, Vogue, Elle, Hypebeast, BoF, WWD, Refinery29, Hypebae, Highsnobiety, SCMP]
# 10 topics, 9 unique sources
# max_ratio = 2/10 = 0.2 (Vogue appears twice)
# avg_ratio = 1/9 ≈ 0.11
# diversity_score = 1 - (0.2 - 0.11) = 0.91 ✅ Good
```

**Acceptance Criteria**:
- diversity_score >= 0.6 → Pass
- diversity_score < 0.6 → Warning alert

---

## Phase 2: Health Monitoring + Persistence (MongoDB Only)

### 2.1 Feed Health Repository (Pure MongoDB)

**Decision**: Use MongoDB only (no Redis for now) to reduce complexity.

```python
class FeedHealthRepository:
    async def is_paused(self, feed_url: str) -> bool:
        """Check if feed is paused (MongoDB query)"""
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        failures = await self.collection.count_documents({
            "feed_url": feed_url,
            "status": "failure",
            "timestamp": {"$gte": one_hour_ago}
        })
        return failures >= 3

    async def record_failure(self, feed_url: str, error: str):
        """Record failure event to MongoDB"""
        await self.collection.insert_one({
            "feed_url": feed_url,
            "status": "failure",
            "error": error,
            "timestamp": datetime.utcnow()
        })

    async def record_success(self, feed_url: str):
        """Record success event to MongoDB"""
        await self.collection.insert_one({
            "feed_url": feed_url,
            "status": "success",
            "timestamp": datetime.utcnow()
        })

    async def get_reliability_score(self, feed_url: str, days: int = 7) -> float:
        """Calculate reliability score over N days"""
        since = datetime.utcnow() - timedelta(days=days)
        total = await self.collection.count_documents({...})
        successes = await self.collection.count_documents({...})
        return successes / total if total > 0 else 0.0
```

### 2.2 Auto-Pause Mechanism

- **Trigger**: 3 consecutive failures within 1 hour
- **Action**: Skip feed for 1 hour
- **Recovery**: Automatic resume after pause period

---

## Phase 3: Health Monitoring API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/feeds/health` | GET | All feeds health status |
| `/feeds/health/{category}` | GET | Category feeds health |
| `/feeds/stats` | GET | Statistics summary |
| `/feeds/{feed_id}/pause` | POST | Manual pause |
| `/feeds/{feed_id}/resume` | POST | Manual resume |
| `/feeds/diversity-report` | GET | Diversity score report |

---

## Phase 4: Config Externalization (Optional)

Move all configurations to YAML:

```yaml
# config/feeds.yaml
categories:
  fashion:
    count: 10
    role_distribution:
      authority: 2
      streetwear: 2
      asian: 2
      industry: 2
      practical: 2
    roles:
      authority:
        - name: Vogue
          url: https://www.vogue.com/feed/rss
          weight: 1.0
        - name: Elle
          url: https://www.elle.com/rss/all.xml
          weight: 0.95
      # ... more roles
```

---

## Phase 5B: Smart Image Matching

### 5.1 Image Scoring Algorithm

**Formula**: ImageScore = 0.4K + 0.25T + 0.15Q + 0.2D

| Dimension | Weight | Description |
|-----------|--------|-------------|
| K (Keyword) | 40% | alt/caption keyword match |
| T (Trust) | 25% | Source credibility tier |
| Q (Quality) | 15% | Resolution >= 800px |
| **D (Diversity)** | **20%** | **Source diversity bonus (NEW)** |

### 5.2 Diversity Bonus (NEW)

```python
def calculate_diversity_bonus(image, selected_images):
    """
    D = 1.0 if image source differs from all selected
    D = 0.0 if image source same as any selected
    """
    selected_sources = {img['source'] for img in selected_images}
    return 1.0 if image['source'] not in selected_sources else 0.0
```

**Effect**:
- Image 1: Select from Vogue (D = 1.0)
- Image 2: Another Vogue image has D = 0.0, loses 20% score
- System prefers images from different sources

---

## Implementation Priority Order

| Order | Task | Est. Hours | Dependency |
|-------|------|------------|------------|
| 1 | Phase 1.1 - RSS Multi-Source Logic | 3 hours | None |
| 2 | Phase 1.3 - Diversity Score | 1 hour | Phase 1.1 |
| 3 | Phase 2 - Health Monitoring | 3 hours | Phase 1.1 |
| 4 | Phase 1.2 - Article Scoring | 2 hours | Phase 2 |
| 5 | Phase 3 - Health API | 2 hours | Phase 2 |
| 6 | Phase 5B - Smart Matching | 3 hours | Phase 1 |
| 7 | Phase 4 - Config (Optional) | 2 hours | All |

**Total Estimated**: ~16 hours

---

## Acceptance Criteria

### RSS Multi-Source
- [ ] Each category pulls from 5+ different roles
- [ ] No single source exceeds 30% of topics
- [ ] diversity_score >= 0.6 for all categories
- [ ] 10 topics per category generated daily

### Health Monitoring
- [ ] Failed feeds auto-paused after 3 failures
- [ ] Paused feeds auto-resume after 1 hour
- [ ] Health report available via API

### Image Matching (Phase 5B)
- [ ] 8-10 matched images per topic
- [ ] Images from diverse sources preferred
- [ ] Each image has score and caption

---

## Expected Results

| Metric | Before | After |
|--------|--------|-------|
| Source diversity | 1 source/category | 5+ sources/category |
| Content uniqueness | Low | High |
| Single feed failure impact | System failure | Graceful degradation |
| Image source diversity | Random | Diverse |

---

## Document References

- `02_Implementation_Checklist.md` - 完整檢查清單
- `03_Technical_Specification.md` - 技術規格
- `04_Image_Matching_Logic.md` - 圖片匹配邏輯詳細規格
- `RSS_Feed多源邏輯問題診斷報告_請求第三方建議.md` - RSS 問題診斷

---

End of Planning Report
