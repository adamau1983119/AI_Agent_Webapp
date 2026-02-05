# Image Matching Logic Specification
# ???寥??摩閬

Version: v1.0
Date: 2026-01-22

---

## Overview / 璁膩

Two-phase image handling to ensure every topic card has photos while maintaining relevance.

?拚?畾萄?????蝣箔?瘥蜓憿???蒂靽??賊??扼?
---

## Phase 1: Article Link ??Basic Photos
## ?挾銝嚗?蝡?? ???箸?抒?

### Goal / ?格?
Ensure every topic card has at least one photo immediately after creation.
蝣箔?瘥蜓憿?遣蝡?蝡?撠?撘萇??
### Flow / 瘚?

`
TopicCollector          ArticleExtractor         Topic Document
      ??                      ??                      ??      ??1. Collect RSS        ??                      ??      ??????????????????????  ??                      ??      ??                      ??                      ??      ??2. For each article   ??                      ??      ??   with link          ??                      ??      ??????????????????????  ??                      ??      ??                      ??                      ??      ??  3. Fetch HTML       ??                      ??      ??  ????????????????    ??                      ??      ??                      ??                      ??      ??  4. Extract images:  ??                      ??      ??     - og:image       ??                      ??      ??     - twitter:image  ??                      ??      ??     - <img> tags     ??                      ??      ??  ???????????????     ??                      ??      ??                      ??                      ??      ??5. Store to           ??                      ??      ??   preview_images     ??                      ??      ????????????????????????????????????????????????嗯?
      ??                      ??                      ??`

### Implementation / 撖虫?

File: backend/app/services/automation/scheduler.py

`python
# BEFORE (Line 139):
topic_data["preview_images"] = []

# AFTER:
# Extract preview images from source
preview_images = []
for source in topic.get("sources", []):
    source_images = source.get("images", [])
    if source_images:
        preview_images.extend(source_images[:3])  # Max 3 per source
        
topic_data["preview_images"] = preview_images[:5]  # Max 5 total
`

### Acceptance Criteria / 撽璅?
- [ ] Every topic card displays at least 1 image after creation
- [ ] Images come from og:image, twitter:image, or <img> tags
- [ ] No external API calls required in Phase 1
- [ ] Topic creation time remains < 1 second per topic

---

## Phase 2: After Translation ??Photo Matching
## ?挾鈭?蝧餉陌??敺????抒??寥?

### Goal / ?格?
Match and rank photos by relevance, select 8-10 best images.
?寞??賊?摨血?????抒?嚗??8-10 撘菜?雿喳???
### Flow / 瘚?

`
Content Generated       Photo Matcher           Image Database
      ??                      ??                      ??      ??1. Extract keywords:  ??                      ??      ??   - Title            ??                      ??      ??   - Summary          ??                      ??      ??   - Names/Brands     ??                      ??      ??????????????????????  ??                      ??      ??                      ??                      ??      ??  2. Score preview    ??                      ??      ??     images:          ??                      ??      ??     - Keyword match  ??                      ??      ??     - Source trust   ??                      ??      ??     - Image quality  ??                      ??      ??  ???????????????     ??                      ??      ??                      ??                      ??      ??  3. If preview < 8:  ??                      ??      ??     Search external  ??                      ??      ??  ??????????????????????????????????????????? ??      ??                      ??                      ??      ??  4. Merge & rank     ??                      ??      ??  ????????????????    ??                      ??      ??                      ??                      ??      ??5. Save top 8-10 to   ??                      ??      ??   images.matched[]   ??                      ??      ??????????????????????????                      ??`

### Image Relevance Score / ???賊?摨血???
Formula: ImageScore = 0.5 * K + 0.3 * T + 0.2 * Q

| Dimension | Weight | Description | Range |
|-----------|--------|-------------|-------|
| K (Keyword Match) | 50% | Keywords in alt/caption/filename | 0-1 |
| T (Source Trust) | 30% | Source credibility tier | 0-1 |
| Q (Quality) | 20% | Resolution >= 800px, aspect ratio | 0-1 |

### Keyword Matching Logic / ?閰??頛?
`python
def compute_keyword_score(image: dict, keywords: list) -> float:
    score = 0.0
    image_text = " ".join([
        image.get("alt", ""),
        image.get("caption", ""),
        image.get("filename", ""),
        image.get("surrounding_text", "")
    ]).lower()
    
    matched = sum(1 for kw in keywords if kw.lower() in image_text)
    return min(1.0, matched / max(len(keywords), 1))
`

