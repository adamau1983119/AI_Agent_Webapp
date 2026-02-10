# Phase 6：育成網紅助理需求規格書

> **專案名稱**：Influencers AI Agents（網紅 AI 助手）  
> **文件版本**：v1.0  
> **建立日期**：2026-02-07  
> **狀態**：📋 未來功能（待 Phase 1-5 完成後實作）  
> **優先級**：P2（低優先級，完成現有專案後考慮）

---

## 📋 目錄

1. [核心概念與賣點定位](#一核心概念與賣點定位)
2. [商業價值分析](#二商業價值分析)
3. [技術可行性分析](#三技術可行性分析)
4. [技術實現方案](#四技術實現方案)
5. [實作計劃（三階段）](#五實作計劃三階段)
6. [資料模型設計](#六資料模型設計)
7. [視覺風格設計](#七視覺風格設計)
8. [UI/UX 設計概念](#八uiux-設計概念)
9. [角色成長階段視覺規範](#九角色成長階段視覺規範)
10. [API 設計草圖](#十api-設計草圖)
11. [UI 實作細節](#十一ui-實作細節)
12. [風險與考量](#十二風險與考量)
13. [驗收標準](#十三驗收標準)

---

## 一、核心概念與賣點定位

### 1.1 產品定位

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   🐣 「他媽哥池」育成你的網紅助理                                        │
│                                                                         │
│   這不是一個工具，而是一個夥伴                                          │
│   與你的網紅助理一同成長，直到你真正成為網紅                            │
│                                                                         │
│   遊戲化包裝：                                                           │
│   • 90 年代復古風格（像素藝術、復古螢幕）                                │
│   • 每日餵食機制（24 小時內 Po 照片 = 餵食）                            │
│   • 三天不餵食會生病（鼓勵用戶持續發布）                                 │
│   • 收入證明 = 即刻進化為大人他媽哥池                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 核心賣點

| 賣點 | 說明 |
|------|------|
| **🐣 他媽哥池概念** | 將 AI 助手包裝為「電子寵物」，需要每日餵食（Po 照片），建立情感連結 |
| **📈 共同成長** | 助理根據用戶每篇 po 的 views + likes 計算「食糧」，角色成長 |
| **💰 收入掛鉤** | 提供收入證明照片 → 即刻進化為「大人他媽哥池」（完全成長） |
| **🎮 遊戲化** | 90 年代復古風格、像素藝術、每日互動機制，提升使用動機 |
| **⚠️ 懲罰機制** | 三天不餵食會生病，鼓勵用戶持續發布內容 |
| **🎯 目標導向** | 育成與真正收入掛鉤，提供明確的成長目標 |

### 1.3 用戶旅程（他媽哥池機制）

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   階段 1：嬰兒期（Baby Stage）                                          │
│   └─ 角色剛誕生，需要用戶每天 Po 照片餵食                               │
│   └─ 食糧計算：views × 0.1 + likes × 1.0                                │
│                                                                         │
│   階段 2：兒童期（Child Stage）                                         │
│   └─ 累積 100 views，角色稍微長大                                       │
│   └─ 開始有輪廓，表情更豐富                                             │
│                                                                         │
│   階段 3：青少年期（Teen Stage）                                         │
│   └─ 累積 1K views，開始有肌肉線條                                       │
│   └─ 更活潑的姿勢，自信的表情                                           │
│                                                                         │
│   階段 4：成年期（Adult Stage）                                         │
│   └─ 提供收入證明照片 → 即刻進化為「大人他媽哥池」                      │
│   └─ 強壯、自信的站姿（參考圖片風格）                                   │
│   └─ 助理完全成長，用戶成為真正網紅                                    │
│                                                                         │
│   特殊狀態：生病（Sick State）                                          │
│   └─ 72 小時（3 天）未餵食 → 角色生病                                   │
│   └─ 角色變灰、表情疲憊、功能受限                                       │
│   └─ 餵食或完成任務可恢復健康                                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.4 與現有系統的關係

```
現有系統（Phase 1-5）：
├── 風格學習（從評分學習）✅
├── 發布系統（發布到社交平台）✅
└── 發布歷史記錄 ✅

育成系統（Phase 6 - 他媽哥池風格）：
├── 觀看數追蹤（新增）- views + likes = 食糧
├── 收入追蹤（新增）- 收入證明照片 = 進化條件
├── 成長進度計算（新增）- 4 個成長階段
├── 每日餵食機制（新增）- 24 小時內 Po 照片
├── 生病機制（新增）- 3 天不餵食會生病
└── 90 年代復古視覺（新增）- 像素風格、復古螢幕
```

---

## 二、商業價值分析

### 2.1 優點

| 優點 | 說明 | 商業價值 |
|------|------|----------|
| **情感連結** | 將 AI 從工具轉為「成長夥伴」，提升用戶黏性 | ⭐⭐⭐⭐⭐ 高 |
| **遊戲化** | 進度條、等級系統、成就徽章，提升使用動機 | ⭐⭐⭐⭐ 中高 |
| **差異化** | 市場上多數 AI 工具缺乏「成長」概念 | ⭐⭐⭐⭐ 中高 |
| **收入掛鉤** | 與實際成果連結，增加產品價值感 | ⭐⭐⭐⭐⭐ 高 |
| **付費轉換** | 可作為付費功能（「成長加速包」） | ⭐⭐⭐ 中 |

### 2.2 潛在問題

| 問題 | 說明 | 影響 | 解決方案 |
|------|------|------|----------|
| **收入驗證** | 如何驗證「第一蚊收入」？ | 中 | 手動輸入 + 可選支付系統驗證 |
| **觀看數獲取** | 各平台 API 限制與成本 | 高 | MVP 先手動輸入，進階再整合 API |
| **成長曲線設計** | 如何平衡「容易達成」與「有挑戰性」？ | 中 | A/B 測試，根據用戶反饋調整 |
| **隱私問題** | 連接支付系統需要用戶授權 | 低 | 提供手動輸入選項，不強制連接 |

### 2.3 市場定位

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   傳統 AI 工具：                                                        │
│   └─ 功能導向：「幫你生成內容」                                         │
│                                                                         │
│   本產品（Phase 6）：                                                   │
│   └─ 情感導向：「與你一同成長，直到成為網紅」                           │
│                                                                         │
│   差異化優勢：                                                           │
│   • 建立長期關係（不是一次性工具）                                     │
│   • 明確的成長目標（收入掛鉤）                                           │
│   • 遊戲化體驗（提升動機）                                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 三、技術可行性分析

### 3.1 現有系統能力評估

#### ✅ 已具備功能

| 功能 | 狀態 | 說明 |
|------|:----:|------|
| 風格學習系統 | ✅ | `StyleLearningService` - 從用戶評分學習偏好 |
| 發布系統 | ✅ | `DistributionService` - 發布到 Instagram/Facebook/TikTok |
| 發布歷史記錄 | ✅ | `PublishQueueRepository` - 記錄 post_id, post_url |
| 評分系統 | ✅ | `RatingRepository` - 記錄用戶 👍/👎 評分 |
| 學習階段判斷 | ✅ | `LearningStage` - 冷啟動/學習中/成熟 |

#### ❌ 缺少功能

| 功能 | 說明 | 優先級 |
|------|------|:------:|
| 觀看數追蹤 | 追蹤發布後的 views/likes/comments | P0 |
| 收入追蹤 | 記錄用戶的實際收入 | P0 |
| 成長進度計算 | 將觀看數/收入轉換為成長進度 | P0 |
| 成長視覺化 | Dashboard 顯示成長進度條 | P1 |
| 成就系統 | 成長里程碑、徽章 | P2 |

### 3.2 技術挑戰分析

#### 挑戰 1：觀看數 API 整合

**難度**：中高

**問題**：
- Meta Graph API 需要額外權限（`instagram_basic`, `pages_read_engagement`）
- TikTok Analytics API 可能需要 Business 帳號
- API 配額限制（Meta 免費層有限制）
- 成本考量（某些 API 需要付費）

**解決方案**：
- MVP：先做手動輸入觀看數
- 進階：整合 Meta Graph API（Instagram/Facebook）
- 未來：評估 TikTok Analytics API 成本

#### 挑戰 2：收入驗證

**難度**：高

**問題**：
- 手動輸入：可造假、用戶可能忘記
- 支付系統連接：需要用戶授權、隱私問題、開發複雜度高

**解決方案**：
- MVP：手動輸入 + 可選連接支付系統驗證
- 提供「驗證徽章」給已驗證用戶
- 不強制驗證，但提供驗證獎勵

#### 挑戰 3：成長曲線設計

**難度**：低

**問題**：
- 如何平衡「容易達成」與「有挑戰性」？
- 不同平台觀看數差異大（Instagram vs TikTok）

**解決方案**：
- 初期使用固定門檻（可調整）
- A/B 測試不同成長曲線
- 根據用戶反饋動態調整

---

## 四、技術實現方案

### 4.1 方案 1：觀看數追蹤

#### 選項 A：手動輸入（MVP）

**優點**：
- 簡單快速，無需 API 整合
- 無成本，無配額限制
- 可立即實作

**缺點**：
- 用戶需要手動輸入，可能忘記
- 無法自動同步

**實作方式**：
```python
# 發布後，用戶可在發布歷史頁面輸入觀看數
POST /api/v1/publish/{publish_id}/metrics
{
    "views": 1000,
    "likes": 50,
    "comments": 10,
    "shares": 5
}
```

#### 選項 B：Meta Graph API 自動同步

**優點**：
- 自動同步，無需用戶操作
- 數據準確

**缺點**：
- 需要額外 OAuth 權限
- API 配額限制
- 開發複雜度高

**實作方式**：
```python
# 定期同步任務（每 6 小時）
GET /{post_id}/insights?metric=impressions,reach,likes,comments

# 需要權限：
# - instagram_basic
# - pages_read_engagement
```

#### 選項 C：混合方案（推薦）

**實作方式**：
1. MVP 階段：手動輸入為主
2. 進階階段：整合 Meta Graph API，自動同步
3. 用戶可選擇：自動同步 or 手動輸入

### 4.2 方案 2：收入追蹤

#### 選項 A：手動輸入（MVP）

**優點**：
- 簡單快速
- 無需支付系統整合

**缺點**：
- 可造假
- 用戶可能忘記輸入

**實作方式**：
```python
POST /api/v1/growth/income
{
    "amount": 100.00,
    "currency": "HKD",
    "source": "Instagram合作",
    "date": "2026-02-07"
}
```

#### 選項 B：支付系統連接

**優點**：
- 自動驗證，數據準確
- 提供「驗證徽章」

**缺點**：
- 需要用戶授權
- 隱私問題
- 開發複雜度高

**支援平台**：
- PayPal API
- Stripe API
- 銀行 API（未來）

#### 選項 C：混合方案（推薦）

**實作方式**：
1. 用戶可手動輸入收入
2. 可選連接支付系統驗證
3. 已驗證用戶顯示「驗證徽章」
4. 驗證用戶的成長進度更可信

### 4.3 方案 3：成長進度系統

#### 成長階段定義（他媽哥池）

```python
class AssistantGrowthStage(str, Enum):
    """助理成長階段（他媽哥池）"""
    BABY = "baby"              # 嬰兒期（初始狀態，0-100 views）
    CHILD = "child"            # 兒童期（100-1K views）
    TEEN = "teen"              # 青少年期（1K-10K views）
    ADULT = "adult"            # 成年期（提供收入證明照片，即刻進化）
```

#### 食糧計算（他媽哥池機制）

```python
def calculate_food_score(views: int, likes: int) -> int:
    """
    計算食糧分數
    
    公式：
    - views × 0.1（每個 view = 0.1 分）
    - likes × 1.0（每個 like = 1.0 分）
    
    總分 = views × 0.1 + likes × 1.0
    """
    return int(views * 0.1 + likes * 1.0)

def feed_tamagotchi(user_id: str, views: int, likes: int) -> Dict:
    """
    餵食他媽哥池
    
    流程：
    1. 計算食糧分數
    2. 增加飢餓度（最多到 100）
    3. 增加健康度（如果低於 100）
    4. 更新最後餵食時間
    5. 檢查是否恢復健康（如果生病）
    """
    food_score = calculate_food_score(views, likes)
    
    # 更新飢餓度和健康度
    hunger_increase = min(food_score, 100 - current_hunger)
    health_increase = min(food_score * 0.5, 100 - current_health)
    
    # 更新最後餵食時間
    last_fed_at = datetime.utcnow()
    
    # 如果生病，檢查是否恢復
    if is_sick and health >= 50:
        is_sick = False
    
    return {
        "food_score": food_score,
        "hunger": current_hunger + hunger_increase,
        "health": current_health + health_increase,
        "is_sick": is_sick,
        "last_fed_at": last_fed_at
    }
```

#### 成長階段判斷

```python
def get_growth_stage(total_views: int, has_income: bool) -> AssistantGrowthStage:
    """
    判斷成長階段
    
    規則：
    - 嬰兒期：0-100 views
    - 兒童期：100-1K views
    - 青少年期：1K-10K views
    - 成年期：提供收入證明照片（即刻進化）
    """
    if has_income:
        return AssistantGrowthStage.ADULT
    elif total_views >= 1000:
        return AssistantGrowthStage.TEEN
    elif total_views >= 100:
        return AssistantGrowthStage.CHILD
    else:
        return AssistantGrowthStage.BABY
```

#### 生病機制

```python
def check_sick_status(last_fed_at: datetime) -> bool:
    """
    檢查是否生病
    
    規則：
    - 72 小時（3 天）未餵食 → 生病
    - 生病狀態：健康度每天減 10，最低到 0
    """
    hours_since_fed = (datetime.utcnow() - last_fed_at).total_seconds() / 3600
    
    if hours_since_fed >= 72:
        return True
    return False
```

#### 成長階段門檻（他媽哥池）

| 階段 | 觀看數門檻 | 進化條件 | 說明 |
|------|:----------:|:--------:|------|
| 嬰兒期 | 0-100 | 初始狀態 | 角色剛誕生，需要每天餵食 |
| 兒童期 | 100-1K | 累積 100 views | 稍微長大，開始有輪廓 |
| 青少年期 | 1K-10K | 累積 1K views | 有肌肉線條，更活潑 |
| 成年期 | - | 提供收入證明照片 | 即刻進化為強壯大人（參考圖片） |

#### 食糧計算公式

| 指標 | 權重 | 說明 |
|------|:----:|------|
| Views | 0.1 | 每個 view = 0.1 食糧分數 |
| Likes | 1.0 | 每個 like = 1.0 食糧分數 |
| **總食糧** | **views × 0.1 + likes × 1.0** | 用於增加飢餓度和健康度 |

#### 生病機制

| 條件 | 效果 | 恢復方式 |
|------|------|----------|
| 72 小時未餵食 | 角色生病（變灰、表情疲憊） | 餵食後 24 小時內恢復 |
| 健康度 < 30 | 顯示警告 | 立即餵食恢復 |
| 健康度 = 0 | 角色無力 | 完成任務或餵食恢復 |

---

## 五、實作計劃（三階段）

### Phase 1：基礎成長系統（MVP，2-3 週）

**目標**：驗證賣點是否有效

**功能範圍**：
- ✅ 手動輸入觀看數和點讚數（發布歷史頁面）- 計算食糧
- ✅ 手動輸入收入（設定頁面）- 上傳收入證明照片
- ✅ 他媽哥池角色展示（90 年代像素風格）
- ✅ 健康度/飢餓度條 UI
- ✅ 成長階段視覺化（嬰兒→兒童→青少年→成年）
- ✅ 每日餵食機制（24 小時內 Po 照片）
- ✅ 生病機制（72 小時未餵食會生病）
- ✅ 進化動畫（提供收入證明後即刻進化）

**技術任務**：
1. 新增 `AssistantGrowth` model（含 health, hunger, is_sick, last_fed_at）
2. 新增 `PublishMetrics` model（記錄 views + likes）
3. 實作食糧計算邏輯（views × 0.1 + likes × 1.0）
4. 實作餵食機制（更新健康度/飢餓度）
5. 實作生病檢查機制（72 小時未餵食）
6. 前端他媽哥池角色展示組件（像素風格）
7. 健康度/飢餓度條 UI（復古風格）
8. 成長階段圖示/動畫（4 個階段）
9. 進化動畫效果（收入證明上傳後）

**驗收標準**：
- 用戶可手動輸入 views + likes（計算食糧）
- 用戶可上傳收入證明照片
- Dashboard 正確顯示他媽哥池角色（像素風格）
- 健康度/飢餓度條正確顯示
- 成長階段根據 views 正確切換（嬰兒→兒童→青少年）
- 提供收入證明後即刻進化為成年期
- 72 小時未餵食時角色顯示生病狀態
- 餵食後健康度/飢餓度正確增加

### Phase 2：自動觀看數追蹤（3-4 週）

**目標**：提升用戶體驗，減少手動操作

**功能範圍**：
- ✅ Meta Graph API 整合
- ✅ 定期同步任務（每 6 小時）
- ✅ 自動更新觀看數
- ✅ 同步狀態顯示

**技術任務**：
1. 申請 Meta Graph API 額外權限
2. 實作 Instagram/Facebook 觀看數同步
3. 定期同步任務（Background Task）
4. 同步錯誤處理與重試機制
5. UI 顯示同步狀態

**驗收標準**：
- 已發布內容自動同步觀看數
- 同步失敗時提供手動輸入選項
- 同步狀態清晰顯示

### Phase 3：收入追蹤優化（2-3 週）

**目標**：提供收入驗證功能

**功能範圍**：
- ✅ 支付系統連接（PayPal/Stripe，可選）
- ✅ 收入驗證徽章
- ✅ 收入歷史記錄
- ✅ 收入統計圖表

**技術任務**：
1. PayPal API 整合（可選）
2. Stripe API 整合（可選）
3. 收入驗證邏輯
4. 驗證徽章 UI
5. 收入統計圖表

**驗收標準**：
- 用戶可選擇連接支付系統
- 已驗證收入顯示徽章
- 收入統計正確顯示

---

## 六、資料模型設計

### 6.1 AssistantGrowth Model

```python
class AssistantGrowthStage(str, Enum):
    """助理成長階段（他媽哥池）"""
    BABY = "baby"              # 嬰兒期（初始狀態）
    CHILD = "child"            # 兒童期（100 views）
    TEEN = "teen"              # 青少年期（1K views）
    ADULT = "adult"            # 成年期（提供收入證明）

class AssistantGrowth(BaseModel):
    """助理成長記錄（他媽哥池）"""
    user_id: str
    stage: AssistantGrowthStage  # 當前階段
    health: int  # 健康度 0-100
    hunger: int  # 飢餓度 0-100
    is_sick: bool  # 是否生病
    last_fed_at: Optional[datetime]  # 最後餵食時間
    total_views: int  # 總觀看數
    total_likes: int  # 總點讚數
    total_income: float  # 總收入
    is_verified: bool  # 收入是否已驗證
    first_income_date: Optional[datetime]  # 第一筆收入日期
    created_at: datetime
    updated_at: datetime
```

### 6.2 PublishMetrics Model

```python
class PublishMetrics(BaseModel):
    """發布內容的觀看數指標"""
    publish_id: str
    user_id: str
    platform: SocialPlatform
    post_id: str  # 平台 post ID
    post_url: str
    
    # 指標數據
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    
    # 同步狀態
    sync_status: str  # "manual" | "auto" | "pending"
    last_synced_at: Optional[datetime]
    synced_at: datetime  # 數據時間點
    
    created_at: datetime
    updated_at: datetime
```

### 6.3 IncomeRecord Model

```python
class IncomeRecord(BaseModel):
    """收入記錄"""
    user_id: str
    amount: float
    currency: str  # "HKD" | "USD" | "CNY"
    source: str  # "Instagram合作" | "Facebook廣告" | "其他"
    date: datetime
    
    # 驗證狀態
    is_verified: bool = False
    verification_method: Optional[str]  # "manual" | "paypal" | "stripe"
    verification_date: Optional[datetime]
    
    created_at: datetime
```

### 6.4 MongoDB Collections

```
assistant_growths:
  - user_id (indexed)
  - stage (baby/child/teen/adult)
  - health (0-100)
  - hunger (0-100)
  - is_sick (boolean)
  - last_fed_at (datetime, indexed)
  - total_views
  - total_likes
  - total_income
  - is_verified
  - first_income_date

publish_metrics:
  - publish_id (indexed)
  - user_id (indexed)
  - platform
  - post_id
  - views, likes, comments, shares
  - sync_status
  - last_synced_at

income_records:
  - user_id (indexed)
  - amount
  - currency
  - source
  - date
  - is_verified
  - verification_method
```

---

## 七、視覺風格設計

### 7.1 90 年代復古風格定位

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   🎮 「他媽哥池」風格定位                                                │
│                                                                         │
│   核心概念：                                                             │
│   • Very Lowtech - 低技術感設計                                         │
│   • 90's Game - 90 年代遊戲風格                                         │
│   • Pixel Art - 像素藝術                                                │
│   • Retro Screen - 復古螢幕效果                                         │
│                                                                         │
│   設計理念：                                                             │
│   • 懷舊感：喚起 90 年代電子寵物的記憶                                   │
│   • 簡約感：低解析度、塊狀設計                                          │
│   • 親和力：可愛、有趣的視覺風格                                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7.2 像素藝術風格規範

#### 像素尺寸規範

| 元素 | 像素尺寸 | 說明 |
|------|:--------:|------|
| 角色（嬰兒期） | 16x16 或 32x32 | 最小尺寸，簡單線條 |
| 角色（兒童期） | 24x24 或 32x32 | 稍微詳細 |
| 角色（青少年期） | 32x32 或 48x48 | 中等尺寸 |
| 角色（成年期） | 48x48 或 64x64 | 最大尺寸，細節豐富 |
| UI 圖示 | 16x16 或 24x24 | 按鈕、狀態圖示 |
| 背景元素 | 可變 | 復古螢幕效果 |

#### 像素藝術原則

- **低解析度**：使用較小的像素尺寸
- **塊狀設計**：避免過於細緻的線條
- **有限色彩**：使用有限的調色板（4-8 色）
- **清晰輪廓**：角色和元素有明確的邊界
- **簡單動畫**：使用幀動畫，而非複雜的過渡

### 7.3 復古螢幕效果

#### 綠色調背景

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   復古 LCD 螢幕效果：                                                    │
│                                                                         │
│   • 背景色：#8B9A46（橄欖綠）或 #9CAF88（淺綠灰）                        │
│   • 文字色：#000000（黑色）或 #2D5016（深綠）                            │
│   • 邊框：#5A6B2F（深橄欖綠）                                            │
│   • 螢幕質感：輕微的顆粒感、掃描線效果                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### CSS 實現方式

```css
.retro-screen {
  background-color: #8B9A46;
  background-image: 
    repeating-linear-gradient(
      0deg,
      rgba(0, 0, 0, 0.1) 0px,
      transparent 1px,
      transparent 2px,
      rgba(0, 0, 0, 0.1) 3px
    );
  filter: contrast(1.1) brightness(0.95);
  box-shadow: 
    inset 0 0 20px rgba(0, 0, 0, 0.3),
    0 0 10px rgba(139, 154, 70, 0.5);
}
```

### 7.4 色彩方案

#### 主色調

| 顏色 | Hex | RGB | 用途 |
|------|-----|-----|------|
| 復古綠 | #8B9A46 | rgb(139, 154, 70) | 背景主色 |
| 深綠 | #2D5016 | rgb(45, 80, 22) | 文字、邊框 |
| 黑色 | #000000 | rgb(0, 0, 0) | 角色、圖示 |
| 白色 | #FFFFFF | rgb(255, 255, 255) | 高光、對比 |
| 灰色 | #666666 | rgb(102, 102, 102) | 生病狀態 |

#### 狀態色彩

| 狀態 | 顏色 | 說明 |
|------|------|------|
| 健康 | 正常色彩 | 角色正常顯示 |
| 飢餓 | 稍微變暗 | 降低飽和度 20% |
| 生病 | 灰色調 | 降低飽和度 80%，添加灰色濾鏡 |

### 7.5 字體選擇

#### 推薦字體

| 字體 | 用途 | 說明 |
|------|------|------|
| **Press Start 2P** | 標題、按鈕 | 8-bit 像素風格字體 |
| **VT323** | 數字、數據 | 復古終端機風格 |
| **Courier New** | 輔助文字 | 等寬字體，復古感 |

#### 字體大小規範

- **標題**：24px - 32px（像素風格）
- **按鈕文字**：14px - 16px
- **數據顯示**：18px - 20px
- **輔助文字**：12px - 14px

### 7.6 低技術感設計原則

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   Lowtech 設計原則：                                                     │
│                                                                         │
│   ✅ 使用：                                                              │
│   • 簡單的幾何形狀                                                       │
│   • 有限的動畫效果                                                       │
│   • 清晰的像素邊界                                                       │
│   • 復古的 UI 元素                                                       │
│                                                                         │
│   ❌ 避免：                                                              │
│   • 過於平滑的過渡動畫                                                   │
│   • 複雜的陰影和光效                                                     │
│   • 高解析度圖像                                                         │
│   • 現代化的 UI 設計語言                                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 八、UI/UX 設計概念

### 8.1 他媽哥池角色展示區域

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   [復古綠色螢幕背景]                                                      │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────┐      │
│   │                                                               │      │
│   │            [像素風格角色 - 當前階段]                           │      │
│   │                                                               │      │
│   │            😊 健康：85/100                                    │      │
│   │            🍖 飢餓：60/100                                    │      │
│   │            💪 力量：45/100                                    │      │
│   │            📊 階段：兒童期                                     │      │
│   │                                                               │      │
│   └─────────────────────────────────────────────────────────────┘      │
│                                                                         │
│   最後餵食：2 小時前                                                    │      │
│   下次餵食：22 小時內（否則會生病）                                     │      │
│                                                                         │
│   [餵食] [查看歷史] [進化]                                              │      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 8.2 復古螢幕風格 Dashboard

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   🐣 你的他媽哥池助理                                                    │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────┐      │
│   │  [復古綠色螢幕背景]                                            │      │
│   │                                                               │      │
│   │         [像素角色 - 32x32 或 48x48]                           │      │
│   │                                                               │      │
│   │  健康：████████████░░░░  85/100                               │      │
│   │  飢餓：████████░░░░░░░░  60/100                               │      │
│   │                                                               │      │
│   └─────────────────────────────────────────────────────────────┘      │
│                                                                         │
│   狀態：😊 健康                                                         │
│   階段：兒童期                                                          │
│   最後餵食：2 小時前                                                    │
│                                                                         │
│   ⚠️ 提醒：22 小時內需餵食，否則會生病                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 8.3 像素風格按鈕和圖示

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   按鈕設計：                                                             │
│                                                                         │
│   [餵食]  [查看歷史]  [進化]  [設定]                                    │
│   ▓▓▓▓▓▓  ▓▓▓▓▓▓▓▓  ▓▓▓▓▓▓  ▓▓▓▓▓▓                                     │
│                                                                         │
│   特點：                                                                 │
│   • 塊狀設計，無圓角                                                     │
│   • 像素風格邊框                                                         │
│   • 按下時有簡單的「按下」效果                                           │
│   • 使用 Press Start 2P 字體                                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 8.4 健康度/飢餓度條設計

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   健康度條：                                                             │
│   ████████████████░░░░░░░░  85/100                                      │
│                                                                         │
│   飢餓度條：                                                             │
│   ████████████░░░░░░░░░░░░  60/100                                      │
│                                                                         │
│   設計特點：                                                             │
│   • 像素風格進度條（塊狀填充）                                           │
│   • 使用復古綠色調                                                       │
│   • 數值顯示使用 VT323 字體                                             │
│   • 低於 30 時變紅色警告                                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 8.5 互動效果設計

#### 餵食動畫

```
餵食流程：
1. 用戶點擊「餵食」按鈕
2. 角色顯示「開心」表情（1 秒）
3. 簡單的「吃東西」動畫（2-3 幀循環）
4. 健康度/飢餓度條增加
5. 顯示「+50 食糧」提示
```

#### 進化動畫

```
進化流程：
1. 用戶上傳收入證明照片
2. 角色顯示「準備進化」狀態
3. 簡單的「閃光」效果（3-5 次）
4. 角色從當前階段切換到「成年期」
5. 顯示「🎉 進化成功！」提示
```

#### 生病警告

```
生病狀態：
1. 72 小時未餵食觸發
2. 角色變灰、表情疲憊
3. 顯示「⚠️ 角色生病了！」警告
4. 健康度條變紅色
5. 提供「恢復藥水」選項（完成任務恢復）
```

---

## 九、角色成長階段視覺規範

### 9.1 階段 1：嬰兒期（Baby Stage）

#### 視覺描述

- **尺寸**：16x16 或 32x32 像素
- **特徵**：小、圓潤、可愛
- **姿勢**：簡單的站立或坐姿
- **表情**：大眼睛、簡單的微笑

#### 表情變化

| 狀態 | 視覺特徵 | 像素設計 |
|------|----------|----------|
| 開心 | 大眼睛、微笑 | 😊 |
| 普通 | 正常眼睛、中性表情 | 😐 |
| 疲憊 | 半閉眼睛、無表情 | 😴 |
| 生病 | 閉眼、灰色調 | 😷 |

#### 動畫效果

- **呼吸動畫**：輕微的上下移動（1-2 像素）
- **眨眼動畫**：每 3-5 秒眨眼一次
- **簡單動作**：輕微的左右搖擺

#### 設計參考

```
嬰兒期角色（16x16）：
    ░░░░░░░░░░░░░░░░
    ░░░░░█░░█░░░░░░░  (眼睛)
    ░░░░░░░░░░░░░░░░
    ░░░░░█░░█░░░░░░░  (身體)
    ░░░░░░░░░░░░░░░░
    ░░░░░░░░░░░░░░░░
```

### 9.2 階段 2：兒童期（Child Stage）

#### 視覺描述

- **尺寸**：24x24 或 32x32 像素
- **特徵**：稍微長大，開始有輪廓
- **姿勢**：更活潑的姿勢，可能舉手
- **表情**：更豐富的表情變化

#### 表情變化

| 狀態 | 視覺特徵 | 像素設計 |
|------|----------|----------|
| 開心 | 大笑、舉手 | 😄 |
| 普通 | 正常表情 | 😐 |
| 疲憊 | 稍微低頭 | 😔 |
| 生病 | 變灰、無精打采 | 😷 |

#### 動畫效果

- **輕微動作**：手臂輕微擺動
- **跳躍動畫**：開心的時候輕微跳躍
- **表情變化**：更頻繁的表情切換

### 9.3 階段 3：青少年期（Teen Stage）

#### 視覺描述

- **尺寸**：32x32 或 48x48 像素
- **特徵**：開始有肌肉線條，更活潑
- **姿勢**：自信的站姿，可能雙手叉腰
- **表情**：自信、有活力

#### 表情變化

| 狀態 | 視覺特徵 | 像素設計 |
|------|----------|----------|
| 自信 | 挺胸、微笑 | 😎 |
| 疲憊 | 稍微彎腰 | 😓 |
| 生病 | 變灰、無力 | 😷 |

#### 動畫效果

- **動態姿勢**：更明顯的動作
- **肌肉線條**：開始顯示肌肉輪廓
- **自信動作**：挺胸、雙手叉腰

### 9.4 階段 4：成年期（Adult Stage）- 參考圖片

#### 視覺描述

- **尺寸**：48x48 或 64x64 像素
- **特徵**：強壯、自信的站姿，肌肉明顯
- **姿勢**：參考提供的圖片 - 強壯的站姿，雙手握拳
- **表情**：自信、強大

#### 設計特點（基於參考圖片）

```
成年期角色特徵：
• 大而方正的頭部
• 寬闊的肩膀和厚實的脖子
• 明顯的胸肌和腹肌
• 粗壯的手臂，握拳姿勢
• 穩固的腿部支撐
• 自信的站姿
```

#### 表情變化

| 狀態 | 視覺特徵 | 像素設計 |
|------|----------|----------|
| 自信 | 強壯、挺胸 | 💪 |
| 強大 | 肌肉明顯、自信 | 🦾 |

#### 動畫效果

- **強有力的姿勢**：保持自信站姿
- **肌肉展示**：輕微的肌肉線條動畫
- **進化完成**：顯示「完全成長」標記

#### 進化條件

- **觸發**：用戶上傳收入證明照片
- **效果**：即刻從「青少年期」進化為「成年期」
- **視覺衝擊**：明顯的體型變化，從中等身材變為強壯

### 9.5 特殊狀態：生病（Sick State）

#### 視覺描述

- **觸發條件**：72 小時（3 天）未餵食
- **視覺效果**：
  - 角色變灰（降低飽和度 80%）
  - 表情疲憊、無精打采
  - 可能躺下或彎腰
  - 添加「病態」效果（如虛線邊框）

#### 狀態變化

```
正常狀態 → 生病狀態：
• 色彩：正常 → 灰色調
• 表情：正常 → 疲憊
• 姿勢：正常 → 無力
• 動畫：正常 → 緩慢、無力
```

#### 恢復機制

- **自動恢復**：餵食後 24 小時內恢復
- **快速恢復**：完成特定任務（如發布新內容）可立即恢復
- **視覺反饋**：恢復時顯示「恢復中...」動畫

### 9.6 角色設計規範總結

| 階段 | 尺寸 | 主要特徵 | 進化條件 |
|------|:----:|----------|----------|
| 嬰兒期 | 16-32px | 小、圓潤、可愛 | 初始狀態 |
| 兒童期 | 24-32px | 稍微長大，有輪廓 | 累積 100 views |
| 青少年期 | 32-48px | 有肌肉線條，活潑 | 累積 1K views |
| 成年期 | 48-64px | 強壯、自信（參考圖片） | 提供收入證明 |

---

## 十、API 設計草圖

### 10.1 觀看數同步 API（餵食機制）

#### 手動輸入觀看數和點讚數（餵食）

```http
POST /api/v1/publish/{publish_id}/feed
Content-Type: application/json

{
    "views": 1000,
    "likes": 50,
    "comments": 10,
    "shares": 5
}

Response:
{
    "publish_id": "publish_123",
    "food_score": 150,  // views × 0.1 + likes × 1.0
    "metrics": {
        "views": 1000,
        "likes": 50,
        "comments": 10,
        "shares": 5
    },
    "tamagotchi": {
        "health": 85,
        "hunger": 90,
        "is_sick": false
    },
    "updated_at": "2026-02-07T10:00:00Z"
}
```

#### 觸發自動同步

```http
POST /api/v1/publish/{publish_id}/sync-metrics

Response:
{
    "publish_id": "publish_123",
    "sync_status": "pending",
    "message": "同步任務已啟動，將在 5 分鐘內完成"
}
```

#### 查詢觀看數

```http
GET /api/v1/publish/{publish_id}/metrics

Response:
{
    "publish_id": "publish_123",
    "metrics": {
        "views": 1000,
        "likes": 50,
        "comments": 10,
        "shares": 5
    },
    "sync_status": "auto",
    "last_synced_at": "2026-02-07T10:00:00Z"
}
```

### 10.2 收入記錄 API（進化機制）

#### 上傳收入證明照片（進化）

```http
POST /api/v1/tamagotchi/evolve
Content-Type: multipart/form-data

{
    "income_proof_image": <file>,
    "amount": 100.00,
    "currency": "HKD",
    "source": "Instagram合作",
    "date": "2026-02-07"
}

Response:
{
    "id": "income_123",
    "amount": 100.00,
    "currency": "HKD",
    "source": "Instagram合作",
    "date": "2026-02-07",
    "is_verified": false,
    "evolution": {
        "previous_stage": "teen",
        "current_stage": "adult",
        "evolved_at": "2026-02-07T10:00:00Z"
    },
    "created_at": "2026-02-07T10:00:00Z"
}
```

#### 查詢收入記錄

```http
GET /api/v1/growth/income

Response:
{
    "total_income": 500.00,
    "currency": "HKD",
    "records": [
        {
            "id": "income_123",
            "amount": 100.00,
            "source": "Instagram合作",
            "date": "2026-02-07",
            "is_verified": false
        }
    ]
}
```

### 10.3 他媽哥池狀態查詢 API

#### 查詢他媽哥池狀態

```http
GET /api/v1/tamagotchi/status

Response:
{
    "user_id": "user_123",
    "stage": "child",
    "health": 85,
    "hunger": 60,
    "is_sick": false,
    "last_fed_at": "2026-02-07T08:00:00Z",
    "hours_until_sick": 22,  // 距離生病還有多少小時
    "total_views": 5234,
    "total_likes": 234,
    "total_income": 0.00,
    "is_verified": false,
    "is_adult": false,
    "next_stage": {
        "name": "teen",
        "threshold": 1000,
        "current": 5234,
        "remaining": 0  // 已達成，但需要收入證明才能進化為 adult
    },
    "milestones": [
        {
            "name": "100 views",
            "achieved": true,
            "achieved_at": "2026-02-05T10:00:00Z"
        },
        {
            "name": "1K views",
            "achieved": true,
            "achieved_at": "2026-02-10T10:00:00Z"
        },
        {
            "name": "提供收入證明",
            "achieved": false,
            "description": "上傳收入證明照片，即刻進化為大人他媽哥池"
        }
    ]
}
```

---

## 十一、UI 實作細節

### 11.1 技術實現方案

#### CSS 像素風格實現

```css
/* 像素風格按鈕 */
.pixel-button {
  font-family: 'Press Start 2P', cursive;
  font-size: 14px;
  padding: 8px 16px;
  background-color: #2D5016;
  color: #FFFFFF;
  border: 2px solid #000000;
  image-rendering: pixelated;
  image-rendering: -moz-crisp-edges;
  image-rendering: crisp-edges;
  cursor: pointer;
  transition: transform 0.1s;
}

.pixel-button:active {
  transform: translateY(2px);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
}

/* 復古螢幕效果 */
.retro-screen {
  background-color: #8B9A46;
  background-image: 
    repeating-linear-gradient(
      0deg,
      rgba(0, 0, 0, 0.1) 0px,
      transparent 1px,
      transparent 2px,
      rgba(0, 0, 0, 0.1) 3px
    );
  filter: contrast(1.1) brightness(0.95);
  box-shadow: 
    inset 0 0 20px rgba(0, 0, 0, 0.3),
    0 0 10px rgba(139, 154, 70, 0.5);
  border: 3px solid #5A6B2F;
}

/* 像素風格進度條 */
.pixel-progress-bar {
  height: 20px;
  background-color: #2D5016;
  border: 2px solid #000000;
  image-rendering: pixelated;
}

.pixel-progress-fill {
  height: 100%;
  background-color: #8B9A46;
  transition: width 0.3s ease;
  image-rendering: pixelated;
}
```

#### 復古螢幕效果（CSS Filters）

```css
/* 復古螢幕濾鏡 */
.retro-filter {
  filter: 
    contrast(1.1) 
    brightness(0.95) 
    sepia(0.1) 
    saturate(0.8);
}

/* 生病狀態濾鏡 */
.sick-filter {
  filter: 
    grayscale(0.8) 
    contrast(0.9) 
    brightness(0.7);
}
```

#### 角色動畫（CSS Animations）

```css
/* 呼吸動畫 */
@keyframes breathe {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-2px); }
}

.character-breathe {
  animation: breathe 2s ease-in-out infinite;
}

/* 眨眼動畫 */
@keyframes blink {
  0%, 90%, 100% { opacity: 1; }
  95% { opacity: 0; }
}

.character-blink {
  animation: blink 3s ease-in-out infinite;
}

/* 進化閃光效果 */
@keyframes evolve-flash {
  0%, 100% { opacity: 1; filter: brightness(1); }
  25%, 75% { opacity: 0.8; filter: brightness(1.5); }
  50% { opacity: 1; filter: brightness(2); }
}

.character-evolving {
  animation: evolve-flash 1s ease-in-out 3;
}
```

#### 響應式設計考量

```css
/* 移動端適配 */
@media (max-width: 768px) {
  .retro-screen {
    padding: 10px;
    font-size: 12px;
  }
  
  .character-display {
    width: 64px;
    height: 64px;
  }
  
  .pixel-button {
    font-size: 10px;
    padding: 6px 12px;
  }
}
```

### 11.2 組件設計

#### TamagotchiDisplay 組件

```typescript
interface TamagotchiDisplayProps {
  stage: 'baby' | 'child' | 'teen' | 'adult';
  health: number;  // 0-100
  hunger: number;  // 0-100
  isSick: boolean;
  lastFedAt: Date;
}

const TamagotchiDisplay: React.FC<TamagotchiDisplayProps> = ({
  stage,
  health,
  hunger,
  isSick,
  lastFedAt
}) => {
  const characterImage = getCharacterImage(stage, isSick);
  const timeSinceFed = Date.now() - lastFedAt.getTime();
  const hoursUntilSick = 72 - (timeSinceFed / (1000 * 60 * 60));
  
  return (
    <div className="retro-screen">
      <div className={`character-display ${isSick ? 'sick-filter' : ''}`}>
        <img 
          src={characterImage} 
          alt={`${stage} character`}
          className="character-breathe character-blink"
          style={{ imageRendering: 'pixelated' }}
        />
      </div>
      
      <HealthBar value={health} max={100} />
      <HungerBar value={hunger} max={100} />
      
      {hoursUntilSick < 24 && (
        <WarningMessage>
          ⚠️ {Math.ceil(hoursUntilSick)} 小時內需餵食，否則會生病
        </WarningMessage>
      )}
    </div>
  );
};
```

#### HealthBar 組件

```typescript
interface HealthBarProps {
  value: number;
  max: number;
}

const HealthBar: React.FC<HealthBarProps> = ({ value, max }) => {
  const percentage = (value / max) * 100;
  const isLow = percentage < 30;
  
  return (
    <div className="pixel-progress-bar">
      <div 
        className={`pixel-progress-fill ${isLow ? 'low-health' : ''}`}
        style={{ width: `${percentage}%` }}
      />
      <span className="progress-text">
        {value}/{max}
      </span>
    </div>
  );
};
```

#### FeedButton 組件

```typescript
interface FeedButtonProps {
  onClick: () => void;
  disabled?: boolean;
}

const FeedButton: React.FC<FeedButtonProps> = ({ onClick, disabled }) => {
  return (
    <button 
      className="pixel-button"
      onClick={onClick}
      disabled={disabled}
      data-testid="btn-tamagotchi-feed"
    >
      🍖 餵食
    </button>
  );
};
```

#### EvolutionModal 組件

```typescript
interface EvolutionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (incomeProof: File) => void;
}

const EvolutionModal: React.FC<EvolutionModalProps> = ({
  isOpen,
  onClose,
  onConfirm
}) => {
  const [incomeProof, setIncomeProof] = useState<File | null>(null);
  
  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <div className="retro-screen">
        <h2 className="pixel-title">進化為大人他媽哥池</h2>
        <p>上傳收入證明照片，即刻進化！</p>
        
        <input 
          type="file" 
          accept="image/*"
          onChange={(e) => setIncomeProof(e.target.files?.[0] || null)}
        />
        
        <div className="button-group">
          <button className="pixel-button" onClick={onClose}>
            取消
          </button>
          <button 
            className="pixel-button"
            onClick={() => incomeProof && onConfirm(incomeProof)}
            disabled={!incomeProof}
          >
            確認進化
          </button>
        </div>
      </div>
    </Modal>
  );
};
```

### 11.3 互動效果

#### 餵食動畫流程

```typescript
const handleFeed = async (views: number, likes: number) => {
  // 1. 顯示「餵食中...」狀態
  setFeeding(true);
  
  // 2. 角色顯示「開心」表情
  setCharacterExpression('happy');
  
  // 3. 簡單的「吃東西」動畫（2-3 幀循環）
  playEatingAnimation();
  
  // 4. 更新健康度/飢餓度
  await updateMetrics(views, likes);
  
  // 5. 顯示「+50 食糧」提示
  showNotification(`+${calculateFoodScore(views, likes)} 食糧`);
  
  // 6. 恢復正常狀態
  setFeeding(false);
  setCharacterExpression('normal');
};
```

#### 進化動畫流程

```typescript
const handleEvolution = async (incomeProof: File) => {
  // 1. 上傳收入證明
  const result = await uploadIncomeProof(incomeProof);
  
  // 2. 角色顯示「準備進化」狀態
  setCharacterExpression('preparing');
  
  // 3. 簡單的「閃光」效果（3-5 次）
  for (let i = 0; i < 5; i++) {
    await flashEffect();
    await delay(200);
  }
  
  // 4. 角色從當前階段切換到「成年期」
  setStage('adult');
  setCharacterExpression('confident');
  
  // 5. 顯示「🎉 進化成功！」提示
  showNotification('🎉 進化成功！你的助理已完全成長！');
};
```

#### 生病警告

```typescript
const checkSickStatus = () => {
  const hoursSinceFed = getHoursSinceLastFed();
  
  if (hoursSinceFed >= 72) {
    // 觸發生病狀態
    setIsSick(true);
    setCharacterExpression('sick');
    showWarning('⚠️ 角色生病了！請立即餵食或完成任務恢復健康。');
  } else if (hoursSinceFed >= 48) {
    // 警告狀態
    showWarning(`⚠️ ${72 - hoursSinceFed} 小時內需餵食，否則會生病`);
  }
};
```

### 11.4 性能優化

#### 像素圖像優化

```typescript
// 使用 SVG 或優化的 PNG
// SVG 優點：可縮放、文件小
// PNG 優點：像素完美、支援透明

// 推薦：使用 SVG 作為基礎，導出為 PNG 用於不同尺寸
const characterImages = {
  baby: {
    normal: '/images/characters/baby-normal.png',
    happy: '/images/characters/baby-happy.png',
    sick: '/images/characters/baby-sick.png',
  },
  // ... 其他階段
};

// 圖像預載入
useEffect(() => {
  Object.values(characterImages).forEach(stage => {
    Object.values(stage).forEach(image => {
      const img = new Image();
      img.src = image;
    });
  });
}, []);
```

#### 動畫性能考量

```css
/* 使用 transform 而非 position，提升性能 */
.character-breathe {
  will-change: transform;
  transform: translateZ(0); /* 啟用硬體加速 */
}

/* 減少重繪 */
.retro-screen {
  contain: layout style paint;
}
```

#### 移動端適配

```typescript
// 響應式角色尺寸
const getCharacterSize = (stage: string, isMobile: boolean) => {
  const baseSizes = {
    baby: isMobile ? 32 : 48,
    child: isMobile ? 40 : 56,
    teen: isMobile ? 48 : 64,
    adult: isMobile ? 56 : 72,
  };
  return baseSizes[stage] || 48;
};

// 觸摸優化
const FeedButton: React.FC = ({ onClick }) => {
  return (
    <button
      className="pixel-button"
      onClick={onClick}
      onTouchStart={(e) => {
        // 觸摸反饋
        e.currentTarget.style.transform = 'scale(0.95)';
      }}
      onTouchEnd={(e) => {
        e.currentTarget.style.transform = 'scale(1)';
      }}
    >
      🍖 餵食
    </button>
  );
};
```

---

## 十二、風險與考量

### 12.1 技術風險

| 風險 | 影響 | 機率 | 緩解措施 |
|------|------|:----:|----------|
| Meta Graph API 配額限制 | 中 | 中 | MVP 先手動輸入，進階再整合 API |
| TikTok Analytics API 成本高 | 中 | 中 | 評估成本後決定是否整合 |
| 支付系統整合複雜度高 | 高 | 低 | 提供手動輸入選項，不強制連接 |
| 成長曲線設計不當 | 中 | 中 | A/B 測試，根據用戶反饋調整 |

### 12.2 商業風險

| 風險 | 影響 | 機率 | 緩解措施 |
|------|------|:----:|----------|
| 用戶不感興趣 | 高 | 中 | MVP 快速驗證，根據反饋調整 |
| 成長門檻過高 | 中 | 中 | 初期使用較低門檻，可動態調整 |
| 收入驗證困難 | 中 | 中 | 提供手動輸入 + 可選驗證 |

### 12.3 隱私考量

| 考量 | 說明 | 處理方式 |
|------|------|----------|
| 支付系統授權 | 用戶需要授權連接支付系統 | 提供手動輸入選項，不強制連接 |
| 觀看數數據 | 追蹤用戶發布內容的表現 | 僅用於成長進度計算，不分享給第三方 |
| 收入數據 | 敏感的財務信息 | 加密儲存，僅用戶可見 |

---

## 十三、驗收標準

### 13.1 Phase 1 MVP 驗收標準（他媽哥池）

- [ ] 用戶可在發布歷史頁面手動輸入 views + likes
- [ ] 系統正確計算食糧分數（views × 0.1 + likes × 1.0）
- [ ] 用戶可上傳收入證明照片（設定頁面）
- [ ] Dashboard 正確顯示他媽哥池角色（90 年代像素風格）
- [ ] 健康度/飢餓度條正確顯示（0-100）
- [ ] 成長階段根據 views 正確切換（嬰兒→兒童→青少年）
- [ ] 提供收入證明後即刻進化為成年期（強壯角色）
- [ ] 72 小時未餵食時角色顯示生病狀態（變灰、表情疲憊）
- [ ] 餵食後健康度/飢餓度正確增加
- [ ] 復古螢幕效果正確顯示（綠色調背景）

### 13.2 Phase 2 自動同步驗收標準

- [ ] Meta Graph API 成功整合
- [ ] 已發布內容每 6 小時自動同步觀看數
- [ ] 同步失敗時提供手動輸入選項
- [ ] UI 清晰顯示同步狀態（自動/手動/待同步）

### 13.3 Phase 3 收入驗證驗收標準

- [ ] 用戶可選擇連接 PayPal/Stripe（可選）
- [ ] 已驗證收入顯示「驗證徽章」
- [ ] 收入統計圖表正確顯示
- [ ] 收入歷史記錄完整

---

## 📝 備註

### 實作優先級

- **Phase 1（MVP）**：P0 - 完成現有專案後優先實作
- **Phase 2（自動同步）**：P1 - 根據 Phase 1 用戶反饋決定
- **Phase 3（收入驗證）**：P2 - 可選功能

### 與現有系統整合

- 成長進度可整合到現有的 `StyleProfile` 系統
- 觀看數數據可擴展現有的 `PublishQueue` 模型
- 收入記錄可作為新的獨立功能模組

### 未來擴展

- 多平台觀看數整合（YouTube, Twitter 等）
- 更細緻的成長階段（如 10 個階段而非 4 個）
- 社交功能（用戶間比較、排行榜）
- 付費功能（「成長加速包」）
- 更多角色造型（不同風格的他媽哥池）
- 角色互動功能（多個角色互動）

---

**文件維護者**：開發團隊  
**最後更新**：2026-02-07  
**狀態**：📋 需求文件已完成（含他媽哥池視覺風格設計），待 Phase 1-5 完成後開始實作

