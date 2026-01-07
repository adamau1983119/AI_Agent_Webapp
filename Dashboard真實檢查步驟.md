# Dashboard 真實檢查步驟

## 📋 檢查前準備

### 1. 確認部署狀態

**前端（Vercel）**：
- 訪問：https://ai-agent-webapp-ten.vercel.app
- 確認頁面能正常載入

**後端（Railway）**：
- 訪問：https://gentle-enchantment-production-1865.up.railway.app/health
- 確認返回 `{"status": "healthy"}` 或 `{"status": "degraded"}`

### 2. 確認環境變數

**Railway 環境變數檢查**：
- `AI_SERVICE=deepseek`
- `DEEPSEEK_API_KEY` 已設定
- `MONGODB_URL` 已設定
- `GOOGLE_API_KEY` 已設定（圖片搜尋）
- `GOOGLE_SEARCH_ENGINE_ID` 已設定（圖片搜尋）

**Vercel 環境變數檢查**：
- `VITE_API_URL=https://gentle-enchantment-production-1865.up.railway.app/api/v1`

---

## 🔍 步驟 1：前端 Dashboard 基本檢查

### 1.1 打開 Dashboard 頁面

1. **訪問 Dashboard**：
   - 打開瀏覽器開發者工具（F12）
   - 訪問：https://ai-agent-webapp-ten.vercel.app
   - 或本地：http://localhost:5173

2. **檢查控制台**：
   - 打開 Console 標籤
   - 確認沒有紅色錯誤訊息
   - 檢查是否有以下調試資訊：
     ```
     🔍 生產環境調試資訊：
       VITE_API_URL: https://gentle-enchantment-production-1865.up.railway.app/api/v1
       當前 API Base URL: ...
     ✅ 已清除所有 React Query 緩存
     ```

3. **檢查 Network 標籤**：
   - 打開 Network 標籤
   - 確認有以下 API 請求：
     - `GET /api/v1/topics` - 狀態碼應該是 200
     - `GET /api/v1/schedules` - 狀態碼應該是 200
   - 如果狀態碼是 500 或 404，記錄錯誤訊息

### 1.2 檢查 Dashboard 顯示內容

**應該看到**：
- ✅ 4 個進度卡片（待審核、已確認、內容評分、今日主題）
- ✅ 日曆組件
- ✅ 今日主題列表
- ✅ 主題卡片網格（至少 3 個主題）
- ✅ 右側資訊欄（推薦主題、即將到來的事件、最近活動）

**不應該看到**：
- ❌ "Failed to fetch" 錯誤
- ❌ 空白頁面
- ❌ 無限載入動畫

---

## 🔍 步驟 2：後端 API 健康檢查

### 2.1 基本健康檢查

**使用瀏覽器或 curl**：

```bash
# 基本健康檢查
curl https://gentle-enchantment-production-1865.up.railway.app/health

# 預期回應：
{
  "status": "healthy" 或 "degraded",
  "environment": "production",
  "version": "1.0.0",
  "database": "connected",
  "timestamp": "2025-12-30T..."
}
```

### 2.2 詳細健康檢查

```bash
# 詳細健康檢查
curl https://gentle-enchantment-production-1865.up.railway.app/health/detailed

# 預期回應應包含：
{
  "status": "healthy" 或 "degraded",
  "checks": {
    "database": true,
    "scheduler": true/false,
    "ai_service": true,
    "image_service": true/false
  },
  "details": {
    "ai_service": {
      "status": "configured",
      "service": "deepseek",
      "api_key_set": true
    },
    "image_service": {
      "status": "configured" 或 "not_configured",
      "services": {
        "unsplash": {"configured": true/false},
        "pexels": {"configured": true/false},
        "pixabay": {"configured": true/false}
      }
    }
  }
}
```

**檢查重點**：
- ✅ `database` 應該是 `true`
- ✅ `ai_service` 應該是 `true`（DeepSeek API Key 已設定）
- ⚠️ `image_service` 可能是 `false`（如果沒有設定圖片 API Key，這是正常的）

---

## 🔍 步驟 3：主題列表 API 檢查

### 3.1 測試主題列表 API

```bash
# 取得主題列表
curl "https://gentle-enchantment-production-1865.up.railway.app/api/v1/topics?page=1&limit=10"

# 預期回應：
{
  "data": [
    {
      "id": "...",
      "title": "...",
      "category": "...",
      "status": "pending" 或 "confirmed",
      ...
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": ...,
    "totalPages": ...
  }
}
```

**檢查重點**：
- ✅ 狀態碼應該是 200
- ✅ `data` 應該是陣列
- ✅ 每個主題應該有 `id`, `title`, `category`, `status` 欄位

