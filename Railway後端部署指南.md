# Railway 後端部署指南

> **專案**：AI Agent Webapp - Backend  
> **GitHub 倉庫**：https://github.com/adamau1983119/AI_Agent_Webapp  
> **框架**：FastAPI + Python

---

## 🚀 步驟 1：訪問 Railway 並登入

1. **訪問 Railway**：https://railway.app
2. **登入**：
   - 點擊右上角 "Login"
   - 選擇 "Continue with GitHub"
   - 授權 Railway 存取您的 GitHub 帳號

---

## 🚀 步驟 2：建立新專案

1. **點擊 "New Project"**（或 "+ New" 按鈕）
2. **選擇 "Deploy from GitHub repo"**
3. **選擇倉庫**：
   - 在倉庫列表中，找到並選擇 `adamau1983119/AI_Agent_Webapp`
   - 如果沒有看到，點擊 "Configure GitHub App" 授權

---

## ⚙️ 步驟 3：設定 Root Directory

**這是最重要的設定！**

1. **點擊專案名稱**（或齒輪圖標）進入專案設定
2. **找到 "Root Directory"** 設定
3. **設定為**：`backend`
4. **保存**

**為什麼重要？**
- 後端代碼在 `backend/` 目錄中
- Railway 需要知道從哪裡開始建置
- 如果設定錯誤，Railway 找不到 `requirements.txt` 和 `app/main.py`

---

## ⚙️ 步驟 4：設定環境變數

在 Railway 專案中，點擊 **"Variables"** 標籤，添加以下環境變數：

### 必須設定的環境變數

#### 1. MONGODB_URL
```
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
```
**說明**：
- 替換 `username`、`password`、`cluster` 為您的 MongoDB Atlas 實際值
- 從 MongoDB Atlas Dashboard 複製連接字串

#### 2. MONGODB_DB_NAME
```
MONGODB_DB_NAME=ai_agent_webapp
```

#### 3. PORT
```
PORT=8000
```
**說明**：Railway 會自動設定 `$PORT`，但我們明確設定以確保正確

#### 4. AI_SERVICE
```
AI_SERVICE=ollama
```
**說明**：根據您使用的 AI 服務設定（ollama、gemini、qwen）

#### 5. ENVIRONMENT
```
ENVIRONMENT=production
```

#### 6. DEBUG
```
DEBUG=false
```

### 強烈建議設定的環境變數

#### 7. API_KEY（如果啟用認證）
```
API_KEY=your_secure_api_key_here
```
**說明**：生成一個安全的隨機字串作為 API Key

#### 8. CORS_ORIGINS
```
CORS_ORIGINS=["https://ai-agent-webapp-ten.vercel.app"]
```
**說明**：
- 使用您的前端 Vercel 網域
- 如果有多個網域，用逗號分隔：`["https://domain1.com","https://domain2.com"]`

### 可選環境變數（根據您使用的服務）

#### AI 服務 API Keys
```
# Ollama（如果使用雲端版本）
OLLAMA_API_KEY=your_ollama_api_key

# Gemini
GEMINI_API_KEY=your_gemini_api_key

# 通義千問
QWEN_API_KEY=your_qwen_api_key
```

#### 圖片搜尋服務 API Keys
```
# Unsplash
UNSPLASH_ACCESS_KEY=your_unsplash_key

# Pexels
PEXELS_API_KEY=your_pexels_key

# Pixabay
PIXABAY_API_KEY=your_pixabay_key

# Google Custom Search
GOOGLE_API_KEY=your_google_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
```

---

## 🚀 步驟 5：生成公開網域

1. **點擊 "Settings"** 標籤
2. **找到 "Networking"** 區塊
3. **點擊 "Generate Domain"**
4. **記下網域**（例如：`ai-agent-webapp-production.up.railway.app`）

**重要**：
- 這個網域將用於前端環境變數
- 格式通常是：`your-project-name.up.railway.app`

---

## ✅ 步驟 6：驗證部署

### 6.1 檢查部署狀態

1. **在 Railway Dashboard**，查看部署進度
2. **等待部署完成**（約 3-5 分鐘）
3. **確認狀態為 "Active"**

### 6.2 測試健康檢查端點

訪問後端健康檢查端點：
```
https://your-railway-domain.railway.app/health
```

**預期回應**：
```json
{
  "status": "healthy",
  "environment": "production",
  "version": "1.0.0",
  "timestamp": "2025-12-29T..."
}
```

### 6.3 測試 API 文檔

訪問後端 API 文檔：
```
https://your-railway-domain.railway.app/docs
```

**應該看到**：
- FastAPI 自動生成的 API 文檔
- 可以測試 API 端點

### 6.4 測試 API 端點

```bash
# 測試主題列表 API
curl https://your-railway-domain.railway.app/api/v1/topics?page=1&limit=1

# 如果啟用了 API Key 認證
curl -H "X-API-Key: your-api-key" https://your-railway-domain.railway.app/api/v1/topics?page=1&limit=1
```

---

## 🔄 步驟 7：更新前端環境變數

後端部署成功後：

1. **回到 Vercel**：https://vercel.com
2. **選擇專案**：`ai-agent-webapp`
3. **點擊 "Settings"** → **"Environment Variables"**
4. **更新 `VITE_API_URL`**：
   - 點擊編輯按鈕
   - 更新值為：`https://your-railway-domain.railway.app/api/v1`
   - 將 `your-railway-domain.railway.app` 替換為實際的 Railway 網域
