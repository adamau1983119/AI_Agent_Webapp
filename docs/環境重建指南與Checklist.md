# 環境重建指南與 Checklist

> **用途**：硬碟遺失、換機、或僅有 Git 可還原時，依本文件**重建可運作之本機開發環境**，並以 Checklist 勾稽進度。  
> **單一真相來源（仍請交叉閱讀）**：詳細規則與驗收以 **[README.md](../README.md)** 為準；時程與測試週以 **[工作記錄.md](../工作記錄.md)** 為準；路由／模組以 **[專案完整架構表.md](../專案完整架構表.md)** 為準。本檔**不取代**測試週文件（如 `docs/test_week_daily_checklist.md`）。

---

## 文件定位

| 本檔涵蓋 | 本檔不涵蓋 |
|----------|------------|
| Git 能／不能還原什麼 | 測試週逐日勾選（請用專用測試清單） |
| Node／Python／Mongo 前置 | 產品需求細節與 UI 驗收 |
| 後端 `venv`、`.env`、`pip`、`uvicorn` | 架構表上每一條路由的手動驗證（請對照架構表） |
| 前端 `npm install`、`.env`、`npm run dev` | Meta／第三方在平台上的商業設定變更流程 |
| **第十節、A+B 併用**（測試週與 `AGENTS` 第 10～14 天） | 環境 Gate（A）＋誠實改期（B）之操作順序與工作記錄模板 |

---

## 一、心態與範圍

### 說明

- **Git 只還原**：已 **commit** 且已 **push** 到遠端的檔案與歷史。
- **Git 無法還原**（須範例重建或其他備份）：`.env`、`.env.local`、`node_modules/`、`backend/venv/`、本機 HTTPS **憑證**、`logs/`、IDE 個人設定（`.vscode/`、`.idea/`）等；見專案 **[.gitignore](../.gitignore)**。
- **MongoDB 資料**：若無 **mongodump／Atlas 備份／雲端庫仍在**，還原程式後資料庫可能是**空庫**，須接受或另行還原資料。

### Checklist

- [ ] 已區分：Git 只還原已 commit 且已 push 的檔案
- [ ] 已區分：`.env`、`node_modules`、`venv`、憑證、日誌、IDE 設定等須自行重建或從其他備份補
- [ ] 已確認：MongoDB 資料是否另有備份／是否接受空庫重來

---

## 二、取得程式（Git）

### 說明

- 先決定要跟的 **ref**（建議日常開發：**`main`**；若要對齊某次標籤快照：**`v6.0.1`** 等）。
- 空目錄：**`git clone <repository-url>`** 後 **`cd`** 進專案。
- 已有 `.git`：**`git fetch origin --tags --prune`**，再 **`git checkout main`**（或目標分支／標籤）。
- 可選：使用 **`python scripts/check_git_v6_refs.py`**（若倉庫內有）比對各 ref 與關鍵路徑；或以 **`git diff --stat refA refB`** 記錄版本差異。

### Checklist

- [ ] 已決定要跟的 ref（例如 `main` 或 `v6.0.1`）
- [ ] 已完成 `git clone` 或 `git fetch` + `git checkout` 到目標 ref
- [ ] （選用）已執行 `python scripts/check_git_v6_refs.py` 確認 ref 與關鍵路徑
- [ ] （選用）已對關心版本執行 `git diff --stat refA refB` 並記下差異重點

---

## 三、執行環境（機器層）

### 說明

對齊 **[README.md](../README.md)**「快速開始 → 前置需求」：

- **Node.js** 18+ 與 **npm**
- **Python** 3.13+（若本機僅有 3.11 等，需自行評估與 README 差異；工作記錄曾出現 3.11 本機重建紀錄，**以 README 與 `requirements.txt` 實際為準**）
- **Git**
- **MongoDB**：本機服務或 **MongoDB Atlas** 連線

### Checklist

- [ ] Node.js 18+、npm 已安裝且版本符合需求
- [ ] Python 3.13+ 已安裝（或已記錄與 README 差異與風險）
- [ ] Git 可用
- [ ] MongoDB 本機可連，或 Atlas 帳號／連線可用

