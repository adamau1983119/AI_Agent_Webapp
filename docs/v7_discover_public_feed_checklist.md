# v7 大眾免費主題卡（Discover SKU）— 工作明細與完成檢查清單

> **SoT 對照**：[`專案完整架構表_v7.md`](../專案完整架構表_v7.md) **「大眾免費主題卡（Discover SKU）」**  
> **依賴（硬門檻）**：**VM 監察週結案**（`log_cost_event`）＋ **v7 Token Phase 1**（`summary_flash`）＋ **Phase 2**（`deepl_provider`）— 見 [`v7_token_cost_phase_checklist.md`](./v7_token_cost_phase_checklist.md)  
> **建議分支**：`feature/v7-discover-feed` 或延續 `feature/v7-cost-pipeline`（勿在 `main` 直接改）  
> **觸發對齊**：**Discover 開發段**須在 Token Phase 0～2 相關項 `[x]` 後執行；日常仍用 **`專案開始`** + [`AGENTS.md`](../AGENTS.md)  
> **填寫規則**：勾選前須**可重現**驗證；禁止未測即勾（規則 #11、#12）。  
> **截圖政策（與 Token 相同）**：`:8000`／`:3000` 驗收 → **必須截圖** → [`v7_evidence_screenshot_guide.md`](./v7_evidence_screenshot_guide.md)（檔名建議前綴 `…_v7_PF-…`）  
> **監控紀律**：[`v7_dev_monitoring_discipline.md`](./v7_dev_monitoring_discipline.md)（`log_cost_event` 五 tag）  
> **實作基礎守則**：[`v7_implementation_basics.md`](./v7_implementation_basics.md)（**BF-***；PF-4 須 **BF-UI-*** + **PD-4-04／CD-4-5**）  
> **程式落地（2026-06-12）**：**PD-0～PD-4** ✅（分支 `feature/v7-cost-pipeline`）；**CD-*／E0-PF** ⏳ **整批測試週**（須截圖才可 `[x]`）。證據：[`docs/evidence/v7/2026-06-12/V7-Discover_program_line_session_log.md`](./evidence/v7/2026-06-12/V7-Discover_program_line_session_log.md)  
> **Key／驗收（2026-06-13）**：DeepSeek production key 已作廢；助手 **A 軌** 驗收見 Token checklist **雙軌驗收**（Discover 手測仍走 **U 軌**）。  
> **GTM 硬化（2026-06-13）**：新增 **PF-H／PF-S／PF-B／PF-M**；開發順序見下節；需求 SoT：[`v7.0.0_需求文件.md`](./v7.0.0_需求文件.md) §12。

---

## 開發順序（GTM · 原子 Phase · 2026-06-13）

> **策略**：先完成功能硬化與 Landing／Post Kit，再**一次過整批測試**（非每日小段）。**禁止**未測即勾 CD-*。

| 序 | Phase | 目標 | 依賴 |
|:--:|-------|------|------|
| 0 | **commit** | `feature/v7-cost-pipeline` 基線（排除 `.env`） | PF-0～4 程式 |
| 1 | **PF-H** | 熔斷三閘 + `safe_batch_size` + dev 禁 8h cron | PF-1～2 |
| 2 | **PF-S** | Mock 煙霧腳本（零 AI；Mongo+Redis） | PF-3 |
| 3 | **PF-B** | 港日同質：批次預寫 zh-TW+ja `topic_translations` | PF-2 DeepL |
| 4 | **PF-M** | v7.1 metadata（`source_country`、`is_trend_alert`） | PF-2 入庫 |
| 5 | **staging** | 真 30 批一輪（受控；後台對帳） | PF-H + PF-B |
| 6 | **Landing** | `/welcome` 導流 | 見 `landing_page_客戶開發需求.md` |
| 7 | **Post Kit** | 付費主路 UI | 既有 spec |
| 8 | **整批測試週** | CD-*／E0-PF／**E0-Discover-i18n** + v7 C*/X* | 上列全完成 |

---

## 實作基礎守則（BF · PF-4 前必讀）

