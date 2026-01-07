# 啟用 Custom Search API 步驟指南

## 🚨 問題：找不到 Custom Search API

如果您在 Google Cloud Console 中找不到 Custom Search API，這表示 API 尚未啟用。請按照以下步驟啟用。

---

## 📋 步驟 1：前往 API 庫

1. **打開瀏覽器**，前往：
   ```
   https://console.cloud.google.com/
   ```

2. **登入 Google 帳號**
   - 使用與 API Key 相關聯的 Google 帳號

3. **選擇專案**
   - 在頂部導航欄中，點擊專案選擇器
   - 選擇與您的 API Key 相關的專案
   - **如果沒有專案，需要先建立專案**（見下方）

---

## 📋 步驟 2：建立專案（如果沒有專案）

### 2.1 建立新專案

1. **點擊頂部的專案選擇器**
   - 顯示「選取專案」下拉選單

2. **點擊「新增專案」**
   - 或前往：https://console.cloud.google.com/projectcreate

3. **填寫專案資訊**
   - **專案名稱**：例如「AI Agent Webapp」或「Custom Search」
   - **組織**：選擇您的組織（如果有）
   - **位置**：選擇位置

4. **點擊「建立」**
   - 等待幾秒鐘讓專案建立完成

5. **選擇新建立的專案**
   - 在專案選擇器中選擇新專案

---

## 📋 步驟 3：啟用 Custom Search API

### 3.1 前往 API 庫

1. **打開左側選單**
   - 點擊「☰」（漢堡選單圖標）

2. **導航到「API 和服務」**
   - 點擊「API 和服務」（APIs & Services）
   - 點擊「程式庫」（Library）

   **或者直接前往：**
   ```
   https://console.cloud.google.com/apis/library
   ```

### 3.2 搜尋 Custom Search API

1. **在搜尋框中輸入**：
   ```
   Custom Search API
   ```
   或
   ```
   customsearch
   ```

2. **點擊搜尋結果中的「Custom Search API」**
   - 應該會看到 Google 的 Custom Search API

### 3.3 啟用 API

1. **在 Custom Search API 頁面中**
   - 您會看到 API 的詳細資訊

2. **點擊「啟用」按鈕**
   - 按鈕通常在頁面頂部
   - 如果已經啟用，會顯示「已啟用」或「管理」

3. **等待啟用完成**
   - 通常只需要幾秒鐘
   - 頁面會刷新，顯示「已啟用」狀態

---

## 📋 步驟 4：確認 API 已啟用

### 4.1 檢查 API 狀態

1. **在 Custom Search API 頁面中**
   - 確認頂部顯示「已啟用」（Enabled）

2. **查看 API 資訊**
   - 確認 API 名稱：Custom Search API
   - 確認 API ID：`customsearch.googleapis.com`

### 4.2 檢查已啟用的 API 列表

1. **導航到「API 和服務」→「已啟用的 API」**
   - 或前往：https://console.cloud.google.com/apis/dashboard

2. **搜尋「Custom Search」**
   - 確認 Custom Search API 在列表中
   - 確認狀態為「已啟用」

---

## 📋 步驟 5：設定 API Key 限制

### 5.1 前往憑證頁面

1. **導航到「API 和服務」→「憑證」**
   - 或前往：https://console.cloud.google.com/apis/credentials

2. **找到您的 API Key**
   - 在「API 金鑰」區段中

### 5.2 設定 API 限制

1. **點擊 API Key 名稱**進入詳細頁面

2. **在「API 限制」區段中**
   - 選擇「限制金鑰」
   - 選擇「限制 API 金鑰」

3. **在「選取 API」中**
   - 點擊「選取 API」
   - 搜尋「Custom Search API」
   - 勾選「Custom Search API」
   - 點擊「確定」

4. **點擊「儲存」**
   - 等待幾秒鐘讓設定生效

---

## 🔍 如果仍然找不到 Custom Search API

### 可能原因 1：API 名稱不同

**嘗試搜尋以下名稱：**
- `Custom Search API`
- `customsearch`
- `Google Custom Search`
- `Custom Search JSON API`

### 可能原因 2：需要啟用計費

**某些 Google API 需要啟用計費：**

1. **前往「帳單」頁面**
   - 導航：IAM 與管理 → 帳單
   - 或前往：https://console.cloud.google.com/billing

2. **檢查帳單帳戶**
   - 如果沒有帳單帳戶，需要建立一個
   - 即使有免費配額，也需要啟用計費帳戶

3. **連結帳單帳戶到專案**
   - 在專案設定中連結帳單帳戶

### 可能原因 3：API 在特定區域不可用

**確認：**
- 您的 Google Cloud 專案區域設定
- Custom Search API 在您的區域是否可用

---

## ✅ 檢查清單

完成後，確認以下項目：

- [ ] Google Cloud 專案已建立
- [ ] Custom Search API 已啟用
- [ ] API 狀態顯示「已啟用」
- [ ] API Key 限制包含 Custom Search API
- [ ] 帳單帳戶已連結（如果需要）

---

## 🔗 直接連結

### 快速連結：

1. **API 庫（搜尋 Custom Search API）：**
   ```
   https://console.cloud.google.com/apis/library/customsearch.googleapis.com
   ```

2. **建立專案：**
   ```
   https://console.cloud.google.com/projectcreate
   ```

3. **已啟用的 API：**
   ```
   https://console.cloud.google.com/apis/dashboard
   ```

4. **憑證（API Keys）：**
   ```
   https://console.cloud.google.com/apis/credentials
   ```

---

## 📝 記錄啟用結果

完成啟用後，記錄以下資訊：

```
啟用日期：2026-01-08
專案名稱：[您的專案名稱]
API 狀態：✅ 已啟用
API ID：customsearch.googleapis.com
API Key：已設定限制
```

---

## 🚨 常見問題

### Q1: 點擊「啟用」後沒有反應？

**解決方法：**
- 刷新頁面
- 檢查瀏覽器控制台是否有錯誤
- 嘗試使用不同的瀏覽器
- 確認您有專案的管理員權限

### Q2: 找不到「啟用」按鈕？

**可能原因：**
- API 已經啟用（會顯示「管理」按鈕）
- 您沒有權限啟用 API
- 需要先啟用計費

**解決方法：**
- 檢查「已啟用的 API」列表
- 確認您的權限
- 啟用計費帳戶

### Q3: 啟用後仍然出現 403 錯誤？

**可能原因：**
- API Key 限制未設定
- API Key 與專案不匹配
- 配額用盡

**解決方法：**
- 確認 API Key 限制包含 Custom Search API
- 確認 API Key 屬於正確的專案
- 檢查配額使用情況

---

**指南建立時間：** 2026-01-07  
**最後更新：** 2026-01-07

