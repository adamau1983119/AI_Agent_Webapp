# TopicCollector Implementation Checklist

Version: v1.0 | Date: 2026-01-22

---

## Phase 1: Core Scoring Function

### 1.1 Preparation
- [ ] Confirm current Git branch
- [ ] Create branch: feature/topic-collector-improvement
- [ ] Backup existing topic_collector.py
- [ ] Confirm backend service starts normally
- [ ] Confirm MongoDB connection works

### 1.2 New Files to Create

app/config/feed_config.py:
- [ ] SCORING_CONFIG (weights: time 0.4, source 0.3, completeness 0.2, relevance 0.1)
- [ ] SOURCE_WEIGHTS (72 sources with tiers S/A/B/C/D)
- [ ] CATEGORY_KEYWORDS (fashion, food, trend)
- [ ] RATE_LIMIT_CONFIG (global and per-domain limits)
- [ ] FEATURE_FLAGS (rollback switches)

app/services/scoring_service.py:
- [ ] ScoringService class
- [ ] compute_score(article, category) -> dict
- [ ] _compute_time_score(article) -> float
- [ ] _compute_source_score(article) -> float
- [ ] _compute_completeness_score(article) -> float
- [ ] _compute_relevance_score(article, category) -> float
- [ ] update_weights(new_weights) -> None

app/services/cache_manager.py:
- [ ] CacheManager class
- [ ] get(url) -> dict or None
- [ ] set(url, data) -> None
- [ ] _set_memory(url, data) with LRU
- [ ] clear() -> None

app/services/rate_limiter.py:
- [ ] RateLimiter class
- [ ] acquire(url) -> awaitable
- [ ] release(url) -> None
- [ ] _get_domain(url) -> str
- [ ] _get_domain_config(domain) -> dict

### 1.3 Files to Modify

app/services/automation/topic_collector.py:
- [ ] Keep _collect_topics_legacy() (old logic for rollback)
- [ ] Add _collect_topics_v2() (new logic with scoring)
- [ ] Integrate ScoringService
- [ ] Integrate CacheManager
- [ ] Integrate RateLimiter
- [ ] Integrate FEATURE_FLAGS
- [ ] Add timeout handling to fetch_feed()
- [ ] Add _deduplicate() method
- [ ] Add _filter_recent(hours=48) method

app/models/topic.py:
- [ ] Add score: Optional[float] = None
- [ ] Add score_breakdown: Optional[Dict[str, float]] = None

app/schemas/topic.py:
- [ ] TopicResponse add score field
- [ ] TopicResponse add score_breakdown field

### 1.4 Unit Tests
tests/test_scoring_service.py:
- [ ] test_compute_score_new_article (< 1 hour should score > 0.8)
- [ ] test_compute_score_old_article (> 48 hours should score low)
- [ ] test_source_weight_tier_s (Vogue should get 1.0)
- [ ] test_source_weight_unknown (unknown source gets 0.5)
- [ ] test_completeness_with_image (+0.5)
- [ ] test_completeness_with_summary (+0.5)
- [ ] test_relevance_keyword_match (match = 1.0)
- [ ] test_update_weights (dynamic update works)

tests/test_cache_manager.py:
- [ ] test_memory_cache_hit
- [ ] test_memory_cache_miss
- [ ] test_cache_expiry (after 10 min)
- [ ] test_lru_eviction (when max size reached)

tests/test_rate_limiter.py:
- [ ] test_global_concurrency_limit (max 10)
- [ ] test_domain_concurrency_limit (max 2 per domain)
- [ ] test_domain_interval (min 12 seconds)
- [ ] test_requests_per_minute (max 5 per domain)

### 1.5 Integration Tests
- [ ] Service startup < 10 seconds
- [ ] Each article has score field (0-1)
- [ ] Each category returns exactly 10 articles
- [ ] Results sorted by score descending
- [ ] Single Feed timeout doesn't affect others
- [ ] Feature flag toggle works

### 1.6 Git Commits for Phase 1
- [ ] feat: add feed_config module with scoring weights
- [ ] feat: add scoring_service for article scoring
- [ ] feat: add cache_manager with LRU eviction
- [ ] feat: add rate_limiter with domain-level limits
- [ ] refactor: update topic_collector with scoring
- [ ] feat: add score fields to topic model
- [ ] test: add unit tests for phase 1 modules

---

## Phase 2: Cache and Persistence

### 2.1 Preparation
- [ ] All Phase 1 tests pass
- [ ] MongoDB writable
- [ ] Redis connection works (if using)

### 2.2 New Files

