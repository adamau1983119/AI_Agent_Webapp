# API Key 配置完整步驟指南

> **目標**：配置所有必需的 API Key，解決核心功能問題  
> **預計時間**：20-30 分鐘  
> **難度**：簡單

---

## 📋 配置清單

### 必須配置（核心功能）

- [ ] **DeepSeek API Key** - 用於生成內容、翻譯標題、生成30字撮要
- [ ] **圖片服務 API Key** - 用於搜尋和匹配照片（至少配置一個）

### 可選配置

- [ ] DeepSeek Model（預設已設置）
- [ ] 其他圖片服務（如果主要服務失敗時的備援）

---

## 🔑 步驟 1：配置 DeepSeek API Key（必須）

### 1.1 獲取 DeepSeek API Key

1. **訪問 DeepSeek 平台**
   - 打開瀏覽器，訪問：https://platform.deepseek.com/api_keys
   - 如果沒有帳號，點擊「註冊」創建新帳號
   - 如果已有帳號，點擊「登入」

2. **創建 API Key**
   - 登入後，點擊「創建 API key」按鈕（通常是黑色按鈕）
   - 輸入 API Key 名稱（例如：`ai-agent-webapp`）
   - 點擊「創建」
   - ⚠️ **重要**：API Key 只在創建時顯示一次，立即複製並保存

3. **複製 API Key**
   - API Key 格式：`sk-26442...2d5e`（以 `sk-` 開頭）
   - 複製完整的 API Key
   - 保存到安全的地方（密碼管理器或文檔）

### 1.2 配置到本地開發環境

1. **打開 `.env` 文件**
   - 路徑：`backend/.env`
   - 使用文本編輯器打開（Notepad++、VS Code 等）

2. **更新配置**
   - 找到這一行：`DEEPSEEK_API_KEY=your_api_key_here`
   - 替換為：`DEEPSEEK_API_KEY=sk-你的實際API Key`
   - 確保 `AI_SERVICE=deepseek` 已設置（應該已經有）

3. **保存文件**
   - 保存 `.env` 文件
   - 確認沒有多餘的空格或引號

**範例：**
```env
DEEPSEEK_API_KEY=sk-26442abcdef1234567890abcdef1234567890abcdef1234567890abcdef
AI_SERVICE=deepseek
```

### 1.3 配置到 Railway 生產環境（如果使用）

1. **訪問 Railway Dashboard**
   - 打開：https://railway.app/dashboard
   - 登入您的帳號
   - 選擇您的專案（例如：`gentle-enchantment`）

2. **進入環境變數設置**
   - 點擊專案名稱
   - 點擊「Settings」標籤
   - 點擊「Variables」子標籤

3. **添加 DeepSeek API Key**
   - 點擊「+ New Variable」或「Add New」
   - **Key**：`DEEPSEEK_API_KEY`
   - **Value**：`sk-你的實際API Key`（從步驟 1.1 獲取）
   - **Environment**：選擇「Production」（或「All Environments」）
   - **Sensitive**：建議啟用（隱藏值）
   - 點擊「Save」或「Add」

4. **確認 AI_SERVICE 設置**
   - 檢查是否有 `AI_SERVICE` 變數
   - 如果沒有，添加：
     - **Key**：`AI_SERVICE`
     - **Value**：`deepseek`
     - **Environment**：All Environments
     - 點擊「Save」

5. **等待重新部署**
   - Railway 會自動檢測環境變數更改並重新部署
   - 等待約 2-5 分鐘
   - 或手動觸發：Deployments → 最新部署 → Redeploy

---

## 🖼️ 步驟 2：配置圖片搜尋服務 API Key（必須）

**選擇一個圖片服務配置（推薦順序）：**

### 選項 A：Google Custom Search API（推薦）⭐

#### 優點：
- 搜尋結果豐富
- 圖片品質高
- 免費額度充足

#### 配置步驟：

1. **獲取 Google API Key**
   - 訪問：https://console.cloud.google.com/
   - 登入 Google 帳號
   - 創建新專案或選擇現有專案
   - 進入「API 和服務」→「憑證」
   - 點擊「建立憑證」→「API 金鑰」
   - 複製 API Key

2. **啟用 Custom Search API**
   - 在 Google Cloud Console 中，進入「API 和服務」→「程式庫」
   - 搜尋「Custom Search API」
   - 點擊「啟用」