> 對齊 [`README.md`](../README.md) 規則 **3、4、6** 與 [`AGENTS.md`](../AGENTS.md) 專案開始前檢查；**禁止** Discover 頁硬編碼可見字串或無 `data-testid` 之新按鈕。

- [x] **BF-DAY-1**～**BF-DAY-3**（見 [`v7_implementation_basics.md`](./v7_implementation_basics.md)）  
  - 證據：i18n 三語、`按鈕測試ID架構表` §1.4；分支 `feature/v7-cost-pipeline`
- [x] **BF-UI-1**～**BF-UI-4**（PF-4 結案前全勾）  
  - 證據：靜態核對 **CD-4-5**；瀏覽器手測留測試週

---

## 每日開工 — 環境截圖（E0 · 必做）

> **未完成 E0 不得勾選當日任何依賴本機的 CD-*。** 通用 E0-B／E0-F 定義見 [`v7_token_cost_phase_checklist.md`](./v7_token_cost_phase_checklist.md) § E0。

- [ ] **E0-B** 後端：`http://localhost:8000/health`（含 `cost_controls` 與 Discover 開關）  
  - 證據：截圖 `YYYY-MM-DD_v7_E0-B_….png` —
- [ ] **E0-F** 前端：`http://localhost:3000` 可開（登入或匿名依當日劇本）  
  - 證據：截圖 `YYYY-MM-DD_v7_E0-F_….png` —
- [ ] **E0-PF** Discover 專用（Phase PF-3／PF-4 起每日必做）  
  - 驗證：`GET /api/v1/public/topics/feed?lang=zh-TW` **200** + 前端 `/discover` 首屏；Network **Fetch/XHR** 僅 feed（**無** `assist`／`generate`／DeepL 網域）  
  - 證據：截圖 `YYYY-MM-DD_v7_E0-PF_feed_….png`、`…_v7_E0-PF_discover_….png` —
- [ ] **E0-Discover-i18n** 港日同質讀取驗收（**PF-B** 結案後；整批測試週必做）  
  - 驗證：`/discover` 切 **zh-TW** 與 **ja** 各一屏；Network **翻譯 API = 0**（無 DeepL／DeepSeek 外連）  
  - 證據：截圖 `…_v7_E0-Discover-i18n_zh-TW_….png`、`…_v7_E0-Discover-i18n_ja_….png` — 詳見 [`v7_evidence_screenshot_guide.md`](./v7_evidence_screenshot_guide.md)

---

## 勾選符號（全檔統一 · 與 Token checklist 相同）

| 符號 | 意義 | 何時使用 |
|:----:|------|----------|
| `[ ]` | 未驗證 | 預設 |
| `[x]` | **PASS**（√） | 驗證通過；證據已記 |
| `[!]` | **FAIL**（×） | 驗證失敗；寫原因 |

**工作項**（**PD-***）與**檢查項**（**CD-***）皆用 `[ ]` / `[x]` / `[!]`。

**填寫範例**

```markdown
- [x] **CD-3-2** …
  - 驗證：停 Redis 後 `curl` feed 仍 200
  - 證據：**截圖** `2026-06-12_v7_CD-3-2_mongo_fallback_….png` — body 含 ≥1 張卡
```

---

## Phase PF-0 — 前置 Gate（依賴 · 無程式亦可先勾文件）

**目標**：確認 **不早於** 監察週與 Token 主幹；Discover **不**改 Node／Postgres／Proxy MVP。

**結案判定**：**CD-0-1～CD-0-4 必須 `[x]`**（可為文件／他檔交叉引用）。

### 工作明細

- [x] **PD-0-01** 確認 [`專案完整架構表_v7.md`](../專案完整架構表_v7.md) Discover 四條鋼鐵修正案已讀  
  - 產出：PR Review 對照表
- [x] **PD-0-02** 確認 [`v7_token_cost_phase_checklist.md`](./v7_token_cost_phase_checklist.md) **Phase 1** `summary_flash` 相關 **C1-*** 已 `[x]` 或註明同批實作  
  - 產出：依賴註記（同批 `feature/v7-cost-pipeline`）