app/services/repositories/feed_state_repository.py:
- [ ] FeedStateRepository class
- [ ] get_feed_state(url) -> dict
- [ ] get_all_feed_states() -> list
- [ ] get_feed_states_by_category(category) -> list
- [ ] update_feed_state(url, data) -> None
- [ ] track_success(url) -> None
- [ ] track_failure(url, error) -> None
- [ ] pause_feed(url, duration) -> None
- [ ] resume_feed(url) -> None
- [ ] get_active_feeds(category) -> list
- [ ] should_skip(url) -> bool

app/services/feed_health_service.py:
- [ ] FeedHealthService class
- [ ] calculate_health_score(metrics) -> int (0-100)
- [ ] get_health_status(score) -> str
- [ ] check_auto_pause(url) -> bool
- [ ] check_auto_resume(url) -> bool
- [ ] get_stats_summary() -> dict

### 2.3 Modify Files

app/services/cache_manager.py:
- [ ] Add L2 MongoDB persistent cache
- [ ] Modify get() for L2 query
- [ ] Modify set() for L2 write

app/services/automation/topic_collector.py:
- [ ] Integrate FeedStateRepository
- [ ] Integrate FeedHealthService
- [ ] Update state after fetch_feed()
- [ ] Filter paused Feeds before collection

app/database.py:
- [ ] Add feed_states collection
- [ ] Add feed_cache collection
- [ ] Create indexes

### 2.4 Database Operations
- [ ] Create feed_states collection
- [ ] Create feed_cache collection
- [ ] Index: feed_states.feed_url (unique)
- [ ] Index: feed_states.category
- [ ] Index: feed_states.status
- [ ] Index: feed_states.pause_until
- [ ] Index: feed_cache.feed_url (unique)
- [ ] TTL Index: feed_cache.expires_at
- [ ] Initialize 72 Feed state records

### 2.5 Tests for Phase 2
- [ ] test_get_feed_state
- [ ] test_track_success (updates stats)
- [ ] test_track_failure (increments counter)
- [ ] test_consecutive_failures (counts correctly)
- [ ] test_pause_feed (status changes)
- [ ] test_resume_feed (clears pause)
- [ ] test_should_skip_paused (returns true)
- [ ] test_health_score_healthy (>= 80)
- [ ] test_health_score_degraded (50-79)
- [ ] test_auto_pause_trigger (3 failures)
- [ ] test_auto_resume_trigger (time expired)
- [ ] test_mongodb_cache_write
- [ ] test_mongodb_cache_read
- [ ] test_cache_recovery_after_restart

### 2.6 Git Commits for Phase 2
- [ ] feat: add feed_state_repository
- [ ] feat: add feed_health_service
- [ ] feat: add L2 persistent cache
- [ ] feat: add feed_states collection
- [ ] refactor: integrate persistence into collector
- [ ] test: add unit tests for phase 2

---

## Phase 3: Health Monitoring API

### 3.1 Preparation
- [ ] All Phase 2 tests pass
- [ ] feed_states collection exists
- [ ] Initial Feed state data populated

### 3.2 New Files

app/api/v1/feeds.py:
- [ ] GET /feeds/health (all Feeds health)
- [ ] GET /feeds/health/{category} (by category)
- [ ] GET /feeds/stats (statistics summary)
- [ ] POST /feeds/{feed_id}/pause (manual pause)
- [ ] POST /feeds/{feed_id}/resume (manual resume)
- [ ] GET /feeds/scoring/config (get config)
- [ ] PUT /feeds/scoring/weights (update weights)
- [ ] POST /feeds/rollback/{feature} (toggle flag)
- [ ] POST /feeds/rollback/emergency (emergency rollback)

app/schemas/feed.py:
- [ ] FeedHealthResponse schema
- [ ] FeedStatsResponse schema
- [ ] FeedPauseRequest schema
- [ ] ScoringWeightsUpdate schema

### 3.3 Modify Files

app/main.py:
- [ ] Import feeds router
- [ ] app.include_router(feeds.router, prefix="/api/v1")

app/api/v1/__init__.py:
- [ ] Add feeds export

### 3.4 API Tests

GET /feeds/health:
- [ ] Returns 72 total Feeds
- [ ] Each has health_score (0-100)
- [ ] Each has health_status (healthy/degraded/unhealthy/paused)
- [ ] Includes summary statistics

GET /feeds/health/fashion:
- [ ] Returns 23 Feeds
- [ ] All are fashion category

GET /feeds/stats:
- [ ] Has overview section
- [ ] Has by_category section

POST /feeds/{id}/pause:
- [ ] Status becomes paused
- [ ] Returns updated state

POST /feeds/{id}/resume:
- [ ] Status becomes active
- [ ] pause_until cleared

GET /feeds/scoring/config:
- [ ] Returns current weights
- [ ] Returns source_weights

PUT /feeds/scoring/weights:
- [ ] Weights update successfully
- [ ] Takes effect immediately

