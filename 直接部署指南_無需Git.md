# 直接部署指南（無需 Git）

> **目標**：快速上線專案，跳過 Git 流程  
> **適用對象**：想要立即部署，不需要版本控制的用戶

---

## 📋 重要說明

### Git 不是必須的！

**好消息**：您**不需要**使用 Git 也可以部署專案！

雖然大部分部署平台推薦使用 Git（因為方便自動更新），但您也可以：
1. ✅ **直接上傳檔案**（ZIP）
2. ✅ **使用 CLI 工具**（命令行）
3. ✅ **手動部署**（FTP/SSH）

---

## 🚀 方法 1：直接上傳 ZIP 檔案（最簡單）

### 前端部署到 Vercel（推薦）

#### 步驟 1：準備前端檔案

1. **進入前端目錄**：
   ```bash
   cd frontend
   ```

2. **安裝依賴並建置**：
   ```bash
   npm install
   npm run build
   ```

3. **壓縮建置結果**：
   - 進入 `frontend/dist` 目錄
   - 將所有檔案壓縮成 ZIP（例如：`frontend-dist.zip`）

#### 步驟 2：部署到 Vercel

1. **訪問 Vercel**：https://vercel.com
2. **登入**：使用 GitHub、GitLab 或 Email 帳號
3. **建立新專案**：
   - 點擊 "Add New..." → "Project"
   - 選擇 "**Upload**" 或 "**Deploy**" 選項
   - 上傳 `frontend-dist.zip` 檔案
4. **設定環境變數**：
   - 在專案設定中添加：
     ```
     VITE_API_URL=https://your-backend-api.railway.app/api/v1
     VITE_USE_MOCK=false
     ```
5. **部署**：
   - Vercel 會自動解壓縮並部署
   - 完成後會獲得 URL（例如：`your-app.vercel.app`）

---

### 後端部署到 Railway（推薦）

#### 步驟 1：準備後端檔案

1. **進入後端目錄**：
   ```bash
   cd backend
   ```

2. **壓縮後端檔案**：
   - 選擇以下檔案和目錄：
     - `app/`（整個目錄）
     - `requirements.txt`
     - `Procfile`
     - `railway.json`
     - `.env.example`（作為參考）
   - **不要包含**：
     - `venv/`（虛擬環境）
     - `__pycache__/`（Python 快取）
     - `node_modules/`（如果有的話）
     - `.env`（敏感檔案）
   - 壓縮成 ZIP（例如：`backend.zip`）

#### 步驟 2：部署到 Railway

1. **訪問 Railway**：https://railway.app
2. **登入**：使用 GitHub 帳號（或 Email）
3. **建立新專案**：
   - 點擊 "New Project"
   - 選擇 "**Deploy from GitHub repo**"（即使您不上傳到 GitHub，也可以先建立空倉庫）
   - **或者**：選擇 "**Empty Project**"，然後手動上傳檔案
4. **上傳檔案**：
   - 如果 Railway 支援直接上傳，上傳 `backend.zip`
   - 或者使用 Railway CLI（見下方方法 2）
5. **設定環境變數**：
   - 在 Railway 專案設定中添加所有必要的環境變數（見下方清單）
6. **設定 Root Directory**：
   - 在專案設定中，設定 Root Directory 為 `backend`（如果上傳的是整個專案）
7. **生成公開網域**：
   - 在 Settings → Networking 中生成網域
   - 記下網域（例如：`your-api.railway.app`）

---

## 🛠️ 方法 2：使用 CLI 工具部署（推薦給進階用戶）

### 前端：Vercel CLI

#### 安裝 Vercel CLI

```bash
npm install -g vercel
```

#### 部署步驟

```bash
# 1. 進入前端目錄
cd frontend

# 2. 登入 Vercel
vercel login

# 3. 部署（會引導您設定）
vercel

# 4. 設定環境變數（如果需要）
vercel env add VITE_API_URL
# 輸入值：https://your-backend-api.railway.app/api/v1

# 5. 生產環境部署
vercel --prod
```

### 後端：Railway CLI

#### 安裝 Railway CLI

```bash
# Windows (使用 PowerShell)
iwr https://railway.app/install.sh | iex

# 或使用 npm
npm install -g @railway/cli
```

#### 部署步驟

```bash
# 1. 進入後端目錄
cd backend

# 2. 登入 Railway
railway login

# 3. 初始化專案
railway init

# 4. 連結到現有專案（或建立新專案）
railway link

# 5. 設定環境變數
railway variables set MONGODB_URL="your-mongodb-url"
railway variables set AI_SERVICE="ollama"
# ... 設定其他環境變數

# 6. 部署
railway up
```

---

## 📦 方法 3：使用 Render（支援直接上傳）

### 前端部署到 Render

1. **訪問 Render**：https://render.com
2. **登入**：使用 GitHub 或 Email
3. **建立新 Static Site**：
   - 點擊 "New +" → "Static Site"
   - 選擇 "**Upload ZIP**" 或 "**Upload Folder**"
   - 上傳 `frontend/dist` 目錄的內容
4. **設定環境變數**（如果需要）
5. **部署**

### 後端部署到 Render

1. **訪問 Render**：https://render.com
2. **登入**：使用 GitHub 或 Email
3. **建立新 Web Service**：
   - 點擊 "New +" → "Web Service"
   - 選擇 "**Upload ZIP**"
   - 上傳 `backend.zip`（包含所有後端檔案）
