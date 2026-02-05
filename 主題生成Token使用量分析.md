# 主題生成 Token 使用量分析

## 📊 概述

本文檔分析系統在生成一個完整主題時使用的 Token 數量。系統使用 **DeepSeek API** 進行 AI 生成。

---

## 🔍 Token 使用流程

### 完整流程中的 AI 調用

生成一個主題的完整流程包括：

1. **主題標題生成**（可選，僅在使用備用關鍵字時）
2. **文章內容生成**（必需）
3. **腳本內容生成**（必需）
4. **圖片匹配**（不使用 AI，使用 Google Custom Search API）

---

## 💰 Token 使用詳情

### 1. 主題標題生成（可選）

**觸發條件：** 當 RSS Feed 無法取得或數量不足時，使用備用關鍵字生成標題

**文件位置：** `backend/app/services/automation/topic_collector.py`

**Prompt 長度：** 約 **200-300 tokens**

**Prompt 範例：**
```
請為以下主題生成一個適合社群媒體的中文標題：

**分類**：時尚
**關鍵字**：2025春夏時尚趨勢

**要求**：
1. 標題吸引人，適合小紅書/Instagram 風格
2. 長度控制在 15-25 字之間
3. 符合 時尚 分類的主題
...
```

**回應長度：** 約 **20-50 tokens**（15-25 字的中文標題）

**單次調用 Token 使用：**
- **Input:** 200-300 tokens
- **Output:** 20-50 tokens
- **總計：** 約 **220-350 tokens**

---

### 2. 文章內容生成（必需）

**文件位置：** `backend/app/services/automation/workflow.py` → `_generate_content()`

**Prompt 長度：** 約 **300-400 tokens**

**Prompt 範例：**
```
請為以下主題生成一篇適合社群媒體的短文：

**主題**：2025春夏時尚趨勢
**分類**：時尚
**關鍵字**：時尚、潮流、風格
**目標長度**：約 500 字

**要求**：
1. 內容生動有趣，適合小紅書/Instagram 風格
2. 語言自然流暢，符合目標受眾
3. 包含實用資訊或觀點
...
```

**回應長度：** 約 **500-800 tokens**（500 字的中文文章）

**單次調用 Token 使用：**
- **Input:** 300-400 tokens
- **Output:** 500-800 tokens
- **總計：** 約 **800-1200 tokens**

---

### 3. 腳本內容生成（必需）

**文件位置：** `backend/app/services/automation/workflow.py` → `_generate_content()`

**Prompt 長度：** 約 **300-400 tokens**

**Prompt 範例：**
```
請為以下主題生成一個適合短影片的腳本：

**主題**：2025春夏時尚趨勢
**分類**：時尚
**關鍵字**：時尚、潮流、風格
**目標時長**：約 30 秒（約 510 字）

**要求**：
1. 腳本適合拍攝短影片（小紅書/YouTube Shorts/Instagram Reels）
2. 語言口語化，適合口述
...
```

**回應長度：** 約 **500-800 tokens**（30 秒腳本，約 510 字）

**單次調用 Token 使用：**
- **Input:** 300-400 tokens
- **Output:** 500-800 tokens
- **總計：** 約 **800-1200 tokens**

---

### 4. 圖片匹配（不使用 AI）

**文件位置：** `backend/app/services/images/enhanced_photo_matcher.py`

**說明：** 圖片匹配使用 **Google Custom Search API**，不消耗 AI Token

---

## 📈 總 Token 使用量

### 情況 1：從 RSS Feed 收集主題（最常見）

如果系統成功從 RSS Feed 收集到主題，**不需要生成標題**：

| 步驟 | Input Tokens | Output Tokens | 總計 |
|------|-------------|---------------|------|
| 文章生成 | 300-400 | 500-800 | 800-1200 |
| 腳本生成 | 300-400 | 500-800 | 800-1200 |
| **總計** | **600-800** | **1000-1600** | **1600-2400** |

**每個主題：約 1600-2400 tokens**

---

### 情況 2：使用備用關鍵字生成標題

如果 RSS Feed 失敗，需要生成標題：

| 步驟 | Input Tokens | Output Tokens | 總計 |
|------|-------------|---------------|------|
| 標題生成 | 200-300 | 20-50 | 220-350 |
| 文章生成 | 300-400 | 500-800 | 800-1200 |
| 腳本生成 | 300-400 | 500-800 | 800-1200 |
| **總計** | **800-1100** | **1020-1650** | **1820-2750** |

**每個主題：約 1820-2750 tokens**

---

## 💵 成本估算（DeepSeek API）

### DeepSeek 定價（參考）

根據 DeepSeek 官方定價（可能會有變動）：

- **Input:** 約 $0.0014 / 1K tokens
- **Output:** 約 $0.0028 / 1K tokens

### 每個主題的成本

#### 情況 1：從 RSS 收集（最常見）
- Input: 600-800 tokens × $0.0014 / 1K = **$0.00084 - $0.00112**
- Output: 1000-1600 tokens × $0.0028 / 1K = **$0.0028 - $0.00448**
- **總成本：約 $0.00364 - $0.0056 / 主題**

