# Facebook App 設定指南

> **用途**：連接 Meta 平台（Instagram、Facebook、Threads）  
> **建立日期**：2026-02-13  
> **相關問題**：問題 #39 - 無法連接 Meta 平台

---

## 📋 步驟一：訪問 Facebook Developers

1. **打開瀏覽器**，訪問：https://developers.facebook.com/
2. **登入 Facebook 帳號**（如果尚未登入）
3. 如果首次使用，需要**同意開發者條款**

---

## 📋 步驟二：建立應用程式

1. **點擊右上角「我的應用程式」** → **「建立應用程式」**
2. **選擇應用程式類型**：
   - 選擇 **「商業」**（Business）類型
   - 點擊「下一步」
3. **填寫應用程式資訊**：
   - **應用程式名稱**：例如 `Influencers AI` 或 `AI Agent Webapp`
   - **應用程式聯絡電子郵件**：您的 Email
   - **應用程式用途**：選擇「管理業務資產」或「其他」
   - 點擊「建立應用程式」

---

## 📋 步驟三：添加產品（Products）

您的應用程式需要以下產品來支援 Instagram、Facebook 和 Threads：

### 3.1 添加 Instagram Basic Display（可選，用於個人帳號）

1. 在應用程式儀表板中，找到 **「新增產品」** 或 **「設定」** → **「基本」**
2. 如果只需要商業帳號，可以跳過此步驟

### 3.2 添加 Instagram Graph API（必須）

1. 在應用程式儀表板中，點擊 **「新增產品」**
2. 找到 **「Instagram Graph API」**，點擊 **「設定」**
3. 按照提示完成設定

### 3.3 添加 Facebook Login（必須）

1. 在應用程式儀表板中，點擊 **「新增產品」**
2. 找到 **「Facebook 登入」**（Facebook Login），點擊 **「設定」**
3. 選擇 **「網頁」**（Web）作為平台

### 3.4 添加 Pages（必須，用於管理 Facebook 頁面）

1. 在應用程式儀表板中，點擊 **「新增產品」**
2. 找到 **「Facebook 登入」**（已添加），在設定中找到 **「頁面」**（Pages）相關設定

---

## 📋 步驟四：配置 OAuth 設定

### 4.1 設定有效的 OAuth 重定向 URI

1. 在應用程式儀表板中，點擊 **「設定」** → **「基本」**
2. 向下滾動找到 **「有效的 OAuth 重新導向 URI」**（Valid OAuth Redirect URIs）
3. **添加以下 URI**（根據您的環境）：
   ```
   http://localhost:8000/api/v1/social/meta/callback
   ```
   - 如果是生產環境，還需要添加生產環境的 URL
   - 例如：`https://your-domain.com/api/v1/social/meta/callback`
4. 點擊 **「儲存變更」**

### 4.2 設定應用程式網域（可選，但建議）

1. 在 **「設定」** → **「基本」** 中
2. 找到 **「應用程式網域」**（App Domains）
3. 添加：`localhost`（開發環境）和您的生產環境網域

---

## 📋 步驟五：取得 App ID 和 App Secret

1. 在應用程式儀表板中，點擊 **「設定」** → **「基本」**
2. **應用程式編號**（App ID）：
   - 顯示在頁面頂部
   - 複製此編號（例如：`1234567890123456`）
3. **應用程式密鑰**（App Secret）：
   - 點擊 **「顯示」** 按鈕（可能需要輸入 Facebook 密碼）
   - 複製此密鑰（例如：`abcdef1234567890abcdef1234567890`）
   - ⚠️ **重要**：請妥善保管 App Secret，不要洩露

---

## 📋 步驟六：配置權限（Permissions）

您的應用程式需要以下權限：

### 6.1 基本權限（自動包含）
- `public_profile`
- `email`

### 6.2 Instagram 權限
- `instagram_basic` - 讀取基本資訊
- `instagram_content_publish` - 發布內容
- `instagram_manage_comments` - 管理留言

### 6.3 Facebook 頁面權限
- `pages_show_list` - 查看頁面列表
- `pages_read_engagement` - 讀取互動數據
- `pages_manage_posts` - 管理貼文（發布內容）

### 6.4 如何添加權限

