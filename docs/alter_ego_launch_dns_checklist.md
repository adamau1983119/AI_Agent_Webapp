# Alter Ego 上線 DNS 一頁 Checklist

> **品牌**：**Alter Ego**（對外寫法；程式庫名仍為 `AI_Agent_Webapp`）  
> **網域**：**`ai-alterego.com`**（Spaceship 註冊；2026-06-02 購入，自動續約至 2027-06-02）  
> **開發階段**：Spaceship DNS **暫不改**；本機 `localhost:3000`／`localhost:8000` 繼續開發  
> **上線觸發**：MVP 程式結案 + 整批測試通過後，依本檔與 [**附錄 A**](#附錄-a-spaceship-dns-要填哪幾行--alter-ego-env-對照表) 一次設定  
> **SoT 交叉**：[`專案完整架構表_v7.md`](../專案完整架構表_v7.md) **品牌與網域**、[`工作記錄.md`](../工作記錄.md) 頂部

---

## 核心（一句）

**上線日**：Spaceship 把 **`ai-alterego.com`** 指到託管主機 → **HTTPS 生效** → **`.env` 網址與 OAuth 回呼** 全改正式域 → **Meta／Google 後台** 補白名單 → **上線驗證路徑**（登入 → MyChannel／Discover）瀏覽器驗證。

---

## 前置（上線前一日可先做）

| # | 項目 | 狀態 | 備註 |
|---|------|:----:|------|
| P1 | 決定託管方案 | ☐ | **A** 單機 VPS（Nginx 反代前後端）或 **B** Vercel 前端 + Railway／Render 後端 |
| P2 | 備妥主機 IP 或平台預設網址 | ☐ | VPS：公網 IPv4；Vercel：專案已建立；Railway：服務已 deploy |
| P3 | TLS 策略 | ☐ | VPS：Let's Encrypt（Certbot）；託管：平台內建 HTTPS |
| P4 | MongoDB Atlas／Redis 生產連線 | ☐ | **勿** commit `.env`；僅 `backend/.env` + 託管平台 Secret |
| P5 | 備份本機 `.env` | ☐ | `backend/.env.backup`（已慣例）；上線前再匯出一份離線保管 |

---

## 上線當日 Checklist（依序勾）

### 1. Spaceship DNS（約 5～15 分 + 傳播）

| # | 項目 | 狀態 | 備註 |
|---|------|:----:|------|
| D1 | 登入 Spaceship → **Domains** → `ai-alterego.com` → **DNS Records** | ☐ | 開發期可維持預設／空白 |
| D2 | 依 [**附錄 A**](#附錄-a-spaceship-dns-要填哪幾行--alter-ego-env-對照表) 填入 **A／CNAME**（方案 A 或 B 擇一） | ☐ | 建議先加 **`www`**，根域 `@` 依平台要求 |
| D3 | 若有 **`api` 子域**：一併新增 **A 或 CNAME** | ☐ | 與 `BACKEND_URL` 一致 |
| D4 | `dig`／`nslookup` 確認解析 | ☐ | `ai-alterego.com`、`www`、`api`（若用）指向預期 |
| D5 | 等待 TTL 傳播（常見 5～30 分；最長 48h） | ☐ | 傳播前勿改 OAuth 白名單以免半套失敗 |

### 2. HTTPS 與反向代理

| # | 項目 | 狀態 | 備註 |
|---|------|:----:|------|
| H1 | 前端 **`https://ai-alterego.com`**（及 `www`）可開、憑證有效 | ☐ | 瀏覽器無 Mixed Content |
| H2 | 後端 **`https://api.ai-alterego.com`**（或同域 `/api`）**200** on `/health` | ☐ | `curl -I` 或瀏覽器 |
| H3 | Nginx／平台：前端靜態 + API 反代規則與 [**附錄 A**](#附錄-a-spaceship-dns-要填哪幾行--alter-ego-env-對照表) 一致 | ☐ | VPS 需手寫 `location /api` |
| H4 | **強制 HTTPS**（301 http→https） | ☐ | OAuth 廠商通常要求 https 回呼 |

### 3. Alter Ego 環境變數（後端 + 前端）

| # | 項目 | 狀態 | 備註 |
|---|------|:----:|------|
| E1 | `backend/.env`（或託管 Secret）依 **附錄 A** 生產欄位更新 | ☐ | `ENVIRONMENT=production`、`DEBUG=false` |
| E2 | `FRONTEND_URL` = 正式前端根 URL（含 `https`，無尾斜線） | ☐ | 郵件驗證／重設密碼連結用 |
| E3 | `BACKEND_URL` = 正式後端根 URL | ☐ | Meta `redirect_uri` 由此衍生 |
| E4 | `CORS_ORIGINS` 含正式前端域 | ☐ | JSON 陣列字串，見 `config_module` |
| E5 | `GOOGLE_OAUTH_REDIRECT_URI` = `{BACKEND_URL}/api/v1/auth/google/callback` | ☐ | 與 Google Cloud Console 一致 |
| E6 | `frontend/.env` **`VITE_API_URL`** 指向正式 API | ☐ | 改後須 **重建** 前端（`npm run build`） |
| E7 | 重啟後端／重新 deploy 前後端 | ☐ | uvicorn 不會熱載入所有 Secret |
| E8 | `python backend/check_meta_config.py` → **[OK]** | ☐ | 上線域下的 `redirect_uri` |

### 4. OAuth／第三方白名單

| # | 項目 | 狀態 | 備註 |
|---|------|:----:|------|
| O1 | **Meta** App → Valid OAuth Redirect URIs：`{BACKEND_URL}/api/v1/social/meta/callback` | ☐ | 與 `check_meta_config.py` 輸出逐字相同 |
| O2 | **Google** Cloud → Authorized redirect URIs：同 **E5** | ☐ | |
| O3 | **Google** Authorized JavaScript origins：`https://ai-alterego.com`（及 `www` 若用） | ☐ | |
| O4 | Meta **App Domains**／隱私權 URL（若上架審核） | ☐ | 指向正式 `/privacy` |

### 5. 上線驗證（禁止 Mock；須真實 API）

| # | 項目 | 狀態 | 備註 |
|---|------|:----:|------|
| S1 | `https://ai-alterego.com` → 語言／登入頁正常 | ☐ | Network 無大量 4xx |
| S2 | 登入（Email 或 Google）→ **MyChannel／dashboard** | ☐ | 對齊 v7.1 規格 |
| S3 | `GET /health` → `database: connected`（Atlas） | ☐ | |
| S4 | `/discover` 讀取真實 feed（**非** mock topics） | ☐ | 對齊 README 禁止模糊驗收 |
| S5 | `/social-connect` → Meta OAuth URL 域名正確 | ☐ | 可進授權頁即 PASS |
| S6 | 截圖存 **`docs/evidence/v7/YYYY-MM-DD/`** | ☐ | 見 `v7_evidence_screenshot_guide.md` |

### 6. 收尾

| # | 項目 | 狀態 | 備註 |
|---|------|:----:|------|
| F1 | `工作記錄.md` 頂部：DNS 上線日 + 方案 A/B 一句 | ☐ | |
| F2 | 本檔各表勾選完成或標 **BLOCK** + 原因 | ☐ | |
| F3 | 確認 **未** commit `.env`／`.env.backup` | ☐ | git status 審核 |

---

## 完成判定

- **PASS**：D2 + H1 + H2 + E1～E8 + O1～O2 + S1～S5 皆勾選，且有至少一張正式域截圖。  
- **BLOCK**：任一 OAuth 回呼 404／CORS 錯誤／憑證無效 — 記錄 URL + status，**不** retroactive 改開發預設。

---

## 附錄 A — Spaceship DNS 要填哪幾行 + Alter Ego `.env` 對照表

> **Placeholder**：`<VPS_IP>`、`<VERCEL_TARGET>`、`<RAILWAY_HOST>` 換成平台畫面顯示之實值。  
> **建議預設（本專案）**：**子域 API** — `api.ai-alterego.com` 指後端；根域指前端（與現有 `VITE_API_URL`／`BACKEND_URL` 拆分一致）。

### 方案 A — 單機 VPS（Nginx 反代前後端）

#### Spaceship DNS 記錄

| 類型 | Host／Name | Value／Points to | TTL | 用途 |
|------|------------|------------------|-----|------|
| **A** | `@` | `<VPS_IP>` | 300～3600 | 根域 → VPS |
| **A** | `www` | `<VPS_IP>` | 300～3600 | 或改 **CNAME** `www` → `ai-alterego.com` |
| **A** | `api` | `<VPS_IP>` | 300～3600 | 後端 API（與 `BACKEND_URL` 一致） |

> **可選**：僅用根域、API 走同機 Nginx `location /api` → 可**不建** `api` 子域；此時 `BACKEND_URL=https://ai-alterego.com` 且 `VITE_API_URL=https://ai-alterego.com/api/v1`（見方案 A′ 環境變數列）。

#### Nginx 概念（VPS）

| 對外 URL | 反代至 |
|----------|--------|
| `https://ai-alterego.com/` | `frontend` 靜態（`dist/`）或 `localhost:3000` |
| `https://api.ai-alterego.com/` | `http://127.0.0.1:8000` |

#### `backend/.env` 生產範例（方案 A · 子域 API）

```env
# —— 應用 ——
APP_NAME=Alter Ego
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
PORT=8000

# —— 網址（OAuth／郵件／CORS）——
FRONTEND_URL=https://ai-alterego.com
BACKEND_URL=https://api.ai-alterego.com
CORS_ORIGINS=["https://ai-alterego.com","https://www.ai-alterego.com"]

# —— Google OAuth ——
GOOGLE_OAUTH_CLIENT_ID=<your_google_client_id>
GOOGLE_OAUTH_CLIENT_SECRET=<your_google_client_secret>
GOOGLE_OAUTH_REDIRECT_URI=https://api.ai-alterego.com/api/v1/auth/google/callback

# —— Meta ——
META_APP_ID=<your_meta_app_id>
META_APP_SECRET=<your_meta_app_secret>

# —— 資料庫（Atlas 生產 cluster）——
MONGODB_URL=mongodb+srv://<user>:<pass>@<cluster>.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=alter_ego_production

# —— v7 生產開關（依營運定案調整；上線初可保守）——
AUTO_START_SCHEDULER=true
ENABLE_SCHEDULED_TOPIC_COLLECTION=false
ENABLE_AI_TOPIC_TRANSLATION=false
ENABLE_PUBLIC_FEED_PIPELINE=true
```

#### `frontend/.env` 生產範例（方案 A · 子域 API）

```env
VITE_API_URL=https://api.ai-alterego.com/api/v1
VITE_USE_MOCK=false
```

#### 方案 A′ — 同域 `/api`（無 `api` 子域）

| 類型 | Host | Value |
|------|------|-------|
| **A** | `@` | `<VPS_IP>` |
| **A** | `www` | `<VPS_IP>` |

```env
# backend
FRONTEND_URL=https://ai-alterego.com
BACKEND_URL=https://ai-alterego.com
GOOGLE_OAUTH_REDIRECT_URI=https://ai-alterego.com/api/v1/auth/google/callback

# frontend
VITE_API_URL=https://ai-alterego.com/api/v1
```

---

### 方案 B — Vercel（前端）+ Railway／Render（後端）

#### Spaceship DNS 記錄

| 類型 | Host／Name | Value／Points to | TTL | 用途 |
|------|------------|------------------|-----|------|
| **A** | `@` | `76.76.21.21` | 300 | Vercel 根域（以 Vercel 專案 **Domains** 頁為準） |
| **CNAME** | `www` | `cname.vercel-dns.com` | 300 | 或 Vercel 指定 target |
| **CNAME** | `api` | `<RAILWAY_HOST>` | 300 | 例：`xxx.up.railway.app`（Railway **Custom Domain** 綁 `api.ai-alterego.com` 後顯示） |

> **注意**：Vercel／Railway 畫面會給**精確** CNAME／A 值；上表為常見模板，**以平台當下指示覆蓋本表**。

#### 平台內設定

| 平台 | 設定項 | 值 |
|------|--------|-----|
| Vercel | Project → Domains | `ai-alterego.com`、`www.ai-alterego.com` |
| Vercel | Environment Variables | `VITE_API_URL=https://api.ai-alterego.com/api/v1` |
| Railway | Service → Settings → Domains | `api.ai-alterego.com` |
| Railway | Variables | 同下方 `backend/.env` 區塊（勿進 git） |

#### `backend/.env` 生產範例（方案 B）

```env
APP_NAME=Alter Ego
ENVIRONMENT=production
DEBUG=false

FRONTEND_URL=https://ai-alterego.com
BACKEND_URL=https://api.ai-alterego.com
CORS_ORIGINS=["https://ai-alterego.com","https://www.ai-alterego.com"]

GOOGLE_OAUTH_REDIRECT_URI=https://api.ai-alterego.com/api/v1/auth/google/callback
META_APP_ID=<your_meta_app_id>
META_APP_SECRET=<your_meta_app_secret>

MONGODB_URL=mongodb+srv://...
MONGODB_DB_NAME=alter_ego_production
```

#### `frontend/.env` 生產範例（方案 B）

```env
VITE_API_URL=https://api.ai-alterego.com/api/v1
VITE_USE_MOCK=false
```

---

### 環境變數 ↔ DNS／OAuth 對照（兩方案共用）

| 變數 | 填什麼 | 必須與誰一致 |
|------|--------|----------------|
| `FRONTEND_URL` | `https://ai-alterego.com`（或含 `www` 若為 canonical） | 使用者瀏覽器網址列；Google **JavaScript origins** |
| `BACKEND_URL` | `https://api.ai-alterego.com` **或** `https://ai-alterego.com` | Spaceship **`api` A/CNAME** 或 Nginx `/api` |
| `VITE_API_URL` | `{BACKEND_URL}/api/v1` | 前端 build 後寫死；改 DNS 後須 **rebuild** |
| `CORS_ORIGINS` | JSON 陣列，含所有前端 origin | 瀏覽器 `Origin` header |
| `GOOGLE_OAUTH_REDIRECT_URI` | `{BACKEND_URL}/api/v1/auth/google/callback` | Google Console **Authorized redirect URIs** |
| Meta `redirect_uri`（自動） | `{BACKEND_URL}/api/v1/social/meta/callback` | Meta App **Valid OAuth Redirect URIs** |
| 郵件內連結（自動） | `{FRONTEND_URL}/verify-email?…` 等 | `email_service` 讀 `FRONTEND_URL` |

### 本機開發對照（勿與上線混用）

| 變數 | 本機開發值 |
|------|------------|
| `FRONTEND_URL` | `http://localhost:3000` |
| `BACKEND_URL` | `http://localhost:8000` |
| `VITE_API_URL` | `http://localhost:8000/api/v1` |
| `CORS_ORIGINS` | `["http://localhost:3000","http://localhost:5173"]` |
| Spaceship DNS | **不變** |

---

## 相關文件

- [`專案完整架構表_v7.md`](../專案完整架構表_v7.md) — 品牌與網域、部署邏輯視圖  
- [`docs/v7_mychannel_checklist.md`](./v7_mychannel_checklist.md) — **DNS-0** 上線前交叉引用  
- [`backend/check_meta_config.py`](../backend/check_meta_config.py) — Meta OAuth 診斷  
- [`docs/環境重建指南與Checklist.md`](./環境重建指南與Checklist.md) — 本機重建（與上線 DNS 分離）
