# AI Agents 後台 API 架構表與生產內容設定

## 📋 目錄
1. [系統架構總覽](#系統架構總覽)
2. [核心思考邏輯](#核心思考邏輯)
3. [系統配置表（專家建議）](#系統配置表專家建議)
4. [API 端點規格](#api-端點規格)
5. [演算法流程（抖音式推薦）](#演算法流程抖音式推薦)
6. [資料流程圖](#資料流程圖)
7. [生產內容設定](#生產內容設定)
8. [思考邏輯與驗證機制](#思考邏輯與驗證機制)
9. [微調功能設計](#微調功能設計)
10. [資料庫 Schema 擴充](#資料庫-schema-擴充)
11. [提示詞系統設計](#提示詞系統設計)
12. [專家建議實施細節](#專家建議實施細節)

---

## 系統架構總覽

### 核心模組架構

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Agents 後台系統                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Scheduler   │  │ Topic Collector│  │  Workflow    │      │
│  │  定時器模組   │→ │  主題發掘模組  │→ │  工作流模組   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                 │                    │             │
│         │                 │                    │             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Data Validator│  │Content Generator│ │Photo Matcher│    │
│  │ 資料驗證模組  │  │  內容生成模組   │  │ 照片匹配模組 │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                 │                    │             │
│         └─────────────────┼────────────────────┘             │
│                           │                                   │
│                  ┌──────────────┐                            │
│                  │ Output Module │                            │
│                  │   輸出模組     │                            │
│                  └──────────────┘                            │
│                           │                                   │
│                  ┌──────────────┐                            │
│                  │   MongoDB    │                            │
│                  │   資料庫      │                            │
│                  └──────────────┘                            │
└─────────────────────────────────────────────────────────────┘
```

### 執行流程

```
每日三次排程（早/中/晚）
    ↓
[1] 主題發掘 → 抓取排行榜關鍵字（Fashion/Food/Social）
    ↓
[2] 資料驗證 → 抓取來源（新聞/榜單/博主/學術）+ 存檔 URL + 截圖
    ↓
[3] 內容生成 → 500字文章（引用來源）+ 1分鐘短片劇本
    ↓
[4] 媒體匹配 → 搜索相關 JPG 照片（≥8張）+ 短片用圖（3-5張）
    ↓
[5] 輸出模組 → 打包 JSON / API Response
    ↓
[6] 前端展示 / 客戶端推送
```

---

## 核心思考邏輯

### 一、系統設計理念

本系統的核心設計理念是**「像抖音演算法一樣的智能學習系統」**，透過持續追蹤顧客互動數據，逐步優化內容生成，讓系統越用越精準。

### 二、三大核心機制

#### 1. 內容生成機制
- **目標**: 自動生成高品質的網紅內容（500字文章 + 8張照片 + 1分鐘劇本）
- **特色**: 
  - 嚴格要求真實來源支持（禁止AI幻想）
  - 文字與照片必須完全匹配
  - 支援版本控制和微調

#### 2. 互動追蹤機制
- **目標**: 記錄顧客的每一次互動行為
- **追蹤項目**:
  - 👍 喜歡（Like）
  - 👎 不喜歡（Dislike）
  - ✏️ 修改（Edit）
  - 🔄 替換照片（Replace）
  - 👁️ 瀏覽時間（View Duration）
- **用途**: 建立顧客偏好模型

#### 3. 智能推薦機制
- **目標**: 根據顧客偏好自動調整生成策略
- **調整項目**:
  - 提升顧客常喜歡的主題曝光率
  - 減少顧客不喜歡的素材
  - 增加顧客互動度高的內容風格
  - 優化照片風格匹配（如食物近拍、秀場細節）

### 三、完整學習循環

```
┌─────────────────────────────────────────────────────────────┐
│                    智能學習循環                                │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  生成內容 → 顧客互動 → 偏好累積 → 優化生成 → 再次生成          │
│     ↓           ↓          ↓          ↓          ↓            │
│  初始內容   記錄行為   建立模型   調整策略   更精準內容        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 四、設計優勢

1. **自動化程度高**: 從主題發掘到內容生成全自動
2. **學習能力強**: 持續優化，越用越精準
3. **品質保證**: 嚴格驗證機制，確保內容真實可靠
4. **靈活調整**: 支援客戶微調，滿足個性化需求
5. **可追溯性**: 完整版本歷史，方便審計和回溯

---

## 系統配置表（專家建議）

### 一、核心模組配置

| 模組 | 配置項 | 建議值 | 說明 |
|------|--------|--------|------|
| **Scheduler** | 任務頻率 | 每日 3 次（08:00 / 14:00 / 20:00） | 定時抓取排行榜 |
| **Topic Collector** | 來源冗餘 | 主來源 + 備用來源 + Fallback | Google Trends HK + 微博熱搜 + 預設庫 |
| | 一致性檢查 | **強制雙來源一致**（事實類）<br>**建議性檢查**（趨勢類） | 保證可信度，不過度阻塞生成 |
| **Data Validator** | 健康度監控頻率 | **5 分鐘探測** + **30 分鐘深度檢查** | API 可用性監控 |
| | 切換閾值 | 健康分數 **< 0.6** 自動切換<br>健康分數 **< 0.4** 降級模式 | 保持穩定性 |
| **Content Generator** | 文章長度 | 500 ± 50 字 | 引用 ≥2 來源 |
| | 劇本結構 | Hook 5s / Main 40s / CTA 15s | 短片標準化 |
| **Photo Matcher** | 匹配度閾值 | **核心 ≥0.85**（品牌、品項、明確詞）<br>**非核心 ≥0.75**（風格、氛圍） | NLP+CV 檢查 |
| | 模型選型 | CLIP/BLIP2 + 輕量微調 | 提升領域精度 |
| **Output Module** | 格式 | JSON + JPG bundle | 統一輸出 |
| **Preference Model** | 冷啟動策略 | 問卷可選 + 靜默探測 | 平衡體驗 |
| | 權重設計 | **指數衰減** α=0.7→0.3 | 適應偏好變化 |
| **Quality Control** | 風險分數閾值 | **≥0.85** 人工審核（P0/P1）<br>**0.7–0.85** 半自動審核 | 平衡速度與品質 |
| | 投訴處理 | 緊急下架 + P0 隊列 | 保護信任 |
| **Evidence Chain** | 截圖存儲 | 雲端主存（S3/OSS）+ 本地緩存 7–14 天 | 成本控制 |
| | 日誌保留期 | 90 天標準，合規可延長至 180–365 天 | 追溯能力 |
| **Observability** | 儀表板指標 | 雙來源覆蓋率、匹配通過率、用戶滿意度、生成成本、錯誤率、Fallback 佔比 | 運維透明化 |

### 二、關鍵參數說明

#### 2.1 一致性檢查分級策略

**強制雙來源一致**（事實類）:
- 活動日期
- 店家地址
- 價格
- 排行榜名次

**建議性檢查**（趨勢類）:
- 允許一來源的熱度 + 一來源的語境補充
- 輸出標註「單來源趨勢」

#### 2.2 健康分數計算

健康分數 = 可用率 × 0.4 + 延遲分數 × 0.3 + 錯誤率分數 × 0.2 + 數據新鮮度 × 0.1

- **可用率**: 過去24小時成功率
- **延遲分數**: < 3秒 = 1.0, 3-5秒 = 0.5, > 5秒 = 0
- **錯誤率分數**: < 5% = 1.0, 5-10% = 0.5, > 10% = 0
- **數據新鮮度**: < 1小時 = 1.0, 1-3小時 = 0.5, > 3小時 = 0

#### 2.3 匹配度分層閾值

**核心要素**（≥ 0.85）:
- 品牌名稱（如 "Dior"）
- 品項名稱（如 "白色喱士裙"）
- 明確詞（如 "燒賣皇后"）

**非核心要素**（≥ 0.75）:
- 風格描述（如 "優雅"、"休閒"）
- 氛圍描述（如 "浪漫"、"現代"）
- 材質推測（如 "絲質"、"棉質"）

#### 2.4 風險分數閾值

- **≥ 0.85**: 必進人工審核（P0/P1）
- **0.7–0.85**: 半自動審核（額外來源補證 + 二次模型檢查）
- **< 0.7**: 自動發布

#### 2.5 指數衰減權重

早期互動權重: α = 0.7  
穩態權重: α = 0.3  
衰減公式: `weight = α * e^(-decay_rate * days)`

---

## API 端點規格

### 一、主題發掘 API

#### 1.1 自動發掘主題（排程觸發）
**Endpoint**: `POST /api/v1/discover/topics/auto`

**功能**: 系統自動發掘當日排行榜前3位關鍵字

**Request Body**:
```json
{
  "category": "fashion" | "food" | "social",
  "region": "global" | "hongkong" | "china" | "us",
  "count": 3,
  "time_slot": "morning" | "afternoon" | "evening"
}
```

**Response**:
```json
{
  "timestamp": "2025-12-30T09:00:00Z",
  "category": "fashion",
  "time_slot": "morning",
  "topics": [
    {
      "id": "topic_fashion_20251230090000_0",
      "keyword": "Dior 2026 春夏秀",
      "rank": 1,
      "source": "Vogue Trending",
      "source_url": "https://www.vogue.com/trending",
      "source_snapshot": "base64_encoded_screenshot",
      "sources": [
        {
          "type": "news",
          "name": "Vogue",
          "url": "https://www.vogue.com/fashion-show",
          "title": "Dior 2026 春夏時裝秀",
          "fetched_at": "2025-12-30T09:00:00Z",
          "verified": true,
          "keywords": ["Dior", "2026春夏", "時裝秀"]
        }
      ],
      "created_at": "2025-12-30T09:00:00Z"
    }
  ]
}
```

#### 1.2 手動發掘主題
**Endpoint**: `POST /api/v1/discover/topics/manual`

**功能**: 手動觸發主題發掘

**Request Body**: 同 1.1

**Response**: 同 1.1

#### 1.3 查詢排行榜關鍵字
**Endpoint**: `GET /api/v1/discover/topics/rankings`

**Query Parameters**:
- `category`: "fashion" | "food" | "social"
- `region`: "global" | "hongkong" | "china" | "us"
- `date`: "YYYY-MM-DD" (可選，預設今天)

**Response**:
```json
{
  "date": "2025-12-30",
  "category": "fashion",
  "region": "global",
  "rankings": [
    {
      "rank": 1,
      "keyword": "Dior 2026 春夏秀",
      "search_volume": 50000,
      "trend": "up",
      "source": "Vogue Trending"
    },
    {
      "rank": 2,
      "keyword": "Gucci 新系列",
      "search_volume": 35000,
      "trend": "stable",
      "source": "WWD"
    },
    {
      "rank": 3,
      "keyword": "巴黎時裝週",
      "search_volume": 28000,
      "trend": "down",
      "source": "Fashion Week"
    }
  ]
}
```

---

### 二、資料驗證 API

#### 2.1 驗證並抓取來源資料
**Endpoint**: `POST /api/v1/validate/sources`

**功能**: 驗證主題的資料來源，抓取並存檔

**Request Body**:
```json
{
  "topic_id": "topic_fashion_20251230090000_0",
  "sources": [
    {
      "type": "news",
      "url": "https://www.vogue.com/fashion-show",
      "name": "Vogue"
    }
  ]
}
```

**Response**:
```json
{
  "topic_id": "topic_fashion_20251230090000_0",
  "validated_sources": [
    {
      "type": "news",
      "name": "Vogue",
      "url": "https://www.vogue.com/fashion-show",
      "title": "Dior 2026 春夏時裝秀完整報導",
      "fetched_at": "2025-12-30T09:05:00Z",
      "verified": true,
      "reliability": "high",
      "content_snippet": "Dior 2026春夏時裝秀在巴黎舉行...",
      "screenshot_url": "https://storage.example.com/screenshots/vogue_20251230.jpg",
      "keywords": ["Dior", "2026春夏", "時裝秀", "白色喱士裙"]
    }
  ],
  "validation_summary": {
    "total_sources": 1,
    "verified_sources": 1,
    "failed_sources": 0
  }
}
```

#### 2.2 取得來源截圖
**Endpoint**: `GET /api/v1/validate/sources/{source_id}/screenshot`

**功能**: 取得來源驗證時的截圖

**Response**: 返回圖片檔案（JPG格式）

---

### 三、內容生成 API

#### 3.1 生成完整內容（文章 + 劇本）
**Endpoint**: `POST /api/v1/generate/content/full`

**功能**: 生成500字文章和1分鐘短片劇本

**Request Body**:
```json
{
  "topic_id": "topic_fashion_20251230090000_0",
  "article_config": {
    "length": 500,
    "style": "influencer" | "formal" | "academic",
    "tone": "enthusiastic" | "professional" | "objective",
    "min_references": 3
  },
  "script_config": {
    "duration": 60,
    "structure": {
      "hook_seconds": 5,
      "main_seconds": 40,
      "cta_seconds": 15
    },
    "style": "fast_paced" | "narrative" | "humorous"
  }
}
```

**Response**:
```json
{
  "topic_id": "topic_fashion_20251230090000_0",
  "article": {
    "content": "Dior 2026春夏時裝秀在巴黎盛大舉行...（500字內容）",
    "word_count": 500,
    "references": [
      {
        "source": "Vogue",
        "url": "https://www.vogue.com/fashion-show",
        "quote": "Dior 2026春夏時裝秀展現了..."
      },
      {
        "source": "WWD",
        "url": "https://wwd.com/runway",
        "quote": "創意總監Maria Grazia Chiuri表示..."
      }
    ],
    "mentioned_items": [
      {
        "item": "白色喱士裙",
        "description": "Dior 2026春夏系列中的經典設計",
        "requires_photo": true
      }
    ]
  },
  "script": {
    "hook": "你知道嗎？Dior 2026春夏時裝秀剛剛結束，這場秀絕對不能錯過！",
    "main": "今天我們來聊聊Dior 2026春夏時裝秀的三大亮點...（40秒內容）",
    "cta": "如果你也喜歡這場秀，記得按讚訂閱，我們下期見！",
    "total_duration": 60,
    "photo_requirements": [
      {
        "segment": "hook",
        "description": "Dior 時裝秀全景",
        "photo_count": 1
      },
      {
        "segment": "main",
        "description": "白色喱士裙細節",
        "photo_count": 3
      },
      {
        "segment": "cta",
        "description": "Dior 品牌標誌",
        "photo_count": 1
      }
    ]
  },
  "generated_at": "2025-12-30T09:10:00Z",
  "model_used": "qwen-turbo",
  "version": 1
}
```

#### 3.2 僅生成文章
**Endpoint**: `POST /api/v1/generate/content/article`

**Request Body**:
```json
{
  "topic_id": "topic_fashion_20251230090000_0",
  "length": 500,
  "style": "influencer",
  "min_references": 3
}
```

#### 3.3 僅生成劇本
**Endpoint**: `POST /api/v1/generate/content/script`

**Request Body**:
```json
{
  "topic_id": "topic_fashion_20251230090000_0",
  "duration": 60,
  "style": "fast_paced"
}
```

---

### 四、照片匹配 API

#### 4.1 搜尋並匹配照片
**Endpoint**: `POST /api/v1/photos/match`

**功能**: 根據文章內容和提及物件，搜尋匹配的照片

**Request Body**:
```json
{
  "topic_id": "topic_fashion_20251230090000_0",
  "article_id": "content_topic_fashion_20251230090000_0",
  "requirements": {
    "min_count": 8,
    "format": "jpg",
    "min_resolution": {
      "width": 1920,
      "height": 1080
    },
    "mentioned_items": [
      {
        "item": "白色喱士裙",
        "priority": "high",
        "required": true
      }
    ]
  }
}
```

**Response**:
```json
{
  "topic_id": "topic_fashion_20251230090000_0",
  "matched_photos": [
    {
      "id": "img_001",
      "url": "https://cdn.example.com/dior-lace-dress.jpg",
      "format": "jpg",
      "source": "Vogue",
      "description": "Dior 白色喱士裙秀場照",
      "matches_item": "白色喱士裙",
      "license": "commercial",
      "width": 1920,
      "height": 1080,
      "photographer": "John Doe",
      "photographer_url": "https://example.com/photographer",
      "order": 1
    }
  ],
  "summary": {
    "total_found": 8,
    "matched_items": 1,
    "unmatched_items": 0,
    "all_jpg": true
  }
}
```

#### 4.2 替換照片
**Endpoint**: `PUT /api/v1/photos/{photo_id}/replace`

**功能**: 替換指定照片，重新搜尋匹配的照片

**Request Body**:
```json
{
  "keyword": "白色喱士裙",
  "source_preference": "Vogue" | "Unsplash" | "Pexels" | "auto"
}
```

#### 4.3 驗證照片與文字匹配
**Endpoint**: `POST /api/v1/photos/validate-match`

**功能**: 驗證照片是否與文字內容匹配

**Request Body**:
```json
{
  "topic_id": "topic_fashion_20251230090000_0",
  "article_id": "content_topic_fashion_20251230090000_0"
}
```

**Response**:
```json
{
  "topic_id": "topic_fashion_20251230090000_0",
  "validation_results": [
    {
      "mentioned_item": "白色喱士裙",
      "has_matching_photo": true,
      "photo_id": "img_001",
      "match_score": 0.95
    }
  ],
  "overall_match": true,
  "warnings": []
}
```

---

### 五、短片輸出 API

#### 5.1 生成短片素材包
**Endpoint**: `POST /api/v1/video-assets/generate`

**功能**: 打包短片所需的文字和照片

**Request Body**:
```json
{
  "topic_id": "topic_fashion_20251230090000_0",
  "script_id": "script_topic_fashion_20251230090000_0"
}
```

**Response**:
```json
{
  "topic_id": "topic_fashion_20251230090000_0",
  "video_assets": {
    "script_text": "完整1分鐘短片文字...",
    "script_structure": {
      "hook": {
        "text": "你知道嗎？Dior 2026春夏時裝秀剛剛結束...",
        "duration": 5,
        "photos": [
          {
            "photo_id": "img_001",
            "sequence_order": 1,
            "display_duration": 5
          }
        ]
      },
      "main": {
        "text": "今天我們來聊聊Dior 2026春夏時裝秀的三大亮點...",
        "duration": 40,
        "photos": [
          {
            "photo_id": "img_002",
            "sequence_order": 2,
            "display_duration": 15
          },
          {
            "photo_id": "img_003",
            "sequence_order": 3,
            "display_duration": 15
          },
          {
            "photo_id": "img_004",
            "sequence_order": 4,
            "display_duration": 10
          }
        ]
      },
      "cta": {
        "text": "如果你也喜歡這場秀，記得按讚訂閱...",
        "duration": 15,
        "photos": [
          {
            "photo_id": "img_005",
            "sequence_order": 5,
            "display_duration": 15
          }
        ]
      }
    },
    "photo_list": [
      {
        "photo_id": "img_001",
        "url": "https://cdn.example.com/dior-show.jpg",
        "sequence_order": 1,
        "segment": "hook"
      }
    ],
    "total_duration": 60,
    "total_photos": 5
  }
}
```

#### 5.2 取得短片素材
**Endpoint**: `GET /api/v1/video-assets/{topic_id}`

**功能**: 取得已生成的短片素材

---

### 六、微調功能 API

#### 6.1 編輯文章內容
**Endpoint**: `PUT /api/v1/contents/{topic_id}/article`

**功能**: 編輯500字文章，支援版本控制

**Request Body**:
```json
{
  "content": "修改後的500字文章內容...",
  "style": "influencer" | "formal" | "academic",
  "create_version": true
}
```

**Response**:
```json
{
  "topic_id": "topic_fashion_20251230090000_0",
  "article": {
    "content": "修改後的500字文章內容...",
    "word_count": 500,
    "version": 2,
    "previous_version": 1,
    "updated_at": "2025-12-30T10:00:00Z"
  }
}
```

#### 6.2 編輯劇本內容
**Endpoint**: `PUT /api/v1/contents/{topic_id}/script`

**功能**: 編輯短片劇本，支援分段編輯

**Request Body**:
```json
{
  "hook": "修改後的5秒開場...",
  "main": "修改後的40秒主體...",
  "cta": "修改後的15秒結尾...",
  "style": "fast_paced" | "narrative" | "humorous",
  "create_version": true
}
```

#### 6.3 替換照片
**Endpoint**: `PUT /api/v1/photos/{photo_id}`

**功能**: 替換照片，重新搜尋匹配

**Request Body**:
```json
{
  "keyword": "白色喱士裙",
  "source_preference": "Vogue",
  "verify_match": true
}
```

#### 6.4 重新排序照片
**Endpoint**: `PUT /api/v1/photos/{topic_id}/reorder`

**功能**: 重新排序主題的照片

**Request Body**:
```json
{
  "image_orders": [
    {
      "image_id": "img_001",
      "order": 1
    },
    {
      "image_id": "img_002",
      "order": 2
    }
  ]
}
```

#### 6.5 取得版本歷史
**Endpoint**: `GET /api/v1/contents/{topic_id}/versions`

**功能**: 取得內容的版本歷史

**Response**:
```json
{
  "topic_id": "topic_fashion_20251230090000_0",
  "versions": [
    {
      "version": 1,
      "type": "generated",
      "article": "原始生成的文章...",
      "script": "原始生成的劇本...",
      "generated_at": "2025-12-30T09:10:00Z",
      "edited_at": null
    },
    {
      "version": 2,
      "type": "edited",
      "article": "修改後的文章...",
      "script": "修改後的劇本...",
      "generated_at": "2025-12-30T09:10:00Z",
      "edited_at": "2025-12-30T10:00:00Z",
      "changes": ["修改了第一段", "更新了引用來源"]
    }
  ]
}
```

#### 6.6 還原到指定版本
**Endpoint**: `POST /api/v1/contents/{topic_id}/restore`

**功能**: 還原到指定版本

**Request Body**:
```json
{
  "version": 1
}
```

---

### 七、輸出格式 API

#### 7.1 打包完整輸出
**Endpoint**: `GET /api/v1/output/{topic_id}/full`

**功能**: 取得完整的輸出（文章 + 照片 + 劇本）

**Query Parameters**:
- `include_photos`: boolean (預設 true)
- `include_script`: boolean (預設 true)
- `photo_format`: "jpg" (預設)

**Response**:
```json
{
  "topic_id": "topic_fashion_20251230090000_0",
  "article": {
    "content": "500字文章...",
    "word_count": 500,
    "references": [...]
  },
  "photos": [
    {
      "id": "img_001",
      "url": "https://cdn.example.com/photo1.jpg",
      "format": "jpg",
      "description": "..."
    }
  ],
  "script": {
    "hook": "...",
    "main": "...",
    "cta": "..."
  },
  "video_assets": {
    "script_text": "...",
    "photo_list": [...]
  }
}
```

#### 7.2 僅輸出文章
**Endpoint**: `GET /api/v1/output/{topic_id}/article`

#### 7.3 僅輸出劇本
**Endpoint**: `GET /api/v1/output/{topic_id}/script`

#### 7.4 僅輸出照片
**Endpoint**: `GET /api/v1/output/{topic_id}/photos`

---

### 八、顧客互動追蹤 API

#### 8.1 記錄互動
**Endpoint**: `POST /api/v1/interactions`

**功能**: 記錄顧客的互動行為（like/dislike/edit/replace/view）

**Request Body**:
```json
{
  "user_id": "user_123",
  "topic_id": "topic_fashion_20251230090000_0",
  "article_id": "content_topic_fashion_20251230090000_0",
  "photo_id": "img_001",
  "script_id": "script_topic_fashion_20251230090000_0",
  "action": "like" | "dislike" | "edit" | "replace" | "view",
  "duration": 30
}
```

**Response**:
```json
{
  "id": "interaction_001",
  "user_id": "user_123",
  "topic_id": "topic_fashion_20251230090000_0",
  "action": "like",
  "duration": 30,
  "created_at": "2025-12-30T10:00:00Z",
  "message": "互動記錄成功"
}
```

#### 8.2 查詢互動歷史
**Endpoint**: `GET /api/v1/interactions/{user_id}`

**功能**: 查詢顧客的所有互動紀錄

**Query Parameters**:
- `action`: "like" | "dislike" | "edit" | "replace" | "view" (可選)
- `category`: "fashion" | "food" | "social" (可選)
- `start_date`: "YYYY-MM-DD" (可選)
- `end_date`: "YYYY-MM-DD" (可選)
- `page`: int (預設 1)
- `limit`: int (預設 20)

**Response**:
```json
{
  "user_id": "user_123",
  "interactions": [
    {
      "id": "interaction_001",
      "topic_id": "topic_fashion_20251230090000_0",
      "action": "like",
      "duration": 30,
      "created_at": "2025-12-30T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 50
  }
}
```

#### 8.3 取得互動統計
**Endpoint**: `GET /api/v1/interactions/{user_id}/stats`

**功能**: 取得顧客的互動統計數據

**Response**:
```json
{
  "user_id": "user_123",
  "stats": {
    "total_likes": 25,
    "total_dislikes": 3,
    "total_edits": 8,
    "total_replaces": 5,
    "total_views": 100,
    "avg_view_time": 45,
    "category_distribution": {
      "fashion": {"likes": 15, "dislikes": 1},
      "food": {"likes": 8, "dislikes": 2},
      "social": {"likes": 2, "dislikes": 0}
    }
  }
}
```

---

### 九、偏好模型 API

#### 9.1 查詢偏好模型
**Endpoint**: `GET /api/v1/preferences/{user_id}`

**功能**: 查詢顧客的偏好模型

**Response**:
```json
{
  "user_id": "user_123",
  "preferences": {
    "category_scores": {
      "fashion": 0.75,
      "food": 0.20,
      "social": 0.05
    },
    "style_preferences": {
      "article_style": "influencer",
      "photo_style": "close_up",
      "script_style": "fast_paced"
    },
    "source_preferences": {
      "fashion": ["Vogue", "WWD"],
      "food": ["OpenRice"],
      "social": []
    },
    "interaction_stats": {
      "total_likes": 25,
      "total_dislikes": 3,
      "total_edits": 8,
      "total_replaces": 5,
      "avg_view_time": 45
    },
    "last_interaction": "2025-12-30T10:00:00Z",
    "updated_at": "2025-12-30T10:00:00Z"
  }
}
```

#### 9.2 更新偏好模型
**Endpoint**: `POST /api/v1/preferences/update`

**功能**: 根據互動紀錄自動更新偏好模型

**Request Body**:
```json
{
  "user_id": "user_123",
  "category": "fashion",
  "action": "like"
}
```

**Response**:
```json
{
  "user_id": "user_123",
  "updated_preferences": {
    "category_scores": {
      "fashion": 0.80,
      "food": 0.15,
      "social": 0.05
    }
  },
  "updated_at": "2025-12-30T10:05:00Z"
}
```

#### 9.3 手動設定偏好
**Endpoint**: `PUT /api/v1/preferences/{user_id}`

**功能**: 手動設定顧客偏好（覆蓋自動計算）

**Request Body**:
```json
{
  "category_scores": {
    "fashion": 0.8,
    "food": 0.15,
    "social": 0.05
  },
  "style_preferences": {
    "article_style": "influencer",
    "photo_style": "close_up",
    "script_style": "fast_paced"
  },
  "source_preferences": {
    "fashion": ["Vogue", "WWD"],
    "food": ["OpenRice"]
  }
}
```

---

### 十、推薦系統 API

#### 10.1 取得推薦主題
**Endpoint**: `GET /api/v1/recommendations/{user_id}`

**功能**: 根據偏好模型生成推薦主題

**Query Parameters**:
- `category`: "fashion" | "food" | "social" (可選)
- `limit`: int (預設 5)

**Response**:
```json
{
  "user_id": "user_123",
  "recommendations": [
    {
      "category": "fashion",
      "keyword": "Gucci 新系列",
      "confidence_score": 0.92,
      "reason": "顧客偏好時尚主題，且喜歡 Gucci 相關內容",
      "generated_at": "2025-12-30T10:10:00Z"
    },
    {
      "category": "food",
      "keyword": "元朗燒賣皇后",
      "confidence_score": 0.87,
      "reason": "顧客偏好美食主題，且喜歡在地美食",
      "generated_at": "2025-12-30T10:10:00Z"
    }
  ]
}
```

#### 10.2 個人化內容生成
**Endpoint**: `POST /api/v1/generate/content/personalized`

**功能**: 根據顧客偏好生成個人化內容

**Request Body**:
```json
{
  "user_id": "user_123",
  "category": "fashion",
  "keyword": "Gucci 新系列",
  "use_preferences": true
}
```

**Response**:
```json
{
  "user_id": "user_123",
  "topic_id": "topic_fashion_20251230101000_0",
  "article": {
    "content": "根據顧客偏好生成的500字文章（網紅語氣）...",
    "style": "influencer",
    "word_count": 500
  },
  "photos": [
    {
      "id": "img_001",
      "url": "https://cdn.example.com/gucci-close-up.jpg",
      "style": "close_up",
      "matches_preference": true
    }
  ],
  "script": {
    "hook": "...",
    "main": "...",
    "cta": "...",
    "style": "fast_paced"
  },
  "preferences_used": {
    "article_style": "influencer",
    "photo_style": "close_up",
    "script_style": "fast_paced"
  }
}
```

#### 10.3 取得推薦歷史
**Endpoint**: `GET /api/v1/recommendations/{user_id}/history`

**功能**: 查詢推薦歷史和效果

**Query Parameters**:
- `start_date`: "YYYY-MM-DD" (可選)
- `end_date`: "YYYY-MM-DD" (可選)

**Response**:
```json
{
  "user_id": "user_123",
  "history": [
    {
      "recommendation_id": "rec_001",
      "category": "fashion",
      "keyword": "Gucci 新系列",
      "confidence_score": 0.92,
      "generated_at": "2025-12-30T10:10:00Z",
      "interaction": {
        "action": "like",
        "duration": 60
      },
      "effectiveness": "high"
    }
  ]
}
```

#### 10.4 取得優化指標
**Endpoint**: `GET /api/v1/analytics/{user_id}`

**功能**: 取得系統優化指標

**Response**:
```json
{
  "user_id": "user_123",
  "metrics": {
    "interaction_rate": 0.85,
    "edit_frequency": 0.15,
    "avg_view_time": 45,
    "recommendation_accuracy": 0.88,
    "preference_stability": 0.92
  },
  "trends": {
    "interaction_rate_trend": "increasing",
    "edit_frequency_trend": "decreasing",
    "recommendation_accuracy_trend": "increasing"
  }
}
```

---

## 演算法流程（抖音式推薦）

### 一、演算法設計理念

本系統採用**類似抖音推薦演算法的智能學習機制**，透過持續追蹤顧客互動數據，建立個人化偏好模型，並在每次生成內容時自動調整策略，讓系統越用越精準。

### 二、五個核心階段

#### 階段 1: 主題生成階段

**目標**: 自動發掘當日熱門主題並生成內容

**流程**:
1. **步驟 1**: 系統每日三次（早/中/晚）抓取排行榜關鍵字
   - Fashion: Vogue Trending, WWD
   - Food: Google Trends (Hong Kong), OpenRice
   - Social: 學術資料庫, 新聞網站
2. **步驟 2**: 生成完整內容
   - 500字文章（引用2-3個真實來源）
   - 至少8張JPG照片（與文字完全匹配）
   - 1分鐘短片劇本（Hook 5s / Main 40s / CTA 15s）
   - 短片用圖（3-5張）
3. **步驟 3**: 保存生成結果至資料庫
   - `topics` 表：主題資訊
   - `articles` 表：文章內容
   - `photos` 表：照片資訊
   - `scripts` 表：劇本內容

**API 端點**:
- `POST /api/v1/discover/topics/auto` - 自動發掘主題
- `POST /api/v1/generate/content/full` - 生成完整內容
- `POST /api/v1/photos/match` - 匹配照片

---

#### 階段 2: 顧客互動階段

**目標**: 記錄顧客的每一次互動行為

**互動類型**:
- 👍 **喜歡（Like）**: 顧客點讚內容
- 👎 **不喜歡（Dislike）**: 顧客不喜歡內容
- ✏️ **修改（Edit）**: 顧客修改文章或劇本
- 🔄 **替換照片（Replace）**: 顧客替換照片
- 👁️ **瀏覽（View）**: 顧客瀏覽內容（記錄停留時間）

**追蹤數據**:
- 互動類型（action）
- 互動時間（created_at）
- 停留時間（duration，秒）
- 互動對象（topic_id, article_id, photo_id, script_id）

**API 端點**:
- `POST /api/v1/interactions` - 記錄互動
- `GET /api/v1/interactions/{user_id}` - 查詢互動歷史

**資料表**: `interactions`

---

#### 階段 3: 偏好累積階段

**目標**: 分析顧客偏好並建立個人化模型

**分析維度**:
1. **主題偏好**:
   - 喜歡的主題類型（Fashion / Food / Social）
   - 不喜歡的主題類型
   - 各類主題的互動率
2. **內容風格偏好**:
   - 文字風格（網紅語氣 / 正式 / 學術）
   - 照片風格（近拍 / 全景 / 細節）
   - 劇本風格（快節奏 / 敘事型 / 幽默型）
3. **來源偏好**:
   - 偏好的資料來源（Vogue / OpenRice / 學術期刊）
   - 偏好的照片來源（Unsplash / Pexels / Vogue）
4. **互動模式**:
   - 平均停留時間
   - 修改頻率
   - 替換照片頻率

**計算邏輯**:
```python
# 偏好分數計算
preference_score = (
    liked_count * 1.0 +           # 喜歡加分
    disliked_count * -0.5 +       # 不喜歡減分
    edit_count * 0.3 +            # 修改表示有興趣
    avg_view_time / 60 * 0.2      # 停留時間加分
)
```

**API 端點**:
- `GET /api/v1/preferences/{user_id}` - 查詢偏好模型
- `POST /api/v1/preferences/update` - 更新偏好模型

**資料表**: `preferences`

---

#### 階段 4: 優化生成階段

**目標**: 根據偏好模型自動調整生成策略

**調整策略**:

1. **主題選擇優化**:
   ```python
   # 根據偏好權重選擇主題
   if user_preference.fashion_score > 0.7:
       # 提升時尚主題曝光率
       category_priority = ["fashion", "food", "social"]
   elif user_preference.food_score > 0.7:
       # 提升美食主題曝光率
       category_priority = ["food", "fashion", "social"]
   ```

2. **內容風格優化**:
   ```python
   # 根據互動數據調整風格
   if user_preference.avg_edit_count > 5:
       # 顧客經常修改，偏好更正式風格
       content_style = "formal"
   elif user_preference.avg_view_time > 120:
       # 顧客停留時間長，偏好深度內容
       content_style = "detailed"
   ```

3. **照片風格優化**:
   ```python
   # 根據替換照片的類型調整
   if user_preference.replaced_photos_style == "close_up":
       # 顧客偏好近拍，增加近拍比例
       photo_style_preference = "close_up"
   ```

4. **來源優化**:
   ```python
   # 根據顧客喜歡的來源調整
   preferred_sources = user_preference.liked_sources
   # 優先使用顧客喜歡的來源
   ```

**API 端點**:
- `POST /api/v1/generate/content/personalized` - 個人化生成
- `GET /api/v1/recommendations/{user_id}` - 取得推薦主題

**提示詞調整**:
- 在生成提示詞中加入偏好參數
- 例如：「根據顧客偏好，使用網紅語氣，優先選擇近拍照片...」

---

#### 階段 5: 持續迭代階段

**目標**: 形成持續學習循環，越用越精準

**迭代流程**:
```
生成內容 → 顧客互動 → 偏好累積 → 優化生成 → 再次生成
    ↓           ↓          ↓          ↓          ↓
  初始內容   記錄行為   建立模型   調整策略   更精準內容
```

**優化指標**:
- 互動率提升（like/dislike 比例）
- 修改次數減少（內容更符合需求）
- 停留時間增加（內容更有吸引力）
- 推薦準確度提升（confidence_score 提高）

**API 端點**:
- `GET /api/v1/analytics/{user_id}` - 取得優化指標
- `GET /api/v1/recommendations/{user_id}/history` - 推薦歷史

---

### 三、演算法核心邏輯

#### 3.1 偏好模型建立

```python
def build_preference_model(user_id: str, interactions: List[Interaction]):
    """
    建立顧客偏好模型
    """
    preferences = {
        "user_id": user_id,
        "category_scores": {
            "fashion": 0.0,
            "food": 0.0,
            "social": 0.0
        },
        "style_preferences": {
            "article_style": "influencer",  # 預設
            "photo_style": "mixed",
            "script_style": "fast_paced"
        },
        "source_preferences": {
            "fashion": [],
            "food": [],
            "social": []
        },
        "interaction_stats": {
            "total_likes": 0,
            "total_dislikes": 0,
            "total_edits": 0,
            "total_replaces": 0,
            "avg_view_time": 0
        }
    }
    
    # 分析互動數據
    for interaction in interactions:
        if interaction.action == "like":
            preferences["category_scores"][interaction.category] += 1.0
            preferences["interaction_stats"]["total_likes"] += 1
        elif interaction.action == "dislike":
            preferences["category_scores"][interaction.category] -= 0.5
            preferences["interaction_stats"]["total_dislikes"] += 1
        elif interaction.action == "edit":
            preferences["interaction_stats"]["total_edits"] += 1
            # 分析修改內容，調整風格偏好
        elif interaction.action == "replace":
            preferences["interaction_stats"]["total_replaces"] += 1
            # 分析替換的照片類型，調整照片風格偏好
    
    # 計算平均停留時間
    view_interactions = [i for i in interactions if i.action == "view"]
    if view_interactions:
        preferences["interaction_stats"]["avg_view_time"] = \
            sum(i.duration for i in view_interactions) / len(view_interactions)
    
    return preferences
```

#### 3.2 推薦分數計算

```python
def calculate_recommendation_score(
    topic: Topic,
    user_preferences: Preferences
) -> float:
    """
    計算推薦分數（0.0 - 1.0）
    """
    score = 0.5  # 基礎分數
    
    # 主題類別匹配
    category_score = user_preferences.category_scores.get(topic.category, 0.0)
    score += category_score * 0.3
    
    # 來源偏好匹配
    if topic.source in user_preferences.source_preferences.get(topic.category, []):
        score += 0.2
    
    # 互動歷史匹配
    # 如果顧客之前喜歡過類似主題，加分
    similar_topics_liked = count_similar_liked_topics(topic, user_preferences)
    score += similar_topics_liked * 0.1
    
    # 時間衰減（新內容優先）
    time_decay = calculate_time_decay(topic.created_at)
    score *= time_decay
    
    return min(1.0, max(0.0, score))
```

---

## 資料流程圖

### 完整自動化流程

```
┌─────────────────────────────────────────────────────────────┐
│  Scheduler (每日三次：07:00, 12:00, 18:00)                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  主題發掘模組 (Topic Discovery)                             │
│  - 抓取排行榜關鍵字（Google Trends / Vogue / OpenRice）     │
│  - 取得前3位關鍵字                                           │
│  - 存檔截圖作為證據                                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  資料驗證模組 (Data Validation)                              │
│  - 抓取來源（新聞/榜單/博主/學術）                          │
│  - 存檔 URL + 時間戳                                          │
│  - 驗證資料可靠性                                             │
│  - 提取關鍵字和提及物件                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  內容生成模組 (Content Generation)                           │
│  - 生成500字文章（引用2-3個來源）                            │
│  - 生成1分鐘短片劇本（Hook 5s / Main 40s / CTA 15s）        │
│  - 標註提及物件（如「白色喱士裙」）                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  媒體匹配模組 (Photo Matching)                               │
│  - 搜索相關 JPG 照片（≥8張）                                 │
│  - 匹配提及物件（如「白色喱士裙」→ 對應照片）                │
│  - 驗證照片格式（必須 JPG）                                   │
│  - 檢查授權狀態                                               │
│  - 短片用圖（3-5張）                                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  輸出模組 (Output Module)                                     │
│  - 打包 JSON / API Response                                   │
│  - 保存至資料庫                                               │
│  - 推送至前端                                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  客戶審閱與微調                                               │
│  - 審閱生成內容                                               │
│  - 編輯文章/劇本                                              │
│  - 替換照片                                                   │
│  - 版本控制                                                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  最終輸出                                                     │
│  - 打包完整輸出                                               │
│  - 推送至客戶端                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 生產內容設定

### 一、時尚趨勢內容設定

#### 1.1 主題發掘邏輯
- **資料來源**: Vogue Trending、WWD、潮流博主
- **搜尋方式**: 每日排行榜前3位關鍵字
- **範例**: "Dior 2026 春夏Fashion show"
- **驗證要求**: 
  - 必須有至少1個時尚媒體來源
  - 必須存檔排行榜截圖
  - 必須記錄來源 URL 和時間戳

#### 1.2 文字內容風格
- **風格**: 網紅口吻、短句、亮點導向
- **字數**: 500字內
- **引用要求**: 
  - 至少引用2-3個真實來源（Vogue、WWD、潮流博主）
  - 每個引用需標註 URL
  - 不得AI自行幻想數據或事件

#### 1.3 照片要求
- **數量**: 至少8張
- **格式**: 必須 JPG
- **類型**: 
  - 秀場全景
  - 細節照片（如白色喱士裙）
- **匹配要求**: 
  - 文字提及「白色喱士裙」，必須提供對應照片
  - 照片需標註來源和授權狀態

#### 1.4 短片劇本結構
- **總時長**: 60秒
- **結構**: 
  - Hook: 5秒（吸引眼球開場）
  - Main: 40秒（描述亮點）
  - CTA: 15秒（互動引導）
- **照片需求**: 每段至少1張照片

---

### 二、美食推薦內容設定

#### 2.1 主題發掘邏輯
- **資料來源**: Google Trends、在地美食榜（OpenRice、大眾點評）
- **搜尋方式**: 按地區搜尋香港排行榜前3位關鍵字
- **範例**: "元朗最好食燒賣top 3"
- **驗證要求**: 
  - 必須有至少1個美食平台來源
  - 必須提供店家地址
  - 必須存檔排行榜截圖

#### 2.2 文字內容風格
- **風格**: 親民試吃敘述 + 評分
- **字數**: 500字內
- **引用要求**: 
  - 至少引用2-3個真實來源（OpenRice、大眾點評、美食博主）
  - 必須提供店家地址
  - 不得AI自行幻想評價

#### 2.3 照片要求
- **數量**: 至少8張
- **格式**: 必須 JPG
- **類型**: 
  - 食物近拍
  - 店外觀
  - 地址照
- **匹配要求**: 
  - 文字提及「燒賣皇后」，必須提供燒賣皇后的地址及相關照片
  - 照片需標註來源和授權狀態

#### 2.4 短片劇本結構
- **總時長**: 60秒
- **結構**: 同時尚趨勢
- **照片需求**: 每段至少1張照片

---

### 三、社會趨勢內容設定

#### 3.1 主題發掘邏輯
- **資料來源**: 學術文章、新聞報導
- **搜尋方式**: 每日排行榜前3位關鍵字
- **範例**: "13-16歲青少年的容貌焦慮"
- **驗證要求**: 
  - 必須有至少1個學術或新聞來源
  - 必須提供研究 DOI 或新聞連結
  - 必須存檔來源截圖

#### 3.2 文字內容風格
- **風格**: 客觀說明 + 來源引用
- **字數**: 500字內
- **引用要求**: 
  - 至少引用2-3個真實來源（學術研究、新聞報導）
  - 必須提供研究 DOI 或新聞連結
  - 必須說明原因及來源
  - 不得AI自行幻想數據

#### 3.3 照片要求
- **數量**: 至少8張
- **格式**: 必須 JPG
- **類型**: 
  - 研究封面
  - 相關書籍封面
  - 相關新聞截圖
- **匹配要求**: 
  - 文字提及「容貌焦慮的書籍」，必須提供相關書籍照片
  - 照片需標註來源和授權狀態

#### 3.4 短片劇本結構
- **總時長**: 60秒
- **結構**: 同時尚趨勢
- **照片需求**: 每段至少1張照片

---

## 思考邏輯與驗證機制

### 一、主題發掘邏輯

#### 1.1 排行榜抓取策略
```
IF category == "fashion":
    sources = [Vogue Trending, WWD, 潮流博主]
    region = "global"
    
ELIF category == "food":
    sources = [Google Trends (Hong Kong), OpenRice, 大眾點評]
    region = "hongkong"
    
ELIF category == "social":
    sources = [學術資料庫, 新聞網站, 社交媒體趨勢]
    region = "global"
```

#### 1.2 關鍵字驗證
- 必須是當日排行榜前3位
- 必須有至少1個可靠來源支持
- 必須存檔截圖作為證據
- 必須記錄時間戳

#### 1.3 去重邏輯
- 檢查當日是否已生成相同關鍵字的主題
- 如果重複，跳過並選擇下一個關鍵字
- 確保每日三次輸出不同內容

---

### 二、資料驗證邏輯

#### 2.1 來源驗證流程
```
1. 抓取來源 URL
2. 驗證 URL 可訪問性
3. 提取內容摘要
4. 提取關鍵字和提及物件
5. 評估可靠性（high/medium/low）
6. 存檔截圖
7. 記錄時間戳
```

#### 2.2 可靠性評估標準
- **High**: 知名媒體（Vogue、WWD、學術期刊）
- **Medium**: 知名博主、美食平台
- **Low**: 未驗證來源、社交媒體

#### 2.3 Fallback 機制
- 如果主要來源失敗，使用備用來源
- 如果所有來源失敗，記錄錯誤並跳過該主題

---

### 三、內容生成邏輯

#### 3.1 文章生成規則
```
1. 讀取主題和關鍵字
2. 讀取驗證過的來源資料
3. 提取關鍵資訊
4. 生成500字文章
5. 確保引用至少2-3個來源
6. 標註提及物件（如「白色喱士裙」）
7. 驗證字數（必須≤500字）
8. 驗證引用數量（必須≥2個）
```

#### 3.2 劇本生成規則
```
1. 讀取主題和關鍵字
2. 生成Hook（5秒，吸引眼球）
3. 生成Main（40秒，描述亮點）
4. 生成CTA（15秒，互動引導）
5. 標註每段所需的照片
6. 驗證總時長（必須=60秒）
```

#### 3.3 禁止事項
- ❌ AI 自行幻想數據或事件
- ❌ 無來源支持的聲稱
- ❌ 非 JPG 格式圖片
- ❌ 未驗證的引用

---

### 四、照片匹配邏輯

#### 4.1 照片搜尋策略
```
1. 提取文章中的提及物件（如「白色喱士裙」）
2. 為每個提及物件搜尋對應照片
3. 搜尋主題相關的通用照片
4. 確保總數≥8張
5. 驗證格式（必須 JPG）
6. 驗證解析度（≥1920x1080）
7. 檢查授權狀態
```

#### 4.2 匹配驗證
```
FOR each mentioned_item IN article:
    IF mentioned_item.requires_photo == true:
        IF has_matching_photo(mentioned_item) == false:
            WARNING: "缺少 {mentioned_item} 的對應照片"
            SEARCH photo for mentioned_item
            IF photo_found:
                ADD photo to topic
            ELSE:
                ERROR: "無法找到 {mentioned_item} 的對應照片"
```

#### 4.3 授權檢查
- 檢查照片授權狀態（commercial/reference/unknown）
- 如果授權不明，嘗試替換為可合法使用的素材
- 記錄授權資訊

---

### 五、一致性檢查

#### 5.1 文字與照片一致性
```
1. 提取文章中的所有提及物件
2. 檢查每個提及物件是否有對應照片
3. 如果缺少，發出警告並嘗試搜尋
4. 如果無法找到，記錄錯誤
```

#### 5.2 引用來源一致性
```
1. 檢查文章中的引用是否都有對應的來源
2. 驗證來源 URL 可訪問
3. 如果來源失效，嘗試尋找替代來源
```

---

## 微調功能設計

### 一、文字內容微調

#### 1.1 編輯模式
- 提供「編輯模式」：客戶可直接修改 500 字文章的段落或語氣
- 支援段落級別編輯
- 支援全文編輯

#### 1.2 風格選項
- **正式**: 專業、客觀的語氣
- **網紅語氣**: 活潑、親民的語氣
- **學術化**: 嚴謹、引用的語氣

#### 1.3 版本控制
- 保留原始生成稿
- 建立「版本控制」，方便回溯
- 記錄每次修改的變更說明

---

### 二、相片微調

#### 2.1 替換功能
- 提供「替換功能」：若客戶覺得某張照片不合適，可重新搜尋同關鍵字的其他 JPG
- 支援批量替換
- 支援單張替換

#### 2.2 標籤檢索
- 支援「標籤檢索」：例如輸入「白色喱士裙」→系統自動篩選相關圖片
- 支援關鍵字搜尋
- 支援來源篩選

#### 2.3 必須匹配檢查
- 建立「必須匹配檢查」：若文字提及某物件，系統提醒客戶必須附上相應照片
- 自動驗證匹配度
- 提供匹配建議

---

### 三、短片劇本微調

#### 3.1 分段編輯
- 劇本分段可編輯：Hook、Main、CTA 三段獨立修改
- 支援單段編輯
- 支援全文編輯

#### 3.2 語速/語氣選項
- **快節奏**: 緊湊、快速的節奏
- **敘事型**: 平緩、敘述的節奏
- **幽默型**: 輕鬆、幽默的節奏

#### 3.3 照片替換與排序
- 客戶可替換短片用圖
- 客戶可重新排序照片
- 自動調整照片顯示時長

---

### 四、資料來源微調

#### 4.1 偏好來源設定
- 客戶可指定「偏好來源」：例如只用 Vogue、或只用 OpenRice
- 支援多個偏好來源
- 支援來源優先級設定

#### 4.2 引用清單管理
- 系統需保留「引用清單」，方便客戶刪減或新增
- 支援新增引用
- 支援刪除引用
- 支援修改引用

#### 4.3 來源失效處理
- 若來源失效，系統自動提示並建議替代
- 自動檢測來源可訪問性
- 提供替代來源建議

---

### 五、輸出格式微調

#### 5.1 打包輸出
- 文章、照片、短片劇本需支援「打包輸出」與「單項輸出」
- 支援完整打包
- 支援單項輸出

#### 5.2 輸出選項
- 客戶可選擇只要文字、不需要照片，或只要短片劇本
- 支援自定義輸出格式
- 支援批量輸出

#### 5.3 格式驗證
- 所有照片必須維持 JPG 格式，避免混入 PNG 或 WebP
- 自動轉換格式
- 驗證格式一致性

---

## 資料庫 Schema 擴充

### 一、Topics 表擴充

```python
{
  "id": "topic_fashion_20251230090000_0",
  "title": "Dior 2026 春夏秀",
  "category": "fashion",
  "status": "pending",
  "source": "Vogue Trending",
  "keyword": "Dior 2026 春夏秀",
  "rank": 1,
  "region": "global",
  "time_slot": "morning",
  "sources": [
    {
      "type": "news",
      "name": "Vogue",
      "url": "https://www.vogue.com/fashion-show",
      "title": "Dior 2026 春夏時裝秀",
      "fetched_at": "2025-12-30T09:00:00Z",
      "verified": true,
      "reliability": "high",
      "screenshot_url": "https://storage.example.com/screenshots/vogue_20251230.jpg",
      "keywords": ["Dior", "2026春夏", "時裝秀"]
    }
  ],
  "source_snapshot": "base64_encoded_screenshot",
  "created_at": "2025-12-30T09:00:00Z",
  "generated_at": "2025-12-30T09:00:00Z",
  "updated_at": "2025-12-30T09:00:00Z"
}
```

### 二、Articles 表擴充

```python
{
  "id": "content_topic_fashion_20251230090000_0",
  "topic_id": "topic_fashion_20251230090000_0",
  "article": {
    "content": "500字文章內容...",
    "word_count": 500,
    "style": "influencer",
    "tone": "enthusiastic"
  },
  "references": [
    {
      "source": "Vogue",
      "url": "https://www.vogue.com/fashion-show",
      "quote": "Dior 2026春夏時裝秀展現了...",
      "verified": true
    }
  ],
  "mentioned_items": [
    {
      "item": "白色喱士裙",
      "description": "Dior 2026春夏系列中的經典設計",
      "requires_photo": true,
      "has_matching_photo": true,
      "photo_id": "img_001"
    }
  ],
  "version": 1,
  "versions": [
    {
      "version": 1,
      "type": "generated",
      "article": "原始生成的文章...",
      "generated_at": "2025-12-30T09:10:00Z",
      "edited_at": null
    }
  ],
  "generated_at": "2025-12-30T09:10:00Z",
  "updated_at": "2025-12-30T09:10:00Z"
}
```

### 三、Scripts 表擴充

```python
{
  "id": "script_topic_fashion_20251230090000_0",
  "topic_id": "topic_fashion_20251230090000_0",
  "hook": {
    "text": "你知道嗎？Dior 2026春夏時裝秀剛剛結束...",
    "duration": 5
  },
  "main": {
    "text": "今天我們來聊聊Dior 2026春夏時裝秀的三大亮點...",
    "duration": 40
  },
  "cta": {
    "text": "如果你也喜歡這場秀，記得按讚訂閱...",
    "duration": 15
  },
  "total_duration": 60,
  "style": "fast_paced",
  "photo_requirements": [
    {
      "segment": "hook",
      "description": "Dior 時裝秀全景",
      "photo_count": 1,
      "photo_ids": ["img_001"]
    },
    {
      "segment": "main",
      "description": "白色喱士裙細節",
      "photo_count": 3,
      "photo_ids": ["img_002", "img_003", "img_004"]
    },
    {
      "segment": "cta",
      "description": "Dior 品牌標誌",
      "photo_count": 1,
      "photo_ids": ["img_005"]
    }
  ],
  "references": [
    {
      "source": "Vogue",
      "url": "https://www.vogue.com/fashion-show",
      "verified": true
    }
  ],
  "version": 1,
  "generated_at": "2025-12-30T09:10:00Z",
  "updated_at": "2025-12-30T09:10:00Z"
}
```

### 四、Photos 表擴充

```python
{
  "id": "img_001",
  "topic_id": "topic_fashion_20251230090000_0",
  "article_id": "content_topic_fashion_20251230090000_0",
  "url": "https://cdn.example.com/dior-lace-dress.jpg",
  "format": "jpg",
  "source": "Vogue",
  "description": "Dior 白色喱士裙秀場照",
  "matches_item": "白色喱士裙",
  "license": "commercial",
  "width": 1920,
  "height": 1080,
  "photographer": "John Doe",
  "photographer_url": "https://example.com/photographer",
  "keywords": ["Dior", "白色喱士裙", "時裝秀"],
  "order": 1,
  "is_video_asset": true,
  "video_segment": "main",
  "video_sequence_order": 2,
  "fetched_at": "2025-12-30T09:15:00Z"
}
```

### 五、Video Assets 表

```python
{
  "id": "video_asset_topic_fashion_20251230090000_0",
  "topic_id": "topic_fashion_20251230090000_0",
  "script_id": "script_topic_fashion_20251230090000_0",
  "script_text": "完整1分鐘短片文字...",
  "photo_list": [
    {
      "photo_id": "img_001",
      "url": "https://cdn.example.com/dior-show.jpg",
      "sequence_order": 1,
      "segment": "hook",
      "display_duration": 5
    }
  ],
  "total_duration": 60,
  "total_photos": 5,
  "created_at": "2025-12-30T09:20:00Z",
  "updated_at": "2025-12-30T09:20:00Z"
}
```

### 六、Users 表（顧客基本資料）

```python
{
  "id": "user_123",
  "name": "顧客名稱",
  "email": "customer@example.com",
  "created_at": "2025-12-01T00:00:00Z",
  "updated_at": "2025-12-30T10:00:00Z"
}
```

### 七、Preferences 表（偏好模型）

```python
{
  "id": "preference_user_123",
  "user_id": "user_123",
  "category_scores": {
    "fashion": 0.75,
    "food": 0.20,
    "social": 0.05
  },
  "style_preferences": {
    "article_style": "influencer",
    "photo_style": "close_up",
    "script_style": "fast_paced"
  },
  "source_preferences": {
    "fashion": ["Vogue", "WWD"],
    "food": ["OpenRice"],
    "social": []
  },
  "interaction_stats": {
    "total_likes": 25,
    "total_dislikes": 3,
    "total_edits": 8,
    "total_replaces": 5,
    "avg_view_time": 45
  },
  "last_interaction": "2025-12-30T10:00:00Z",
  "created_at": "2025-12-01T00:00:00Z",
  "updated_at": "2025-12-30T10:00:00Z"
}
```

### 八、Interactions 表（互動紀錄）

```python
{
  "id": "interaction_001",
  "user_id": "user_123",
  "topic_id": "topic_fashion_20251230090000_0",
  "article_id": "content_topic_fashion_20251230090000_0",
  "photo_id": "img_001",
  "script_id": "script_topic_fashion_20251230090000_0",
  "action": "like" | "dislike" | "edit" | "replace" | "view",
  "duration": 30,
  "category": "fashion",
  "created_at": "2025-12-30T10:00:00Z"
}
```

### 九、Recommendations 表（推薦結果）

```python
{
  "id": "recommendation_001",
  "user_id": "user_123",
  "category": "fashion",
  "keyword": "Gucci 新系列",
  "confidence_score": 0.92,
  "reason": "顧客偏好時尚主題，且喜歡 Gucci 相關內容",
  "generated_at": "2025-12-30T10:10:00Z",
  "interaction_result": {
    "action": "like",
    "duration": 60
  },
  "effectiveness": "high"
}
```

### 十、Schema 關聯圖

```
Users (顧客)
  ├── Preferences (偏好模型) - 1:1
  ├── Interactions (互動紀錄) - 1:N
  └── Recommendations (推薦結果) - 1:N

Topics (主題)
  ├── Articles (文章) - 1:1
  ├── Photos (照片) - 1:N
  ├── Scripts (劇本) - 1:1
  └── Video Assets (短片素材) - 1:1

Interactions (互動紀錄)
  ├── Topics - N:1
  ├── Articles - N:1
  ├── Photos - N:1
  └── Scripts - N:1

Recommendations (推薦結果)
  └── Topics - N:1 (推薦的主題)
```

---

## 提示詞系統設計

### 一、提示詞設計理念

本系統的提示詞設計遵循**「像抖音演算法一樣的智能學習」**原則，透過持續優化提示詞參數，讓生成內容越來越符合顧客需求。

### 二、核心提示詞模組

#### 2.1 內容生成提示詞

**基礎模板**:
```
根據今日排行榜的前三位關鍵字，生成500字文章，引用至少2個真實來源，
並提供8張與文字描述完全匹配的JPG照片。文章需保持{style}語氣，
並在結尾引導互動。若文字提及具體物件（如白色喱士裙），必須附上相應照片。

關鍵字: {keyword}
分類: {category}
來源: {sources}
```

**個人化版本**（加入偏好參數）:
```
根據今日排行榜的前三位關鍵字，生成500字文章，引用至少2個真實來源，
並提供8張與文字描述完全匹配的JPG照片。

【顧客偏好設定】
- 文字風格: {user_preference.article_style}（顧客偏好此風格）
- 照片風格: {user_preference.photo_style}（顧客偏好此類型照片）
- 來源偏好: {user_preference.source_preferences}（優先使用顧客喜歡的來源）

文章需保持{user_preference.article_style}語氣，並在結尾引導互動。
若文字提及具體物件（如白色喱士裙），必須附上相應照片。

關鍵字: {keyword}
分類: {category}
來源: {sources}
```

#### 2.2 短片劇本提示詞

**基礎模板**:
```
生成1分鐘短片劇本，結構為：
Hook(5秒) → Main(40秒) → CTA(15秒)，
並提供3-5張JPG照片作為短片素材。劇本需口語化、快節奏，
適合TikTok/IG Reels，並引用真實來源支持主題。

關鍵字: {keyword}
分類: {category}
```

**個人化版本**:
```
生成1分鐘短片劇本，結構為：
Hook(5秒) → Main(40秒) → CTA(15秒)，
並提供3-5張JPG照片作為短片素材。

【顧客偏好設定】
- 劇本風格: {user_preference.script_style}（顧客偏好此風格）
- 照片風格: {user_preference.photo_style}（顧客偏好此類型照片）

劇本需{user_preference.script_style}風格，適合TikTok/IG Reels，
並引用真實來源支持主題。

關鍵字: {keyword}
分類: {category}
```

#### 2.3 顧客偏好累積提示詞

**分析提示詞**:
```
分析顧客對文章與照片的喜好（點讚、修改、替換、刪除），
累積偏好數據，並在下一次生成時優先匹配顧客喜歡的風格與素材。

互動數據:
- 喜歡次數: {liked_count}
- 不喜歡次數: {disliked_count}
- 修改次數: {edit_count}
- 替換照片次數: {replace_count}
- 平均停留時間: {avg_view_time}秒

分析結果:
1. 顧客偏好哪類主題？（Fashion/Food/Social）
2. 顧客偏好哪種文字風格？（網紅語氣/正式/學術）
3. 顧客偏好哪種照片風格？（近拍/全景/細節）
4. 顧客偏好哪些來源？（Vogue/OpenRice/學術期刊）
```

#### 2.4 內容優化提示詞

**優化提示詞**:
```
檢查生成的文字與照片是否一致，若不一致則自動提醒並替換。
保存顧客修改後的版本，並建立版本控制。下一次生成時，
自動引用顧客修改過的風格與偏好，避免重複錯誤。

當前內容:
- 文章: {article}
- 照片: {photos}
- 劇本: {script}

顧客修改歷史:
- 修改次數: {edit_count}
- 修改內容: {edit_history}
- 替換照片: {replace_history}

優化建議:
1. 根據顧客修改歷史，調整生成風格
2. 避免顧客不喜歡的內容類型
3. 增加顧客喜歡的內容元素
```

#### 2.5 演算法提示詞（模仿抖音）

**推薦演算法提示詞**:
```
根據顧客互動數據（喜歡、不喜歡、修改次數、停留時間），
建立偏好模型，並在下一次生成時自動調整：

互動數據:
- 喜歡: {liked_count}次
- 不喜歡: {disliked_count}次
- 修改: {edit_count}次
- 平均停留時間: {avg_view_time}秒

調整策略:
1. 提升顧客常喜歡的主題曝光率（{preferred_category}）
2. 減少顧客不喜歡的素材（{disliked_items}）
3. 增加顧客互動度高的內容風格（{preferred_style}）

推薦分數計算:
- 基礎分數: 0.5
- 主題匹配: +{category_score} * 0.3
- 來源匹配: +{source_score} * 0.2
- 互動歷史: +{interaction_score} * 0.1
- 時間衰減: *{time_decay}

最終推薦分數: {confidence_score}
```

### 三、提示詞使用流程

```
1. 初始生成
   ↓
   使用基礎提示詞模板
   ↓
2. 顧客互動
   ↓
   記錄互動數據
   ↓
3. 偏好分析
   ↓
   使用偏好累積提示詞分析
   ↓
4. 模型更新
   ↓
   更新偏好模型
   ↓
5. 優化生成
   ↓
   使用個人化提示詞（加入偏好參數）
   ↓
6. 持續迭代
   ↓
   重複步驟2-5，逐步優化
```

### 四、提示詞參數說明

| 參數 | 說明 | 來源 |
|------|------|------|
| `{keyword}` | 排行榜關鍵字 | 主題發掘模組 |
| `{category}` | 主題分類 | 主題發掘模組 |
| `{sources}` | 資料來源列表 | 資料驗證模組 |
| `{style}` | 文字風格 | 預設或偏好模型 |
| `{user_preference.article_style}` | 顧客偏好的文章風格 | 偏好模型 |
| `{user_preference.photo_style}` | 顧客偏好的照片風格 | 偏好模型 |
| `{user_preference.script_style}` | 顧客偏好的劇本風格 | 偏好模型 |
| `{user_preference.source_preferences}` | 顧客偏好的來源 | 偏好模型 |
| `{liked_count}` | 喜歡次數 | 互動數據 |
| `{disliked_count}` | 不喜歡次數 | 互動數據 |
| `{edit_count}` | 修改次數 | 互動數據 |
| `{replace_count}` | 替換次數 | 互動數據 |
| `{avg_view_time}` | 平均停留時間 | 互動數據 |
| `{confidence_score}` | 推薦信心分數 | 推薦演算法 |

---

## 總結

### 核心特點

1. **完整的自動化流程**: 從主題發掘到最終輸出的全自動化
2. **嚴格的資料驗證**: 確保所有內容都有真實來源支持
3. **智能照片匹配**: 自動匹配文字提及物件與照片
4. **靈活的微調功能**: 支援客戶自定義編輯和調整
5. **版本控制**: 完整記錄每次修改的歷史
6. **一致性檢查**: 確保文字與照片的一致性
7. **智能學習系統**: 像抖音演算法一樣，持續學習顧客偏好
8. **個人化推薦**: 根據互動數據自動調整生成策略
9. **持續優化**: 越用越精準，推薦準確度逐步提升

### 技術優勢

1. **模組化設計**: 每個模組獨立，易於維護和擴展
2. **Fallback 機制**: 多層備援，確保系統穩定性
3. **可擴展性**: 易於添加新的資料來源和功能
4. **API 優先**: 完整的 RESTful API，易於前端整合

### 客戶價值

1. **節省時間**: 自動化生成，減少人工操作
2. **保證品質**: 嚴格的驗證機制，確保內容品質
3. **靈活調整**: 完整的微調功能，滿足個性化需求
4. **可追溯性**: 完整的版本歷史，方便回溯和審計
5. **智能學習**: 系統自動學習顧客偏好，越用越精準
6. **個人化體驗**: 根據互動數據自動調整，提供個人化內容
7. **持續優化**: 推薦準確度逐步提升，減少修改次數

---

---

## 架構思考邏輯總結

### 一、為什麼這樣設計？

#### 1.1 為什麼需要演算法流程？
- **問題**: 如何讓系統越用越精準？
- **解決方案**: 模仿抖音演算法，透過互動數據建立偏好模型
- **效果**: 系統自動學習顧客喜好，減少修改次數，提升滿意度

#### 1.2 為什麼需要互動追蹤？
- **問題**: 如何知道顧客喜歡什麼？
- **解決方案**: 記錄每一次互動（like/dislike/edit/replace/view）
- **效果**: 建立完整的顧客畫像，為推薦提供數據支持

#### 1.3 為什麼需要偏好模型？
- **問題**: 如何將互動數據轉化為生成策略？
- **解決方案**: 建立偏好模型，量化顧客喜好
- **效果**: 在生成內容時自動調整風格和素材

#### 1.4 為什麼需要推薦系統？
- **問題**: 如何選擇最適合的主題？
- **解決方案**: 根據偏好模型計算推薦分數
- **效果**: 優先生成顧客最可能喜歡的內容

### 二、系統如何運作？

#### 2.1 初始階段（冷啟動）
```
1. 系統生成內容（使用預設風格）
2. 顧客瀏覽和互動
3. 系統記錄互動數據
4. 建立初步偏好模型
```

#### 2.2 學習階段（累積數據）
```
1. 系統根據偏好模型調整生成策略
2. 生成個人化內容
3. 顧客繼續互動
4. 更新偏好模型（更精準）
```

#### 2.3 優化階段（持續迭代）
```
1. 推薦準確度提升
2. 修改次數減少
3. 停留時間增加
4. 系統越用越精準
```

### 三、關鍵設計決策

#### 3.1 為什麼使用互動數據而非問卷？
- **原因**: 互動數據更真實、更即時
- **優勢**: 不需要顧客主動填寫，自動收集

#### 3.2 為什麼要記錄停留時間？
- **原因**: 停留時間反映內容吸引力
- **用途**: 長停留時間 = 內容有吸引力，短停留時間 = 內容不吸引

#### 3.3 為什麼要追蹤修改和替換？
- **原因**: 修改和替換反映顧客真實需求
- **用途**: 分析修改內容，了解顧客偏好的風格和素材

#### 3.4 為什麼要建立推薦分數？
- **原因**: 量化推薦準確度，方便優化
- **用途**: 追蹤推薦效果，持續改進演算法

### 四、系統優勢

#### 4.1 對顧客的優勢
- **個人化體驗**: 內容越來越符合需求
- **減少修改**: 系統自動學習，減少手動調整
- **節省時間**: 自動生成，無需手動創作

#### 4.2 對系統的優勢
- **持續優化**: 越用越精準，推薦準確度提升
- **數據驅動**: 基於真實互動數據，而非猜測
- **可擴展性**: 易於添加新的偏好維度

#### 4.3 對業務的優勢
- **提升滿意度**: 內容更符合需求，顧客更滿意
- **降低成本**: 減少人工調整，降低運營成本
- **競爭優勢**: 智能學習系統，領先競爭對手

---

**文件版本**: v3.0（已整合專家建議與實施細節）  
**最後更新**: 2025-12-30  
**作者**: AI Agents 後台系統設計團隊  
**專家審核**: 已通過第三方專家評估，所有建議已整合

