# 部署指南

> **專案名稱**：AI Agent Webapp for Social Media Content Generation  
> **版本**：1.0.0  
> **最後更新**：2025-12-24

---

## 📋 部署前準備

### 檢查清單

- [ ] 所有環境變數已設定
- [ ] MongoDB Atlas 已建立並可連接
- [ ] 至少一個 AI 服務已配置
- [ ] 至少一個圖片搜尋服務已配置（或使用 DuckDuckGo）
- [ ] 已閱讀 [網域設定指南.md](./網域設定指南.md)
- [ ] 已準備好部署平台的帳號

---

## 🚀 部署平台選擇

### 推薦組合

#### 選項 1：分離部署（推薦）
- **前端**：Vercel（免費，自動 HTTPS）
- **後端**：Railway（免費額度，易於設定）
- **資料庫**：MongoDB Atlas（已使用）

#### 選項 2：全端部署
- **平台**：Railway 或 Render（同時部署前後端）
- **資料庫**：MongoDB Atlas（已使用）

---

## 📦 前端部署

### Vercel 部署（推薦）

#### 步驟 1：準備專案

1. 確保 `frontend/package.json` 包含建置腳本：
   ```json
   {
     "scripts": {
       "build": "tsc && vite build"
     }
   }
   ```

2. 建立 `frontend/vercel.json`（可選）：
   ```json
   {
     "buildCommand": "npm run build",
     "outputDirectory": "dist",
     "devCommand": "npm run dev",
     "installCommand": "npm install"
   }
   ```

#### 步驟 2：部署到 Vercel

