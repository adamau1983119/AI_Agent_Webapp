# Google Cloud Console 檢查步驟指南

## 📋 檢查 Google Custom Search API 配置

---

## 🔐 步驟 1：登入 Google Cloud Console

1. **打開瀏覽器**，前往：
   ```
   https://console.cloud.google.com/
   ```

2. **登入 Google 帳號**
   - 使用與 API Key 相關聯的 Google 帳號登入

3. **選擇專案**
   - 在頂部導航欄中，點擊專案選擇器
   - 選擇與您的 API Key 相關的專案

---

## 🔑 步驟 2：檢查 API Key 是否有效

### 2.1 前往 API 和服務 → 憑證

1. **打開左側選單**
   - 點擊「☰」（漢堡選單）

2. **導航到「API 和服務」**
   - 點擊「API 和服務」（APIs & Services）
   - 點擊「憑證」（Credentials）

3. **查看 API Key 列表**
   - 在「API 金鑰」區段中，您會看到所有 API Key
   - 找到您的 `GOOGLE_API_KEY`

### 2.2 檢查 API Key 狀態

**檢查項目：**
- ✅ **名稱**：確認 API Key 名稱正確
- ✅ **狀態**：應該是「已啟用」（Enabled）
- ✅ **建立日期**：確認日期合理
- ✅ **最後使用時間**：確認最近有使用

**如果 API Key 被停用：**
- 點擊 API Key 名稱
- 在「限制」頁面中，確認「API 金鑰限制」設定正確
- 如果被停用，點擊「啟用」按鈕

### 2.3 檢查 API Key 限制

1. **點擊 API Key 名稱**進入詳細頁面

2. **檢查「應用程式限制」**
   - 「無限制」或「HTTP 參照網址（網站）」
   - 如果有限制，確認包含您的網域

3. **檢查「API 限制」**
   - 應該包含「Custom Search API」
   - 如果沒有，需要添加：
     - 點擊「限制金鑰」
     - 選擇「限制 API 金鑰」
     - 在「選取 API」中，搜尋並選擇「Custom Search API」
     - 點擊「儲存」

---

## 🔌 步驟 3：檢查 Custom Search API 是否已啟用

### 3.1 前往 API 庫

1. **打開左側選單**
   - 點擊「☰」（漢堡選單）

2. **導航到「API 和服務」**
   - 點擊「API 和服務」（APIs & Services）
   - 點擊「程式庫」（Library）

### 3.2 搜尋 Custom Search API

1. **在搜尋框中輸入**：
   ```
   Custom Search API
   ```

2. **點擊「Custom Search API」**

### 3.3 檢查 API 狀態

**檢查項目：**
- ✅ **狀態**：應該是「已啟用」（Enabled）
- ✅ **配額**：查看配額使用情況
- ✅ **計量**：查看 API 呼叫次數

**如果 API 未啟用：**
- 點擊「啟用」按鈕
- 等待幾秒鐘讓 API 啟用
- 確認狀態變為「已啟用」

---

## 📊 步驟 4：檢查配額是否用盡

### 4.1 前往配額頁面

1. **在 Custom Search API 頁面中**
   - 點擊左側選單中的「配額」（Quotas）

2. **或者從 API 和服務頁面**
   - 點擊「API 和服務」→「配額」（Quotas）
   - 在「篩選器」中選擇「Custom Search API」

### 4.2 檢查配額使用情況

**查看以下配額：**

1. **每日配額（Daily quota）**
   - 查看「已使用」vs「限制」
   - 如果接近或達到限制，需要增加配額

2. **每 100 秒配額（Per 100 seconds quota）**
   - 查看短期配額使用情況
   - 如果經常達到限制，可能需要調整請求頻率

### 4.3 增加配額（如果需要）

1. **點擊配額項目**
2. **點擊「編輯配額」**
3. **輸入新的配額限制**
4. **填寫配額增加請求表單**
   - 說明為什麼需要增加配額
   - 提交請求