### 3.2 在前端驗證

1. **打開 Dashboard**
2. **檢查主題卡片**：
   - 應該顯示至少 3 個主題卡片
   - 每個卡片應該顯示：
     - 主題標題
     - 分類標籤
     - 狀態標籤（待審核/已確認）
     - 圖片（如果有）

---

## 🔍 步驟 4：圖片搜尋功能檢查（重點：Google API）

### 4.1 測試圖片搜尋 API（自動選擇來源）

```bash
# 測試圖片搜尋（會自動嘗試所有服務，包括 Google Custom Search）
curl "https://gentle-enchantment-production-1865.up.railway.app/api/v1/images/search?keywords=時尚&page=1&limit=10"

# 預期回應：
{
  "data": [
    {
      "id": "...",
      "url": "https://...",
      "source": "Unsplash" 或 "Pexels" 或 "Pixabay" 或 "Google Custom Search" 或 "DuckDuckGo",
      "photographer": "...",
      "license": "...",
      ...
    }
  ],
  "pagination": {...}
}
```

**檢查重點**：
- ✅ 狀態碼應該是 200
- ✅ `data` 應該是陣列，包含圖片
- ✅ 檢查 `source` 欄位，確認是否包含 "Google Custom Search"

### 4.2 測試 Google Custom Search（指定來源）

```bash
# 測試 Google Custom Search（需要設定 GOOGLE_API_KEY 和 GOOGLE_SEARCH_ENGINE_ID）
curl "https://gentle-enchantment-production-1865.up.railway.app/api/v1/images/search?keywords=時尚&source=Google%20Custom%20Search&page=1&limit=10"
```

**預期結果**：

**如果 Google API Key 已設定**：
- ✅ 狀態碼 200
- ✅ 返回圖片列表
- ✅ `source` 欄位為 "Google Custom Search"

**如果 Google API Key 未設定**：
- ✅ 狀態碼 200（因為會自動使用其他服務或 DuckDuckGo）
- ✅ 返回圖片列表
- ✅ `source` 欄位為其他服務（Unsplash/Pexels/Pixabay/DuckDuckGo）

### 4.3 檢查後端日誌（Railway）

1. **訪問 Railway Dashboard**：
   - https://railway.app/dashboard
   - 選擇專案
   - 打開 Logs 標籤

2. **搜尋關鍵字**：
   - 搜尋 "Google Custom Search"
   - 應該看到以下日誌之一：

   **如果 API Key 已設定**：
   ```
   INFO | 嘗試使用 Google Custom Search 搜尋圖片...
   INFO | ✅ Google Custom Search 搜尋成功，找到 X 張圖片
   ```

   **如果 API Key 未設定**：
   ```
   WARNING | Google Custom Search API Key 或 Search Engine ID 未設定
   WARNING | Google Custom Search API Key 未設定，跳過
   INFO | 嘗試使用 DuckDuckGo 搜尋圖片...
   ```

### 4.4 在前端測試圖片搜尋

1. **打開主題詳情頁**：
   - 從 Dashboard 點擊一個主題
   - 或直接訪問：`/topics/{topic_id}`

2. **測試圖片搜尋**：
   - 點擊「+ 新增圖片」按鈕
   - 應該打開圖片搜尋對話框
   - 輸入關鍵字（例如：「時尚」）
   - 點擊「搜尋」

3. **檢查結果**：
   - ✅ 應該顯示圖片網格
   - ✅ 圖片應該能正常顯示
   - ✅ 檢查圖片來源標籤（如果有顯示）

4. **檢查 Network 標籤**：
   - 打開開發者工具 Network 標籤
   - 確認有 `GET /api/v1/images/search?keywords=...` 請求
   - 狀態碼應該是 200
   - 檢查回應內容，確認包含圖片數據

---

## 🔍 步驟 5：內容生成功能檢查

### 5.1 測試內容生成 API

```bash
# 測試生成內容（需要替換 {topic_id} 為實際的主題 ID）
curl -X POST "https://gentle-enchantment-production-1865.up.railway.app/api/v1/contents/{topic_id}/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "both",
    "article_length": 500,
    "script_duration": 30
  }'
```

**預期回應**：
```json
{
  "id": "...",
  "topic_id": "...",
  "article": "生成的500字文章...",
  "script": "生成的30秒腳本...",
  "word_count": 500,
  "estimated_duration": 30,
  "model_used": "deepseek-chat",
  ...
}
```

**檢查重點**：
- ✅ 狀態碼應該是 200
- ✅ `article` 應該有內容（約 500 字）
- ✅ `script` 應該有內容（約 30 秒腳本）
- ✅ `model_used` 應該是 "deepseek-chat"