#### 情況 2：使用備用關鍵字
- Input: 800-1100 tokens × $0.0014 / 1K = **$0.00112 - $0.00154**
- Output: 1020-1650 tokens × $0.0028 / 1K = **$0.002856 - $0.00462**
- **總成本：約 $0.003976 - $0.00616 / 主題**

---

## 📊 每日 Token 使用量

### 每日主題數量

- **每個時間段：** 3 個主題
- **每日時間段：** 3 個（07:00, 12:00, 18:00）
- **每日總主題數：** 9 個主題

### 每日 Token 使用量

#### 情況 1：全部從 RSS 收集（理想情況）
- 9 個主題 × 1600-2400 tokens = **14,400 - 21,600 tokens/天**

#### 情況 2：全部使用備用關鍵字（最壞情況）
- 9 個主題 × 1820-2750 tokens = **16,380 - 24,750 tokens/天**

#### 實際情況（混合）
假設 70% 從 RSS 收集，30% 使用備用關鍵字：
- 6.3 個主題 × 2000 tokens（平均） = 12,600 tokens
- 2.7 個主題 × 2300 tokens（平均） = 6,210 tokens
- **總計：約 18,810 tokens/天**

---

## 💰 每日成本估算

### 每日成本（DeepSeek API）

#### 情況 1：全部從 RSS 收集
- **Token 使用：** 14,400 - 21,600 tokens
- **成本：** 約 **$0.033 - $0.05 / 天**

#### 情況 2：全部使用備用關鍵字
- **Token 使用：** 16,380 - 24,750 tokens
- **成本：** 約 **$0.036 - $0.055 / 天**

#### 實際情況（混合）
- **Token 使用：** 約 18,810 tokens
- **成本：** 約 **$0.04 - $0.05 / 天**

### 每月成本估算

- **每日成本：** $0.04 - $0.05
- **每月成本（30天）：** 約 **$1.2 - $1.5 / 月**

---

## 📝 代碼位置參考

### 1. 標題生成
- **文件：** `backend/app/services/automation/topic_collector.py`
- **方法：** `_generate_from_keywords()`
- **Prompt：** `backend/app/prompts/title_prompt.py`

### 2. 文章生成
- **文件：** `backend/app/services/automation/workflow.py`
- **方法：** `_generate_content()` → `ai_service.generate_article()`
- **Prompt：** `backend/app/prompts/article_prompt.py`

### 3. 腳本生成
- **文件：** `backend/app/services/automation/workflow.py`
- **方法：** `_generate_content()` → `ai_service.generate_script()`
- **Prompt：** `backend/app/prompts/script_prompt.py`

### 4. AI 服務調用
- **文件：** `backend/app/services/ai/deepseek.py`
- **方法：** `_call_api()`
- **設定：** `max_tokens: 2000`（每次調用的最大輸出 Token）

---

## ⚠️ 注意事項

1. **Token 計數方式：**
   - 中文 Token 計數：通常 1 個中文字 = 1-2 tokens
   - 英文 Token 計數：通常 1 個英文單詞 = 1 token
   - 實際計數可能因模型而異

2. **實際使用量可能因以下因素變化：**
   - Prompt 長度（關鍵字數量）
   - 生成內容長度（實際可能超過目標長度）
   - 模型版本差異

3. **成本優化建議：**
   - 優先使用 RSS Feed 收集主題（避免標題生成）
   - 考慮調整 `max_tokens` 限制（目前為 2000）
   - 監控實際 Token 使用量（如果 API 提供使用量統計）

4. **Token 使用監控：**
   - 目前代碼中**沒有記錄 Token 使用量**
   - 建議在 AI 服務中添加 Token 使用量日誌
   - 可以從 API 回應中提取 `usage` 字段（如果 API 提供）

---

## 🔧 改進建議

### 1. 添加 Token 使用量日誌

在 `backend/app/services/ai/deepseek.py` 中添加：

```python
# 在 _call_api() 方法中
result = response.json()

# 記錄 Token 使用量
if "usage" in result:
    usage = result["usage"]
    logger.info(f"Token 使用量 - Prompt: {usage.get('prompt_tokens', 0)}, "
                f"Completion: {usage.get('completion_tokens', 0)}, "
                f"Total: {usage.get('total_tokens', 0)}")
```

### 2. 數據庫記錄 Token 使用量

在主題或內容記錄中添加 `tokens_used` 字段，追蹤每個主題的 Token 消耗。

### 3. 成本監控儀表板

創建一個儀表板顯示：
- 每日 Token 使用量
- 每日成本
- 每個主題的平均 Token 使用量

---

## 📊 總結

### 每個主題的 Token 使用量

| 情況 | Input Tokens | Output Tokens | 總計 Tokens |
|------|-------------|---------------|-------------|
| RSS 收集（常見） | 600-800 | 1000-1600 | **1600-2400** |
| 備用關鍵字 | 800-1100 | 1020-1650 | **1820-2750** |

### 每日成本

- **Token 使用：** 約 14,400 - 24,750 tokens/天
- **成本：** 約 **$0.033 - $0.055 / 天**
- **每月成本：** 約 **$1.2 - $1.5 / 月**

### 關鍵發現

1. **每個主題平均使用約 2000 tokens**
2. **每日 9 個主題約使用 18,000 tokens**
3. **成本相對較低，約 $0.04-0.05 / 天**