1. 在應用程式儀表板中，點擊 **「工具」** → **「圖形 API 總管」**（Graph API Explorer）
2. 選擇您的應用程式
3. 在 **「權限」**（Permissions）中，可以查看和測試權限
4. **注意**：某些權限需要 **應用程式審查**（App Review）才能使用

---

## 📋 步驟七：設定應用程式為開發模式（開發環境）

1. 在應用程式儀表板中，點擊 **「設定」** → **「基本」**
2. 找到 **「應用程式審查」**（App Review）區段
3. 確認應用程式處於 **「開發模式」**（Development Mode）
4. **添加測試用戶**（如果需要測試）：
   - 點擊 **「角色」** → **「測試用戶」**
   - 點擊 **「新增測試用戶」**

---

## 📋 步驟八：配置環境變數

1. **打開 `backend/.env` 文件**（如果不存在，請建立）
2. **添加以下環境變數**：
   ```env
   # Meta (Instagram + Facebook + Threads)
   META_APP_ID=your_app_id_here
   META_APP_SECRET=your_app_secret_here
   BACKEND_URL=http://localhost:8000
   ```
3. **替換值**：
   - `your_app_id_here` → 您的 App ID（步驟五取得）
   - `your_app_secret_here` → 您的 App Secret（步驟五取得）
   - `BACKEND_URL` → 您的後端 URL（開發環境通常是 `http://localhost:8000`）

---

## 📋 步驟九：重啟後端服務

1. **停止後端服務**（如果正在運行）
2. **重新啟動後端服務**：
   ```bash
   cd backend
   .\venv\Scripts\activate
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

---

## 📋 步驟十：測試連接

1. **打開前端應用**：http://localhost:3000
2. **導航到「平台連接」頁面**：`/social-connect`
3. **點擊「連接 Meta」按鈕**
4. **應該會跳轉到 Facebook 授權頁面**（而不是錯誤頁面）
5. **授權後應該成功連接**

---

## ⚠️ 常見問題

### Q1: 仍然顯示「應用程式編號無效」錯誤
- **檢查**：確認 `META_APP_ID` 和 `META_APP_SECRET` 已正確設置在 `.env` 文件中
- **檢查**：確認已重啟後端服務
- **檢查**：確認 App ID 和 App Secret 沒有多餘的空格

### Q2: 授權後顯示「重定向 URI 不匹配」錯誤
- **檢查**：確認在 Facebook App 設定中添加了正確的重定向 URI
- **檢查**：確認 `BACKEND_URL` 環境變數與重定向 URI 一致

### Q3: 某些權限需要審查
- **說明**：某些進階權限（如 `pages_manage_posts`）需要通過 Facebook 應用程式審查
- **解決**：開發環境可以使用測試用戶，或申請應用程式審查

### Q4: 無法發布到 Instagram
- **檢查**：確認已添加「Instagram Graph API」產品
- **檢查**：確認 Instagram 帳號已連接到 Facebook 頁面
- **檢查**：確認使用的是 Instagram Business 或 Creator 帳號（不是個人帳號）

---

## 📝 所需權限完整列表

根據代碼 `backend/app/models/social_connection.py:209-220`，應用程式需要以下權限：

```python
META_OAUTH_SCOPES = [
    "instagram_basic",              # Instagram 基本資訊
    "instagram_content_publish",     # Instagram 發布內容
    "instagram_manage_comments",     # Instagram 管理留言
    "pages_show_list",               # 查看 Facebook 頁面列表
    "pages_read_engagement",         # 讀取 Facebook 頁面互動數據
    "pages_manage_posts",            # 管理 Facebook 頁面貼文（發布）
    # 可能還有其他權限...
]
```

---

## 🔗 相關資源

- **Facebook Developers 文檔**：https://developers.facebook.com/docs/
- **Instagram Graph API 文檔**：https://developers.facebook.com/docs/instagram-api/
- **Facebook Login 文檔**：https://developers.facebook.com/docs/facebook-login/
- **應用程式審查指南**：https://developers.facebook.com/docs/app-review/

---

## 📝 備註

- 此指南適用於開發環境設定
- 生產環境需要額外配置（SSL、網域驗證等）
- 某些權限可能需要應用程式審查才能使用
- 請妥善保管 App Secret，不要提交到 Git 倉庫

---

**建立日期**：2026-02-13  
**最後更新**：2026-02-13