- [x] **PD-0-03** 確認 **Phase 2** `deepl_provider`／**C2-*** 已 `[x]` 或同批實作  
  - 產出：依賴註記
- [x] **PD-0-04** 確認 [`工作記錄.md`](../工作記錄.md) **V7-0 ☑**（監察週）已結案  
  - 產出：VM-4 2026-06-06

### Phase PF-0 完成檢查清單

- [x] **CD-0-1** 架構表 v7 含 Discover SKU 章節（2026-06-05+）  
  - 驗證：打開架構表「大眾免費主題卡」
  - 證據：`專案完整架構表_v7.md` 2026-06-12 更新 —
- [x] **CD-0-2** 本檔 checklist 已建立且與架構表 PF 表一致  
  - 驗證：對照架構表 PF-1～PF-6 摘要
  - 證據：本檔 2026-06-12 —
- [ ] **CD-0-3** `ENABLE_SCHEDULED_TOPIC_COLLECTION=false`（舊 6h 不與公共 8h 混用）  
  - 驗證：`/health` → `cost_controls`
  - 證據：**截圖** E0-B —（VM-4 舊圖可參；**06-16** 補 `public_feed_pipeline`）
- [x] **CD-0-4** 分支策略：非 `main` 直推  
  - 驗證：`git branch --show-current`
  - 證據：`feature/v7-cost-pipeline` —

---

## Phase PF-1 — 政策、config 與 PR 拒絕線（四條鋼鐵）

**目標**：常數寫死、`cost_controls` 暴露開關；PR 可機械拒絕違規依賴。

**結案判定**：**CD-1-1～CD-1-6 必須 `[x]`**。

### 工作明細

- [x] **PD-1-01** `config_module.py`：`PUBLIC_FEED_BATCH_SIZE=30`、`PUBLIC_FEED_INTERVAL_HOURS=8`、`PUBLIC_FEED_WINDOW_HOURS=36`、`PUBLIC_FEED_MAX_CARDS=135`（assert 公式）  
  - 產出：`backend/app/config_module.py`
- [x] **PD-1-02** `MAX_TRANSLATION_RETRIES=3`（Discover 標題 DeepL；**單卡單語**）  
  - 產出：`deepl_title.py` + `translate_deepl_once`
- [x] **PD-1-03** `ENABLE_PUBLIC_FEED_PIPELINE`（預設 `false`）納入 `cost_controls.py` 與 `GET /health`  
  - 產出：`cost_controls.py`、`main.py` `/health`
- [x] **PD-1-04** `grep` CI／PR 說明：無 `puppeteer`／`playwright`／`brightdata`／`oxylabs`／`sqlalchemy`／`psycopg` 新增依賴  
  - 產出：session log 2026-06-12 grep 0 命中
- [x] **PD-1-05** `.env.example` 補 Discover 開關與常數說明（**不提交** `.env`）  
  - 產出：`backend/.env.example`

**建議 `.env`（Discover 開發用 · 疊加 Token 範本）**

```env
ENABLE_PUBLIC_FEED_PIPELINE=false
ENABLE_SCHEDULED_TOPIC_COLLECTION=false
ENABLE_AI_TOPIC_TRANSLATION=false
DEEPL_API_KEY=<your_key>
DEEPSEEK_MODEL_FLASH=deepseek-v4-flash
```

### Phase PF-1 完成檢查清單

- [x] **CD-1-1** **P1** 無 Node 執行期、無 PostgreSQL 連線程式  
  - 驗證：`grep` backend `*.py` 0 命中
  - 證據：session log 2026-06-12 —
- [x] **CD-1-2** **P2** MVP 無住宅 Proxy／無頭瀏覽器**必達**依賴  
  - 驗證：`grep` backend 0 命中
  - 證據：session log 2026-06-12 —
- [x] **CD-1-3** **P4** config 四常數與架構表一致（30／8／36／135）  
  - 驗證：`config_module` assert 135；`python -c` import OK
  - 證據：session log —