POST /feeds/rollback/emergency:
- [ ] use_legacy_collector = True
- [ ] Subsequent collections use legacy logic

### 3.5 Git Commits for Phase 3
- [ ] feat: add feeds health API endpoints
- [ ] feat: add feed schemas
- [ ] chore: register feeds router in main
- [ ] test: add API tests for feeds endpoints
- [ ] docs: update API documentation

---

## Phase 4: Config Externalization (Optional)

### 4.1 Option A: YAML Config
- [ ] config/feeds.yaml (72 feed URLs with weights)
- [ ] config/scoring.yaml (weights and keywords)
- [ ] app/config/config_loader.py (load and reload)

### 4.2 Option B: MongoDB Config
- [ ] feed_configs collection
- [ ] scoring_configs collection
- [ ] Config management API

### 4.3 Git Commits for Phase 4
- [ ] feat: externalize feed configuration
- [ ] feat: add config_loader module
- [ ] refactor: load feeds from external config

---

## Phase 5: Image Matching Logic (NEW)

### 5.1 Phase 5A - Immediate Preview / 即時預覽

#### Goal / 目標
Every topic card has at least 1 photo immediately after creation.
每個主題卡片建立後立即有至少 1 張照片。

#### Preparation
- [ ] Confirm ArticleExtractor extracts images correctly
- [ ] Confirm sources[].images field is populated
- [ ] Backup current scheduler.py

#### File Changes

app/services/automation/scheduler.py:
- [ ] Line ~139: Remove `preview_images = []`
- [ ] Add logic to extract images from sources[].images
- [ ] Set preview_images = first 3-5 source images
- [ ] Add fallback to empty array if no images

Code Change:
```python
# BEFORE:
topic_data["preview_images"] = []

# AFTER:
preview_images = []
for source in topic.get("sources", []):
    source_imgs = source.get("images", [])
    preview_images.extend(source_imgs[:3])
topic_data["preview_images"] = preview_images[:5] if preview_images else []
```

#### Tests
- [ ] test_topic_has_preview_images_after_creation
- [ ] test_preview_from_og_image
- [ ] test_preview_from_img_tags
- [ ] test_preview_fallback_empty
- [ ] test_no_performance_impact (< 1s per topic)

#### Acceptance
- [ ] 100% of topics have preview_images (if source has images)
- [ ] Topic creation time unchanged (< 1s)
- [ ] Frontend displays preview immediately

---

### 5.2 Phase 5B - Smart Matching / 智能匹配

#### Goal / 目標
Match photos by relevance after content generation, select 8-10 best images.
內容生成後根據相關度匹配照片，選出 8-10 張最佳圖片。

#### New Files

app/services/images/image_matcher.py:
- [ ] ImageMatcher class
- [ ] match_images(topic_id, content) -> List[MatchedImage]
- [ ] _extract_keywords(content) -> List[str]
- [ ] _compute_keyword_score(image, keywords) -> float
- [ ] _compute_trust_score(source) -> float
- [ ] _compute_quality_score(image) -> float
- [ ] _compute_total_score(image, keywords) -> float

app/services/images/keyword_extractor.py:
- [ ] KeywordExtractor class
- [ ] extract_from_title(title) -> List[str]
- [ ] extract_from_summary(summary) -> List[str]
- [ ] extract_entities(text) -> List[str] (names, brands, places)

app/schemas/matched_image.py:
- [ ] MatchedImage schema (url, score, score_breakdown, caption)
- [ ] ImageMatchResult schema

#### Modified Files

app/models/topic.py:
- [ ] Add images field with nested structure:
  - images.preview: List[str]
  - images.matched: List[MatchedImage]

app/services/automation/workflow.py:
- [ ] Import ImageMatcher
- [ ] After content generation: call image_matcher.match_images()
- [ ] Update topic with images.matched

app/services/repositories/topic_repository.py:
- [ ] Add update_matched_images(topic_id, images)
- [ ] Support nested images structure

#### Score Formula
ImageScore = 0.5 * K + 0.3 * T + 0.2 * Q

| Dimension | Weight | Description |
|-----------|--------|-------------|
| K (Keyword) | 50% | alt/caption/filename keyword match |
| T (Trust) | 30% | Source credibility tier |
| Q (Quality) | 20% | Resolution >= 800px |

#### Trust Tiers
- [ ] Tier S (1.0): Vogue, Elle, NYT, BBC
- [ ] Tier A (0.8): BoF, WWD, Hypebeast
- [ ] Tier B (0.6): Unsplash, Pexels (external)
- [ ] Tier C (0.4): Unknown sources

#### External Search Fallback
- [ ] Trigger when matched < 8 images
- [ ] Search Unsplash/Pexels with top 3 keywords
- [ ] Add external images with trust = 0.6
- [ ] Mark source as 'external'

