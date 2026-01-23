# 📋 RSS Feed 多源邏輯問題診斷報告

> **文件用途**：請求第三方專家審查與建議  
> **版本**：v3.0.0-development  
> **報告日期**：2026-01-23  
> **報告人**：AI Assistant  
> **狀態**：待審查

---

## 📌 執行摘要

本專案是一個「為網紅提供獨特內容素材」的 AI 內容生成平台。診斷發現 **RSS Feed 收集邏輯存在嚴重的「單一來源壟斷」問題**，導致：

1. 所有 Fashion 主題都來自 Vogue（單一來源）
2. 內容缺乏獨特性和多樣性
3. 無法達成「為網紅提供差異化內容」的核心目標

**請求第三方專家審查本報告並提供修改建議。**

---

## 1. 專案背景與核心目標

### 1.1 專案定位

```
專案名稱：AI Agent Webapp for Social Media Content Generation
目標用戶：社交媒體網紅、內容創作者
核心價值：提供獨特、多元的內容素材，幫助網紅吸引更多粉絲
```

### 1.2 核心需求

| 需求 | 說明 | 重要性 |
|------|------|--------|
| **獨特性** | 提供與其他平台不同的內容角度 | ⭐⭐⭐⭐⭐ |
| **廣泛性** | 覆蓋多種風格和受眾偏好 | ⭐⭐⭐⭐⭐ |
| **專業性** | 內容來自權威可靠的來源 | ⭐⭐⭐⭐ |
| **時效性** | 緊跟最新趨勢和熱點 | ⭐⭐⭐⭐ |

### 1.3 每日生成規格

```yaml
每日主題生成：
  時間: 07:00 (香港時間)
  分類:
    - Fashion（時尚趨勢）: 10 個主題
    - Food（美食推薦）: 10 個主題
    - Trend（社會趨勢）: 10 個主題
  總計: 30 個主題/天
```

---

## 2. 當前實現分析

### 2.1 RSS Feed 配置

目前已配置 72 個 RSS Feed：

| 分類 | Feed 數量 | 主要來源 |
|------|----------|---------|
| Fashion | 23 | Vogue, Elle, Hypebeast, BoF, WWD, Popbee... |
| Food | 19 | Eater, Bon Appétit, Epicurious, The Kitchn... |
| Trend | 30 | WIRED, TechCrunch, The Verge, MIT Tech Review... |

### 2.2 當前收集邏輯（問題所在）

**檔案位置**：`backend/app/services/automation/topic_collector.py`

**關鍵代碼**（第 284-365 行）：

```python
async def _collect_from_rss(self, category: Category, count: int):
    topics = []
    feeds = self.rss_feeds.get(category, [])  # 取得該分類的所有 feeds
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for feed_url in feeds:  # 循序遍歷每個 feed
            try:
                response = await client.get(feed_url)
                feed = feedparser.parse(response.text)
                
                for entry in feed.entries[:count * 3]:
                    # ... 處理每個條目 ...
                    topics.append(topic)
                    
                    if len(topics) >= count:  # ⚠️ 問題點！
                        break  # 達到數量就停止
                        
            except Exception as e:
                logger.warning(f"無法從 RSS {feed_url} 收集主題: {e}")
                continue
    
    return topics
```

### 2.3 問題診斷

#### 問題 1：先到先得邏輯

```
執行流程（以 Fashion 分類為例，count=10）：

Step 1: 請求 Vogue RSS Feed
        → 成功返回 30 篇文章
        → 取 10 篇（達到 count）
        → break 內層循環

Step 2: 請求 Elle RSS Feed
        → 成功返回 25 篇文章
        → 但 len(topics) 已經 = 10
        → 內層循環立即 break，不添加任何文章

Step 3-23: 重複 Step 2
        → 全部跳過

結果：10 個主題全部來自 Vogue！
```

#### 問題 2：Feed 順序決定內容