- [ ] **CD-1-4** `/health` 含 `enable_public_feed_pipeline`（或同名鍵）  
  - 驗證：`curl -s http://localhost:8000/health`
  - 證據：**截圖** E0-B — **06-16**
- [x] **CD-1-5** v7 新檔 ≤150 行（M2）；無 `CRITICAL ENGINE` 頂部註解  
  - 驗證：`public_feed/*` 各檔 ≤70 行
  - 證據：session log —
- [x] **CD-1-6** 預算項註記：Proxy 成本 **0**（文件或工作記錄一句）  
  - 驗證：架構表 P2；本檔 CD-1-2
  - 證據：工作記錄 2026-06-12 —

---

## Phase PF-2 — 批次管線（8h · RSS · Flash 骨 · DeepL 皮）

**目標**：`scheduler.py` 獨立公共 job；每批 30 張；寫 Mongo SoT；**禁止**收集管線 AI 翻譯與 **Pro**。

**結案判定**：**CD-2-1、CD-2-2、CD-2-4、CD-2-6 必須 `[x]`**；其餘允許 1 項 `[!]` 並註延後。

### 工作明細（原子化）

- [x] **PD-2-01** `scheduler.py`：新增 `run_public_feed_batch()`（或同名），僅在 `public_feed_pipeline_enabled()` 為真時執行  
  - 產出：`scheduler.py` `_run_public_feed_batch`
- [x] **PD-2-02** 排程註冊：每 **8h** 觸發（與 channel prefetch、6h 三類 **分 job id**）  
  - 產出：job id `public_feed_batch`
- [x] **PD-2-03** RSS 抓取：僅 **Feed Health 通過** 之白名單源；三領域（時尚／美食／時事）合計 **≤30** 篇／批  
  - 產出：`rss_fetcher.py`
- [x] **PD-2-04** L0 清洗：原文入庫；**禁止** `original_content` 進任何 LLM prompt（D5）  
  - 產出：`strip_html` + snippet only
- [x] **PD-2-05** Flash：**僅** `DEEPSEEK_MODEL_FLASH` 寫入 `summary_flash`（+ 規劃內多語 JSON 欄位）  
  - 產出：`item_builder.py` → `generate_summary_flash`
- [x] **PD-2-06** DeepL 皮：標題 **≤20 字** → `zh-TW`／`ja`；逾 **3 次** → 字串 Fallback + `log_cost_event(TRANSLATION_FALLBACK_TRIGGERED)`  
  - 產出：`deepl_title.py`
- [x] **PD-2-07** 入庫：`topics` 設 `public_feed_flag=true`、`source_lang="en"`（或架構表選定之 collection）  
  - 產出：`models/topic.py`、`public_feed_repository.py`
- [x] **PD-2-08** 36h 滾動：刪除或歸檔逾窗卡片；庫內公共卡 **≤135**  
  - 產出：`cleanup()` in repository
- [x] **PD-2-09** 手動觸發入口（dev only）：管理腳本或 `POST`（需 auth／feature flag）跑 **1 批** 煙霧  
  - 產出：`scripts/run_public_feed_batch.py`

### Phase PF-2 完成檢查清單

- [ ] **CD-2-1** 單批執行後 Mongo 新增 **≤30** 筆 `public_feed_flag=true`  
  - 驗證：Compass／`mongosh` count 或 API 管理查詢
  - 證據：查詢輸出 + 日期 —
- [ ] **CD-2-2** 批次日誌含 `[SUMMARY_FLASH_SUCCESS]`（每卡或摘要一行）  
  - 驗證：重啟 uvicorn 後跑 1 批；終端**輔助**截圖
  - 證據：終端截圖 `…_v7_CD-2-2_….png` —
- [ ] **CD-2-3** DeepL 失敗第 4 次走 Fallback（可 mock 錯 key）  
  - 驗證：單卡單語；日誌 `[TRANSLATION_FALLBACK_TRIGGERED]`
  - 證據：終端或測試輸出 —
- [x] **CD-2-4** 公共批次 **無** `DEEPSEEK_MODEL_PRO`／無 `POST .../generate` 呼叫  
  - 驗證：grep `public_feed/` 0 命中
  - 證據：session log 2026-06-12 —
