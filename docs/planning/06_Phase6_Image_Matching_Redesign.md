# Phase 6：圖片匹配系統重構

## 📋 概述

### 目標
重構圖片匹配系統，解決三大痛點：
1. 關鍵字提取不準確（太泛泛）
2. 返回圖片經常是 0 張
3. 匹配出來的圖片與文章內容不相關

### 核心改進
- 建立 `articles` + `photos` 雙 Collection 結構
- 從 RSS Feed 提取原文照片
- 使用 hashtags + photo_index.keywords 進行匹配
- MongoDB 聚合查詢實現高效匹配

### 預估時間
- 總計：5-6 小時
- 分 8 個子階段實施

---

## 🏗️ 架構設計

### 數據流程圖

```
┌─────────────────────────────────────────────────────────────┐
│                      Phase 6 架構                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  RSS Feed                                                   │
│      │                                                      │
│      ▼                                                      │
│  TopicCollector                                             │
│      │                                                      │
│      ├─→ OriginalImageExtractor → 提取原文照片              │
│      │         │                                            │
│      │         ▼                                            │
│      │   photos Collection ← 存入照片索引                   │
│      │                                                      │
│      ├─→ HashtagExtractor → 提取 hashtags                   │
│      │     │                                                │
│      │     ├─→ 正則提取（品牌、專有名詞）                    │
│      │     └─→ AI 生成（語義主題詞）                        │
│      │                                                      │
│      └─→ articles Collection ← 存入文章                     │
│                │                                            │
│                ▼                                            │
│      ImageMatchingService                                   │
│                │                                            │
│                └─→ MongoDB 聚合查詢                         │
│                         │                                   │
│                         ▼                                   │
│                   images.matched[]                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Collection 結構

#### articles Collection
```json
{
  "article_id": "A20260123-001",
  "title": "Valentino 在巴黎時裝週發表新系列",
  "original_title": "Valentino Presents New Collection at Paris Fashion Week",
  "description": "...",
  "content": "...",
  "link": "https://vogue.com/article/...",
  "source": "Vogue",
  "category": "fashion",
  "hashtags": ["Valentino", "ParisFashionWeek", "Runway", "Spring2026"],
  "images": {
    "preview": [
      {
        "photo_id": "P1001",
        "url": "https://vogue.com/img1.jpg",
        "thumbnail_url": "https://vogue.com/img1_thumb.jpg",
        "caption": "Valentino runway look"
      }
    ],
    "matched": []
  },
  "published_at": "2026-01-23T10:00:00Z",
  "collected_at": "2026-01-23T12:00:00Z",
  "score": 0.85,
  "legacy_topic_id": "ObjectId(...)"
}
```

#### photos Collection
```json
{
  "photo_id": "P1001",
  "keywords": ["Valentino", "Paris Fashion Week", "runway", "fashion show"],
  "source_url": "https://vogue.com/img1.jpg",
  "thumbnail_url": "https://vogue.com/img1_thumb.jpg",
  "caption": "Valentino Spring 2026 Collection",
  "article_id": "A20260123-001",
  "source": "Vogue",
  "quality_score": 0.9,
  "width": 1920,
  "height": 1080,
  "created_at": "2026-01-23T12:00:00Z"
}
```

---

## 📝 工作內容明細

### Phase 6.1：數據模型設計
| 編號 | 任務 | 文件路徑 | 說明 |
|------|------|----------|------|
| 6.1.1 | 設計 Article 模型 | `backend/app/models/article.py` | 新文章結構，包含 images.preview/matched |
| 6.1.2 | 設計 Photo 模型 | `backend/app/models/photo.py` | 照片索引結構 |
| 6.1.3 | 設計 ImagePreview 模型 | `backend/app/models/article.py` | 原文照片子結構 |
| 6.1.4 | 設計 ImageMatched 模型 | `backend/app/models/article.py` | 匹配照片子結構 |
| 6.1.5 | 更新 __init__.py | `backend/app/models/__init__.py` | 導出新模型 |

### Phase 6.2：Repository 層
| 編號 | 任務 | 文件路徑 | 說明 |
|------|------|----------|------|
| 6.2.1 | 建立 ArticleRepository | `backend/app/services/repositories/article_repository.py` | 文章 CRUD |
| 6.2.2 | 建立 PhotoRepository | `backend/app/services/repositories/photo_repository.py` | 照片索引 CRUD |
| 6.2.3 | 實現 create_article() | `article_repository.py` | 創建文章 |
| 6.2.4 | 實現 get_by_id() | `article_repository.py` | 根據 ID 獲取 |
| 6.2.5 | 實現 get_by_category() | `article_repository.py` | 根據分類獲取 |
| 6.2.6 | 實現 create_photo() | `photo_repository.py` | 創建照片索引 |
| 6.2.7 | 實現 find_by_keywords() | `photo_repository.py` | 根據關鍵字查找 |
| 6.2.8 | 實現 get_by_article_id() | `photo_repository.py` | 獲取文章的照片 |

### Phase 6.3：雙寫機制
| 編號 | 任務 | 文件路徑 | 說明 |
|------|------|----------|------|
| 6.3.1 | 建立 DualWriteService | `backend/app/services/migration/dual_write.py` | 雙寫服務 |
| 6.3.2 | 實現 write_article() | `dual_write.py` | 同時寫入 articles + topics |
| 6.3.3 | 實現 migrate_topic() | `dual_write.py` | 單筆遷移 |
| 6.3.4 | 建立遷移腳本 | `backend/scripts/migrate_topics_to_articles.py` | 批量遷移腳本 |
| 6.3.5 | 實現回滾機制 | `dual_write.py` | 遷移失敗時回滾 |

### Phase 6.4：原文照片提取
| 編號 | 任務 | 文件路徑 | 說明 |
|------|------|----------|------|
| 6.4.1 | 建立 OriginalImageExtractor | `backend/app/services/automation/image_extractor.py` | 原文照片提取器 |
| 6.4.2 | 實現 extract_from_entry() | `image_extractor.py` | 從 RSS entry 提取 |
| 6.4.3 | 實現 _extract_media_content() | `image_extractor.py` | 提取 media_content |
| 6.4.4 | 實現 _extract_media_thumbnail() | `image_extractor.py` | 提取 media_thumbnail |
| 6.4.5 | 實現 _extract_enclosures() | `image_extractor.py` | 提取 enclosures |
| 6.4.6 | 實現 _extract_from_html() | `image_extractor.py` | 從 HTML 提取 <img> |
| 6.4.7 | 實現 _deduplicate() | `image_extractor.py` | 去重 |
| 6.4.8 | 實現 generate_photo_id() | `image_extractor.py` | 生成唯一 photo_id |

### Phase 6.5：Hashtag 提取器
| 編號 | 任務 | 文件路徑 | 說明 |
|------|------|----------|------|
| 6.5.1 | 建立 HashtagExtractor | `backend/app/services/hashtag_extractor.py` | Hashtag 提取器 |
| 6.5.2 | 實現 extract() | `hashtag_extractor.py` | 主提取方法 |
| 6.5.3 | 實現 _extract_by_regex() | `hashtag_extractor.py` | 正則提取 |
| 6.5.4 | 實現 _extract_existing_hashtags() | `hashtag_extractor.py` | 提取已有 #tag |
| 6.5.5 | 實現 _extract_proper_nouns() | `hashtag_extractor.py` | 提取專有名詞 |
| 6.5.6 | 實現 _extract_brands() | `hashtag_extractor.py` | 提取品牌名稱 |
| 6.5.7 | 實現 _extract_by_ai() | `hashtag_extractor.py` | AI 生成 |
| 6.5.8 | 實現 _filter_and_dedupe() | `hashtag_extractor.py` | 過濾和去重 |
| 6.5.9 | 定義品牌列表 | `backend/app/config/brands.py` | 品牌名稱配置 |

### Phase 6.6：聚合查詢服務
| 編號 | 任務 | 文件路徑 | 說明 |
|------|------|----------|------|
| 6.6.1 | 建立 ImageMatchingService | `backend/app/services/image_matching_service.py` | 圖片匹配服務 |
| 6.6.2 | 實現 get_matched_images() | `image_matching_service.py` | 獲取匹配圖片 |
| 6.6.3 | 實現 _build_aggregation_pipeline() | `image_matching_service.py` | 構建聚合管道 |
| 6.6.4 | 實現 _calculate_score() | `image_matching_service.py` | 計算匹配分數 |
| 6.6.5 | 實現 update_matched_images() | `image_matching_service.py` | 更新文章的匹配圖片 |
| 6.6.6 | 實現 batch_match() | `image_matching_service.py` | 批量匹配 |

### Phase 6.7：API 端點
| 編號 | 任務 | 文件路徑 | 說明 |
|------|------|----------|------|
| 6.7.1 | 建立 articles router | `backend/app/api/v1/articles.py` | 文章 API |
| 6.7.2 | GET /articles | `articles.py` | 獲取文章列表 |
| 6.7.3 | GET /articles/{id} | `articles.py` | 獲取單篇文章 |
| 6.7.4 | GET /articles/{id}/matched-images | `articles.py` | 獲取匹配圖片 |
| 6.7.5 | POST /articles/{id}/refresh-images | `articles.py` | 重新匹配圖片 |
| 6.7.6 | 註冊 router | `backend/app/main.py` | 註冊到 app |
| 6.7.7 | 更新 topics router | `backend/app/api/v1/topics.py` | 兼容舊 API |

### Phase 6.8：整合與測試
| 編號 | 任務 | 文件路徑 | 說明 |
|------|------|----------|------|
| 6.8.1 | 修改 TopicCollector | `backend/app/services/automation/topic_collector.py` | 整合新流程 |
| 6.8.2 | 整合 OriginalImageExtractor | `topic_collector.py` | 提取原文照片 |
| 6.8.3 | 整合 HashtagExtractor | `topic_collector.py` | 提取 hashtags |
| 6.8.4 | 整合 DualWriteService | `topic_collector.py` | 雙寫機制 |
| 6.8.5 | 建立測試文件 | `backend/tests/test_phase6_*.py` | 單元測試 |
| 6.8.6 | 建立整合測試 | `backend/tests/test_phase6_integration.py` | 整合測試 |

---

## ✅ 檢查列表

### Phase 6.1 檢查項
- [ ] Article 模型包含所有必要欄位
- [ ] Photo 模型包含所有必要欄位
- [ ] ImagePreview 和 ImageMatched 結構正確
- [ ] 模型已正確導出
- [ ] Pydantic 驗證正常工作

### Phase 6.2 檢查項
- [ ] ArticleRepository 可正確連接 MongoDB
- [ ] PhotoRepository 可正確連接 MongoDB
- [ ] CRUD 操作正常工作
- [ ] 查詢方法返回正確格式
- [ ] 錯誤處理完善

### Phase 6.3 檢查項
- [ ] 雙寫機制同時寫入 articles 和 topics
- [ ] 遷移腳本可正確執行
- [ ] 回滾機制正常工作
- [ ] 數據一致性檢查通過
- [ ] 遷移日誌記錄完整

### Phase 6.4 檢查項
- [ ] 可從 media_content 提取圖片
- [ ] 可從 media_thumbnail 提取圖片
- [ ] 可從 enclosures 提取圖片
- [ ] 可從 HTML 內容提取 <img>
- [ ] 去重邏輯正確
- [ ] photo_id 生成唯一

### Phase 6.5 檢查項
- [ ] 正則提取可識別專有名詞
- [ ] 正則提取可識別品牌名稱
- [ ] AI 生成返回合理的 hashtags
- [ ] 過濾和去重正常工作
- [ ] 停用詞列表完整
- [ ] 錯誤處理（AI 失敗時降級）

### Phase 6.6 檢查項
- [ ] 聚合管道正確構建
- [ ] $lookup 正確關聯 photos
- [ ] 關鍵字合併邏輯正確
- [ ] 分數計算公式正確
- [ ] 排序和限制數量正確
- [ ] 性能可接受（< 500ms）

### Phase 6.7 檢查項
- [ ] API 端點可正常訪問
- [ ] 返回格式符合規範
- [ ] 錯誤處理完善
- [ ] 與舊 API 兼容
- [ ] API 文檔更新

### Phase 6.8 檢查項
- [ ] TopicCollector 整合完成
- [ ] 完整流程可正常運行
- [ ] 所有測試通過
- [ ] 性能測試通過
- [ ] 日誌記錄完整

---

## 🧪 測試列表

### 6.1 數據模型測試 (`test_phase6_models.py`)
| 測試編號 | 測試名稱 | 測試內容 |
|----------|----------|----------|
| T6.1.1 | test_article_model_creation | 測試 Article 模型創建 |
| T6.1.2 | test_article_model_validation | 測試 Article 欄位驗證 |
| T6.1.3 | test_article_model_defaults | 測試 Article 預設值 |
| T6.1.4 | test_photo_model_creation | 測試 Photo 模型創建 |
| T6.1.5 | test_photo_model_validation | 測試 Photo 欄位驗證 |
| T6.1.6 | test_image_preview_structure | 測試 ImagePreview 結構 |
| T6.1.7 | test_image_matched_structure | 測試 ImageMatched 結構 |
| T6.1.8 | test_article_to_dict | 測試 Article.dict() 輸出 |

### 6.2 Repository 測試 (`test_phase6_repositories.py`)
| 測試編號 | 測試名稱 | 測試內容 |
|----------|----------|----------|
| T6.2.1 | test_article_repo_create | 測試創建文章 |
| T6.2.2 | test_article_repo_get_by_id | 測試根據 ID 獲取 |
| T6.2.3 | test_article_repo_get_by_category | 測試根據分類獲取 |
| T6.2.4 | test_article_repo_update | 測試更新文章 |
| T6.2.5 | test_article_repo_delete | 測試刪除文章 |
| T6.2.6 | test_photo_repo_create | 測試創建照片索引 |
| T6.2.7 | test_photo_repo_find_by_keywords | 測試關鍵字查找 |
| T6.2.8 | test_photo_repo_get_by_article_id | 測試獲取文章照片 |
| T6.2.9 | test_photo_repo_bulk_insert | 測試批量插入 |

### 6.3 雙寫機制測試 (`test_phase6_dual_write.py`)
| 測試編號 | 測試名稱 | 測試內容 |
|----------|----------|----------|
| T6.3.1 | test_dual_write_creates_both | 測試雙寫創建兩個記錄 |
| T6.3.2 | test_dual_write_consistency | 測試數據一致性 |
| T6.3.3 | test_migrate_single_topic | 測試單筆遷移 |
| T6.3.4 | test_migrate_batch_topics | 測試批量遷移 |
| T6.3.5 | test_rollback_on_failure | 測試失敗回滾 |
| T6.3.6 | test_legacy_topic_id_preserved | 測試保留舊 ID |

### 6.4 原文照片提取測試 (`test_phase6_image_extractor.py`)
| 測試編號 | 測試名稱 | 測試內容 |
|----------|----------|----------|
| T6.4.1 | test_extract_media_content | 測試 media_content 提取 |
| T6.4.2 | test_extract_media_thumbnail | 測試 media_thumbnail 提取 |
| T6.4.3 | test_extract_enclosures | 測試 enclosures 提取 |
| T6.4.4 | test_extract_from_html_img | 測試 HTML <img> 提取 |
| T6.4.5 | test_extract_multiple_sources | 測試多來源提取 |
| T6.4.6 | test_deduplicate_images | 測試去重 |
| T6.4.7 | test_generate_unique_photo_id | 測試 photo_id 唯一性 |
| T6.4.8 | test_empty_entry | 測試空 entry 處理 |
| T6.4.9 | test_invalid_url_filtered | 測試無效 URL 過濾 |

### 6.5 Hashtag 提取測試 (`test_phase6_hashtag_extractor.py`)
| 測試編號 | 測試名稱 | 測試內容 |
|----------|----------|----------|
| T6.5.1 | test_extract_existing_hashtags | 測試提取已有 #tag |
| T6.5.2 | test_extract_proper_nouns | 測試提取專有名詞 |
| T6.5.3 | test_extract_brands | 測試提取品牌名稱 |
| T6.5.4 | test_extract_chinese_keywords | 測試中文關鍵字 |
| T6.5.5 | test_ai_generation | 測試 AI 生成 |
| T6.5.6 | test_ai_fallback_on_error | 測試 AI 失敗降級 |
| T6.5.7 | test_filter_stop_words | 測試停用詞過濾 |
| T6.5.8 | test_deduplicate_hashtags | 測試去重 |
| T6.5.9 | test_limit_count | 測試數量限制 |
| T6.5.10 | test_combined_extraction | 測試組合提取 |

### 6.6 聚合查詢測試 (`test_phase6_image_matching.py`)
| 測試編號 | 測試名稱 | 測試內容 |
|----------|----------|----------|
| T6.6.1 | test_get_matched_images_basic | 測試基本匹配 |
| T6.6.2 | test_get_matched_images_with_original | 測試包含原文照片 |
| T6.6.3 | test_score_calculation | 測試分數計算 |
| T6.6.4 | test_original_photo_priority | 測試原文照片優先 |
| T6.6.5 | test_keyword_intersection | 測試關鍵字交集 |
| T6.6.6 | test_limit_results | 測試結果限制 |
| T6.6.7 | test_empty_hashtags | 測試空 hashtags |
| T6.6.8 | test_no_matching_photos | 測試無匹配照片 |
| T6.6.9 | test_batch_match | 測試批量匹配 |
| T6.6.10 | test_performance_under_1000_photos | 測試 1000 張照片性能 |

### 6.7 API 端點測試 (`test_phase6_api.py`)
| 測試編號 | 測試名稱 | 測試內容 |
|----------|----------|----------|
| T6.7.1 | test_get_articles_list | 測試獲取文章列表 |
| T6.7.2 | test_get_article_by_id | 測試獲取單篇文章 |
| T6.7.3 | test_get_article_not_found | 測試文章不存在 |
| T6.7.4 | test_get_matched_images_api | 測試獲取匹配圖片 API |
| T6.7.5 | test_refresh_images_api | 測試刷新圖片 API |
| T6.7.6 | test_api_response_format | 測試響應格式 |
| T6.7.7 | test_backward_compatibility | 測試向後兼容 |

### 6.8 整合測試 (`test_phase6_integration.py`)
| 測試編號 | 測試名稱 | 測試內容 |
|----------|----------|----------|
| T6.8.1 | test_full_flow_rss_to_matched | 測試完整流程 |
| T6.8.2 | test_topic_collector_integration | 測試 TopicCollector 整合 |
| T6.8.3 | test_dual_write_integration | 測試雙寫整合 |
| T6.8.4 | test_image_extraction_integration | 測試圖片提取整合 |
| T6.8.5 | test_hashtag_extraction_integration | 測試 hashtag 提取整合 |
| T6.8.6 | test_matching_integration | 測試匹配整合 |
| T6.8.7 | test_end_to_end_fashion | 測試 Fashion 分類端到端 |
| T6.8.8 | test_end_to_end_food | 測試 Food 分類端到端 |
| T6.8.9 | test_end_to_end_trend | 測試 Trend 分類端到端 |

---

## 📊 測試統計

| 階段 | 測試數量 | 文件 |
|------|----------|------|
| 6.1 數據模型 | 8 | `test_phase6_models.py` |
| 6.2 Repository | 9 | `test_phase6_repositories.py` |
| 6.3 雙寫機制 | 6 | `test_phase6_dual_write.py` |
| 6.4 原文照片提取 | 9 | `test_phase6_image_extractor.py` |
| 6.5 Hashtag 提取 | 10 | `test_phase6_hashtag_extractor.py` |
| 6.6 聚合查詢 | 10 | `test_phase6_image_matching.py` |
| 6.7 API 端點 | 7 | `test_phase6_api.py` |
| 6.8 整合測試 | 9 | `test_phase6_integration.py` |
| **總計** | **68** | |

---

## 🚀 實施順序

```
Phase 6.1 (數據模型)
     │
     ▼
