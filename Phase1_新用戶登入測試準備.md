# Phase 1 測試準備 - 新用戶 Google OAuth 登入流程

> **測試日期**：2026-02-03  
> **測試場景**：新客戶首次使用 → 語言選擇 → 繁體中文 → Google 登入

---

## 📋 測試流程

1. **進入首頁** → 自動重定向到語言選擇頁面
2. **選擇繁體中文** → 儲存語言偏好，跳轉到登入頁面
3. **點擊 Google 登入** → 跳轉到 Google 授權頁面
4. **Google 授權** → 回調後建立新帳號，自動登入
5. **進入 Dashboard** → 測試完成

---

## 🔧 步驟 1：後端環境變數檢查

### 必要的環境變數（backend/.env）

```env
# ============================================
# JWT 認證配置（必須）
# ============================================
JWT_SECRET=請設定一個至少32字元的隨機密鑰
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080

# ============================================
# Google OAuth 配置（必須）
# ============================================
GOOGLE_OAUTH_CLIENT_ID=你的Google Client ID.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=你的Google Client Secret
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback

# ============================================
# MongoDB 配置（必須）
# ============================================
MONGODB_URL=你的MongoDB連接字串
MONGODB_DB_NAME=ai_agent_webapp

# ============================================
# 會員系統配置
# ============================================
MAX_USERS=100
```

### 如何獲取 Google OAuth 憑證

1. **前往 Google Cloud Console**
   - https://console.cloud.google.com/

2. **建立專案或選擇現有專案**

3. **啟用 API**
   - 導航到「API 和服務」→「程式庫」
   - 搜尋「Google+ API」或「People API」
   - 點擊「啟用」

4. **建立 OAuth 憑證**
   - 導航到「API 和服務」→「憑證」
   - 點擊「建立憑證」→「OAuth 用戶端 ID」
   - 選擇「網路應用程式」
   - 設定授權重新導向 URI：
     - `http://localhost:8000/api/v1/auth/google/callback`
   - 複製 Client ID 和 Client Secret

5. **設定 OAuth 同意畫面**
   - 導航到「OAuth 同意畫面」
   - 選擇「外部」使用者類型
   - 填寫必要資訊（應用程式名稱、使用者支援電子郵件等）
   - 新增範圍：`email`, `profile`, `openid`
   - 如果是測試環境，新增測試使用者

---

## 🔧 步驟 2：前端環境變數檢查

### 必要的環境變數（frontend/.env）

```env
VITE_API_URL=http://localhost:8000/api/v1
```

---

## 🚀 步驟 3：啟動服務

### 3.1 啟動後端

```powershell
cd backend
.\venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**成功標誌：**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

### 3.2 啟動前端

```powershell
cd frontend
npm run dev
```

**成功標誌：**
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:3000/
```

> ⚠️ **重要**：確認 `backend/.env` 中的 `FRONTEND_URL` 設定與前端實際運行的端口一致：
> ```env
> FRONTEND_URL=http://localhost:3000
> ```

---

## 🧹 步驟 4：清除瀏覽器數據（模擬新用戶）

### 方法 1：瀏覽器開發者工具

1. **打開 Chrome DevTools**（F12 或 Ctrl+Shift+I）
2. **進入 Application 標籤**
3. **清除 Local Storage**
   - 在左側選擇「Local Storage」→ `http://localhost:5173`
   - 點擊右鍵 → 「Clear」
4. **清除 Session Storage**
   - 在左側選擇「Session Storage」→ `http://localhost:5173`
   - 點擊右鍵 → 「Clear」
5. **刷新頁面**

### 方法 2：在前端開發環境使用測試按鈕

語言選擇頁面（`/language`）在開發環境下有一個「[測試] 清除語言偏好」按鈕，點擊即可清除。

### 需要清除的 localStorage 項目

| Key | 說明 |
|-----|------|
| `preferred-language` | 語言偏好 |
| `i18n-storage` | i18n 儲存 |
| `auth_token` | JWT Token |

---

## ✅ 測試檢查清單

### 環境準備

- [ ] `JWT_SECRET` 已設定
- [ ] `GOOGLE_OAUTH_CLIENT_ID` 已設定
- [ ] `GOOGLE_OAUTH_CLIENT_SECRET` 已設定
- [ ] `GOOGLE_OAUTH_REDIRECT_URI` 設定為 `http://localhost:8000/api/v1/auth/google/callback`
- [ ] MongoDB 連接正常
- [ ] 後端服務運行在 http://localhost:8000
- [ ] 前端服務運行在 http://localhost:5173
- [ ] 瀏覽器 localStorage 已清除

### 測試步驟驗證

- [ ] 訪問 `http://localhost:5173/` 自動跳轉到 `/language`
- [ ] 語言選擇頁面顯示正常
- [ ] 點擊「繁體中文」後跳轉到 `/login`
- [ ] 登入頁面顯示繁體中文 UI
- [ ] 點擊「使用 Google 登入」跳轉到 Google 授權頁面
- [ ] Google 授權後回調到 `/oauth-callback`
- [ ] 自動建立新帳號並登入
- [ ] 成功跳轉到 Dashboard

---

## 🐛 常見問題排查

### 問題 1：Google OAuth 未配置

**症狀：** 點擊 Google 登入按鈕顯示「Google OAuth 未配置」

**解決：**
1. 確認 `GOOGLE_OAUTH_CLIENT_ID` 已設定
2. 確認 `GOOGLE_OAUTH_CLIENT_SECRET` 已設定
3. 重啟後端服務

### 問題 2：Redirect URI 不匹配

**症狀：** Google 授權頁面顯示「redirect_uri_mismatch」錯誤

**解決：**
1. 在 Google Cloud Console 的 OAuth 憑證設定中
2. 確認「授權重新導向 URI」包含：
   - `http://localhost:8000/api/v1/auth/google/callback`
3. 確認 `GOOGLE_OAUTH_REDIRECT_URI` 環境變數設定正確

### 問題 3：Token 交換失敗

**症狀：** 回調後顯示「token_exchange_failed」錯誤

**解決：**
1. 確認 `GOOGLE_OAUTH_CLIENT_SECRET` 正確
2. 檢查後端日誌獲取詳細錯誤

### 問題 4：語言選擇後沒有跳轉

**症狀：** 選擇語言後停留在同一頁面

**解決：**
1. 清除瀏覽器快取
2. 檢查瀏覽器 console 是否有 JavaScript 錯誤
3. 確認 React Router 正常工作

---

## 📝 測試記錄模板

```
測試日期：2026-02-03
測試人員：
測試環境：本地開發環境

【環境準備】
- 後端狀態：✅/❌
- 前端狀態：✅/❌
- Google OAuth：✅/❌

【測試結果】
1. 首頁重定向到語言選擇：✅/❌
2. 語言選擇頁面顯示：✅/❌
3. 選擇繁體中文：✅/❌
4. 登入頁面顯示：✅/❌
5. Google 登入按鈕：✅/❌
6. Google 授權頁面：✅/❌
7. OAuth 回調：✅/❌
8. 新帳號建立：✅/❌
9. 自動登入：✅/❌
10. Dashboard 顯示：✅/❌

【問題記錄】
- 

【備註】
- 
```

---

**文件建立時間：** 2026-02-03

