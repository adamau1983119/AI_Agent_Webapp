# RSS 配置與更新邏輯報告

> **專案**：Influencers AI Agents v4.0  
> **建立日期**：2026-01-29  
> **目的**：供第三方審視 RSS 配置架構與更新邏輯  
> **重要性**：🔴 專案成敗關鍵

---

## 📋 目錄

1. [現有 RSS 配置概覽](#一現有-rss-配置概覽)
2. [角色分配策略詳解](#二角色分配策略詳解)
3. [健康監控機制](#三健康監控機制)
4. [評分與多樣性系統](#四評分與多樣性系統)
5. [v4.0 更新：會員頻道 RSS](#五v40-更新會員頻道-rss)
6. [v4.0 更新：每 4 小時收集](#六v40-更新每-4-小時收集)
7. [RSS 來源風險評估](#七rss-來源風險評估)
8. [建議改進方向](#八建議改進方向)

---

## 一、現有 RSS 配置概覽

### 1.1 配置文件結構

```
backend/
├── app/config/
│   ├── feed_roles.py          # RSS 來源角色分配 ⭐ 核心
│   └── topic_config.py        # 主題生成配置讀取器
├── config/
│   └── topic_generation.yaml  # 生成參數配置檔
└── app/services/
    ├── automation/
    │   └── topic_collector.py # 主題收集器 ⭐ 核心邏輯
    ├── feed_health_service.py # 健康監控服務
    └── scoring_service.py     # 評分服務
```

### 1.2 主打分類 RSS 來源統計

| 分類 | 角色數 | RSS 來源數 | 每日主題數 |
|------|:------:|:----------:|:----------:|
| **Fashion** | 5 | 11 | 10 |
| **Food** | 5 | 9 | 10 |
| **Trend** | 5 | 11 | 10 |
| **總計** | 15 | **31** | **30** |

---

## 二、角色分配策略詳解

### 2.1 設計理念

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     角色分配策略 (Role-Based Distribution)               │
│                                                                         │
│   目的：確保內容來源多樣性，避免單一來源主導                              │
│                                                                         │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐            │
│   │ 角色 A  │    │ 角色 B  │    │ 角色 C  │    │ 角色 D  │            │
│   │ 2 主題  │    │ 2 主題  │    │ 2 主題  │    │ 2 主題  │  ...       │
│   │         │    │         │    │         │    │         │            │
│   │ Feed 1  │    │ Feed 3  │    │ Feed 5  │    │ Feed 7  │            │
│   │ Feed 2  │    │ Feed 4  │    │ Feed 6  │    │ Feed 8  │            │
│   └─────────┘    └─────────┘    └─────────┘    └─────────┘            │
│        │              │              │              │                  │
│        └──────────────┴──────────────┴──────────────┘                  │
│                              │                                          │
│                              ▼                                          │
│                    每日 10 個主題（來自 5 個角色）                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Fashion 角色配置

```python
# backend/app/config/feed_roles.py

FASHION_ROLES = {
    # 角色: [(來源名稱, URL, 權重)]
    
    "authority": [  # 權威時尚媒體
        ("Vogue", "https://www.vogue.com/feed/rss", 1.0),
        ("Elle", "https://www.elle.com/rss/all.xml", 0.95),
    ],
    
    "streetwear": [  # 街頭潮牌
        ("Hypebeast", "https://hypebeast.com/feed", 0.9),
        ("Highsnobiety", "https://www.highsnobiety.com/feeds/rss", 0.85),
    ],
    
    "asian": [  # 亞洲時尚
        ("Popbee", "https://popbee.com/feed", 0.8),
        ("SCMP Style", "https://www.scmp.com/rss/91/feed/", 0.75),
    ],
    
    "industry": [  # 產業分析
        ("Business of Fashion", "https://www.businessoffashion.com/arc/outboundfeeds/rss/", 0.9),
        ("WWD", "https://wwd.com/feed/", 0.85),
    ],
    
    "practical": [  # 實用穿搭
        ("Who What Wear", "https://www.whowhatwear.com/feeds.xml", 0.8),
        ("Fashionista", "https://fashionista.com/.rss/excerpt/", 0.75),
        ("Refinery29", "https://www.refinery29.com/rss.xml", 0.7),
    ],
}

# 角色分配比例：每角色 2 個主題 = 10 個主題/日
FASHION_DISTRIBUTION = {
    "authority": 2,
    "streetwear": 2,
    "asian": 2,
    "industry": 2,
    "practical": 2,
}
```

### 2.3 Food 角色配置

```python
FOOD_ROLES = {
    "mainstream": [  # 主流美食
        ("Eater", "https://www.eater.com/rss/index.xml", 1.0),
        ("Bon Appétit", "https://www.bonappetit.com/feed/rss", 0.95),
    ],
    
    "professional": [  # 專業料理
        ("Epicurious", "https://www.epicurious.com/feed/rss", 0.9),
        ("The Kitchn", "https://www.thekitchn.com/main.rss", 0.85),
    ],
    
    "cultural": [  # 文化美食
        ("BBC Good Food", "https://www.bbcgoodfood.com/feed", 0.85),
        ("Simply Recipes", "https://feeds.feedburner.com/simplyrecipes", 0.8),
    ],
    
    "healthy": [  # 健康飲食
        ("Eat This Not That", "https://www.eatthis.com/feed/", 0.8),
    ],
    
    "casual": [  # 輕鬆美食
        ("The Takeout", "https://www.thetakeout.com/feed/", 0.75),
        ("Mashed", "https://www.mashed.com/feed/", 0.7),
    ],
}
```

### 2.4 Trend 角色配置

```python
TREND_ROLES = {
    "tech": [  # 科技新聞
        ("TechCrunch", "https://techcrunch.com/feed/", 1.0),
        ("The Verge", "https://www.theverge.com/rss/index.xml", 0.95),
    ],
    
    "science": [  # 科學技術
        ("Ars Technica", "https://arstechnica.com/feed/", 0.9),
        ("IEEE Spectrum", "https://spectrum.ieee.org/feeds/feed.rss", 0.85),
    ],
    
    "culture": [  # 文化分析
        ("Vox", "https://www.vox.com/rss/index.xml", 0.85),
        ("The Atlantic", "https://www.theatlantic.com/feed/all/", 0.8),
    ],
    
    "innovation": [  # 創新趨勢
        ("WIRED", "https://www.wired.com/feed/rss", 0.95),
        ("MIT Technology Review", "https://www.technologyreview.com/feed/", 0.9),
        ("Singularity Hub", "https://singularityhub.com/feed/", 0.8),
    ],
    
    "lifestyle": [  # 生活方式
        ("Fast Company", "https://www.fastcompany.com/latest/rss", 0.85),
        ("Rest of World", "https://restofworld.org/feed/latest/", 0.8),
        ("The Next Web", "https://thenextweb.com/feed", 0.75),
    ],
}
```

### 2.5 來源權重分級

```python
SOURCE_WEIGHTS = {
    # Tier S (1.0) - 權威來源
    "Vogue": 1.0,
    "TechCrunch": 1.0,
    "Eater": 1.0,
    
    # Tier A (0.85-0.95) - 專業來源
    "Elle": 0.95,
    "WIRED": 0.95,
    "The Verge": 0.9,
    "Hypebeast": 0.85,
    
    # Tier B (0.7-0.8) - 可靠來源
    "Highsnobiety": 0.8,
    "Ars Technica": 0.8,
    "Epicurious": 0.75,
    
    # Tier C (0.5-0.7) - 一般來源
    "Popbee": 0.7,
    "Fashionista": 0.65,
    "Mashed": 0.55,
    
    # 未知來源預設
    "default": 0.5,
}
```

---

## 三、健康監控機制

### 3.1 健康監控流程

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Feed 健康監控流程                                 │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                     每次 RSS 抓取                                │  │
│   │                                                                 │  │
│   │   1. 檢查 Feed 是否被暫停                                        │  │
│   │      └── 是 → 跳過此 Feed                                        │  │
│   │      └── 否 → 繼續抓取                                           │  │
│   │                                                                 │  │
│   │   2. 嘗試抓取 RSS                                               │  │
│   │      └── 成功 → 記錄成功，重置失敗計數                           │  │
│   │      └── 失敗 → 記錄失敗，累加失敗計數                           │  │
│   │                                                                 │  │
│   │   3. 檢查連續失敗次數                                            │  │
│   │      └── >= 3 次 → 暫停 Feed 1 小時                              │  │
│   │      └── < 3 次 → 繼續下次抓取                                   │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 健康狀態分級

| 分數 | 狀態 | 說明 |
|:----:|------|------|
| 90-100 | 🟢 Healthy | 運作正常 |
| 70-89 | 🟡 Degraded | 偶爾失敗 |
| 50-69 | 🟠 Warning | 頻繁失敗 |
| 1-49 | 🔴 Unhealthy | 嚴重問題 |
| 0 | ⏸️ Paused | 已暫停 |

### 3.3 健康監控配置

```yaml
# config/topic_generation.yaml

health_monitoring:
  enabled: true
  failure_threshold: 3      # 連續 3 次失敗觸發暫停
  pause_duration: 3600      # 暫停 1 小時
  record_ttl_days: 30       # 記錄保留 30 天
```

### 3.4 健康監控 API

| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/v1/feeds/health` | GET | 所有 Feed 健康狀態 |
| `/api/v1/feeds/health/{category}` | GET | 分類健康狀態 |
| `/api/v1/feeds/stats` | GET | 統計摘要 |
| `/api/v1/feeds/pause` | POST | 手動暫停 Feed |
| `/api/v1/feeds/resume` | POST | 手動恢復 Feed |

---

## 四、評分與多樣性系統

### 4.1 文章評分公式

```python
# 總分 = 時效性×0.4 + 來源權重×0.3 + 完整度×0.2 + 相關度×0.1

score = (
    time_score * 0.4 +        # 發布時間越近分數越高
    source_weight * 0.3 +     # 來源權重（Tier S/A/B/C）
    completeness * 0.2 +      # 有圖片、有摘要加分
    relevance * 0.1           # 關鍵字匹配度
)
```

### 4.2 多樣性評分

```python
# 多樣性分數 = 唯一來源數 / 總主題數

diversity_score = unique_sources / total_topics

# 驗收標準
if diversity_score >= 0.6:
    status = "passed"
else:
    status = "warning"  # 記錄警告但不阻擋
```

### 4.3 多樣性報告範例

```json
{
  "score": 0.73,
  "status": "passed",
  "unique_sources": 8,
  "total_topics": 10,
  "source_distribution": {
    "Vogue": 1,
    "Hypebeast": 2,
    "Popbee": 1,
    "Business of Fashion": 2,
    "Who What Wear": 1,
    "Elle": 1,
    "WWD": 1,
    "Fashionista": 1
  }
}
```

---

## 五、v4.0 更新：會員頻道 RSS

### 5.1 新增 RSS 分類

| 類別 | 代碼 | 優先級 | 預設 RSS 狀態 |
|------|------|:------:|:------------:|
| 財經 | `finance` | 🔴 P0 | ⬜ 待建立 |
| 運動 | `sports` | 🔴 P0 | ⬜ 待建立 |
| 科技 | `technology` | 🔴 P0 | ⬜ 待建立 |
| 娛樂 | `entertainment` | 🔴 P0 | ⬜ 待建立 |
| 化妝 | `beauty` | 🟡 P1 | ⬜ 待建立 |
| 其他 | `custom` | 🟢 P2 | 動態搜尋 |

### 5.2 地區 × 類別 RSS 矩陣

```
         香港  台灣  日本  美國  中國  韓國  英國  全球
財經      ⬜    ⬜    ⬜    ⬜    ⬜    ⬜    ⬜    ⬜
運動      ⬜    ⬜    ⬜    ⬜    ⬜    ⬜    ⬜    ⬜
科技      ⬜    ⬜    ⬜    ⬜    ⬜    ⬜    ⬜    ⬜
娛樂      ⬜    ⬜    ⬜    ⬜    ⬜    ⬜    ⬜    ⬜

共計：4 類別 × 8 地區 = 32 組 RSS 配置待建立
每組 3-10 個 RSS 來源
```

### 5.3 預設 RSS 資料庫結構

```javascript
// Collection: default_rss_sources
{
  "_id": ObjectId,
  "category": "finance",           // 類別
  "region": "hong_kong",           // 地區
  "sources": [
    {
      "name": "經濟日報",
      "url": "https://www.hkej.com/rss",
      "language": "zh-TW",
      "weight": 0.9,
      "role": "mainstream",
      "verified": true,
      "last_checked": datetime,
      "health_score": 95
    },
    // ... 更多來源
  ],
  "min_sources": 3,
  "max_sources": 10,
  "created_at": datetime,
  "updated_at": datetime
}
```

### 5.4 會員頻道 RSS 運作流程

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    會員頻道 RSS 運作流程                                 │
│                                                                         │
│   ┌───────────────────────────────────────────────────────────────┐    │
│   │  會員建立頻道                                                  │    │
│   │                                                               │    │
│   │  1. 選擇類別（財經/運動/科技/娛樂/化妝/其他）                  │    │
│   │  2. 選擇地區（香港/台灣/日本/美國/中國/韓國/英國/全球）        │    │
│   │  3. 如選「其他」→ 輸入自定義關鍵字                            │    │
│   └───────────────────────────────────────────────────────────────┘    │
│                              │                                          │
│                              ▼                                          │
│   ┌───────────────────────────────────────────────────────────────┐    │
│   │  系統分配 RSS 來源                                             │    │
│   │                                                               │    │
│   │  A. 預設類別（財經/運動/科技/娛樂/化妝）                       │    │
│   │     └── 從 default_rss_sources 取得 3-10 個來源               │    │
│   │                                                               │    │
│   │  B. 自定義類別（其他）                                         │    │
│   │     └── 使用 Google Custom Search 搜尋相關 RSS                │    │
│   │     └── 驗證 RSS 有效性                                       │    │
│   │     └── 取得 3-10 個有效來源                                  │    │
│   └───────────────────────────────────────────────────────────────┘    │
│                              │                                          │
│                              ▼                                          │
│   ┌───────────────────────────────────────────────────────────────┐    │
│   │  定時收集（每 4 小時）                                         │    │
│   │                                                               │    │
│   │  1. 使用角色分配策略從頻道 RSS 收集                           │    │
│   │  2. 每次收集 10 個主題                                        │    │
│   │  3. 記錄健康狀態                                              │    │
│   │  4. 多樣性檢查                                                │    │
│   └───────────────────────────────────────────────────────────────┘    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.5 自定義頻道 RSS 搜尋邏輯

```python
# services/rss_discovery_service.py

async def discover_rss_for_custom_channel(
    keyword: str,
    region: str,
    min_sources: int = 3,
    max_sources: int = 10
) -> List[RSSSource]:
    """
    為自定義頻道搜尋 RSS 來源
    
    流程：
    1. 使用 Google Custom Search 搜尋「{keyword} RSS feed site:{region_domain}」
    2. 提取搜尋結果中的 RSS URL
    3. 驗證每個 RSS URL 是否有效
    4. 按相關度排序
    5. 返回 min_sources ~ max_sources 個有效來源
    """
    
    # 地區域名映射
    region_domains = {
        "hong_kong": ".hk",
        "taiwan": ".tw",
        "japan": ".jp",
        "usa": ".com",
        "china": ".cn",
        "korea": ".kr",
        "uk": ".uk",
        "global": "",  # 不限制
    }
    
    search_queries = [
        f"{keyword} RSS feed",
        f"{keyword} news RSS",
        f"{keyword} blog feed",
    ]
    
    discovered_sources = []
    
    for query in search_queries:
        results = await google_custom_search(query, region=region)
        
        for result in results:
            rss_url = await extract_rss_url(result["link"])
            if rss_url and await validate_rss(rss_url):
                discovered_sources.append({
                    "name": result["title"],
                    "url": rss_url,
                    "weight": calculate_relevance(result, keyword),
                    "verified": True
                })
    
    # 去重並排序
    unique_sources = deduplicate(discovered_sources)
    sorted_sources = sorted(unique_sources, key=lambda x: x["weight"], reverse=True)
    
    return sorted_sources[:max_sources]
```

---

## 六、v4.0 更新：每 4 小時收集

### 6.1 排程變更

| 項目 | v3.0（舊） | v4.0（新） |
|------|:----------:|:----------:|
| 收集頻率 | 每日 1 次 | **每 4 小時** |
| 收集時間 | 07:00 HKT | 00:00/04:00/08:00/12:00/16:00/20:00 |
| 資料保留 | 永久 | **15 天** |

### 6.2 更新後的排程配置

```yaml
# config/topic_generation.yaml (v4.0)

daily_generation:
  # 改為每 4 小時收集
  interval_hours: 4
  timezone: "Asia/Hong_Kong"
  
  # 收集時間點
  schedule:
    - "00:00"
    - "04:00"
    - "08:00"
    - "12:00"
    - "16:00"
    - "20:00"
  
  categories:
    fashion:
      count: 10
      preview_images: 1
      generate_content: false
      
    food:
      count: 10
      preview_images: 1
      generate_content: false
      
    trend:
      count: 10
      preview_images: 1
      generate_content: false

# 資料保留設定
data_retention:
  enabled: true
  retention_days: 15
  cleanup_time: "03:00"  # 每日凌晨 3 點清理
```

### 6.3 收集流程圖

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      每 4 小時收集流程                                   │
│                                                                         │
│   00:00        04:00        08:00        12:00        16:00        20:00│
│     │            │            │            │            │            │  │
│     ▼            ▼            ▼            ▼            ▼            ▼  │
│   ┌────┐      ┌────┐      ┌────┐      ┌────┐      ┌────┐      ┌────┐ │
│   │收集│      │收集│      │收集│      │收集│      │收集│      │收集│ │
│   │30個│      │30個│      │30個│      │30個│      │30個│      │30個│ │
│   └────┘      └────┘      └────┘      └────┘      └────┘      └────┘ │
│                                                                         │
│   每次收集：                                                            │
│   ├── Fashion: 10 個                                                   │
│   ├── Food: 10 個                                                      │
│   ├── Trend: 10 個                                                     │
│   └── 會員頻道: 各 10 個（按需）                                        │
│                                                                         │
│   每日總計（主打）：6 次 × 30 個 = 180 個主題                           │
│   15 天累積：180 × 15 = 2,700 個主題                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 七、RSS 來源風險評估

### 7.1 現有來源可靠性評估

| 來源 | 可靠性 | 更新頻率 | 風險 |
|------|:------:|:--------:|:----:|
| **Vogue** | 🟢 高 | 高 | 低 |
| **TechCrunch** | 🟢 高 | 高 | 低 |
| **Eater** | 🟢 高 | 高 | 低 |
| **Hypebeast** | 🟢 高 | 中 | 低 |
| **WIRED** | 🟢 高 | 高 | 低 |
| **Popbee** | 🟡 中 | 中 | 中 |
| **SCMP Style** | 🟡 中 | 中 | 中 |
| **Fashionista** | 🟡 中 | 中 | 中 |
| **Mashed** | 🟠 低 | 低 | 高 |

### 7.2 潛在風險與緩解

| 風險 | 可能性 | 影響 | 緩解策略 |
|------|:------:|:----:|----------|
| RSS URL 變更 | 🟡 中 | 🔴 高 | 健康監控 + 備用來源 |
| 網站關閉 | 🟢 低 | 🔴 高 | 每角色多個來源 |
| 內容品質下降 | 🟡 中 | 🟡 中 | 評分系統過濾 |
| 抓取被封鎖 | 🟡 中 | 🟡 中 | 請求間隔 + User-Agent 輪換 |
| 編碼問題 | 🟢 低 | 🟢 低 | UTF-8 強制轉換 |

### 7.3 緊急備用方案

```python
# 當某角色所有 RSS 都失敗時的備用方案

FALLBACK_KEYWORDS = {
    Category.FASHION: [
        "2025春夏時尚趨勢", "可持續時尚", "復古風格回歸",
        "街頭時尚", "時尚科技", "環保時尚",
    ],
    Category.FOOD: [
        "香港美食推薦", "街頭小吃", "傳統美食",
        "新興餐廳", "美食趨勢", "健康飲食",
    ],
    Category.TREND: [
        "AI技術發展", "可持續發展", "社會趨勢",
        "科技創新", "文化現象", "生活方式",
    ],
}

# 使用 AI 生成主題作為最後備用
```

---

## 八、建議改進方向

### 8.1 短期改進（v4.0）

| 項目 | 優先級 | 說明 |
|------|:------:|------|
| 建立 32 組預設 RSS | 🔴 P0 | 財經/運動/科技/娛樂 × 8 地區 |
| 加入 RSS 自動發現 | 🔴 P0 | 支援自定義頻道 |
| 修改收集頻率 | 🔴 P0 | 每日 → 每 4 小時 |
| 加入資料清理 | 🔴 P0 | 15 天自動清除 |

### 8.2 中期改進（v4.1）

| 項目 | 優先級 | 說明 |
|------|:------:|------|
| RSS 來源自動更新 | 🟡 P1 | 定期檢查並更新失效來源 |
| 來源評分優化 | 🟡 P1 | 基於用戶互動調整權重 |
| 區域化內容優化 | 🟡 P1 | 根據用戶語言偏好排序 |

### 8.3 長期改進（v5.0）

| 項目 | 優先級 | 說明 |
|------|:------:|------|
| 機器學習來源推薦 | 🟢 P2 | 根據用戶偏好推薦新來源 |
| 內容去重演算法 | 🟢 P2 | 跨來源相似內容合併 |
| 即時新聞追蹤 | 🟢 P2 | WebSocket 推送突發新聞 |

### 8.4 待建立的 RSS 來源清單

**優先建立順序**：

```
Phase 1: 財經 × 8 地區 = 24-80 個 RSS
Phase 2: 運動 × 8 地區 = 24-80 個 RSS
Phase 3: 科技 × 8 地區 = 24-80 個 RSS
Phase 4: 娛樂 × 8 地區 = 24-80 個 RSS
Phase 5: 化妝 × 8 地區 = 24-80 個 RSS

總計：120-400 個 RSS 來源待建立
```

---

## 九、第三方審核 Checklist

```
☐ 1. 現有 31 個 RSS 來源是否穩定？
☐ 2. 角色分配策略是否合理？
☐ 3. 健康監控機制是否足夠？
☐ 4. 評分系統是否準確？
☐ 5. 多樣性驗收標準 0.6 是否合理？
☐ 6. 每 4 小時收集是否會造成伺服器負擔？
☐ 7. 15 天資料保留是否足夠？
☐ 8. 會員頻道 RSS 自動發現是否可行？
☐ 9. 32 組預設 RSS 的建立時間估計？
☐ 10. 備用關鍵字方案是否足夠？
```

---

## 十、第三方審核回饋與改進方案

### 10.1 問題與回應

| # | 問題 | 回應 | 狀態 |
|:-:|------|------|:----:|
| 1 | RSS 來源合法性是否有授權清單？ | 目前沒有，需建立白名單/黑名單/灰名單機制 | 🟢 採納 |
| 2 | 角色分配固定 2 個是否僵化？ | 同意動態化，但保留最低保障（每角色至少 1 個） | 🟢 採納 |
| 3 | 健康監控 3 次失敗暫停 1 小時是否足夠？ | 不足夠，需建立分級機制（Level 1-4） | 🟢 採納 |
| 4 | 多樣性門檻 0.6 是否合適？ | 需按分類細分（Fashion 0.65, Food 0.55, Trend 0.75） | 🟢 採納 |
| 5 | 自定義頻道 Google 搜尋是否可靠？ | 有風險，需建立三層備用機制 | 🟢 採納 |

### 10.2 改進方案一：白名單/黑名單機制

```python
# 來源分類
RSS_WHITELIST = {
    # 已確認合法且穩定
    "Vogue": {"status": "approved", "license": "public_rss"},
    "TechCrunch": {"status": "approved", "license": "public_rss"},
    "Eater": {"status": "approved", "license": "public_rss"},
    # ... 其他已確認來源
}

RSS_BLACKLIST = {
    # 禁止使用（版權問題/不穩定）
    # 待建立
}

RSS_GRAYLIST = {
    # 需要確認（付費牆/授權不明）
    "Business of Fashion": {"reason": "partial_paywall"},
    "MIT Technology Review": {"reason": "partial_paywall"},
}
```

### 10.3 改進方案二：角色分配動態化

```python
def calculate_role_allocation(role_name, base_count=2):
    """
    動態計算角色分配數量
    
    公式：adjusted = base × (health×0.5 + success×0.3 + 0.2)
    保底：最少 1 個，最多 4 個
    """
    health_factor = get_role_health_score(role_name)
    success_rate = get_role_success_rate(role_name)
    
    adjusted = base_count * (health_factor * 0.5 + success_rate * 0.3 + 0.2)
    return max(1, min(4, round(adjusted)))
```

### 10.4 改進方案三：分級健康監控

| Level | 條件 | 動作 | 通知 |
|:-----:|------|------|:----:|
| 1 | 連續 3 次失敗 | 暫停 1 小時 | ❌ |
| 2 | 24h 內失敗 ≥5 次 | 暫停 24 小時 | ❌ |
| 3 | 7 天失敗率 >50% | 標記待替換 | ✅ |
| 4 | 30 天無成功 | 自動停用 + 切換備用 | ✅ |

### 10.5 改進方案四：多樣性門檻細分

```yaml
diversity:
  thresholds:
    # 主打分類
    fashion: 0.65
    food: 0.55
    trend: 0.75
    
    # 會員頻道
    finance: 0.70
    sports: 0.60
    technology: 0.70
    entertainment: 0.55
    custom: 0.50  # 來源有限，放寬
```

### 10.6 改進方案五：三層備用機制

```
會員頻道主題收集流程：

Layer 1: 從頻道配置的 RSS 收集
    ↓ 不足
Layer 2: 使用相近類別的預設 RSS
    ↓ 仍不足
Layer 3: AI 生成主題（DeepSeek）

保證：會員頻道永遠有內容，不會出現「空白」
```

### 10.7 實施優先級

| 改進項目 | 優先級 | 預估時間 | Phase |
|----------|:------:|:--------:|:-----:|
| 白名單/黑名單機制 | 🔴 P0 | 2 天 | Phase 0 |
| 分級健康監控 | 🔴 P0 | 3 天 | Phase 0 |
| 多樣性門檻細分 | 🟡 P1 | 1 天 | Phase 2 |
| 角色分配動態化 | 🟡 P1 | 2 天 | Phase 2 |
| 三層備用機制 | 🟡 P1 | 2 天 | Phase 2 |

---

## 📝 文件資訊

| 項目 | 內容 |
|------|------|
| 建立日期 | 2026-01-29 |
| 專案版本 | v4.0.0-development |
| 相關文件 | `feed_roles.py`, `topic_collector.py`, `topic_generation.yaml` |

---

**報告結束**

