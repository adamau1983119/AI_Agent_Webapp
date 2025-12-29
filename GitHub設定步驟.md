# GitHub 倉庫設定步驟

> **專案名稱**：AI Agent Webapp for Social Media Content Generation  
> **GitHub 用戶名**：adamau1983119

---

## 📋 步驟 1：在 GitHub 建立倉庫（您現在正在做）

### 在 GitHub 頁面上設定：

1. **Repository name**（倉庫名稱）：
   ```
   AI_Agent_Webapp
   ```
   或您喜歡的其他名稱（例如：`ai-agent-social-media`）

2. **Description**（描述，可選）：
   ```
   AI Agent Webapp for Social Media Content Generation - Full-stack application with React frontend and FastAPI backend
   ```

3. **Visibility**（可見性）：
   - ✅ 選擇 **Public**（公開）- 免費，任何人都可以看到
   - 或 **Private**（私有）- 只有您可以訪問（需要付費方案）

4. **其他選項**：
   - ❌ **不要**勾選 "Add a README file"（我們已經有 README.md）
   - ❌ **不要**選擇 ".gitignore"（我們已經有 .gitignore）
   - ❌ **不要**選擇 "Add a license"（可選）

5. **點擊綠色按鈕**："Create repository"

---

## 📋 步驟 2：提交本地代碼到 Git

在 PowerShell 中執行以下命令：

```powershell
# 1. 確保在專案目錄
cd "F:\Adam 2025\Myproject\AI_Agent_Wbbapp_for_Social_Media_Content_Generation"

# 2. 添加所有檔案（包括未追蹤的檔案）
git add .

# 3. 提交代碼
git commit -m "Initial commit: AI Agent Webapp with frontend and backend"

# 4. 檢查狀態（應該顯示 "nothing to commit"）
git status
```

---

## 📋 步驟 3：連接本地倉庫到 GitHub

在 PowerShell 中執行（**將 YOUR_REPO_NAME 替換為您在步驟 1 中建立的倉庫名稱**）：

```powershell
# 1. 添加遠端倉庫
git remote add origin https://github.com/adamau1983119/YOUR_REPO_NAME.git

# 例如，如果倉庫名稱是 AI_Agent_Webapp：
# git remote add origin https://github.com/adamau1983119/AI_Agent_Webapp.git

# 2. 將分支重命名為 main（GitHub 的標準）
git branch -M main

# 3. 推送到 GitHub
git push -u origin main
```

---

## 🔐 步驟 4：認證（如果需要）

如果 `git push` 時要求輸入用戶名和密碼：

### 方法 1：使用 Personal Access Token（推薦）

1. **建立 Token**：
   - 訪問：https://github.com/settings/tokens
   - 點擊 "Generate new token" → "Generate new token (classic)"
   - 勾選 `repo` 權限
   - 點擊 "Generate token"
   - **複製 Token**（只會顯示一次！）

2. **使用 Token**：
   - 用戶名：`adamau1983119`
   - 密碼：**貼上剛才複製的 Token**（不是 GitHub 密碼）

### 方法 2：使用 GitHub Desktop（更簡單）

1. 下載並安裝：https://desktop.github.com
2. 登入您的 GitHub 帳號
3. 在 GitHub Desktop 中：
   - File → Add Local Repository
   - 選擇專案目錄
   - 點擊 "Publish repository"

---

## ✅ 步驟 5：驗證

1. **訪問您的 GitHub 倉庫**：
   ```
   https://github.com/adamau1983119/YOUR_REPO_NAME
   ```

2. **確認所有檔案都已上傳**：
   - 應該看到 `backend/` 目錄
   - 應該看到 `frontend/` 目錄
   - 應該看到 `README.md`

---

## 🚀 步驟 6：在 Vercel 部署前端

1. **訪問 Vercel**：https://vercel.com
2. **登入**（使用 GitHub 帳號）
3. **建立新專案**：
   - 點擊 "New Project"
   - 選擇您剛建立的 GitHub 倉庫
   - **Root Directory**：選擇 `frontend`（重要！）
   - **Framework Preset**：選擇 `Vite`
   - **Build Command**：`npm run build`
   - **Output Directory**：`dist`
4. **設定環境變數**（可先留空，等後端部署完成後再填入）：
   ```
   VITE_API_URL=https://your-backend-api.railway.app/api/v1
   VITE_USE_MOCK=false
   ```
5. **點擊 "Deploy"**

---

## 🚀 步驟 7：在 Railway 部署後端

1. **訪問 Railway**：https://railway.app
2. **登入**（使用 GitHub 帳號）
3. **建立新專案**：
   - 點擊 "New Project"
   - 選擇 "Deploy from GitHub repo"
   - 選擇您剛建立的倉庫
4. **設定專案**：
   - **Root Directory**：`backend`
   - Railway 會自動偵測 Python 專案
5. **設定環境變數**：
   ```
   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/...
   MONGODB_DB_NAME=ai_agent_webapp
   PORT=8000
   AI_SERVICE=ollama
   ENVIRONMENT=production
   DEBUG=false
   ```
6. **生成公開網域**：
   - Settings → Networking → Generate Domain
   - 記下網域（例如：`your-api.railway.app`）

---

## 🔄 步驟 8：更新前端環境變數

1. **回到 Vercel**專案設定
2. **更新環境變數**：
   - `VITE_API_URL` = `https://your-api.railway.app/api/v1`
   - 將 `your-api.railway.app` 替換為實際的 Railway 網域
3. **重新部署**：Vercel 會自動重新部署

---

## 🔄 步驟 9：更新後端 CORS

1. **回到 Railway**專案設定
2. **更新環境變數**：
   - `CORS_ORIGINS` = `["https://your-app.vercel.app"]`
   - 將 `your-app.vercel.app` 替換為實際的 Vercel 網域
3. **重新部署**：Railway 會自動重新部署

---

## 📝 快速命令參考

```powershell
# 提交代碼
git add .
git commit -m "描述您的變更"
git push

# 查看狀態
git status

# 查看遠端倉庫
git remote -v
```

---

## 🆘 常見問題

### 問題 1：git push 失敗 - 認證錯誤

**解決**：
- 使用 Personal Access Token 而不是密碼
- 或使用 GitHub Desktop

### 問題 2：倉庫名稱已存在

**解決**：
- 選擇不同的倉庫名稱
- 或刪除現有的同名倉庫

### 問題 3：遠端倉庫已存在

**解決**：
```powershell
# 移除現有的遠端倉庫
git remote remove origin

# 重新添加
git remote add origin https://github.com/adamau1983119/YOUR_REPO_NAME.git
```

---

**最後更新**：2025-12-29  
**狀態**：✅ 準備就緒，可以開始設定！

