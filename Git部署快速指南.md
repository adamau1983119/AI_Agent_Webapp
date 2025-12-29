# Git 部署快速指南

> **為什麼使用 Git 更簡單？**
> - ✅ **自動部署**：推送代碼後自動觸發部署
> - ✅ **版本控制**：可以追蹤所有變更
> - ✅ **快速回滾**：出問題可以快速恢復
> - ✅ **協作方便**：多人協作更容易
> - ✅ **一鍵部署**：連接 GitHub 後，Vercel 和 Railway 會自動部署

---

## 🚀 快速步驟（約 10 分鐘）

### 步驟 1：提交本地代碼到 Git（2 分鐘）

```powershell
# 1. 進入專案目錄
cd "F:\Adam 2025\Myproject\AI_Agent_Wbbapp_for_Social_Media_Content_Generation"

# 2. 添加所有檔案（包括未追蹤的檔案）
git add .

# 3. 提交代碼
git commit -m "準備部署：添加部署配置檔案"

# 4. 檢查狀態
git status
```

### 步驟 2：在 GitHub 建立倉庫（3 分鐘）

1. **訪問 GitHub**：https://github.com
2. **登入**您的帳號
3. **建立新倉庫**：
   - 點擊右上角 "+" → "New repository"
   - 倉庫名稱：`AI_Agent_Webapp`（或您喜歡的名稱）
   - 選擇 **Public** 或 **Private**
   - **不要**勾選 "Initialize this repository with a README"（因為我們已經有代碼）
   - 點擊 "Create repository"

### 步驟 3：連接本地倉庫到 GitHub（2 分鐘）

```powershell
# 1. 添加遠端倉庫（將 YOUR_USERNAME 替換為您的 GitHub 用戶名）
git remote add origin https://github.com/YOUR_USERNAME/AI_Agent_Webapp.git

# 2. 推送到 GitHub
git branch -M main
git push -u origin main
```

**如果遇到認證問題**：
- 使用 GitHub Personal Access Token（推薦）
- 或使用 GitHub Desktop 應用程式

### 步驟 4：在 Vercel 部署前端（3 分鐘）

1. **訪問 Vercel**：https://vercel.com
2. **登入**（使用 GitHub 帳號）
3. **建立新專案**：
   - 點擊 "New Project"
   - 選擇您剛建立的 GitHub 倉庫
   - **Root Directory**：選擇 `frontend`
   - **Framework Preset**：Vite
   - **Build Command**：`npm run build`
   - **Output Directory**：`dist`
4. **設定環境變數**：
   ```
   VITE_API_URL=https://your-backend-api.railway.app/api/v1
   VITE_USE_MOCK=false
   ```
   （先留空，等後端部署完成後再填入）
5. **部署**：點擊 "Deploy"

### 步驟 5：在 Railway 部署後端（5 分鐘）

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

### 步驟 6：更新前端環境變數（2 分鐘）

1. **回到 Vercel**專案設定
2. **更新環境變數**：
   - `VITE_API_URL` = `https://your-api.railway.app/api/v1`
   - 將 `your-api.railway.app` 替換為實際的 Railway 網域
3. **重新部署**：Vercel 會自動重新部署

### 步驟 7：更新後端 CORS（1 分鐘）

1. **回到 Railway**專案設定
2. **更新環境變數**：
   - `CORS_ORIGINS` = `["https://your-app.vercel.app"]`
   - 將 `your-app.vercel.app` 替換為實際的 Vercel 網域
3. **重新部署**：Railway 會自動重新部署

---

## ✅ 完成！

現在您的專案已經：
- ✅ 代碼已推送到 GitHub
- ✅ 前端已部署到 Vercel
- ✅ 後端已部署到 Railway
- ✅ 自動部署已啟用（每次推送代碼都會自動部署）

---

## 🔄 更新代碼流程

以後更新代碼只需要：

```powershell
# 1. 修改代碼
# ... 編輯檔案 ...

# 2. 提交變更
git add .
git commit -m "更新：描述您的變更"

# 3. 推送到 GitHub
git push

# 4. Vercel 和 Railway 會自動部署！
```

---

## 🎯 優勢總結

### 使用 Git 部署的優勢：

1. **自動化**：推送代碼後自動部署，無需手動操作
2. **版本控制**：可以查看所有變更歷史
3. **快速回滾**：出問題可以快速恢復到之前的版本
4. **協作方便**：多人可以同時開發
5. **CI/CD**：自動測試和部署流程

### 不使用 Git 的缺點：

1. **手動操作**：每次更新都需要手動上傳檔案
2. **沒有版本控制**：無法追蹤變更歷史
3. **無法回滾**：出問題難以恢復
4. **協作困難**：多人協作時容易衝突

---

## 📝 注意事項

1. **不要提交敏感資訊**：
   - `.env` 檔案已在 `.gitignore` 中
   - 環境變數在部署平台設定，不要提交到 Git

2. **定期提交**：
   - 完成一個功能就提交一次
   - 使用清晰的 commit 訊息

3. **分支管理**（可選）：
   - `main` 分支用於生產環境
   - `develop` 分支用於開發（可選）

---

## 🆘 遇到問題？

### 問題 1：Git 推送失敗

**解決**：
- 檢查網路連接
- 確認 GitHub 認證（使用 Personal Access Token）
- 確認倉庫 URL 正確

### 問題 2：Vercel/Railway 無法連接 GitHub

**解決**：
- 確認已授權 GitHub 存取
- 檢查倉庫是否為 Private（可能需要升級方案）
- 確認 Root Directory 設定正確

### 問題 3：部署失敗

**解決**：
- 檢查部署日誌
- 確認環境變數已正確設定
- 確認建置命令正確

---

**最後更新**：2025-12-29  
**狀態**：✅ 準備就緒，可以開始部署！