- [x] **CD-2-5** 公共批次 **無** `topic_collector._translate_title` 收集翻譯路徑  
  - 驗證：`item_builder.py` 獨立路徑
  - 證據：session log —
- [ ] **CD-2-6** 36h 窗內卡片數 **≤135** 且符合 config 公式  
  - 驗證：DB count + config assert
  - 證據：—
- [ ] **CD-2-7** 僅 RSS：無 Proxy 連線 log／無瀏覽器 launch log  
  - 驗證：跑批後查日誌
  - 證據：—

---

## Phase PF-3 — 讀取 API（Redis 熱 · Mongo 冷備）

**目標**：`GET /api/v1/public/topics/feed`；**讀取零 LLM**；Redis 掛了仍 200。

**結案判定**：**CD-3-1～CD-3-4 必須 `[x]`**。

### 工作明細

- [x] **PD-3-01** 新建 `backend/app/api/v1/public_topics.py`（或等價）並掛載 router  
  - 產出：`public_topics.py`、`main.py` include
- [x] **PD-3-02** `GET .../feed?lang=zh-TW|ja`：schema 含標題、摘要、`summary_flash` 譯文、圖片 URL、時間  
  - 產出：`schemas/public_feed.py`
- [x] **PD-3-03** 讀取順序：**Redis** key（TTL ≤36h）→ miss 則 **Mongo** 查 `public_feed_flag` + `created_at` 窗  
  - 產出：`public_feed_cache.py`
- [x] **PD-3-04** 寫入 Redis：批次結束後刷新快取（或逐卡 pipeline 尾寫）  
  - 產出：`refresh_feed_cache` in pipeline
- [x] **PD-3-05** **禁止** 在 feed 路由內呼叫 `AIServiceFactory`／DeepL／DeepSeek  
  - 產出：`public_topics.py` 零 LLM import

### Phase PF-3 完成檢查清單

- [ ] **CD-3-1** `curl "http://localhost:8000/api/v1/public/topics/feed?lang=zh-TW"` → **200** + JSON 陣列  
  - 驗證：至少 1 張卡；欄位非空（標題／摘要）
  - 證據：**截圖** Postman 或瀏覽器 `…_v7_CD-3-1_….png` —
- [ ] **CD-3-2** **Redis 停用**（或 flush）後同一 URL 仍 **200**（Mongo fallback）  
  - 驗證：停 Redis 或 `cache_service` 失敗模擬
  - 證據：**截圖** `…_v7_CD-3-2_….png` — 註明延遲可接受
- [ ] **CD-3-3** feed 請求過程 **無** 對 `api.deepseek.com`／`api-free.deepl.com` 外連  
  - 驗證：後端 log 或 egress 監控；Network 僅適用前端
  - 證據：—
- [x] **CD-3-4** `discover.py` 之 `POST` 收集端點 **未** 被公共頁預設呼叫  
  - 驗證：`Discover.tsx` 僅 `publicFeedAPI.getFeed`
  - 證據：`frontend/src/pages/Discover.tsx` —

---

## Phase PF-4 — 前端 `/discover`（只讀 · 0 LLM）

**目標**：母語牆、無閃爍骨架；初次載入 **0** LLM API。

**結案判定**：**CD-4-1～CD-4-5 必須 `[x]`**；**E0-PF 必須 `[x]`**；**BF-UI-1～BF-UI-4 必須 `[x]`**（見 [`v7_implementation_basics.md`](./v7_implementation_basics.md)）。

### 工作明細

- [x] **PD-4-01** 路由 `/discover` + 元件（列表／卡片 RWD 最小集）  
  - 產出：`App.tsx`、`Discover.tsx`
- [x] **PD-4-02** 僅呼叫 `GET /api/v1/public/topics/feed?lang=`（跟隨 UI 語言 `zh-TW`／`ja`）  
  - 產出：`publicFeed.ts`
- [x] **PD-4-03** i18n：可見字串進 `frontend/src/i18n/index.ts`（**zh-TW／en／ja**；**禁止硬編碼**，對齊 README 規則 6）  
  - 產出：`nav.discover`、`discover.*`