---

## 四、後端重建（`backend/`）

### 說明

步驟摘要同 README「後端設定」：

1. **`cd backend`**
2. **`python -m venv venv`**
3. Windows PowerShell：**`.\venv\Scripts\Activate.ps1`**
4. **`pip install -r requirements.txt`**
5. 複製環境檔：**`copy .env.example .env`**（PowerShell；Linux／Mac 使用 **`cp .env.example .env`**）
6. 編輯 **`.env`**（完整欄位說明見 **`backend/.env.example`**），至少包含：
   - **`MONGODB_URL`**（及 **`MONGODB_DB_NAME`** 依範例）
   - **`AI_SERVICE`** 及所選服務之 **URL／API Key／模型名**（依實際使用）
   - **`CORS_ORIGINS`**：與前端實際 **origin／埠** 一致（範例常含 `http://localhost:3000`、`http://localhost:5173`）
7. 啟動（擇一）：
   - **`uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`**
   - 或專案內既有 **`.bat`**（見 README）
8. 驗證：瀏覽器開 **`http://localhost:8000/docs`**

### Checklist

- [ ] 已進入 `backend/`
- [ ] 已建立虛擬環境 `python -m venv venv`
- [ ] 已啟用 venv（Windows：`.\venv\Scripts\Activate.ps1`）
- [ ] 已執行 `pip install -r requirements.txt`
- [ ] 已 `copy`／`cp`：`.env.example` → `.env` 並編輯
- [ ] `.env` 已填 `MONGODB_URL`（及 `MONGODB_DB_NAME` 若需要）
- [ ] `.env` 已設 `AI_SERVICE` 及所選服務所需之 URL／Key／模型（依實際使用）
- [ ] CORS 與前端實際 origin／埠一致
- [ ] 已啟動後端（`uvicorn` 或專案 `.bat`）
- [ ] 已開啟 `http://localhost:8000/docs` 確認 API 文件可載入

---

## 五、前端重建（`frontend/`）

### 說明

步驟摘要同 README「前端設定」：

1. **`cd frontend`**
2. **`npm install`**
3. **`copy .env.example .env`**（或 `cp`）
4. 設定 **`VITE_API_URL`**（預設與 README 一致：**`http://localhost:8000/api/v1`**）
5. **`VITE_USE_MOCK`**：連真後端時通常為 **`false`**（見 **`frontend/.env.example`**）
6. **`npm run dev`**（或專案內 **`.bat`**）
7. 瀏覽器開發伺服器位址以終端機輸出為準；README 寫 **`http://localhost:3000`** 或 **`http://localhost:5173`**

### Checklist

- [ ] 已進入 `frontend/`
- [ ] 已執行 `npm install`
- [ ] 已 `copy`／`cp`：`.env.example` → `.env` 並編輯
- [ ] `VITE_API_URL` 指向正確後端（預設 `http://localhost:8000/api/v1`）
- [ ] `VITE_USE_MOCK` 已依需求設定（連真後端通常 `false`）
- [ ] 已 `npm run dev`（或專案 `.bat`）
- [ ] 已用瀏覽器開前端（`localhost:3000` 或 `5173`，以終端機顯示為準）

---

## 六、Git 無法還原之項目（逐一確認）

### 說明

下列項目**不會**因 `git pull` 自動出現，須依範例、腳本或備份補齊：

- **`.env` 系列**：機密僅存本機；可參考工作記錄慣例維護 **`backend/.env.backup`**（勿提交 Git，見 `.gitignore`）。
- **`node_modules/`**：一律 **`npm install`**。
- **`backend/venv/`**：重建後 **`pip install`**。
- **本機 HTTPS 憑證**（`backend/certs/`）：若需要，依 **`backend/scripts/gen_ssl_cert.py`** 等專案內說明重新產生（勿將私鑰提交版本庫）。
- **`logs/`**：執行後產生或自備份還原。
- **IDE**：`.vscode`、`.idea` 被 ignore 時屬正常，接受重設。

### Checklist