5. **等待 Google 審核**（通常需要幾個小時到幾天）

---

## 🔍 步驟 5：檢查 Search Engine ID

### 5.1 前往 Google Custom Search Engine

1. **打開瀏覽器**，前往：
   ```
   https://cse.google.com/
   ```

2. **登入 Google 帳號**
   - 使用與 API Key 相同的 Google 帳號

### 5.2 查看搜尋引擎列表

1. **在「控制台」頁面中**
   - 您會看到所有自訂搜尋引擎

2. **找到您的搜尋引擎**
   - 點擊搜尋引擎名稱

### 5.3 檢查搜尋引擎設定

**檢查項目：**

1. **搜尋引擎 ID**
   - 在「基本資訊」頁面中
   - 確認 ID 與 Railway 環境變數中的 `GOOGLE_SEARCH_ENGINE_ID` 一致

2. **搜尋設定**
   - 點擊「設定」→「基本」
   - 確認「搜尋整個網路」已啟用
   - 確認「圖片搜尋」已啟用

3. **進階設定**
   - 點擊「設定」→「進階」
   - 確認「安全搜尋」設定適當
   - 確認「語言」設定正確

---

## ✅ 檢查清單

### API Key 檢查
- [ ] API Key 存在且可見
- [ ] API Key 狀態為「已啟用」
- [ ] API Key 限制包含 Custom Search API
- [ ] API Key 沒有過期

### Custom Search API 檢查
- [ ] Custom Search API 已啟用
- [ ] API 狀態正常
- [ ] 配額未用盡
- [ ] 配額足夠使用

### Search Engine ID 檢查
- [ ] Search Engine ID 正確
- [ ] 搜尋引擎已啟用「搜尋整個網路」
- [ ] 圖片搜尋已啟用
- [ ] 搜尋引擎設定正確

---

## 🚨 常見問題排查

### 問題 1：API Key 無效

**症狀：** 403 錯誤，`INVALID_CONFIG_OR_PERMISSION`

**解決方法：**
1. 確認 API Key 正確複製到 Railway 環境變數
2. 確認 API Key 沒有多餘的空格或換行
3. 確認 API Key 限制包含 Custom Search API
4. 嘗試重新建立 API Key

### 問題 2：API 未啟用

**症狀：** 403 錯誤，API 無法使用

**解決方法：**
1. 前往 API 庫
2. 搜尋 Custom Search API
3. 點擊「啟用」
4. 等待幾秒鐘

### 問題 3：配額用盡

**症狀：** 403 錯誤，配額相關錯誤

**解決方法：**
1. 檢查配額使用情況
2. 如果接近限制，減少請求頻率
3. 如果需要，申請增加配額
4. 等待配額重置（每日配額會在 UTC 午夜重置）

### 問題 4：Search Engine ID 錯誤

**症狀：** 403 錯誤或搜尋結果不正確

**解決方法：**
1. 確認 Search Engine ID 正確
2. 確認搜尋引擎設定正確
3. 確認搜尋引擎已啟用「搜尋整個網路」

---

## 📝 記錄檢查結果

完成檢查後，記錄以下資訊：

```
檢查日期：2026-01-08
API Key 狀態：✅ 已啟用 / ❌ 已停用
Custom Search API 狀態：✅ 已啟用 / ❌ 未啟用
配額使用情況：XX / 100（每日）
Search Engine ID：確認正確 / 需要更新
```

---

## 🔗 相關連結

- **Google Cloud Console：** https://console.cloud.google.com/
- **Custom Search API 文檔：** https://developers.google.com/custom-search/v1/overview
- **Google Custom Search Engine：** https://cse.google.com/
- **API 配額管理：** https://console.cloud.google.com/apis/api/customsearch.googleapis.com/quotas

---

**指南建立時間：** 2026-01-07  
**最後更新：** 2026-01-07