- [x] **PD-4-04** 按鈕／連結：`data-testid` + 更新 [`按鈕測試ID架構表.md`](../按鈕測試ID架構表.md)（對齊 README 規則 3、4）  
  - 產出：§1.4 Discover
- [x] **PD-4-05** 骨架／placeholder（對齊 Phase 4 skeleton 精神，可簡版）  
  - 產出：`PublicFeedSkeleton.tsx`
- [x] **PD-4-06** `npm run build` PASS  
  - 產出：exit 0（2026-06-12）

### Phase PF-4 完成檢查清單

- [ ] **CD-4-1** `/discover` 首屏顯示 **≥1** 張卡；繁中或日文依 `lang`  
  - 驗證：瀏覽器；標題 ≤20 字體感
  - 證據：**截圖** `…_v7_E0-PF_discover_….png` —
- [ ] **CD-4-2** DevTools Network：**僅** feed GET **200**；**無** `assist`／`generate`／`translate-display`  
  - 驗證：Preserve log + 篩選 XHR
  - 證據：併入 E0-PF 或獨立截圖 —
- [ ] **CD-4-3** 切換語言 `zh-TW`↔`ja` 再請求 feed；內容隨 `lang` 變化  
  - 驗證：兩次 GET 參數不同
  - 證據：**截圖** 兩語各一 —
- [x] **CD-4-4** `npm run build` exit 0  
  - 驗證：`cd frontend && npm run build`
  - 證據：2026-06-12 exit 0 —
- [x] **CD-4-5** 靜態核對：Discover 相關按鈕皆有 **`data-testid`**；i18n key 已 `grep` 存在（**BF-UI-3／BF-UI-4**）  
  - 驗證：`page-discover`、`discover-feed-grid`、`card-discover-feed-{n}`
  - 證據：`按鈕測試ID架構表` §1.4 —

---

## Phase PF-H — 硬化（熔斷三閘 · 環境分流）

**目標**：防 6/6 翻版；dev 誤開 pipeline 不燒 Token；staging／prod 真 30 批受控。

**結案判定**：**CD-H-1～CD-H-4 必須 `[x]`**（可含 1 項 `[!]` 並註延後）。

### 工作明細（原子化）

- [ ] **PD-H-01** `config_module.py`：新增 **`safe_batch_size`** property（`development` 且 pipeline 誤開 → **2**；`staging`／`production` → **30**）  
  - 產出：`safe_batch_size` + 單元 assert
- [ ] **PD-H-02** `run_public_feed_batch` 入口：`batch_size = min(PUBLIC_FEED_BATCH_SIZE, safe_batch_size)`；迴圈硬 **break**  
  - 產出：`scheduler.py` 或 `public_feed/pipeline.py`
- [ ] **PD-H-03** `ENVIRONMENT=development` 時 **不註冊** 8h `public_feed_batch` cron（僅 CLI／腳本可觸發）  
  - 產出：`scheduler.py` 條件註冊
- [ ] **PD-H-04** dev 降級時 `log_cost_event` 記錄（例如 `PUBLIC_FEED_DEV_CAP`）  
  - 產出：`logger.py` tag 或既有 tag 擴充
- [ ] **PD-H-05** 複核 **熔斷三閘**：DeepL retries≤3（PD-1-02）、`public_topics` 零 LLM（PD-3-05）  
  - 產出：grep／靜態審計 session log

### Phase PF-H 完成檢查清單

- [ ] **CD-H-1** `ENVIRONMENT=development` + 誤開 `ENABLE_PUBLIC_FEED_PIPELINE=true` → 單批 **≤2** 卡  
  - 驗證：手動跑 1 批；Mongo count ≤2
  - 證據：終端 + count 輸出 —
- [ ] **CD-H-2** development **無** 8h cron 註冊 log（重啟 uvicorn 後查 scheduler 啟動輸出）  
  - 驗證：grep log `public_feed_batch` 僅手動觸發
  - 證據：終端截圖 —