### 5.2 在前端測試內容生成

1. **打開主題詳情頁**：
   - 選擇一個沒有內容的主題
   - 或訪問：`/topics/{topic_id}`

2. **生成內容**：
   - 如果內容不存在，應該看到「生成內容（500字文章 + 30秒腳本）」按鈕
   - 點擊按鈕
   - 應該顯示載入狀態

3. **檢查結果**：
   - ✅ 應該顯示成功提示
   - ✅ 內容區塊應該顯示：
     - 短文（約 500 字）
     - 腳本（約 30 秒）
   - ✅ 應該顯示字數和時長統計

4. **檢查 Network 標籤**：
   - 確認有 `POST /api/v1/contents/{topic_id}/generate` 請求
   - 狀態碼應該是 200
   - 檢查回應內容

### 5.3 檢查後端日誌（內容生成）

1. **訪問 Railway Logs**
2. **搜尋關鍵字**：
   - "生成內容"
   - "DeepSeek"
   - "調用 DeepSeek API"

3. **應該看到**：
   ```
   INFO | 調用 DeepSeek API 生成內容...
   INFO | ✅ 內容生成成功
   ```

**如果出現錯誤**：
- ❌ "DeepSeek API Key 未設定" → 檢查環境變數
- ❌ "調用 DeepSeek API 時發生錯誤" → 檢查 API Key 是否有效
- ❌ "生成內容失敗" → 檢查錯誤詳情

---

## 🔍 步驟 6：智能匹配照片功能檢查

### 6.1 測試智能匹配照片 API

```bash
# 測試智能匹配照片（需要替換 {topic_id} 為實際的主題 ID，且該主題必須有內容）
curl -X POST "https://gentle-enchantment-production-1865.up.railway.app/api/v1/images/{topic_id}/match?min_count=8"
```

**預期回應**：
```json
{
  "data": [
    {
      "id": "...",
      "url": "https://...",
      "source": "...",
      "match_score": 0.85,
      ...
    }
  ]
}
```

**檢查重點**：
- ✅ 狀態碼應該是 200
- ✅ `data` 應該包含至少 8 張圖片（如果 `min_count=8`）
- ✅ 每張圖片應該有 `match_score` 欄位

### 6.2 在前端測試智能匹配

1. **打開主題詳情頁**：
   - 選擇一個有內容但沒有圖片的主題

2. **智能匹配照片**：
   - 應該看到「智能匹配照片（8張）」按鈕
   - 點擊按鈕
   - 應該顯示載入狀態

3. **檢查結果**：
   - ✅ 應該顯示成功提示
   - ✅ 圖片區塊應該顯示匹配的照片
   - ✅ 照片應該能正常顯示

---

## 🔍 步驟 7：錯誤處理檢查

### 7.1 測試錯誤情況

1. **測試無效的主題 ID**：
   ```bash
   curl "https://gentle-enchantment-production-1865.up.railway.app/api/v1/topics/invalid_id"
   ```
   - 預期：狀態碼 404，錯誤訊息清晰

2. **測試無效的內容生成請求**：
   ```bash
   curl -X POST "https://gentle-enchantment-production-1865.up.railway.app/api/v1/contents/invalid_id/generate" \
     -H "Content-Type: application/json" \
     -d '{"type": "both"}'
   ```
   - 預期：狀態碼 404，錯誤訊息清晰

3. **測試無效的圖片搜尋**：
   ```bash
   curl "https://gentle-enchantment-production-1865.up.railway.app/api/v1/images/search?keywords="
   ```
   - 預期：狀態碼 400，錯誤訊息清晰

### 7.2 檢查前端錯誤處理

1. **斷開網路連接**：
   - 打開開發者工具
   - 選擇 "Offline" 模式
   - 重新載入 Dashboard
   - ✅ 應該顯示友善的錯誤訊息
   - ✅ 應該提供重試按鈕

2. **測試無效的 API URL**：
   - 暫時修改 `VITE_API_URL` 為無效 URL
   - 重新載入 Dashboard
   - ✅ 應該顯示連接錯誤訊息

---

## 🔍 步驟 8：完整流程測試

### 8.1 完整內容生成流程

1. **生成今日主題**：
   - 在 Dashboard 點擊「立即生成」按鈕
   - ✅ 應該顯示載入狀態
   - ✅ 應該顯示成功提示
   - ✅ 3 秒後應該自動刷新主題列表

2. **打開主題詳情**：
   - 點擊一個新生成的主題
   - ✅ 應該正常載入主題詳情

3. **生成內容**：
   - 點擊「生成內容（500字文章 + 30秒腳本）」按鈕
   - ✅ 應該顯示載入狀態
   - ✅ 應該顯示成功提示
   - ✅ 應該顯示生成的內容