Phase 6.2 (Repository)
     │
     ▼
Phase 6.3 (雙寫機制)
     │
     ├─────────────────┬─────────────────┐
     ▼                 ▼                 ▼
Phase 6.4          Phase 6.5         Phase 6.6
(原文照片提取)      (Hashtag提取)      (聚合查詢)
     │                 │                 │
     └─────────────────┴─────────────────┘
                       │
                       ▼
                 Phase 6.7 (API)
                       │
                       ▼
                 Phase 6.8 (整合測試)
```

---

## ⚠️ 風險與緩解

| 風險 | 影響 | 緩解措施 |
|------|------|----------|
| RSS Feed 無圖片 | 無法提取原文照片 | 備援：使用外部圖片搜尋 |
| AI 服務不可用 | Hashtag 提取不完整 | 備援：僅使用正則提取 |
| 遷移數據丟失 | 舊數據無法恢復 | 先備份、回滾機制 |
| 聚合查詢性能差 | API 響應慢 | 建立索引、分頁查詢 |
| 雙寫數據不一致 | 前端顯示錯誤 | 一致性檢查、自動修復 |

---

## 📅 時間估算

| 階段 | 預估時間 | 依賴 |
|------|----------|------|
| 6.1 | 30 分鐘 | 無 |
| 6.2 | 45 分鐘 | 6.1 |
| 6.3 | 30 分鐘 | 6.2 |
| 6.4 | 45 分鐘 | 6.2 |
| 6.5 | 60 分鐘 | 6.2 |
| 6.6 | 45 分鐘 | 6.2 |
| 6.7 | 30 分鐘 | 6.6 |
| 6.8 | 45 分鐘 | 全部 |
| **總計** | **5.5 小時** | |

---

## 📝 備註

1. **雙寫過渡期**：建議保持 2 週，確認新結構穩定後再完全切換
2. **數據備份**：遷移前務必備份現有 topics Collection
3. **索引建立**：需要在 photos Collection 建立 keywords 索引
4. **性能監控**：部署後監控聚合查詢性能

---

*文件建立日期：2026-01-23*
*版本：1.0*