```python
# RSS Feed 列表（Fashion）
Category.FASHION: [
    "https://www.vogue.com/feed/rss",      # 第 1 個 → 佔據所有名額
    "https://www.elle.com/rss/all.xml",    # 第 2 個 → 永遠沒機會
    "https://hypebeast.com/feed",          # 第 3 個 → 永遠沒機會
    # ...
]
```

#### 問題 3：錯誤被靜默處理

```python
except Exception as e:
    logger.warning(...)  # 只記錄警告
    continue             # 繼續下一個 feed，不影響主流程
```

- 無法知道哪些 feeds 失敗
- 無法追蹤來源多樣性

---

## 3. 對專案目標的影響

### 3.1 獨特性喪失

| 情境 | 影響 |
|------|------|
| 網紅 A 使用本系統 | 獲得 Vogue 觀點的內容 |
| 網紅 B 使用本系統 | 獲得相同的 Vogue 觀點內容 |
| 網紅 C 直接看 Vogue | 獲得相同的 Vogue 內容 |

**結果**：使用本系統的網紅與直接看 Vogue 的讀者沒有差異化

### 3.2 受眾覆蓋受限

```
Vogue 風格：高端時裝秀、奢侈品牌、名流穿搭
缺失風格：
  - 街頭潮流（Hypebeast, Highsnobiety）
  - 亞洲審美（Popbee）
  - 實用穿搭（Who What Wear）
  - 產業分析（BoF, WWD）
```

**結果**：只能吸引高端時尚愛好者，無法覆蓋更廣泛的受眾

### 3.3 對 Phase 5B（智能圖片匹配）的影響

```
Phase 5B 演算法：
ImageScore = 0.5K + 0.3T + 0.2Q

T = Trust Score（來源信任度），佔 30%

問題：
- 所有圖片來自同一來源（Vogue）
- Trust Score 全部相同，無法區分優劣
- 圖片風格單一（秀場照為主）
```

---

## 4. 建議修改方案

### 4.1 方案 A：按角色分配（推薦）

**核心思路**：將 RSS Feeds 按「角色」分類，每個角色各取 N 篇

```python
# 新的 Feed 結構
RSS_FEEDS_BY_ROLE = {
    Category.FASHION: {
        "authority": [      # 權威來源（高端趨勢）
            ("Vogue", "https://www.vogue.com/feed/rss"),
            ("Elle", "https://www.elle.com/rss/all.xml"),
        ],
        "streetwear": [     # 街頭潮流
            ("Hypebeast", "https://hypebeast.com/feed"),
            ("Highsnobiety", "https://www.highsnobiety.com/feeds/rss"),
        ],
        "asian": [          # 亞洲視角
            ("Popbee", "https://popbee.com/feed"),
        ],
        "industry": [       # 產業分析
            ("BoF", "https://www.businessoffashion.com/..."),
            ("WWD", "https://wwd.com/feed/"),
        ],
        "practical": [      # 實用穿搭
            ("Who What Wear", "https://www.whowhatwear.com/feeds.xml"),
            ("Fashionista", "https://fashionista.com/.rss/excerpt/"),
        ],
    }
}
```

**分配邏輯**（count=10）：

| 角色 | 來源 | 分配數量 | 風格 |
|------|------|---------|------|
| authority | Vogue, Elle | 2 | 高端時裝 |
| streetwear | Hypebeast, Highsnobiety | 2 | 街頭潮流 |
| asian | Popbee | 2 | 亞洲審美 |
| industry | BoF, WWD | 2 | 產業分析 |
| practical | Who What Wear, Fashionista | 2 | 實用穿搭 |
| **總計** | | **10** | **多元化** |

**修改後的收集邏輯**：

```python
async def _collect_from_rss(self, category: Category, count: int):
    topics = []
    feeds_by_role = RSS_FEEDS_BY_ROLE.get(category, {})
    
    # 計算每個角色應取多少篇
    roles_count = len(feeds_by_role)
    per_role = max(1, count // roles_count)
    remaining = count % roles_count
    
    for role_name, feeds in feeds_by_role.items():
        # 每個角色取 per_role 篇
        role_count = per_role + (1 if remaining > 0 else 0)
        remaining -= 1
        
        role_topics = await self._fetch_from_feeds(feeds, role_count)
        topics.extend(role_topics)
        
        logger.info(f"從 {role_name} 角色取得 {len(role_topics)} 篇")
    
    # 隨機打亂順序
    import random
    random.shuffle(topics)
    
    return topics[:count]
```