3. **創建 Custom Search Engine**
   - 訪問：https://programmablesearchengine.google.com/controlpanel/create
   - 填寫表單：
     - **搜尋引擎名稱**：例如「AI Agent Image Search」
     - **要搜尋的網站**：輸入 `*`（搜尋整個網路）
     - **語言**：選擇「中文（繁體）」或「所有語言」
   - 點擊「建立」
   - 點擊「控制台」進入設定頁面
   - 點擊「基本設定」
   - 找到「搜尋引擎 ID」，複製這個 ID

4. **配置到本地環境**
   - 打開 `backend/.env` 文件
   - 添加：
     ```env
     GOOGLE_API_KEY=your_google_api_key
     GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
     ```

5. **配置到 Railway**
   - 在 Railway Variables 中添加：
     - `GOOGLE_API_KEY` = `your_google_api_key`
     - `GOOGLE_SEARCH_ENGINE_ID` = `your_search_engine_id`

---

### 選項 B：Unsplash API（簡單）⭐

#### 優點：
- 配置簡單
- 圖片品質高
- 免費使用

#### 配置步驟：

1. **獲取 Unsplash API Key**
   - 訪問：https://unsplash.com/developers
   - 點擊「Your apps」
   - 點擊「New Application」
   - 填寫應用資訊：
     - **Application name**：例如「AI Agent Webapp」
     - **Description**：例如「Social media content generation」
   - 接受條款並點擊「Accept terms」
   - 創建後，複製 **Access Key**

2. **配置到本地環境**
   - 打開 `backend/.env` 文件
   - 添加：
     ```env
     UNSPLASH_ACCESS_KEY=your_unsplash_access_key
     ```

3. **配置到 Railway**
   - 在 Railway Variables 中添加：
     - `UNSPLASH_ACCESS_KEY` = `your_unsplash_access_key`

---

### 選項 C：Pexels API（免費）⭐

#### 優點：
- 完全免費
- 配置簡單
- 圖片品質好

#### 配置步驟：

1. **獲取 Pexels API Key**
   - 訪問：https://www.pexels.com/api/
   - 點擊「Get Started」或「Get API Key」
   - 登入或註冊帳號
   - 複製 API Key

2. **配置到本地環境**
   - 打開 `backend/.env` 文件
   - 添加：
     ```env
     PEXELS_API_KEY=your_pexels_api_key
     ```

3. **配置到 Railway**
   - 在 Railway Variables 中添加：
     - `PEXELS_API_KEY` = `your_pexels_api_key`

---

## ✅ 步驟 3：驗證配置

### 3.1 檢查 `.env` 文件（本地開發）

打開 `backend/.env` 文件，確認包含以下內容：

```env
# MongoDB 配置（應該已經有）
MONGODB_URL=mongodb+srv://...
MONGODB_DB_NAME=ai_agent_webapp

# 環境設定
ENVIRONMENT=development

# AI 服務配置（必須）
DEEPSEEK_API_KEY=sk-你的實際API Key（不是 your_api_key_here）
AI_SERVICE=deepseek

# 圖片服務配置（至少一個，必須）
# 選項 A：Google Custom Search（推薦）
GOOGLE_API_KEY=your_google_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id

# 或選項 B：Unsplash
# UNSPLASH_ACCESS_KEY=your_unsplash_access_key

# 或選項 C：Pexels
# PEXELS_API_KEY=your_pexels_api_key
```

### 3.2 重啟後端服務

**本地開發環境：**

1. **停止當前運行的服務**
   - 在終端中按 `Ctrl+C` 停止服務

