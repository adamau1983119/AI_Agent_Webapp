# Vercel 部署設定指南

> **專案**：AI Agent Webapp - Frontend  
> **GitHub 倉庫**：https://github.com/adamau1983119/AI_Agent_Webapp  
> **框架**：Vite + React + TypeScript

---

## 🚀 步驟 1：訪問 Vercel 並登入

1. **訪問 Vercel**：https://vercel.com
2. **登入**：
   - 點擊右上角 "Sign In"
   - 選擇 "Continue with GitHub"
   - 授權 Vercel 存取您的 GitHub 帳號

---

## 🚀 步驟 2：建立新專案

1. **點擊 "Add New..."** → **"Project"**
2. **選擇 GitHub 倉庫**：
   - 在倉庫列表中，找到並選擇 `adamau1983119/AI_Agent_Webapp`
   - 如果沒有看到，點擊 "Adjust GitHub App Permissions" 授權

---

## ⚙️ 步驟 3：設定專案配置

### 3.1 基本設定

在專案設定頁面，您會看到以下選項：

#### **Project Name（專案名稱）**
```
ai-agent-webapp
```
或您喜歡的其他名稱

#### **Framework Preset（框架預設）**
- 選擇：**Vite**

#### **Root Directory（根目錄）** ⚠️ **重要！**
- 點擊 "Edit" 按鈕
- 輸入：`frontend`
- **這是最重要的設定！** 因為前端代碼在 `frontend/` 目錄中

---

### 3.2 建置和輸出設定（展開後檢查）

點擊 **"> 建置和輸出設定"** 展開，確認以下設定：

#### **Build Command（建置命令）**
```
npm run build
```

#### **Output Directory（輸出目錄）**
```
dist
```

#### **Install Command（安裝命令）**
```
npm install
```

#### **Development Command（開發命令）**
```
npm run dev
```

---

### 3.3 環境變數設定（展開後設定）

點擊 **"> 環境變數"** 展開，添加以下環境變數：

#### **環境變數 1：VITE_API_URL**

1. 點擊 "Add New"
2. **Key（鍵）**：`VITE_API_URL`
3. **Value（值）**：
   ```
   https://your-backend-api.railway.app/api/v1
   ```
   ⚠️ **注意**：先留空或使用臨時值，等後端部署完成後再更新為實際的 Railway 網域
4. **Environment（環境）**：選擇所有環境
   - ✅ Production
   - ✅ Preview
   - ✅ Development

#### **環境變數 2：VITE_USE_MOCK**

1. 點擊 "Add New"
2. **Key（鍵）**：`VITE_USE_MOCK`
3. **Value（值）**：`false`
4. **Environment（環境）**：選擇所有環境
   - ✅ Production
   - ✅ Preview
   - ✅ Development

---

## 🚀 步驟 4：部署

1. **檢查所有設定**：
   - ✅ Root Directory：`frontend`
   - ✅ Framework Preset：`Vite`
   - ✅ Build Command：`npm run build`
   - ✅ Output Directory：`dist`
   - ✅ 環境變數已設定

2. **點擊綠色按鈕**："Deploy"

3. **等待部署完成**（約 2-5 分鐘）：
   - Vercel 會自動安裝依賴
   - 執行建置
   - 部署到 CDN

---

## ✅ 步驟 5：驗證部署

### 5.1 檢查部署狀態

1. 在 Vercel 專案頁面，您會看到部署進度
2. 部署成功後，會顯示：
   - ✅ "Ready" 狀態
   - 一個 URL（例如：`ai-agent-webapp.vercel.app`）

### 5.2 訪問網站

1. **點擊部署的 URL** 或 **"Visit"** 按鈕
2. **檢查網站**：
   - 頁面應該可以正常載入
   - 如果看到錯誤，檢查瀏覽器 Console（F12）

### 5.3 檢查環境變數