- [ ] `.env` 系列：已從範例重建並補齊秘密（非 Git 內容）
- [ ] `node_modules/`：已用 `npm install` 重建
- [ ] `backend/venv/`：已重建並 `pip install`
- [ ] 本機 HTTPS 憑證（`backend/certs/`）：若需要，已依專案腳本／文件重新產生
- [ ] `logs/`：接受新產生或已從其他備份還原（若有需求）
- [ ] IDE 設定（`.vscode`／`.idea`）：已接受重設或手動還原

---

## 七、資料與第三方整合

### 說明

- **MongoDB**：程式還原後，資料是否還在取決於您是否另有庫備份或雲端庫未刪除。
- **Meta／OAuth**：App ID、Secret、Redirect URI 等須與各平台後台及 **`.env`** 一致；診斷可選用 **`python backend/check_meta_config.py`**（若本輪要驗 Meta）。
- **AI／圖搜等**：依要測的功能填入各 API Key；不測則記錄「本輪不測」即可。

### Checklist

- [ ] MongoDB：已還原備份 **或** 已確認空庫／測試資料策略
- [ ] Meta／OAuth 等：已在各平台後台與 `.env` 對齊 App ID、Secret、Redirect URI 等
- [ ] （選用）已執行 `python backend/check_meta_config.py`（若本輪要驗 Meta）
- [ ] AI／圖搜等 API：依要測的功能已填入 Key 或已記錄「本輪不測」

---

## 八、可選驗證（專案樹與建置）

### 說明

- **專案目錄結構**：專案根目錄可執行 **`python scripts/validate_structure.py`**（若存在），檢查核心目錄與關鍵檔。
- **前端建置抽查**（對齊工作記錄曾記載之做法）：在 **`frontend/`** 執行 **`npm run build`**，確認可通過建置（與「能 `dev`」互補）。

### Checklist

- [ ] 已在專案根執行 `python scripts/validate_structure.py` 且通過（或已記錄缺項與原因）
- [ ] （建議）已在 `frontend/` 執行 `npm run build` 且通過（或已記錄錯誤與略過原因）

---

## 九、建議執行順序（整條路徑）

將以上章節收斂為最短成功路徑：

1. Git 取得並 checkout 目標 ref  
2. MongoDB／Atlas 可連  
3. 後端：`venv` → `pip` → `.env` → 啟動 → `/docs`  
4. 前端：`npm install` → `.env` → 啟動 → 開站  
5. 依功能補齊選用金鑰與整合設定  
6. （建議）`npm run build`、（選用）`validate_structure.py`

### Checklist

- [ ] 1：Git 取得並 checkout 目標 ref  
- [ ] 2：MongoDB／Atlas 可連  
- [ ] 3：後端：venv → pip → `.env` → 啟動 → `/docs`  
- [ ] 4：前端：`npm install` → `.env` → 啟動 → 開站  
- [ ] 5：依功能補齊選用金鑰與整合設定  

---

## 十、測試週併用：**作法 A（Gate）** + **作法 B（日曆漂移）**

> **適用**：已進入 **`AGENTS.md` 第 10～14 工作天（測試專用段）**，但本機曾遺失／換機／尚未有可跑環境，或**實曆已跨過**原訂測試日（例：原訂 05-12 起未執行）。  
> **原則**：**A 管順序**（先能跑再測）；**B 管紀錄**（日期可移，主旨不造假）。兩者同時採用，不互斥。

### 作法 A — 環境 Gate（順序，必守）

在勾選 **`AGENTS.md` 任一天「完成判定」**或宣稱該日測試完成前，須先完成本檔：

| Gate | 最低限度（建議全勾） | 通過判準（簡易） |
|:----:|----------------------|------------------|
| **G0** | **二**～**三**（Git、Node／Python／Mongo） | `git status` 乾淨或已記錄意圖；版本符合 README |
| **G1** | **四**（後端 `venv`、`pip`、`.env`、啟動） | `http://localhost:8000/docs` 可開 |
| **G2** | **五**（前端 `npm install`、`.env`、`dev`） | 瀏覽器可開首頁／登入流程可試 |
| **G3**（建議） | **八**（`validate_structure.py`、`npm run build`） | 與工作記錄 2026-05-09 建置抽查敘述對齊 |