4. **設定**：
   - **Environment**：Python 3
   - **Build Command**：`pip install -r requirements.txt`
   - **Start Command**：`uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. **設定環境變數**（見下方清單）
6. **部署**

---

## 🔐 必須設定的環境變數

### 後端環境變數（Railway/Render）

**必須設定**：
```
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=ai_agent_webapp
PORT=8000
AI_SERVICE=ollama
```

**強烈建議設定**：
```
ENVIRONMENT=production
DEBUG=false
API_KEY=your_secure_api_key_here
CORS_ORIGINS=["https://your-frontend-domain.vercel.app"]
```

**可選設定**（根據您使用的服務）：
```
# AI 服務
OLLAMA_API_KEY=...
GEMINI_API_KEY=...
OPENAI_API_KEY=...

# 圖片搜尋服務
UNSPLASH_ACCESS_KEY=...
PEXELS_API_KEY=...
PIXABAY_API_KEY=...
GOOGLE_API_KEY=...
GOOGLE_SEARCH_ENGINE_ID=...
```

### 前端環境變數（Vercel/Render）

**必須設定**：
```
VITE_API_URL=https://your-backend-api.railway.app/api/v1
VITE_USE_MOCK=false
```

**注意**：將 `your-backend-api.railway.app` 替換為實際的後端網域

---

## 📋 部署檢查清單

### 部署前準備

- [ ] 後端檔案已準備（`backend/` 目錄，排除 `venv/` 和 `__pycache__/`）
- [ ] 前端已建置（`frontend/dist/` 目錄）
- [ ] MongoDB Atlas 已建立並可連接
- [ ] 至少一個 AI 服務已配置
- [ ] 至少一個圖片搜尋服務已配置（或使用 DuckDuckGo）
- [ ] 已準備好部署平台帳號（Vercel、Railway、Render）

### 部署步驟

- [ ] 後端已部署並可訪問
- [ ] 後端健康檢查正常：`https://your-api.railway.app/health`
- [ ] 前端已部署並可訪問
- [ ] 前端可以連接後端 API
- [ ] CORS 設定正確
- [ ] 所有環境變數已設定

### 部署後驗證

- [ ] 前端頁面可以正常載入
- [ ] 可以連接後端 API
- [ ] 所有功能正常運作
- [ ] HTTPS 已啟用

---

## 🎯 推薦部署流程（無需 Git）

### 步驟 1：準備檔案（5-10 分鐘）

```bash
# 1. 建置前端
cd frontend
npm install
npm run build
# 現在 frontend/dist/ 包含建置好的檔案

# 2. 準備後端（確保在 backend/ 目錄）
cd ../backend
# 確認以下檔案存在：
# - app/（整個目錄）
# - requirements.txt
# - Procfile
# - railway.json
```

### 步驟 2：部署後端（10-15 分鐘）

1. 登入 Railway：https://railway.app
2. 建立新專案
3. 上傳後端檔案（ZIP 或使用 CLI）
4. 設定環境變數
5. 生成公開網域
6. 記下後端 URL（例如：`your-api.railway.app`）

### 步驟 3：部署前端（5-10 分鐘）

1. 登入 Vercel：https://vercel.com
2. 建立新專案
3. 上傳 `frontend/dist/` 的內容（ZIP 或直接上傳）
4. 設定環境變數：
   ```
   VITE_API_URL=https://your-api.railway.app/api/v1
   ```
5. 記下前端 URL（例如：`your-app.vercel.app`）

### 步驟 4：更新 CORS（2 分鐘）

1. 回到 Railway 後端設定
2. 更新 `CORS_ORIGINS` 環境變數：
   ```
   CORS_ORIGINS=["https://your-app.vercel.app"]
   ```
3. 重新部署後端（如果需要）

### 步驟 5：測試（5 分鐘）

1. 訪問前端 URL
2. 測試所有功能
3. 檢查後端健康檢查：`https://your-api.railway.app/health`
4. 檢查 API 文檔：`https://your-api.railway.app/docs`

---

## ⚠️ 注意事項

### 不使用 Git 的缺點

1. **無法自動更新**：每次更新需要手動重新上傳
2. **沒有版本控制**：無法追蹤變更歷史
3. **無法回滾**：如果部署出問題，無法快速恢復

### 建議

即使不使用 Git 進行版本控制，也建議：
- ✅ 定期備份專案檔案
- ✅ 保留部署前的檔案副本
- ✅ 記錄每次部署的變更

---

## 🔄 更新部署（不使用 Git）

### 更新前端

1. 修改前端代碼
2. 重新建置：`cd frontend && npm run build`
3. 重新上傳 `frontend/dist/` 到 Vercel

### 更新後端

1. 修改後端代碼
2. 重新壓縮後端檔案
3. 重新上傳到 Railway/Render
4. 或使用 CLI：`railway up` 或 `vercel --prod`

---

## 📞 需要幫助？

如果遇到問題：

1. **檢查環境變數**：確保所有必要的環境變數已設定
2. **檢查日誌**：在部署平台查看部署日誌
3. **檢查網路**：確保 MongoDB 和外部 API 可以訪問
4. **檢查 CORS**：確保前端網域已添加到 CORS 允許列表

---

## ✅ 總結

**您不需要 Git 也可以部署！**

推薦方式：
1. **最簡單**：使用 ZIP 上傳到 Vercel（前端）和 Railway（後端）
2. **最靈活**：使用 CLI 工具（Vercel CLI、Railway CLI）
3. **最快速**：直接上傳建置好的檔案

**總時間**：約 30-60 分鐘即可完成部署！

---

**最後更新**：2025-12-29

