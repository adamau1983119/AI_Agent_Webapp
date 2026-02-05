# TopicCollector Technical Specification
# TopicCollector 技術規格

Version: v1.2
Date: 2026-01-22

---

## Table of Contents / 目錄

1. [Article Scoring Algorithm](#1-scoring-algorithm-details)
2. [Configuration Structure](#2-configuration-structure)
3. [Data Flow](#3-data-flow)
4. [Health Monitoring](#4-health-monitoring)
5. [API Response Examples](#5-api-response-examples)
6. [Error Handling](#6-error-handling)
7. [Monitoring and Logging](#7-monitoring-and-logging)
8. [Image Matching Logic (NEW)](#8-image-matching-logic-new)

---

## 1. Scoring Algorithm Details

### 1.1 Formula
Score = 0.4 * T + 0.3 * S + 0.2 * C + 0.1 * R

### 1.2 Time Score (T) - 40%
T = max(0, 1 - hours_since_published / 48)

| Published | T Score |
|-----------|---------|
| 0 hours | 1.0 |
| 12 hours | 0.75 |
| 24 hours | 0.5 |
| 36 hours | 0.25 |
| 48+ hours | 0 |

### 1.3 Source Weight (S) - 30%

Tier S (1.0): Vogue, Elle, NYT, BBC, WSJ
Tier A (0.8): BoF, WWD, TechCrunch, Fast Company
Tier B (0.6): Hypebeast, Eater, The Verge, Wired
Tier C (0.4): Popbee, SCMP
Tier D (0.2): Other/Unknown (default: 0.5)

### 1.4 Completeness Score (C) - 20%
- Has image: +0.5
- Has summary (>50 chars): +0.5
- Has author: +0 (optional bonus)

### 1.5 Relevance Score (R) - 10%
Binary: 1.0 if any keyword matches, else 0

Fashion keywords: fashion, style, runway, designer, collection
Food keywords: food, recipe, restaurant, chef, cuisine
Trend keywords: trend, tech, innovation, AI, digital

---

## 2. Configuration Structure

### 2.1 SCORING_CONFIG
`python
SCORING_CONFIG = {
    "weights": {
        "time": 0.4,
        "source": 0.3,
        "completeness": 0.2,
        "relevance": 0.1
    },
    "time_decay_hours": 48,
    "default_source_weight": 0.5
}
`

### 2.2 SOURCE_WEIGHTS
`python
SOURCE_WEIGHTS = {
    # Tier S
    "Vogue": 1.0,
    "Elle": 1.0,
    "The New York Times": 1.0,
    "BBC News": 1.0,
    # ... (72 total sources)
}
`

### 2.3 RATE_LIMIT_CONFIG
`python
RATE_LIMIT_CONFIG = {
    "global": {
        "max_concurrent": 10,
        "requests_per_minute": 60
    },
    "per_domain_default": {
        "max_concurrent": 2,
        "requests_per_minute": 5,
        "min_interval_seconds": 12
    }
}
`

### 2.4 FEATURE_FLAGS
`python
FEATURE_FLAGS = {
    "scoring_enabled": True,
    "memory_cache_enabled": True,
    "persistent_cache_enabled": True,
    "rate_limiting_enabled": True,
    "domain_rate_limiting_enabled": True,
    "health_tracking_enabled": True,
    "auto_pause_enabled": True,
    "use_legacy_collector": False
}
`

---

## 3. Data Flow

1. SchedulerService triggers collection
2. TopicCollector.collect_topics(category, limit=10)
3. Get Feed URL list from FeedConfig
4. Filter paused Feeds via FeedStateTracker
5. Check cache via CacheManager (L1 memory, L2 MongoDB)
6. Parallel fetch RSS Feeds with RateLimiter
7. Parse articles with feedparser
8. Deduplicate by URL and title similarity
9. Filter recent (last 48 hours)
10. Calculate scores via ScoringService
11. Sort by score descending
12. Return top 10 articles

---

## 4. Health Monitoring

### 4.1 Health Score Calculation (0-100)
- Start with 100
- Consecutive failures: -15 per failure
- Success rate < 90%: -(90 - rate) * 100
- Avg response > 2s: -5 per 500ms over
- Paused: 0

### 4.2 Health Status
- healthy: score >= 80
- degraded: score >= 50
- unhealthy: score > 0
- paused: score = 0

### 4.3 Auto Pause Rules
- 3 consecutive failures: pause 1 hour
- 5 consecutive failures: pause 4 hours
- 10 consecutive failures: pause 24 hours

---

## 5. API Response Examples

### GET /feeds/health
`json
{
    "summary": {
        "total": 72,
        "by_status": {
            "healthy": 65,
            "degraded": 4,
            "unhealthy": 2,
            "paused": 1
        },
        "overall_health_score": 87
    },
    "feeds": [
        {
            "feed_url": "https://www.vogue.com/feed/rss",
            "name": "Vogue",
            "category": "fashion",
            "health_score": 95,
            "health_status": "healthy",
            "success_rate": 0.96
        }
    ]
}
`

### Topic with Score
`json
{
    "id": "topic_fashion_202601221000_0",
    "title": "Paris Fashion Week 2026",
    "category": "fashion",
    "score": 0.87,
    "score_breakdown": {
        "time": 0.92,
        "source": 1.0,
        "completeness": 1.0,
        "relevance": 1.0
    }
}
`

---

## 6. Error Handling

### 6.1 RSS Fetch Errors
- Timeout (10s): log warning, skip feed
- Connection error: log warning, track failure
- Parse error: log warning, skip feed
- Rate limit (429): pause feed, exponential backoff

### 6.2 Database Errors
- MongoDB connection: graceful degradation (skip persistence)
- Write error: log error, continue with memory cache only

### 6.3 Scoring Errors
- Missing fields: use defaults
- Invalid data: log warning, score as 0

---

## 7. Monitoring and Logging

### 7.1 Key Metrics
- RSS fetch success rate
- Average response time
- Cache hit rate
- Scoring distribution
- Collection duration

### 7.2 Log Levels
- INFO: normal operations
- WARNING: recoverable errors
- ERROR: failures requiring attention
- CRITICAL: emergency rollback triggered

---

## 8. Image Matching Logic (NEW)
## 圖片匹配邏輯

### 8.1 Two-Phase Design / 兩階段設計

```
┌─────────────────────────────────────────────────────────────────┐
│                    Image Processing Pipeline                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Phase 5A: Immediate Preview (Topic Creation)                    │
│  ┌─────────┐     ┌─────────────┐     ┌─────────────┐            │
│  │ Article │ ──▶ │ Extractor   │ ──▶ │ preview[]   │            │
│  │ HTML    │     │ og:image    │     │ (1-5 imgs)  │            │
│  │         │     │ <img> tags  │     │             │            │
│  └─────────┘     └─────────────┘     └─────────────┘            │
│                                              │                   │
│                                              ▼                   │
│                                       Card displays              │
│                                       photo NOW ✅               │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Phase 5B: Smart Matching (After Content Generation)             │
│  ┌─────────┐     ┌─────────────┐     ┌─────────────┐            │
│  │ Content │ ──▶ │ Keyword     │ ──▶ │ ImageMatcher│            │
│  │ Title   │     │ Extractor   │     │ Score+Rank  │            │
│  │ Summary │     │             │     │             │            │
│  └─────────┘     └─────────────┘     └─────────────┘            │
│                                              │                   │
│                                              ▼                   │
│                  ┌─────────────┐     ┌─────────────┐            │
│                  │ External    │ ◀── │ matched[]   │            │
│                  │ Search      │     │ (8-10 imgs) │            │
│                  │ (if < 8)    │     │             │            │
│                  └─────────────┘     └─────────────┘            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 Image Scoring Formula / 圖片評分公式

**Formula**: `ImageScore = 0.5 * K + 0.3 * T + 0.2 * Q`

| Dimension | Weight | Calculation | Range |
|-----------|--------|-------------|-------|
| **K (Keyword)** | 50% | Matched keywords / Total keywords | 0 ~ 1 |
| **T (Trust)** | 30% | Source tier lookup | 0 ~ 1 |
| **Q (Quality)** | 20% | Resolution check (>= 800px) | 0 or 1 |

### 8.3 Keyword Score (K) - 50%

```python
def compute_keyword_score(image: dict, keywords: list) -> float:
    """
    Calculate keyword match score from image metadata
    """
    image_text = " ".join([
        image.get("alt", ""),
        image.get("caption", ""),
        image.get("filename", ""),
        image.get("surrounding_text", "")
    ]).lower()
    
    matched = sum(1 for kw in keywords if kw.lower() in image_text)
    return min(1.0, matched / max(len(keywords), 1))
```

### 8.4 Trust Score (T) - 30%

| Tier | Score | Sources |
|------|-------|---------|
| S | 1.0 | Vogue, Elle, NYT, BBC, WSJ |
| A | 0.8 | BoF, WWD, TechCrunch, Hypebeast |
| B | 0.6 | Unsplash, Pexels (external APIs) |
| C | 0.4 | Unknown / Other sources |

```python
SOURCE_IMAGE_TRUST = {
    # Tier S - Fashion Authority
    "vogue.com": 1.0,
    "elle.com": 1.0,
    "harpersbazaar.com": 1.0,
    
    # Tier A - Industry Professional
    "businessoffashion.com": 0.8,
    "wwd.com": 0.8,
    "hypebeast.com": 0.8,
    
    # Tier B - External Image APIs
    "unsplash.com": 0.6,
    "pexels.com": 0.6,
    "pixabay.com": 0.6,
    
    # Default
    "default": 0.4
}
```

### 8.5 Quality Score (Q) - 20%

```python
def compute_quality_score(image: dict) -> float:
    """
    Check image quality based on resolution
    """
    width = image.get("width", 0)
    height = image.get("height", 0)
    
    # Minimum 800px on any dimension
    if width >= 800 or height >= 800:
        return 1.0
    elif width >= 400 or height >= 400:
        return 0.5
    else:
        return 0.0
```

### 8.6 MongoDB Schema / 資料庫結構

```javascript
// Topic Document with Image Structure
{
    "_id": ObjectId("..."),
    "title": "2026 巴黎時裝週：Valentino 春夏系列震撼登場",
    "category": "fashion",
    "status": "confirmed",
    
    // Source information
    "sources": [{
        "type": "rss",
        "name": "Vogue",
        "url": "https://www.vogue.com/article/valentino-2026",
        "images": [                    // Raw extracted images
            "https://vogue.com/img1.jpg",
            "https://vogue.com/img2.jpg"
        ]
    }],
    
    // NEW: Structured images field
    "images": {
        // Phase 5A: Immediate preview
        "preview": [
            "https://vogue.com/img1.jpg",
            "https://vogue.com/img2.jpg"
        ],
        
        // Phase 5B: Matched after generation
        "matched": [
            {
                "url": "https://vogue.com/img1.jpg",
                "score": 0.92,
                "score_breakdown": {
                    "keyword": 0.95,
                    "trust": 1.0,
                    "quality": 0.8
                },
                "caption": "Valentino Spring 2026 runway",
                "source": "source_article",
                "source_domain": "vogue.com",
                "matched_keywords": ["valentino", "runway", "spring"],
                "width": 1200,
                "height": 800
            },
            {
                "url": "https://images.unsplash.com/photo-paris-fashion.jpg",
                "score": 0.78,
                "score_breakdown": {
                    "keyword": 0.7,
                    "trust": 0.6,
                    "quality": 1.0
                },
                "caption": "Paris Fashion Week atmosphere",
                "source": "external",
                "source_domain": "unsplash.com",
                "matched_keywords": ["paris", "fashion"],
                "width": 1920,
                "height": 1080
            }
        ]
    },
    
    // Legacy field (backward compatibility)
    "preview_images": ["https://vogue.com/img1.jpg"]
}
```

### 8.7 External Search Fallback / 外部搜尋補充

```python
async def supplement_images_if_needed(
    topic_id: str,
    current_matched: list,
    target_count: int = 8
) -> list:
    """
    Search external APIs when matched images < target
    """
    if len(current_matched) >= target_count:
        return current_matched
    
    needed = target_count - len(current_matched)
    
    # Extract keywords from topic
    topic = await topic_repo.get_topic_by_id(topic_id)
    keywords = extract_keywords_from_content(topic)
    search_query = " ".join(keywords[:3])
    
    # Search external sources
    external_images = await image_service.search_images(
        keywords=search_query,
        limit=needed,
        sources=["unsplash", "pexels"]
    )
    
    # Add with trust score = 0.6 (Tier B)
    for img in external_images:
        matched_image = {
            "url": img["url"],
            "score": compute_image_score(img, keywords, trust=0.6),
            "caption": img.get("description", ""),
            "source": "external",
            "source_domain": extract_domain(img["url"]),
            "matched_keywords": find_matched_keywords(img, keywords)
        }
        current_matched.append(matched_image)
    
    # Sort by score and return top N
    current_matched.sort(key=lambda x: x["score"], reverse=True)
    return current_matched[:target_count]
```

### 8.8 Image Type Enum / 圖片類型列舉

```python
class ImageType(str, Enum):
    SOURCE = "source"        # From original article HTML
    PREVIEW = "preview"      # Phase 5A immediate preview
    MATCHED = "matched"      # Phase 5B matched by algorithm
    EXTERNAL = "external"    # From Unsplash/Pexels fallback
```

### 8.9 API Response Example / API 回應範例

```json
// GET /api/v1/topics/{topic_id}
{
    "id": "topic_fashion_202601221000_0",
    "title": "2026 巴黎時裝週：Valentino 春夏系列震撼登場",
    "category": "fashion",
    "images": {
        "preview": [
            "https://vogue.com/img1.jpg",
            "https://vogue.com/img2.jpg"
        ],
        "matched": [
            {
                "url": "https://vogue.com/img1.jpg",
                "score": 0.92,
                "caption": "Valentino runway"
            },
            {
                "url": "https://unsplash.com/photo.jpg",
                "score": 0.78,
                "caption": "Paris Fashion Week"
            }
        ]
    },
    "preview_images": ["https://vogue.com/img1.jpg"]
}
```

### 8.10 Implementation Files / 實作檔案

| File | Purpose |
|------|---------|
| `app/services/images/image_matcher.py` | Core matching service |
| `app/services/images/keyword_extractor.py` | Keyword extraction |
| `app/schemas/matched_image.py` | Data schemas |
| `app/services/automation/scheduler.py` | Phase 5A integration |
| `app/services/automation/workflow.py` | Phase 5B integration |

---

## 9. Summary / 總結

This technical specification covers:
1. **Article Scoring** - Rank articles by time, source, completeness, relevance
2. **Image Matching** - Two-phase design for guaranteed image display
3. **Health Monitoring** - Track feed status and auto-pause failures
4. **Rate Limiting** - Prevent IP blocking with domain-level controls
5. **Caching** - L1 memory + L2 MongoDB for performance

本技術規格涵蓋：
1. **文章評分** - 按時間、來源、完整度、相關度排序
2. **圖片匹配** - 兩階段設計確保圖片顯示
3. **健康監控** - 追蹤 Feed 狀態並自動暫停故障
4. **速率限制** - 域名級控制防止 IP 封鎖
5. **快取機制** - L1 記憶體 + L2 MongoDB 提升效能

---

End of Technical Specification