4. **智能匹配照片**：
   - 點擊「智能匹配照片（8張）」按鈕
   - ✅ 應該顯示載入狀態
   - ✅ 應該顯示成功提示
   - ✅ 應該顯示匹配的照片

5. **手動搜尋圖片**：
   - 點擊「+ 新增圖片」按鈕
   - 輸入關鍵字
   - 點擊「搜尋」
   - ✅ 應該顯示搜尋結果
   - ✅ 可以選擇圖片並添加到主題

---

## 📊 檢查結果記錄表

### 基本功能檢查

| 功能 | 狀態 | 備註 |
|------|------|------|
| Dashboard 載入 | ⬜ 通過 / ⬜ 失敗 | |
| 主題列表顯示 | ⬜ 通過 / ⬜ 失敗 | |
| 進度卡片顯示 | ⬜ 通過 / ⬜ 失敗 | |
| 後端健康檢查 | ⬜ 通過 / ⬜ 失敗 | |
| 資料庫連接 | ⬜ 通過 / ⬜ 失敗 | |

### API 功能檢查

| API | 狀態 | 備註 |
|-----|------|------|
| GET /api/v1/topics | ⬜ 通過 / ⬜ 失敗 | |
| GET /api/v1/schedules | ⬜ 通過 / ⬜ 失敗 | |
| POST /api/v1/contents/{id}/generate | ⬜ 通過 / ⬜ 失敗 | |
| GET /api/v1/images/search | ⬜ 通過 / ⬜ 失敗 | |
| POST /api/v1/images/{id}/match | ⬜ 通過 / ⬜ 失敗 | |

### 圖片搜尋功能檢查（重點）

| 功能 | 狀態 | 備註 |
|------|------|------|
| 自動選擇來源（包含 Google） | ⬜ 通過 / ⬜ 失敗 | |
| Google Custom Search（指定來源） | ⬜ 通過 / ⬜ 失敗 | |
| 備援機制（DuckDuckGo） | ⬜ 通過 / ⬜ 失敗 | |
| 前端圖片搜尋 UI | ⬜ 通過 / ⬜ 失敗 | |

### AI 服務檢查

| 項目 | 狀態 | 備註 |
|------|------|------|
| DeepSeek API Key 設定 | ⬜ 已設定 / ⬜ 未設定 | |
| 內容生成功能 | ⬜ 通過 / ⬜ 失敗 | |
| 錯誤處理 | ⬜ 通過 / ⬜ 失敗 | |

---

## 🐛 常見問題排查

### 問題 1：Dashboard 顯示 "Failed to fetch"

**可能原因**：
- 後端服務未運行
- API URL 設定錯誤
- CORS 設定問題

**解決步驟**：
1. 檢查後端健康檢查端點
2. 檢查 `VITE_API_URL` 環境變數
3. 檢查瀏覽器控制台錯誤訊息
4. 檢查 Network 標籤的請求詳情

### 問題 2：圖片搜尋返回空結果

**可能原因**：
- 所有圖片服務 API Key 都未設定
- DuckDuckGo 服務也失敗
- 關鍵字無效

**解決步驟**：
1. 檢查後端日誌，確認使用的服務
2. 檢查至少一個圖片服務 API Key 是否設定
3. 嘗試不同的關鍵字

### 問題 3：Google Custom Search 未使用

**可能原因**：
- `GOOGLE_API_KEY` 未設定
- `GOOGLE_SEARCH_ENGINE_ID` 未設定
- API Key 無效或配額用完

**解決步驟**：
1. 檢查 Railway 環境變數
2. 檢查後端日誌，確認是否跳過 Google Custom Search
3. 驗證 Google API Key 是否有效

### 問題 4：內容生成失敗

**可能原因**：
- DeepSeek API Key 未設定或無效
- API 配額用完
- 網路連接問題

**解決步驟**：
1. 檢查 `DEEPSEEK_API_KEY` 環境變數
2. 檢查後端日誌，查看具體錯誤
3. 測試 DeepSeek API Key 是否有效

---

## ✅ 檢查完成確認

完成所有檢查後，確認：

- [ ] Dashboard 能正常載入和顯示
- [ ] 所有 API 端點都能正常回應
- [ ] 圖片搜尋功能正常（包括 Google Custom Search）
- [ ] 內容生成功能正常
- [ ] 錯誤處理正常
- [ ] 完整流程測試通過

**檢查日期**：_____________  
**檢查人員**：_____________  
**檢查結果**：⬜ 全部通過 / ⬜ 部分失敗（見備註）

---

**最後更新**：2025-12-30  
**版本**：1.0