### Source Trust Tiers / 靘?靽∩遙蝑?

| Tier | Trust Score | Sources |
|------|-------------|---------|
| S | 1.0 | Vogue, Elle, NYT, BBC |
| A | 0.8 | BoF, WWD, Hypebeast |
| B | 0.6 | Unsplash, Pexels (external) |
| C | 0.4 | Unknown sources |

### Fallback to External Search / 憭??鋆?

Trigger: When matched images < 8

`python
async def supplement_images(topic_id: str, current_count: int, target: int = 8):
    if current_count >= target:
        return
    
    needed = target - current_count
    keywords = extract_keywords_from_content(topic_id)
    
    # Search external sources
    external_images = await image_service.search_images(
        keywords=" ".join(keywords[:3]),
        limit=needed
    )
    
    # Add with lower trust score
    for img in external_images:
        img["source_trust"] = 0.6  # External = Tier B
        await save_matched_image(topic_id, img)
`

---

## Data Model / 鞈?璅∪?

### MongoDB Schema

`javascript
// Topic Document
{
  "_id": ObjectId("..."),
  "title": "2026 撌湧????梧?Valentino ?亙?蝟餃???餃",
  "category": "fashion",
  
  // Source information (from ArticleExtractor)
  "sources": [{
    "type": "rss",
    "name": "Vogue",
    "url": "https://www.vogue.com/article/valentino-2026-spring-summer",
    "images": [
      "https://vogue.com/img1.jpg",
      "https://vogue.com/img2.jpg"
    ]
  }],
  
  // Images structure
  "images": {
    // Phase 1: Immediate preview (from source)
    "preview": [
      "https://vogue.com/img1.jpg",
      "https://vogue.com/img2.jpg"
    ],
    
    // Phase 2: Matched after generation
    "matched": [
      {
        "url": "https://vogue.com/img1.jpg",
        "score": 0.92,
        "score_breakdown": {
          "keyword": 0.95,
          "trust": 1.0,
          "quality": 0.8
        },
        "caption": "Valentino runway show",
        "source": "source_article",
        "matched_keywords": ["valentino", "runway", "fashion week"]
      },
      {
        "url": "https://unsplash.com/photo-paris-fashion.jpg",
        "score": 0.78,
        "score_breakdown": {
          "keyword": 0.7,
          "trust": 0.6,
          "quality": 1.0
        },
        "caption": "Paris Fashion Week atmosphere",
        "source": "unsplash",
        "matched_keywords": ["paris", "fashion"]
      }
    ]
  },
  
  // Legacy field (for backward compatibility)
  "preview_images": ["https://vogue.com/img1.jpg"]
}
`

### Image Types / ??憿?

`python
class ImageType(str, Enum):
    SOURCE = "source"      # From original article
    MATCHED = "matched"    # Matched by algorithm
    EXTERNAL = "external"  # From external search (Unsplash, Pexels)
    PREVIEW = "preview"    # Initial preview (Phase 1)
`

---

## Implementation Checklist / 撖行瑼Ｘ皜

### Phase 1 Changes

- [ ] scheduler.py: Extract source images to preview_images
- [ ] topic_collector.py: Ensure ArticleExtractor runs for all articles
- [ ] article_extractor.py: Improve image extraction (add fallback)
- [ ] Frontend: Display preview_images immediately

### Phase 2 Changes

- [ ] New: app/services/images/image_matcher.py
- [ ] New: app/services/images/keyword_extractor.py
- [ ] Modify: workflow.py - Add Phase 2 matching after content generation
- [ ] Modify: image_repository.py - Support images.matched structure

### Tests

- [ ] test_phase1_preview: Topic has preview_images after creation
- [ ] test_phase2_matching: images.matched populated after generation
- [ ] test_fallback_search: External search when preview < 8
- [ ] test_score_calculation: Image scores calculated correctly

---

## Expected Results / ????

| Metric | Before | After |
|--------|--------|-------|
| Cards with images (creation) | ~30% | 100% |
| Cards with 8+ images (after gen) | ~60% | 95%+ |
| Image-content relevance | Low | High |
| Image source traceability | None | Full |

---

End of Image Matching Logic Specification