- [ ] **CD-H-3** staging 設定下單批可達 **30**（或 config 上限）  
  - 驗證：`ENVIRONMENT=staging` + 受控 1 批
  - 證據：—（真 30 批留 **staging 輪** 序 5）
- [ ] **CD-H-4** `/health` 仍暴露 `public_feed_pipeline` 與 `cost_controls` 六開關  
  - 驗證：`curl /health`
  - 證據：**截圖** E0-B —

---

## Phase PF-S — Mock 煙霧（零 AI）

**目標**：dev 演示 `/discover` 有卡；**零** DeepSeek／DeepL；寫 Mongo + Redis。

**結案判定**：**CD-S-1～CD-S-3 必須 `[x]`**。

### 工作明細（原子化）

- [ ] **PD-S-01** 新建 `backend/scripts/trigger_public_feed_smoke.py`（或同名）  
  - 產出：腳本檔 ≤150 行
- [ ] **PD-S-02** 寫入 **≥3** 筆 mock `topics`（`public_feed_flag=true`、`titles_i18n` zh-TW+ja、`summary_flash` 固定字串）  
  - 產出：直接 Motor insert 或 repository helper
- [ ] **PD-S-03** 呼叫 `refresh_feed_cache`（或等價）刷新 Redis  
  - 產出：pipeline 尾寫邏輯複用
- [ ] **PD-S-04** 腳本 docstring／README 一句：**禁止**在 production 無旗標執行  
  - 產出：腳本頂部註解

### Phase PF-S 完成檢查清單

- [ ] **CD-S-1** 執行腳本後 `GET .../feed?lang=zh-TW` → **200** + **≥3** 卡  
  - 驗證：`curl` 或 Postman
  - 證據：截圖 `…_v7_CD-S-1_….png` —
- [ ] **CD-S-2** 執行過程 **無** `api.deepseek.com`／`api-free.deepl.com` 外連  
  - 驗證：終端 log；後台用量 **0**
  - 證據：—
- [ ] **CD-S-3** `/discover` 首屏可見 mock 卡（與 CD-S-1 併測）  
  - 驗證：瀏覽器
  - 證據：併入 E0-PF 或獨立截圖 —

---

## Phase PF-B — 港日同質（批次預載雙語）

**目標**：批次內預寫 `topic_translations` **zh-TW + ja** `standard_translation`；讀取零翻譯 API。

**結案判定**：**CD-B-1～CD-B-3 必須 `[x]`**；**E0-Discover-i18n 必須 `[x]`**。

### 工作明細（原子化）

- [ ] **PD-B-01** `item_builder`／pipeline：每卡批次內呼叫 DeepL 寫入 **zh-TW** 與 **ja** `standard_translation`（標題 ≤20 字）  
  - 產出：`topic_translations` upsert ×2
- [ ] **PD-B-02** `GET .../feed` 讀取優先 `topic_translations`（fallback `titles_i18n`）  
  - 產出：`public_topics.py` 或 feed schema mapper
- [ ] **PD-B-03** 骨：feed 回傳共用 `summary_flash`（或依 lang 之顯示欄位）；**禁止**讀取時 Flash  
  - 產出：schema 對齊架構表

### Phase PF-B 完成檢查清單

- [ ] **CD-B-1** 跑 1 批（或 mock 擴充）後 Mongo `topic_translations` 含 **zh-TW + ja** 各 ≥1 筆／卡  
  - 驗證：`mongosh` 或 Compass
  - 證據：查詢輸出 —
- [ ] **CD-B-2** `/discover` 切 zh-TW／ja 標題不同且皆為母語（非 key 洩漏）  
  - 驗證：瀏覽器兩語
  - 證據：**E0-Discover-i18n** 兩張截圖 —
- [ ] **CD-B-3** 讀取時 Network **無** DeepL／DeepSeek（與 CD-4-2 複核）  
  - 驗證：DevTools XHR
  - 證據：併入 E0-Discover-i18n —

---

## Phase PF-M — v7.1 metadata 伏筆（僅 schema）

**目標**：為變現路線圖埋欄位；**MVP 不跑** Trend Alert／聚類 job。