### 4.2 方案 B：並行請求 + 加權隨機

**核心思路**：並行請求所有 feeds，合併後加權隨機選取

```python
async def _collect_from_rss(self, category: Category, count: int):
    feeds = self.rss_feeds.get(category, [])[:10]  # 取前 10 個主要來源
    
    # 並行請求所有 feeds
    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks = [self._fetch_single_feed(client, url) for url in feeds]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 合併所有結果
    all_topics = []
    for i, result in enumerate(results):
        if isinstance(result, list) and len(result) > 0:
            # 每個來源最多取 3 篇
            for topic in result[:3]:
                topic["_source_index"] = i  # 記錄來源
                all_topics.append(topic)
    
    # 加權隨機選取（確保來源多樣性）
    selected = self._weighted_random_select(all_topics, count)
    
    return selected
```

### 4.3 方案比較

| 方案 | 優點 | 缺點 | 複雜度 |
|------|------|------|--------|
| **A: 按角色分配** | 可控、可預測、易於調整 | 需要手動定義角色 | 中 |
| **B: 並行+加權** | 自動化程度高 | 結果較不可預測 | 高 |

**建議採用方案 A**，因為：
1. 更符合「為網紅提供多元內容」的需求
2. 角色分配可根據客戶反饋調整
3. 實現和維護相對簡單

---

## 5. 附加建議

### 5.1 移除非專業新聞來源

目前每個分類都包含通用新聞來源（BBC, NYT, Guardian 等），建議：

| 行動 | 理由 |
|------|------|
| 從 Fashion 移除 BBC, NYT 等 | 它們不是時尚專業來源 |
| 從 Food 移除 BBC, NYT 等 | 它們不是美食專業來源 |
| 從 Trend 保留部分 | 趨勢類可以包含綜合新聞觀點 |

### 5.2 增加來源健康監控

```python
# 建議增加的監控指標
class FeedHealthMonitor:
    def track_feed_status(self, feed_url: str, status: str):
        """
        追蹤每個 feed 的健康狀態：
        - success: 成功返回
        - timeout: 超時
        - error: 錯誤
        - empty: 無內容
        """
        pass
    
    def get_feed_health_report(self) -> Dict:
        """返回所有 feed 的健康報告"""
        pass
```

### 5.3 增加來源多樣性指標

```python
# 在主題生成後記錄來源分布
{
    "generation_date": "2026-01-23",
    "category": "fashion",
    "total_topics": 10,
    "source_distribution": {
        "Vogue": 2,
        "Hypebeast": 2,
        "Popbee": 2,
        "BoF": 2,
        "Who What Wear": 2
    },
    "diversity_score": 1.0  # 0-1，越高越多元
}
```

---

## 6. 請求第三方專家審查

### 6.1 需要確認的問題

1. **方案選擇**：方案 A（按角色分配）是否適合本專案需求？
2. **角色定義**：Fashion/Food/Trend 的角色劃分是否合理？
3. **分配比例**：每個角色 2 篇（共 10 篇）的分配是否適當？
4. **新聞來源**：是否應該從專業分類中移除通用新聞來源？
5. **其他建議**：是否有更好的實現方式？

### 6.2 期望獲得的建議

- [ ] 方案選擇的建議
- [ ] 角色定義的優化建議
- [ ] 分配邏輯的改進建議
- [ ] 任何潛在風險的提醒
- [ ] 其他最佳實踐

---

## 7. 附錄

### 7.1 當前 RSS Feed 完整列表

<details>
<summary>點擊展開 Fashion Feeds（23 個）</summary>