1. 在 Vercel 專案頁面，點擊 **"Settings"**
2. 點擊 **"Environment Variables"**
3. 確認環境變數已正確設定

---

## 🔄 步驟 6：更新環境變數（後端部署後）

等後端在 Railway 部署完成後：

1. **記下 Railway 後端網域**（例如：`your-api.railway.app`）

2. **回到 Vercel 專案設定**：
   - Settings → Environment Variables

3. **更新 `VITE_API_URL`**：
   - 點擊編輯按鈕
   - 更新值為：`https://your-api.railway.app/api/v1`
   - 將 `your-api.railway.app` 替換為實際的 Railway 網域

4. **重新部署**：
   - Vercel 會自動重新部署
   - 或手動點擊 "Redeploy"

---

## 📋 設定檢查清單

### 部署前
- [ ] 已登入 Vercel（使用 GitHub）
- [ ] 已選擇正確的 GitHub 倉庫
- [ ] Root Directory 設定為 `frontend`
- [ ] Framework Preset 選擇 `Vite`
- [ ] Build Command 為 `npm run build`
- [ ] Output Directory 為 `dist`
- [ ] 環境變數 `VITE_API_URL` 已設定（可先留空）
- [ ] 環境變數 `VITE_USE_MOCK` 已設定為 `false`

### 部署後
- [ ] 部署狀態顯示 "Ready"
- [ ] 可以訪問網站 URL
- [ ] 頁面可以正常載入
- [ ] 瀏覽器 Console 沒有錯誤（F12 檢查）

### 後端部署後
- [ ] 已更新 `VITE_API_URL` 為實際的 Railway 網域
- [ ] 已重新部署前端
- [ ] 前端可以成功連接後端 API

---

## 🆘 常見問題

### 問題 1：部署失敗 - "Build Error"

**可能原因**：
- Root Directory 設定錯誤（應該是 `frontend`）
- 建置命令錯誤

**解決**：
1. 檢查 Root Directory 是否為 `frontend`
2. 檢查 Build Command 是否為 `npm run build`
3. 查看部署日誌中的錯誤訊息

### 問題 2：頁面空白

**可能原因**：
- 環境變數未正確設定
- API URL 錯誤

**解決**：
1. 檢查瀏覽器 Console（F12）的錯誤訊息
2. 確認 `VITE_API_URL` 環境變數已正確設定
3. 確認後端 API 可以訪問

### 問題 3：找不到倉庫

**解決**：
1. 確認已授權 Vercel 存取 GitHub
2. 點擊 "Adjust GitHub App Permissions"
3. 確認倉庫是 Public 或已授權 Vercel 存取 Private 倉庫

### 問題 4：環境變數未生效

**解決**：
1. 確認環境變數已添加到所有環境（Production, Preview, Development）
2. 重新部署專案
3. 清除瀏覽器快取

---

## 📝 重要提示

1. **Root Directory 必須是 `frontend`**：
   - 這是專案結構的要求
   - 如果設定錯誤，Vercel 會找不到 `package.json`

2. **環境變數更新後需要重新部署**：
   - 更新環境變數後，Vercel 會自動觸發重新部署
   - 或手動點擊 "Redeploy"

3. **自動部署已啟用**：
   - 每次推送代碼到 GitHub 的 `main` 分支
   - Vercel 會自動重新部署

4. **預覽部署**：
   - 每次推送到其他分支或 Pull Request
   - Vercel 會建立預覽部署
   - 方便測試新功能

---

## 🎯 下一步

部署完成後：

1. **記下 Vercel 網域**（例如：`ai-agent-webapp.vercel.app`）
2. **部署後端到 Railway**（參考 `Railway部署設定指南.md`）
3. **更新前端環境變數**（使用 Railway 後端網域）
4. **更新後端 CORS**（允許 Vercel 前端網域）

---

**最後更新**：2025-12-29  
**狀態**：✅ 準備就緒，可以開始部署！