- **未完成 Gate**：僅可記「環境 BLOCK／進行中」，**不**將 `AGENTS` 第 10～14 天標為完成。  
- **Gate 與 45′ 段**：單段 45 分鐘通常**無法**同時做完完整 Gate + 當日全部測試；請拆成**多段或多日**（見 **九**）。

### 作法 B — 日曆漂移（排程與誠實）

當**原訂日期**已過、或當日無法排段，仍要執行「第 10 天**主旨**、第 11 天**主旨**…」時：

1. **不改寫** `AGENTS.md` 內對各天主題的定義（Meta+2.6、RWD、42 點…仍依該檔）。  
2. **改的是「哪一個實曆日執行哪一個邏輯工作天」**：將第 10～14 天**依序**排到接下來的**週二～週五**可排日（**週一不排本專案**，見 `AGENTS.md`）。  
3. 必須在 **`工作記錄.md`** 寫明漂移（見下「模板」），避免之後誤以為「原日曆日已測完」。

### A + B 合併流程（建議照做）

```
完成 Gate（A）→ 在工作記錄登記「邏輯第 10 天」對應之實曆日（B）
    → 當日依 AGENTS 第 10 天 + test_week_daily_checklist 執行
    → 次日類推（邏輯第 11、12…），直到第 14 天匯總
```

### 工作記錄.md — 建議貼上一句（可複製改日期）

```text
【測試週 A+B】因本機重建／日曆漂移：環境 Gate（README／本檔二～五＋建議八）已於 yyyy-mm-dd 完成。
AGENTS 邏輯第 10～14 天改排為：第10天→yyyy-mm-dd、第11天→…、第12天→…、第13天→…、第14天→…。
原日曆 2026-05-12～05-21 之中未執行之日＝未測，不以原日回填完成。
```

### 對照表（自行填實曆，執行完打勾）

| `AGENTS` 邏輯工作天 | 原訂參考日（日曆總表） | 實際執行日（B） | Gate（A）已 OK | 當日測試完成 |
|:-------------------:|------------------------|-----------------|:---------------:|:-------------:|
| 第 10 天 | 2026-05-12（二） |  | ☐ | ☐ |
| 第 11 天 | 2026-05-13（三） |  | ☐ | ☐ |
| 第 12 天 | 2026-05-14（四） |  | ☐ | ☐ |
| 第 13 天 | 2026-05-15（五） |  | ☐ | ☐ |
| 第 14 天 | 2026-05-21（四） |  | ☐ | ☐ |

**每日第一入口**：`docs/test_week_daily_checklist.md`；建立頻道收口另對照 `docs/channel_create_new_scheme_checklist.md` **I 節**（與 `AGENTS` 一致）。

---

## 附錄 A：與三份主文件的關係

| 文件 | 與本檔關係 |
|------|------------|
| [README.md](../README.md) | 安裝指令、埠號、環境變數欄位之**主要依據**；本檔為濃縮 Checklist。 |
| [工作記錄.md](../工作記錄.md) | **測試週**、建置抽查、Redis 選用等**額外敘述**；環境可跑後仍須依該檔指向的測試清單執行。 |
| [專案完整架構表.md](../專案完整架構表.md) | **模組／路由**對照；重建完成後若要驗證「頁面與 API 是否齊」，請對照此表，非本檔逐步安裝範圍。 |

---

## 附錄 B：常用指令速查（Windows PowerShell）

```powershell
# 更新遠端與標籤
git fetch origin --tags --prune

# 後端（於 backend 目錄）
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 前端（於 frontend 目錄）
npm install
copy .env.example .env
npm run dev

# 建置抽查（於 frontend 目錄）
npm run build
```

---

## 修訂記錄

| 日期 | 說明 |
|------|------|
| 2026-05-15 | 初版：整合環境重建說明、細節與九段 Checklist，並對齊 README／工作記錄／專案完整架構表之職責分工。 |
| 2026-05-15 | 新增 **第十節**：測試週 **作法 A（Gate）+ 作法 B（日曆漂移）** 併用流程、工作記錄模板與對照表。 |