#### Tests
- [ ] test_keyword_extraction
- [ ] test_score_calculation
- [ ] test_match_from_preview
- [ ] test_external_fallback_trigger
- [ ] test_top_10_selection
- [ ] test_score_sorting_desc

#### Acceptance
- [ ] images.matched has 8-10 items (95%+ of topics)
- [ ] Images sorted by score descending
- [ ] Each image has score and caption
- [ ] External search used only when preview < 8

---

### 5.3 MongoDB Schema Update

#### New Structure
```javascript
{
  "sources": [{
    "images": ["url1", "url2"]  // Raw extracted from article
  }],
  "images": {
    "preview": ["url1", "url2"],  // Phase 5A: Immediate
    "matched": [                   // Phase 5B: After generation
      {
        "url": "url1",
        "score": 0.92,
        "score_breakdown": { "keyword": 0.95, "trust": 1.0, "quality": 0.8 },
        "caption": "Valentino runway",
        "source": "source_article",
        "matched_keywords": ["valentino", "runway"]
      }
    ]
  },
  "preview_images": ["url1"]  // Legacy field (backward compatible)
}
```

#### Migration Tasks
- [ ] Add images field to existing topics
- [ ] Copy preview_images to images.preview
- [ ] Set images.matched = [] initially
- [ ] Keep preview_images for backward compatibility

---

### 5.4 Frontend Updates (Optional)

TopicCard.tsx:
- [ ] Display images.preview[0] as card thumbnail
- [ ] Show placeholder if no images
- [ ] No blank cards allowed

TopicDetail.tsx:
- [ ] Display images.matched[] in gallery
- [ ] Show score badge on hover
- [ ] Fallback to preview if matched empty

---

### 5.5 Git Commits for Phase 5
- [ ] feat: extract preview_images from source in scheduler
- [ ] feat: add ImageMatcher service
- [ ] feat: add KeywordExtractor service
- [ ] feat: add matched image schema
- [ ] refactor: update topic model with images structure
- [ ] feat: integrate matching into workflow
- [ ] feat: add external search fallback
- [ ] test: add image matching tests
- [ ] docs: update API documentation

---

### 5.6 Expected Results

| Metric | Before | After |
|--------|--------|-------|
| Cards with images (creation) | ~30% | 100% |
| Cards with 8+ images (after gen) | ~60% | 95%+ |
| Image-content relevance | Low | High |
| Image source traceability | None | Full |

---

### 5.7 Sign-off

| Sub-Phase | Date | Executor | Reviewer |
|-----------|------|----------|----------|
| 5A Immediate Preview | | | |
| 5B Smart Matching | | | |
| 5.3 Schema Update | | | |
| Phase 5 Complete | | | |

---

## Final Acceptance Checklist

### Pre-Acceptance
- [ ] All Phase checklists completed
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Code reviewed
- [ ] Documentation updated
- [ ] Git branch organized

### Functional Acceptance

| ID | Item | Criteria | Pass |
|----|------|----------|------|
| AC-01 | Startup | < 10 seconds | [ ] |
| AC-02 | Scoring | Has score field | [ ] |
| AC-03 | Top 10 | Returns 10/category | [ ] |
| AC-04 | Timeout | Single timeout OK | [ ] |
| AC-05 | Cache | Uses within 10 min | [ ] |
| AC-06 | Health API | Returns metrics | [ ] |
| AC-07 | Config | Weights adjustable | [ ] |
| AC-08 | L2 Cache | Survives restart | [ ] |
| AC-09 | Rate Limit | 12s domain interval | [ ] |
| AC-10 | Rollback | One-click legacy | [ ] |
| AC-11 | Preview Images | Every card has image | [ ] |
| AC-12 | Matched Images | 8-10 after generation | [ ] |
| AC-13 | Image Scoring | Has score + caption | [ ] |

### Performance Acceptance

| ID | Metric | Target | Actual | Pass |
|----|--------|--------|--------|------|
| PC-01 | Startup | < 10s | _____ | [ ] |
| PC-02 | Collect | < 60s | _____ | [ ] |
| PC-03 | API | < 3s | _____ | [ ] |
| PC-04 | Memory | < 100MB | _____ | [ ] |

### Merge and Deploy
- [ ] Create Pull Request
- [ ] Code Review passed
- [ ] CI tests passed
- [ ] Squash Merge to main
- [ ] Tag version
- [ ] Deploy to staging
- [ ] Staging test passed
- [ ] Deploy to production
- [ ] Production verification
- [ ] Update CHANGELOG

---

## Sign-off

| Phase | Date | Executor | Reviewer |
|-------|------|----------|----------|
| Phase 1 | | | |
| Phase 2 | | | |
| Phase 3 | | | |
| Phase 4 | | | |
| Phase 5 | | | |
| Final | | | |

---

End of Checklist