2. **重新啟動服務**
   ```powershell
   cd backend
   .\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **檢查啟動日誌**
   - 應該看到：
     - ✅ `✅ DEEPSEEK_API_KEY 存在`
     - ✅ `✅ 圖片服務已配置` 或類似的訊息
   - 不應該看到：
     - ❌ `DeepSeek API Key 未設定`
     - ❌ `所有圖片服務的 API Key 都未設定`

**Railway 生產環境：**

1. **等待自動重新部署**
   - Railway 會在環境變數更改後自動重新部署
   - 等待約 2-5 分鐘

2. **檢查部署日誌**
   - 訪問 Railway Dashboard → Logs
   - 查看最新的部署日誌
   - 確認沒有配置錯誤

### 3.3 測試功能

1. **測試生成內容**
   - 訪問前端應用
   - 進入主題詳情頁面
   - 點擊「生成內容（500字文章 + 30秒腳本）」按鈕
   - 應該能夠成功生成內容，不應該顯示「API Key 未設定」錯誤

2. **測試圖片搜尋**
   - 在主題詳情頁面
   - 點擊「智能匹配照片（8張）」按鈕
   - 應該能夠搜尋並匹配照片
   - 不應該顯示「所有圖片服務的 API Key 都未設定」錯誤

---

## 🔍 步驟 4：故障排除

### 問題 1：API Key 無效

**症狀：**
- 後端日誌顯示「401 Unauthorized」或「API Key 無效」

**解決方案：**
1. 確認 API Key 完整且正確（沒有多餘空格）
2. 確認 API Key 沒有過期或被禁用
3. 在對應平台檢查 API Key 狀態
4. 如果無效，創建新的 API Key 並更新配置

### 問題 2：環境變數未生效

**症狀：**
- 後端日誌仍顯示「API Key 未設定」
- 即使已設置環境變數

**解決方案：**

**本地開發：**
1. 確認 `.env` 文件在 `backend` 目錄下
2. 確認 `.env` 文件格式正確（沒有語法錯誤）
3. 確認已重啟後端服務
4. 檢查 `.env` 文件是否被 `.gitignore` 忽略（應該被忽略）

**Railway：**
1. 確認環境變數已保存（點擊 Save 按鈕）
2. 確認選擇了正確的環境（Production）
3. 觸發手動重新部署
4. 檢查 Railway Logs 確認環境變數已讀取

### 問題 3：Google Custom Search Engine 未設置

**症狀：**
- Google API Key 有效，但搜尋失敗
- 錯誤訊息提到「Search Engine ID」

**解決方案：**
1. 確認已創建 Custom Search Engine
2. 確認已複製正確的 Search Engine ID
3. 確認 `GOOGLE_SEARCH_ENGINE_ID` 環境變數已設置
4. 在 Custom Search Engine 控制台確認設定正確

### 問題 4：圖片搜尋返回空結果

**症狀：**
- API Key 有效，但搜尋不到圖片
- 返回空數組

**解決方案：**
1. 檢查 API Key 額度是否充足
2. 檢查搜尋關鍵字是否合適
3. 嘗試使用不同的圖片服務（如果配置了多個）
4. 檢查網路連接和 API 服務狀態

---

## 📝 配置檢查清單

### 本地開發環境

- [ ] `backend/.env` 文件存在
- [ ] `DEEPSEEK_API_KEY` 已設置（不是 `your_api_key_here`）
- [ ] `AI_SERVICE=deepseek` 已設置
- [ ] 至少一個圖片服務 API Key 已設置：
  - [ ] `GOOGLE_API_KEY` + `GOOGLE_SEARCH_ENGINE_ID`
  - [ ] 或 `UNSPLASH_ACCESS_KEY`
  - [ ] 或 `PEXELS_API_KEY`
- [ ] `MONGODB_URL` 已設置
- [ ] `MONGODB_DB_NAME` 已設置
- [ ] 已重啟後端服務
- [ ] 後端日誌沒有配置錯誤

### Railway 生產環境

- [ ] `DEEPSEEK_API_KEY` 環境變數已添加
- [ ] `AI_SERVICE=deepseek` 環境變數已添加
- [ ] 至少一個圖片服務環境變數已添加
- [ ] 環境變數已保存
- [ ] Railway 已重新部署
- [ ] Railway Logs 沒有配置錯誤

---

## 🎯 完成後的預期結果

配置完成後，您應該能夠：

1. ✅ **生成主題** - 自動生成30個主題（3個分類 × 10個主題）
2. ✅ **顯示30字撮要** - 每個主題都有內容摘要
3. ✅ **顯示預覽圖片** - 每個主題都有至少1張預覽圖片
4. ✅ **生成500字內容** - 點擊生成內容按鈕後成功生成文章和腳本
5. ✅ **匹配8張照片** - 根據文章內容智能匹配相關照片
6. ✅ **完整流程** - 從主題生成到內容和圖片匹配的完整流程都能正常工作

---

## 📞 需要幫助？

如果按照上述步驟操作後仍有問題：

1. **檢查後端日誌** - 查看具體錯誤訊息
2. **驗證 API Key** - 確認 API Key 格式正確且有效
3. **檢查環境變數** - 確認環境變數已正確設置並生效
4. **測試 API 連接** - 確認後端能夠訪問外部 API
5. **查看詳細報告** - 參考 `核心功能問題診斷報告與解決方案.md`

---

**配置完成後，請重新生成主題並測試所有功能！**

