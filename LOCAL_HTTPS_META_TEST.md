# 用本機 HTTPS 測試 Meta 連接（不需 ngrok）

Meta 要求 OAuth 回調網址為 **https**。若不想用 ngrok，可改為在**本機用自簽憑證跑 HTTPS**，一樣能測「平台連接」與「一鍵發文」。

**優點**：不需帳號、無第三方服務、網址固定為 `https://localhost:8000`，測完還原即可，不影響其他功能。（執行前請先關閉佔用 8000 的程式。）

---

## 一、前置：產生自簽憑證（只需做一次）

在 **backend** 目錄執行其一：

**方式 A：PowerShell（需系統有 OpenSSL，例如已安裝 Git for Windows）**

```powershell
cd "f:\Adam 2025\Myproject\AI_Agent_Wbbapp_for_Social_Media_Content_Generation\backend"
.\scripts\gen_ssl_cert.ps1
```

**方式 B：Python（需已安裝 `cryptography`）**

```powershell
cd "f:\Adam 2025\Myproject\AI_Agent_Wbbapp_for_Social_Media_Content_Generation\backend"
pip install cryptography
python scripts/gen_ssl_cert.py
```

會產生 `backend/certs/key.pem` 與 `backend/certs/cert.pem`（此目錄已加入 .gitignore，不會被提交）。

---

## 二、測試 Meta 時的步驟

### 1. 改後端 .env（僅測試時）

編輯 **backend\.env**，暫時改為：

```env
BACKEND_URL=https://localhost:8000
```

### 2. 用 HTTPS 啟動後端

**請先關閉佔用 8000 的程式**，然後在 **backend** 目錄執行：

```powershell
.\scripts\start_backend_https.ps1
```

或手動：

```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --ssl-keyfile=certs/key.pem --ssl-certfile=certs/cert.pem
```

### 3. 信任自簽憑證（瀏覽器一次）

用瀏覽器開啟：**https://localhost:8000/health**  
若出現「連線不是私密」之類警告，點「進階」→「繼續前往 localhost」即可。

### 4. 改前端 API 網址（僅測試時）

在 **frontend** 目錄建立或編輯 **.env**：

```env
VITE_API_URL=https://localhost:8000/api/v1
```

儲存後**重啟前端**。

### 5. 改 Meta 後台回調網址

1. 開啟 [Meta for Developers](https://developers.facebook.com/) → 你的應用程式
2. **應用程式設定** → **進階**
3. **授權回呼網址** 填：
   ```text
   https://localhost:8000/api/v1/social/meta/callback
   ```
4. 儲存變更。

### 6. 測試

瀏覽器開前端（例如 `http://localhost:3000`）→ **平台連接** → 連接 Meta → 完成授權後再試 **一鍵發布**。

---

## 三、測完後還原（避免影響其他功能）

- **backend\.env**：改回 `BACKEND_URL=http://localhost:8000`
- **frontend**：刪除 `frontend\.env` 或將 `VITE_API_URL` 改回 `http://localhost:8000/api/v1`
- 之後一般開發用**一般指令**啟動後端（不加 `--ssl-keyfile` / `--ssl-certfile`）即可。

---

## 四、與 ngrok 的取捨

| 項目         | 本機 HTTPS（本文件） | ngrok                |
|--------------|------------------------|----------------------|
| 是否需要帳號 | 否                     | 是（免費帳號+ token）|
| 網址是否固定 | 是（localhost）       | 免費版每次重開會變   |
| 是否改 .env  | 要，僅測試時           | 要，僅測試時         |
| 測完還原     | 要                     | 要                   |

若本機 HTTPS 可正常完成 Meta 授權與發文，就不必再依賴 ngrok。