5. **保存**：Vercel 會自動重新部署

---

## 🔄 步驟 8：驗證前端連接

1. **訪問前端**：https://ai-agent-webapp-ten.vercel.app/
2. **打開瀏覽器開發者工具**（F12）
3. **檢查 Console**：
   - 應該沒有 CORS 錯誤
   - 應該沒有 API 連接錯誤
4. **檢查 Network 標籤**：
   - API 請求應該返回 200 狀態碼
   - 可以看到 API 回應數據

---

## 📋 設定檢查清單

### 部署前
- [ ] 已登入 Railway（使用 GitHub）
- [ ] 已選擇正確的 GitHub 倉庫
- [ ] Root Directory 設定為 `backend`
- [ ] 所有必須的環境變數已設定
- [ ] MongoDB URL 已正確設定
- [ ] CORS_ORIGINS 已設定（包含前端網域）

### 部署後
- [ ] 部署狀態顯示 "Active"
- [ ] 健康檢查端點正常（`/health`）
- [ ] API 文檔可訪問（`/docs`）
- [ ] 前端環境變數已更新（使用後端網域）
- [ ] 前端可以成功連接後端 API
- [ ] 所有功能正常運作

---

## 🆘 常見問題

### 問題 1：部署失敗 - "Build Error"

**可能原因**：
- Root Directory 設定錯誤（應該是 `backend`）
- `requirements.txt` 有問題
- Python 版本不兼容

**解決**：
1. 檢查 Root Directory 是否為 `backend`
2. 查看 Railway 部署日誌中的錯誤訊息
3. 確認 `requirements.txt` 格式正確
4. 檢查 Python 版本（Railway 通常自動偵測）

### 問題 2：後端無法連接 MongoDB

**可能原因**：
- `MONGODB_URL` 環境變數錯誤
- MongoDB Atlas IP 白名單未設定

**解決**：
1. 檢查 `MONGODB_URL` 是否正確
2. 在 MongoDB Atlas Dashboard：
   - Network Access → Add IP Address
   - 添加 `0.0.0.0/0`（允許所有 IP）
3. 確認 MongoDB 用戶名和密碼正確

### 問題 3：CORS 錯誤

**可能原因**：
- 後端 `CORS_ORIGINS` 未包含前端網域
- 環境變數格式錯誤

**解決**：
1. 檢查 `CORS_ORIGINS` 環境變數
2. 確保格式正確：`["https://ai-agent-webapp-ten.vercel.app"]`
3. 確保包含完整的前端網域（包括 `https://`）
4. 重新部署後端

### 問題 4：API 請求返回 401 錯誤

**可能原因**：
- 啟用了 API Key 認證，但前端未發送
- API Key 不匹配

**解決**：
1. 檢查後端是否啟用了 API Key 認證
2. 如果啟用，檢查前端是否正確發送 `X-API-Key` header
3. 確認 API Key 值一致

### 問題 5：找不到模組（ModuleNotFoundError）

**可能原因**：
- `requirements.txt` 缺少依賴
- 依賴安裝失敗

**解決**：
1. 檢查 `requirements.txt` 是否包含所有依賴
2. 查看 Railway 部署日誌
3. 確認所有 Python 套件都已列出

---

## 📝 重要提示

1. **Root Directory 必須是 `backend`**：
   - 這是專案結構的要求
   - 如果設定錯誤，Railway 會找不到 `app/main.py`

2. **環境變數更新後需要重新部署**：
   - 更新環境變數後，Railway 會自動觸發重新部署
   - 或手動點擊 "Redeploy"

3. **自動部署已啟用**：
   - 每次推送代碼到 GitHub 的 `main` 分支
   - Railway 會自動重新部署

4. **MongoDB Atlas IP 白名單**：
   - Railway 的 IP 是動態的
   - 建議設定為 `0.0.0.0/0`（允許所有 IP）
   - 或使用 MongoDB Atlas 的 "Allow access from anywhere"

5. **API Key 安全**：
   - 生成一個強隨機字串作為 API Key
   - 不要提交到 GitHub
   - 只在部署平台設定

---

## 🎯 部署後的重要資訊

### 記錄這些資訊

1. **Railway 網域**：
   ```
   https://your-railway-domain.railway.app
   ```

2. **健康檢查端點**：
   ```
   https://your-railway-domain.railway.app/health
   ```

3. **API 文檔**：
   ```
   https://your-railway-domain.railway.app/docs
   ```

4. **API 基礎路徑**：
   ```
   https://your-railway-domain.railway.app/api/v1
   ```

### 更新部署記錄

部署完成後，記得更新 `部署記錄_重要資訊.md` 文件，填入實際的 Railway 網域。

---

## 🔄 更新代碼流程

以後更新後端代碼只需要：

```bash
# 1. 修改代碼
# ... 編輯檔案 ...

# 2. 提交變更
git add .
git commit -m "更新：描述您的變更"

# 3. 推送到 GitHub
git push

# 4. Railway 會自動部署！
```

---

## 📚 相關文件

- `部署記錄_重要資訊.md` - 完整部署記錄
- `部署完成_下一步指引.md` - 部署後指引
- `backend/README.md` - 後端說明
- `backend/requirements.txt` - Python 依賴清單

---

**最後更新**：2025-12-29  
**狀態**：✅ 準備就緒，可以開始部署！