| # | 來源 | URL | 類型 |
|---|------|-----|------|
| 1 | Vogue | https://www.vogue.com/feed/rss | 權威 |
| 2 | Elle | https://www.elle.com/rss/all.xml | 權威 |
| 3 | BoF | https://www.businessoffashion.com/... | 產業 |
| 4 | WWD | https://wwd.com/feed/ | 產業 |
| 5 | Hypebeast | https://hypebeast.com/feed | 街頭 |
| 6 | Highsnobiety | https://www.highsnobiety.com/feeds/rss | 街頭 |
| 7 | Who What Wear | https://www.whowhatwear.com/feeds.xml | 實用 |
| 8 | Popbee | https://popbee.com/feed | 亞洲 |
| 9 | Fashionista | https://fashionista.com/.rss/excerpt/ | 評論 |
| 10 | Cosmopolitan | https://www.cosmopolitan.com/rss/all.xml | 生活 |
| 11 | GQ | https://www.gq.com/feed/rss | 男裝 |
| 12 | Dazed | https://www.dazeddigital.com/rss | 藝術 |
| 13 | Marie Claire | https://www.marieclaire.com/rss/all.xml | 生活 |
| 14-23 | BBC, NYT, Guardian... | ... | 新聞 |

</details>

<details>
<summary>點擊展開 Food Feeds（19 個）</summary>

| # | 來源 | URL | 類型 |
|---|------|-----|------|
| 1 | Eater | https://www.eater.com/rss/index.xml | 餐廳 |
| 2 | Bon Appétit | https://www.bonappetit.com/feed/rss | 食譜 |
| 3 | Epicurious | https://www.epicurious.com/feed/rss | 食譜 |
| 4 | The Kitchn | https://www.thekitchn.com/main.rss | 家庭 |
| 5 | Simply Recipes | https://feeds.feedburner.com/simplyrecipes | 食譜 |
| 6 | Eat This | https://www.eatthis.com/feed/ | 健康 |
| 7 | The Takeout | https://www.thetakeout.com/feed/ | 文化 |
| 8 | Mashed | https://www.mashed.com/feed/ | 趣聞 |
| 9 | BBC Good Food | https://www.bbcgoodfood.com/feed | 國際 |
| 10-19 | BBC, NYT, Guardian... | ... | 新聞 |

</details>

<details>
<summary>點擊展開 Trend Feeds（30 個）</summary>

| # | 來源 | URL | 類型 |
|---|------|-----|------|
| 1 | WIRED | https://www.wired.com/feed/rss | 科技 |
| 2 | MIT Tech Review | https://www.technologyreview.com/feed/ | 前瞻 |
| 3 | TechCrunch | https://techcrunch.com/feed/ | 新創 |
| 4 | The Verge | https://www.theverge.com/rss/index.xml | 產品 |
| 5 | Engadget | https://www.engadget.com/rss.xml | 產品 |
| 6 | Ars Technica | https://arstechnica.com/feed/ | 分析 |
| 7 | Fast Company | https://www.fastcompany.com/latest/rss | 商業 |
| 8 | Vox | https://www.vox.com/rss/index.xml | 文化 |
| 9 | Rest of World | https://restofworld.org/feed/latest/ | 國際 |
| 10-30 | CNET, Mashable, BBC... | ... | 綜合 |

</details>

### 7.2 相關文件

- `backend/app/services/automation/topic_collector.py` - 主題收集器
- `backend/app/services/automation/scheduler.py` - 排程服務
- `backend/config/topic_generation.yaml` - 生成配置
- `docs/planning/04_Image_Matching_Logic.md` - Phase 5B 圖片匹配邏輯

---

**報告完成時間**：2026-01-23  
**期待回覆**：第三方專家建議  
**下一步**：根據建議實施修改

---

## 📝 第三方專家回覆區

> *請在此區域填寫您的建議和意見*

### 專家意見：

```
（待填寫）
```

### 建議的修改方向：

```
（待填寫）
```

### 其他注意事項：

```
（待填寫）
```