1. 登入 [Vercel](https://vercel.com)
2. 點擊 "New Project"
3. 連接 GitHub/GitLab 倉庫
4. 設定專案：
   - **Root Directory**：`frontend`
   - **Framework Preset**：Vite
   - **Build Command**：`npm run build`
   - **Output Directory**：`dist`

#### 步驟 3：設定環境變數

在 Vercel 專案設定中添加：

```
VITE_API_URL=https://your-backend-api.railway.app/api/v1
VITE_USE_MOCK=false
```

#### 步驟 4：部署

- Vercel 會自動部署
- 部署完成後會獲得一個 URL（例如：`your-app.vercel.app`）

---

### Netlify 部署

#### 步驟 1：準備專案

建立 `frontend/netlify.toml`：

```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

#### 步驟 2：部署到 Netlify

1. 登入 [Netlify](https://netlify.com)
2. 點擊 "New site from Git"
3. 連接倉庫並選擇 `frontend` 目錄
4. 設定環境變數（同 Vercel）
5. 部署

---

## 🔧 後端部署

### Railway 部署（推薦）

#### 步驟 1：準備專案

建立 `backend/railway.json`（可選）：

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### 步驟 2：部署到 Railway

1. 登入 [Railway](https://railway.app)
2. 點擊 "New Project"
3. 選擇 "Deploy from GitHub repo"
4. 選擇倉庫和 `backend` 目錄

#### 步驟 3：設定環境變數

在 Railway 專案設定中添加所有必要的環境變數（參考 `backend/.env.example`）：

**必須設定**：
```
MONGODB_URL=mongodb+srv://...
MONGODB_DB_NAME=ai_agent_webapp
AI_SERVICE=ollama
```

**建議設定**：
```
API_KEY=your_secure_api_key_here
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=["https://your-frontend-domain.vercel.app"]
```

#### 步驟 4：設定公開網域

1. 在 Railway 專案中點擊 "Settings"
2. 在 "Networking" 中生成公開網域
3. 記下網域（例如：`your-api.railway.app`）

---

### Render 部署

#### 步驟 1：準備專案

建立 `backend/render.yaml`（可選）：

```yaml
services:
  - type: web
    name: ai-agent-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: MONGODB_URL
        sync: false
      - key: AI_SERVICE
        value: ollama
```

#### 步驟 2：部署到 Render

1. 登入 [Render](https://render.com)
2. 點擊 "New +" → "Web Service"
3. 連接 GitHub 倉庫
4. 設定：
   - **Root Directory**：`backend`
   - **Environment**：Python 3
   - **Build Command**：`pip install -r requirements.txt`
   - **Start Command**：`uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### 步驟 3：設定環境變數

在 Render 專案設定中添加環境變數（同 Railway）

---

## 🔒 HTTPS 設定

### 自動 HTTPS（推薦）

大部分部署平台（Vercel、Netlify、Railway、Render）會自動提供 HTTPS，無需額外設定。

### 自訂網域 HTTPS

如果需要使用自訂網域：

1. **Vercel**：
   - 在專案設定中添加自訂網域
   - Vercel 會自動設定 SSL 憑證

2. **Railway/Render**：
   - 添加自訂網域
   - 使用 Let's Encrypt 自動生成 SSL 憑證

---

## 🌐 網域設定

### 必須開通的網域

詳見 [網域設定指南.md](./網域設定指南.md)

#### 核心服務
- `*.mongodb.net` - MongoDB Atlas
- 圖片搜尋服務網域（至少一個）
- AI 服務網域（如果使用雲端版本）

#### 部署平台網域
- 前端部署網域（例如：`your-app.vercel.app`）
- 後端 API 網域（例如：`your-api.railway.app`）

### CORS 設定（生產環境）

在後端環境變數中設定：

```env
CORS_ORIGINS=["https://your-frontend-domain.vercel.app","https://www.your-frontend-domain.com"]
```

或使用逗號分隔：

```env
CORS_ORIGINS=https://your-frontend-domain.vercel.app,https://www.your-frontend-domain.com
```

---

## 🔐 環境變數設定

### 後端環境變數（生產環境）

**必須設定**：
```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/...
MONGODB_DB_NAME=ai_agent_webapp
AI_SERVICE=ollama
ENVIRONMENT=production
DEBUG=false
```

**強烈建議設定**：
```env
API_KEY=your_secure_api_key_here
CORS_ORIGINS=["https://your-frontend-domain.com"]
```

**可選設定**：
```env
# AI 服務 API Key
OLLAMA_API_KEY=...
GEMINI_API_KEY=...
OPENAI_API_KEY=...

# 圖片搜尋服務 API Key
UNSPLASH_ACCESS_KEY=...
PEXELS_API_KEY=...
PIXABAY_API_KEY=...
GOOGLE_API_KEY=...
GOOGLE_SEARCH_ENGINE_ID=...
```

### 前端環境變數（生產環境）

**必須設定**：
```env
VITE_API_URL=https://your-backend-api.railway.app/api/v1
VITE_USE_MOCK=false
```

---

## 📊 部署後驗證

### 檢查清單

1. **前端檢查**：
   - [ ] 前端頁面可以正常載入
   - [ ] 可以連接後端 API
   - [ ] 所有功能正常運作

2. **後端檢查**：
   - [ ] 健康檢查端點正常：`https://your-api.railway.app/health`
   - [ ] API 文檔可訪問：`https://your-api.railway.app/docs`
   - [ ] 可以連接 MongoDB
   - [ ] AI 服務可以正常調用
   - [ ] 圖片搜尋功能正常

3. **整合檢查**：
   - [ ] 前端可以成功調用後端 API
   - [ ] CORS 設定正確
   - [ ] 認證功能正常（如果啟用）

### 測試命令

```bash
# 測試後端健康檢查
curl https://your-api.railway.app/health

# 測試後端 API（如果未啟用認證）
curl https://your-api.railway.app/api/v1/topics?page=1&limit=1

# 測試後端 API（如果啟用認證）
curl -H "X-API-Key: your-api-key" https://your-api.railway.app/api/v1/topics?page=1&limit=1
```

---

## 🐛 故障排除

### 常見問題

#### 1. CORS 錯誤

**問題**：前端無法連接後端 API，出現 CORS 錯誤

**解決**：
- 檢查後端 `CORS_ORIGINS` 環境變數
- 確保前端網域已添加到 CORS 允許列表
- 檢查前端 `VITE_API_URL` 是否正確

#### 2. MongoDB 連接失敗

**問題**：後端無法連接 MongoDB

**解決**：
- 檢查 `MONGODB_URL` 是否正確
- 檢查 MongoDB Atlas 的 IP 白名單設定
- 確認 MongoDB 用戶名和密碼正確

#### 3. API Key 認證失敗

**問題**：API 請求返回 401 錯誤

**解決**：
- 檢查前端是否正確發送 `X-API-Key` header
- 確認後端 `API_KEY` 環境變數已設定
- 確認 API Key 值一致

#### 4. 圖片搜尋失敗

**問題**：圖片搜尋返回錯誤

**解決**：
- 檢查圖片搜尋服務的 API Key 是否正確
- 確認至少一個圖片搜尋服務已配置
- 如果所有服務都失敗，系統會自動使用 DuckDuckGo（不需要 API Key）

#### 5. AI 服務調用失敗

**問題**：內容生成失敗

**解決**：
- 檢查 AI 服務的 API Key 是否正確
- 確認 `AI_SERVICE` 環境變數設定正確
- 檢查 AI 服務的網域是否可以存取

---

## 📚 相關文件

- [README.md](./README.md) - 專案總體說明
- [網域設定指南.md](./網域設定指南.md) - 網域設定說明
- [backend/.env.example](./backend/.env.example) - 後端環境變數範例
- [frontend/.env.example](./frontend/.env.example) - 前端環境變數範例
- [後端服務啟動步驟.md](./後端服務啟動步驟.md) - 本地開發指南

---

## 🔄 更新部署

### 自動部署（推薦）

如果使用 GitHub/GitLab 連接部署平台，推送代碼到主分支會自動觸發部署。

### 手動部署

1. 更新代碼
2. 提交並推送到遠端倉庫
3. 在部署平台手動觸發部署（如果需要）

---

## 📝 部署檢查清單

### 部署前
- [ ] 所有環境變數已設定
- [ ] 已閱讀網域設定指南
- [ ] 已準備好部署平台帳號
- [ ] 代碼已提交到 Git 倉庫

### 部署中
- [ ] 前端已部署並可訪問
- [ ] 後端已部署並可訪問
- [ ] 環境變數已正確設定
- [ ] CORS 設定正確

### 部署後
- [ ] 前端可以正常載入
- [ ] 前端可以連接後端 API
- [ ] 所有功能正常運作
- [ ] HTTPS 已啟用
- [ ] 健康檢查端點正常

---

**最後更新**：2025-12-24  
**維護者**：開發團隊