**結案判定**：**CD-M-1～CD-M-2 必須 `[x]`**。

### 工作明細（原子化）

- [ ] **PD-M-01** `models/topic.py`：新增 `source_country: Optional[str]`、`is_trend_alert: bool = False`  
  - 產出：Pydantic model + 遷移註記（Mongo 無強制 migrate）
- [ ] **PD-M-02** 公共批次入庫：依 RSS 源或白名單表預填 `source_country`（可簡化為 `US`／`GB` 等）  
  - 產出：`item_builder.py`
- [ ] **PD-M-03** 文件連結 [`v7.1_ROADMAP.md`](./v7.1_ROADMAP.md) 於架構表與本檔  
  - 產出：本 commit 文件

### Phase PF-M 完成檢查清單

- [ ] **CD-M-1** 新卡 JSON／Compass 可見 `source_country`（可為 null 舊卡）  
  - 驗證：查 1 筆新卡
  - 證據：—
- [ ] **CD-M-2** `is_trend_alert` 預設 **false**；**無** 背景 alert job 註冊  
  - 驗證：grep scheduler 0 命中 `trend_alert`
  - 證據：session log —

---

## 跨 Phase 總驗收（Discover SKU 結案 · PF-X）

**目標**：對齊架構表 **PF-1～PF-6** 摘要；可宣告 **V7-Discover ☑**（工作記錄自訂列）。

**結案判定**：**CD-X-1～CD-X-6 必須 `[x]`**。

- [ ] **CD-X-1** **PF-1** 8h job 僅 RSS（複核 CD-2-7）  
  - 證據：—
- [ ] **CD-X-2** **PF-2** 批次 30、窗內 ≤135（複核 CD-2-1、CD-2-6）  
  - 證據：—
- [ ] **CD-X-3** **PF-3** Redis 掛載 Mongo fallback（複核 CD-3-2）  
  - 證據：—
- [ ] **CD-X-4** **PF-4** `/discover` 0 LLM（複核 CD-4-2）  
  - 證據：—
- [ ] **CD-X-5** **PF-5** 日誌 tag 齊全（SUMMARY_FLASH／CACHE_MISS／TRANSLATION_FALLBACK 至少各見 1 次於合理情境）  
  - 證據：終端摘錄 —
- [ ] **CD-X-6** **PF-6** PR 審計無 Node／SQL／Proxy SDK  
  - 證據：PR 連結 —

---

## 對照架構表 PF 摘要（勿雙份漂移）

| 架構 PF | 本檔檢查項 |
|---------|------------|
| PF-1 | CD-2-7、CD-X-1 |
| PF-2 | CD-2-1、CD-2-6、CD-X-2 |
| PF-3 | CD-3-2、CD-X-3 |
| PF-4 | CD-4-2、CD-X-4 |
| PF-5 | CD-2-2、CD-2-3、CD-X-5 |
| PF-6 | CD-1-1、CD-1-2、CD-X-6 |
| PF-H | CD-H-1～CD-H-4 |
| PF-S | CD-S-1～CD-S-3 |
| PF-B | CD-B-1～CD-B-3、E0-Discover-i18n |
| PF-M | CD-M-1～CD-M-2 |

---

## 證據記錄模板（貼至工作記錄）

```text
## v7 Discover Phase {PF-N} 結案 — {日期}
- 分支／commit：
- 檢查清單：（本檔該 Phase 區塊 [x]/[!]）
- 指令：curl feed、停 Redis 測試、npm run build
- 截圖檔名：E0-PF_*、CD-*_*
- DeepSeek／DeepL 後台：（公共讀取應為 0）
- 已知限制／變現 Phase 2+：
```

---

## 版本

| 日期 | 說明 |
|------|------|
| 2026-06-05 | 初版：Phase PF-0～PF-4 + PF-X；PD-*／CD-*；格式對齊 `v7_token_cost_phase_checklist.md` |
| 2026-06-13 | GTM：開發順序表；PF-H／PF-S／PF-B／PF-M 原子 Phase；E0-Discover-i18n；測試週改整批 |
