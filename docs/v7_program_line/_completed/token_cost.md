# v7 Token 省成本 — Phase 工作明細與完成檢查清單

> **專區 SoT（2026-06-23）**：本檔位於 `docs/v7_program_line/_completed/token_cost.md` · **狀態**：**程式 ✅**（Phase 0～5 · `bebf6d0`）· **C1～C4** ⏳ 整批測試週  
> **進入專區前必讀**：[`_GATE.md`](../_GATE.md) · **總表**：[`index.md`](../index.md)

> **SoT 對照**：[`專案完整架構表_v7.md`](../../../../../專案完整架構表_v7.md) 「Token 省成本」D1～D5  
> **實作計畫**：`.cursor/plans/v7_token_省成本整合_050d25e8.plan.md`  
> **建議分支**：`feature/v7-cost-pipeline`（勿在 `main` 直接改）  
> **觸發對齊**：**v7 程式段** → `專案開始，並對照工作記錄「v7 程式段（排程 B）」@AGENTS.md` + [`AGENTS.md`](../../../AGENTS.md)「專案開始（v7 · 程式段）」；核證勾選同步 [`工作記錄.md`](../../../工作記錄.md) **「v7 程式段」**。**`專案開始 v6`** 才走 R+T 測試週表；**整批測試週**（C*／CD*）須 **程式全線結案後**。  
> **填寫規則**：每 Phase 結案時在 [`工作記錄.md`](../../../工作記錄.md) 貼「證據」；勾選前須**可重現**驗證，禁止未測即勾。  
> **截圖政策（不變 · 首要）**：凡依 **`:8000` / `:3000`** 判斷是否 PASS → **必須有截圖** 才能改 `[x]`；格式與批次做法 → **[`v7_evidence_screenshot_guide.md`](../../../../v7_evidence_screenshot_guide.md)**。  
> **監控紀律 Checklist（CTO 鎖定）**：**[`v7_dev_monitoring_discipline.md`](../../../../v7_dev_monitoring_discipline.md)**（**MD-E0、MD-M1～M3** 可勾選；對照本檔 **P0-06／P0-07、E0**）。  
> **Discover SKU（2026-06-12）**：**[`v7_discover_public_feed_checklist.md`](../../../../v7_discover_public_feed_checklist.md)** — **PD-0～4 程式** `[x]`；**CD-*／E0-PF** 留 **整批測試週**（先寫完 **PF-B～Post Kit**；~~**PF-S**~~ **廢止**；**勿**與本檔 C* 混勾）。  
> **Alter Ego SKU（2026-06-17）**：**[`v7_alter_ego_checklist.md`](../../../../v7_alter_ego_checklist.md)** — **Post Kit 後** AE-0→AE-1；原子验收 **A→B→C**；**勿**与 PF-B 混勾。  
> **實作基礎守則（改碼前必讀）**：**[`v7_implementation_basics.md`](../../../../v7_implementation_basics.md)**（**BF-***；含 README i18n／按鈕 testid／六必讀門檻）。  
> **Key 輪換（2026-06-11）**：舊 `ai-agent-webapp-production`／`production 2` 已刪；本機新 key 尾碼 **ebe36**（**勿** commit `.env`）。見 [`deepseek_cost_investigation_2026-05.md`](../../../../deepseek_cost_investigation_2026-05.md) **頻道區塊 8**。

---

## 雙軌驗收（2026-06-10 決策 · commit 前／測試週並用）

> **目的**：區分 **助手可自動跑** 與 **用家必須親測**；避免 A 軌觸發大量 Token。

| 軌 | 負責 | 允許 | 禁止 |
|----|------|------|------|
| **A 軌** | Cursor 助手 | `GET /health`（含 `cost_controls`）、`npm run build`、靜態 grep、單次 `curl` feed／topics（**無 body 重放**） | `POST …/collect`、`generate-today`、批次翻譯、未授權之 `assist` 迴圈 |
| **U 軌** | 用家 | 登入 → 主題列表 → `/discover` → `/channels/create` 開助手（**不**連點生成）~20～30′ | — |

**A 軌代理勾選規則**：僅當日 session log 有 **URL + status + 一句結論** 才可將對應 **靜態項** 標 `[x]`；**C* 截圖項** 仍須 U 軌或手動 PNG。  
**證據**：[`docs/evidence/v7/2026-06-10/A-track_agent_session_log.md`](../../../../evidence/v7/2026-06-10/A-track_agent_session_log.md)、[`docs/evidence/v7/2026-06-11/KEY_rotation_session_log.md`](../../../../evidence/v7/2026-06-11/KEY_rotation_session_log.md)

- [x] **DT-1** 雙軌政策寫入本檔 + 工作記錄  
- [x] **DT-2** A 軌 2026-06-10 已跑一輪（build／health／C3-3 靜態）  
- [ ] **DT-3** U 軌用家 E2E 回歸（5 步；每步 **UI + Network**）— **整批測試週**（禁止「能開頁」签收）  
- [x] **DT-4** P0 Key 輪換（舊 production 作廢；新 key 載入驗證）  
- [x] **DT-5** DeepSeek 後台 **餘額預警**（2026-07-31：人民幣 ON、閾值 ¥20；平台無每日硬上限）

---

## 實作基礎守則（BF · 與 README 對齊）

> **下週編碼起**：任何 **commit 前**須完成 [`v7_implementation_basics.md`](../../../../v7_implementation_basics.md) 當日適用之 **BF-DAY-***；**Phase 4** 或任何前端檔另須 **BF-UI-***。  
> **觸發**：`專案開始` → [`AGENTS.md`](../../../AGENTS.md) 專案開始前檢查（含 [`按鈕測試ID架構表.md`](../../../按鈕測試ID架構表.md)、[`品牌設計規範.md`](../../../品牌設計規範.md) 若動 UI）。

- [ ] **BF-DAY-1** 專案開始前檢查結果表已輸出（分支、必讀、規則 #11～#14）
- [ ] **BF-DAY-2** 本日若新增／修改按鈕：已對照 **按鈕測試ID架構表**（→ Phase 4 **P4-03**）
- [ ] **BF-DAY-3** 本日若新增可見字串：已進 **i18n 三語**（→ Phase 4 **P4-04**）

---

## 每日開工 — 環境截圖（E0 · 必做）

> **未完成的 E0 不得勾選當日任何依賴本機服務的 C*-*。** 證據檔名見截圖指南 頻道區塊 3。

- [x] **E0-B** 後端：`http://localhost:8000/health` 整页 JSON（含 `cost_controls`）  
  - 證據：截圖 `2026-06-06_v7_E0-B_health_cost_controls.png` — `cost_controls` 四開關 false + Flash
- [x] **E0-F** 前端：`http://localhost:3000` 已登入 P0 頁；Console 無未處理紅錯  
  - 證據：VM-1 使用者 PNG（`VM1_session_log.md`；建議檔名 `2026-06-06_v7_E0-F_dashboard.png`）
- [ ] **E0-N** Network 面板已開 **Fetch/XHR** + **Preserve log**（可併入 E0-F 同圖）  
  - 證據：截圖或註明併入 E0-F —

---

## 勾選符號（全檔統一）

| 符號 | 意義 | 何時使用 |
|:----:|------|----------|
| `[ ]` | 未驗證 | 預設；尚未執行驗證 |
| `[x]` | **PASS**（√） | 驗證通過；證據已記 |
| `[!]` | **FAIL**（×） | 驗證失敗；同一行下方寫原因 |

**填寫範例**

```markdown
- [x] **C0-1** …
  - 驗證：curl …/health
  - 證據：**截圖** `2026-06-05_v7_C0-1_….png` — `/health` 內 `scheduled_topic_collection: false`
- [!] **C0-5** …
  - 驗證：…
  - 證據：**截圖** DeepSeek 後台或註明無權限之 FAIL 畫面
  - FAIL 原因：…
```

**工作項**（P*-*）與**檢查項**（C*-*）皆用同一三態 `[ ]` / `[x]` / `[!]`。

---

## Phase 0 — 政策、環境與量測基線

**目標**：開發／測試環境與 **D1～D5** 一致；建立 Token 對照基線。

**結案判定**：**E0-B、E0-F 必須 `[x]`（截圖）**；C0-1～C0-5 至少 **4 項 `[x]`**；**C0-4 必須 `[x]`**。

### 工作明細

- [x] **P0-01** 撰寫 `.env.example`（或 README 表）含 FLASH/PRO、DeepL、定向排程開關  
  - 產出：`backend/.env.example`（2026-06-10 v7 cost_controls + DeepL 區塊）
- [x] **P0-02** 本機 `.env` 設為省 Token 組（見下方範本；**不提交** `.env`）
- [x] **P0-03** 確認 `GET /health` → `cost_controls` 與實際 env 一致  
  - 產出：`backend/app/main.py` 根 `/health` + `api/v1/health.py`
- [x] **P0-04** DeepSeek 後台：記錄「實作前」Flash/Pro 次數與 Token  
  - 產出：`docs/deepseek_cost_investigation_2026-05.md`（2026-05 基線）
- [x] **P0-05** 工作記錄新增「v7 Token Phase 0 基線」一節  
  - 產出：`工作記錄.md` 「Phase 0 監察線結案」
- [x] **P0-06** **M1**：`logger.py` 新增 **`log_cost_event(tag, level="info", **fields)`** — **內部**將 kwargs 格式為 `[TAG] k=v …`（key 排序、同步函數、函數內不 `await`）；`colorize=True`；**嚴禁** pino／`vercel dev`  
  - 官方 tag：`SUMMARY_FLASH_SUCCESS`、`I18N_CACHE_HIT`、`CACHE_MISS`、`TRANSLATION_FALLBACK_TRIGGERED`、`TOKEN_GATEWAY_PASSED`  
  - 驗證：本機僅 `uvicorn … :8000`；呼叫含**多個 kwargs** 時終端工整 `key=value`（見 [`v7_dev_monitoring_discipline.md`](../../../../v7_dev_monitoring_discipline.md) **MD-M1-3**）  
  - 證據：可選終端截圖 + **仍須** E0-B／E0-F 瀏覽器截圖
- [x] **P0-07** **M2**：v7 **新建** `.py` 模組單檔 **≤150 行**（超則拆檔）；**禁止**頂部 `// CRITICAL…` 類註解  
  - 驗證：PR 說明列檔名 + 行數；Review 對照 [`v7_dev_monitoring_discipline.md`](../../../../v7_dev_monitoring_discipline.md) **M2**

**建議 `.env`（Phase 0～4 開發用）**

```env
DEEPSEEK_MODEL_FLASH=deepseek-v4-flash
DEEPSEEK_MODEL_PRO=deepseek-v4-pro
ENABLE_SCHEDULED_TOPIC_COLLECTION=false
ENABLE_AI_TOPIC_TRANSLATION=false
ENABLE_AI_TOPIC_FALLBACK=false
ENABLE_CHANNEL_PREFETCH_PIPELINE=false
AUTO_START_SCHEDULER=false
DEEPL_API_KEY=<your_key>
TRANSLATION_TIMEOUT_SEC=5
```

### Phase 0 完成檢查清單

- [x] **C0-1** `ENABLE_SCHEDULED_TOPIC_COLLECTION=false`  
  - 驗證：`curl -s http://localhost:8000/health | jq .cost_controls`
  - 證據：截圖 `2026-06-06_v7_E0-B_health_cost_controls.png` — `scheduled_topic_collection: false`
- [x] **C0-2** `ENABLE_AI_TOPIC_TRANSLATION=false`  
  - 驗證：同上
  - 證據：同上 E0-B — `ai_topic_translation: false`
- [x] **C0-3** 未在 production 預設全站 `DEEPSEEK_MODEL=pro`  
  - 驗證：讀 `config_module` / `.env`；grep 無單一 MODEL 覆寫 generate
  - 證據：E0-B — `deepseek_model: deepseek-v4-flash`
- [x] **C0-4** 架構表 v7 已含 D1～D5（2026-06-05）  
  - 驗證：打開 `專案完整架構表_v7.md` 「Token 省成本」
  - 證據：`專案完整架構表_v7.md` L104～L164
- [x] **C0-5** 基線 Token 數據已記錄  
  - 驗證：工作記錄有日期 + 數字或「無帳單存取」說明
  - 證據：`docs/deepseek_cost_investigation_2026-05.md`（2026-05 ¥63.43）

---

## Phase 1 — 大文本斷流 + 雙模型路由（P0）

**目標**：`summary_flash` 寫庫；收集零 AI 翻譯；`article_prompt` 禁止全文；**僅** generate/regenerate 用 Pro。

**依賴**：Phase 0 完成。

**結案判定**：**C1-1、C1-2、C1-3、C1-5、C1-7 必須 `[x]`**；其餘允許 1 項 `[!]` 並註明延後 Phase。

### 工作明細

- [ ] **P1-01** `Topic` model 新增 `summary_flash: Optional[str]`  
  - 產出：`backend/app/models/topic.py`、`schemas/topic.py`
- [ ] **P1-02** 新增 `summary_flash_service`：Flash 一次提煉 ~300 字  
  - 產出：`backend/app/services/summarization/summary_flash_service.py`
- [ ] **P1-03** 收集管線：L0 清洗後呼叫 P1-02，寫入 `topics.summary_flash`  
  - 產出：`channel_collector.py`、`topic_collector.py`
- [ ] **P1-04** **禁止** `original_content` 進 title 翻譯／summary 以外之 LLM  
  - 驗證：grep `_translate_title`、`article_prompt`
- [ ] **P1-05** `article_prompt.py` 僅 `summary_flash`（無則短 `description`）；移除 `original_content[:2000]`  
  - 產出：`backend/app/prompts/article_prompt.py`
- [ ] **P1-06** 固化精簡 `SYSTEM_PROMPT` 常數（D5）  
  - 產出：`backend/app/prompts/` 或各 service
- [ ] **P1-07** `config_module`：`DEEPSEEK_MODEL_FLASH`、`DEEPSEEK_MODEL_PRO`  
  - 產出：`backend/app/config_module.py`
- [ ] **P1-08** `deepseek.py` / factory：generate 任務 → PRO  
  - 產出：`backend/app/services/ai/deepseek.py`
- [ ] **P1-09** `contents.py` generate/regenerate 強制 PRO；**事實源僅 DB `summary_flash`**（不以 request body 的 `llm_input` 為 SoT）  
  - 產出：`backend/app/api/v1/contents.py`  
  - 備註：Phase 3 `token_gateway` 讀 body 後須 **receive 重放**（見 P3-01、**C3-9**）
- [ ] **P1-10** 拆開翻譯開關：收集不呼叫 AI；translate-display 不綁全拒  
  - 產出：`cost_controls.py`、`topic_display_translation_service.py`
- [ ] **P1-11** 日誌：`[SUMMARY_FLASH_SUCCESS]` topic_id=… chars=…  
  - 產出：`summary_flash_service.py`
- [ ] **P1-12** 單元或手動：mock RSS → DB 有 `summary_flash`  
  - 產出：`backend/tests/` 或手測步驟

### Phase 1 完成檢查清單

- [ ] **C1-1** Mongo `topics` 存在 `summary_flash` 欄位  
  - 驗證：`db.topics.findOne({summary_flash:{$exists:true}})` 或 Compass
  - 證據：
- [ ] **C1-2** collect 後新 topic 有非空 `summary_flash`  
  - 驗證：`POST /channels/{id}/collect` → 查 DB；日誌 `[SUMMARY_FLASH_SUCCESS]`
  - 證據：
- [ ] **C1-3** `article_prompt.py` 無 `original_content[:2000]`  
  - 驗證：`grep "original_content\[:2000\]" backend/app/prompts/article_prompt.py` 無命中
  - 證據：
- [ ] **C1-4** generate 無 HTML 長文進 prompt；且 **POST generate 可正常完成**  
  - 驗證：Network payload 或 log prompt 長度 < 2k chars  
  - 驗證（Phase 1，尚無 gateway）：`curl -X POST .../api/v1/contents/{topic_id}/generate`（Bearer）→ **200**，非卡住／非逾時  
  - 驗證（Phase 3 回歸）：掛 `token_gateway` 後同上 → 見 **C3-9**（body 重放）
  - 證據：
- [ ] **C1-5** `POST .../contents/{id}/generate` 使用 **pro**  
  - 驗證：回應 `model_used` 或 DeepSeek 後台
  - 證據：
- [ ] **C1-6** assist / summary 使用 **flash**（非 pro）  
  - 驗證：觸發 assist 一次 → log / 後台
  - 證據：
- [ ] **C1-7** collect 10 則 → DeepSeek ≈ 10 次（僅 summary），非 20+ 翻譯  
  - 驗證：DeepSeek 後台次數統計
  - 證據：
- [ ] **C1-8** `npm run build`（若動前端）或 `pytest` 通過  
  - 驗證：CI／本機
  - 證據：
- [ ] **C1-9** 無新增 SQL / SQLAlchemy  
  - 驗證：`git diff --name-only` 無 `*.sql`、無 `sqlalchemy` import
  - 證據：

### Phase 1 禁止項回歸（持續為 `[x]` 才合格）

- [ ] 收集管線**未**恢復逐則 `_translate_title`（DeepSeek）
- [ ] `article_prompt`**未**恢復塞入 2000 字原文

---

## Phase 2 — topic_translations + DeepL + 定向夜間預載（P1）

**目標**：`topic_translations` + 唯一索引；DeepL + 字串 Fallback；cache-first；夜間 channel 流水線（**無** kol_style）。

**依賴**：Phase 1（C1-1、C1-2 為 `[x]`）。

**結案判定**：**C2-1、C2-3、C2-5、C2-6、C2-7、C2-8 必須 `[x]`**；若實作防擊穿 in-flight 鎖，**C2-11 必須 `[x]`**。

### 工作明細

- [ ] **P2-01** Model + schema `topic_translation`  
  - 產出：`models/topic_translation.py`、`schemas/`
- [ ] **P2-02** `topic_translation_repository`（Motor CRUD + upsert）  
  - 產出：`repositories/topic_translation_repository.py`
- [ ] **P2-03** 建立 unique 索引 `(topic_id, lang, type)`  
  - 產出：`scripts/ensure_topic_translations_indexes.py` 或 `db_init.py`
- [ ] **P2-04** `deepl_provider.py`：`translate_with_fallback`，5s timeout，D4 前綴  
  - 產出：`services/translation/deepl_provider.py`
- [ ] **P2-05** `topic_display_translation_service`：cache-first → DeepL → 寫回  
  - 產出：既有 service 擴充
- [ ] **P2-13** 防快取擊穿：模組級 `_inflight`（或 `asyncio.Lock` per `topic_id:lang:type`）；`try`/`finally` **必**刪除 in-flight 條目（對應第三方 Promise 鎖，本 stack 為 **asyncio**）  
  - 產出：`topic_display_translation_service.py` 或 `translation/inflight_guard.py`
- [ ] **P2-06** `POST /topics/{id}/translate-display`：standard→DeepL；kol→Flash 按需  
  - 產出：`api/v1/topics.py`
- [ ] **P2-07** 港日 Channel RSS 清單（config 或 DB）  
  - 產出：`config/` 或 channel 標記欄位
- [ ] **P2-08** `scheduler.py` 新 job：`channel_prefetch_pipeline`  
  - 產出：`automation/scheduler.py`
- [ ] **P2-09** `ENABLE_CHANNEL_PREFETCH_PIPELINE` + `/health` cost_controls  
  - 產出：`cost_controls.py`
- [ ] **P2-10** 舊三類 6h job 在 env false 時不註冊  
  - 產出：`scheduler.py`
- [ ] **P2-11** 日誌：`[I18N_CACHE_HIT]`、`[CACHE_MISS]`、`[TRANSLATION_FALLBACK_TRIGGERED]`  
  - 產出：translation 層
- [x] **P2-12** 前端：卡片 standard；「網紅風格」才 kol（可併 Phase 4）  
  - 產出：`TopicCard.tsx`、`i18n`

### Phase 2 完成檢查清單

- [ ] **C2-1** `topic_translations` 有 compound **unique** 索引  
  - 驗證：`db.topic_translations.getIndexes()`
  - 證據：
- [ ] **C2-2** 重複 `(topic_id,lang,type)` 失敗或 upsert  
  - 驗證：手動 Mongo 或單測
  - 證據：
- [ ] **C2-3** 有快取 → `translate-display` + `[I18N_CACHE_HIT]`  
  - 驗證：curl + Bearer
  - 證據：
- [ ] **C2-4** 無快取 → DeepL + `[CACHE_MISS]` + 寫回 DB  
  - 驗證：刪快取後再請求
  - 證據：
- [ ] **C2-5** DeepL 錯誤/timeout → `[Fallback-JA]` 或 `[Fallback-EN]`  
  - 驗證：錯 key 或 mock timeout
  - 證據：
- [ ] **C2-6** 夜間 job 後有 ja/en `standard_translation`  
  - 驗證：手動觸發 job；DB count ≥ 1
  - 證據：
- [ ] **C2-7** 夜間 job 日誌**無** `kol_style`  
  - 驗證：grep scheduler log
  - 證據：
- [ ] **C2-8** 三類 6h 排程**未**執行  
  - 驗證：`/health` + scheduler 註冊表
  - 證據：
- [ ] **C2-9** 舊 `titles_i18n` 仍可 fallback  
  - 驗證：舊 topic 無 translation 文檔時 UI 可顯示
  - 證據：
- [x] **C2-10** 無 SQL / NLLB 新增  
  - 驗證：`grep sqlalchemy|nllb` 無新增
  - 證據：Phase 5 **P5-02** 審計（`V7-5_Phase5_session_log.md`）
- [ ] **C2-11** in-flight 鎖錯誤邊界：Exception 後鎖仍釋放，後續請求不永久懸掛  
  - 驗證：故意讓鎖內 DeepL／Flash 拋錯（mock 或錯 key）→ 確認 `_inflight`／`finally` 已清除 → **第二次** `translate-display` 可完成（非 Timeout／非永遠等待）  
  - 證據：日誌含 release／第二次請求 status + 耗時 ms

---

## Phase 3 — Token Gateway + 終極產文加固（P1）

**目標**：gateway 阻斷大文本；強制 `summary_flash`；`max_tokens=1500`；Pro 產文。

**依賴**：Phase 1（C1-3、C1-5）；Phase 2（C2-3 建議 `[x]`）。

**結案判定**：**C3-1、C3-2、C3-3、C3-5、C3-9 必須 `[x]`**；C3-7 可延後 P3.1。

### 工作明細

- [ ] **P3-01** `token_gateway.py`：strip `llm_input`；**FastAPI/Starlette body 重放**（讀取 `await request.body()` 後以新 `_receive` 回灌，避免路由 `await request.json()` 卡死／逾時）  
  - 產出：`middleware/token_gateway.py`（僅掛 generate/regenerate 路徑或 path 前綴過濾）
- [ ] **P3-02** 掛載於 generate/regenerate 路由  
  - 產出：`main.py` 或 router deps
- [ ] **P3-03** 無 `summary_flash` → generate 400 明確錯誤  
  - 產出：`contents.py`
- [ ] **P3-04** Pro 呼叫 `max_tokens=1500`（可 env）  
  - 產出：`deepseek.py`
- [ ] **P3-05** 日誌：`[TOKEN_GATEWAY_PASSED]`  
  - 產出：gateway
- [ ] **P3-06** DNA：對接 `style_profile` / `style_dna` 進 prompt（精簡）  
  - 產出：style 相關 service
- [ ] **P3-07** `facebook_shell.py` 純函數（Post Kit）  
  - 產出：`utils/facebook_shell.py`
- [ ] **P3-08** （可選）Free/Pro 月 Token Redis → 標 P3.1 延後

### Phase 3 完成檢查清單

- [ ] **C3-1** 惡意超大 `user_prompt` → 忽略或 400/413  
  - 驗證：curl 大 payload
  - 證據：
- [ ] **C3-2** 正常 generate 日誌含 `[TOKEN_GATEWAY_PASSED]`  
  - 驗證：成功路徑一次
  - 證據：
- [ ] **C3-3** 無 `summary_flash` → generate **失敗**；有 `summary_flash` 時產文**僅**來自 DB  
  - 驗證：空 topic → 400／明確錯誤（非 500 逾時）  
  - 驗證（Context 依賴）：request body 帶與 DB **矛盾** 的 `llm_input`／長文 → 產出事實仍與 DB `summary_flash` 一致（grep 產文或 log prompt 無前端殘留全文）  
  - 驗證：`contents.py` 內 generate **不**以 `request.json()` 內容為事實 SoT（code review 或斷點）
  - 證據：
- [ ] **C3-4** `max_tokens` 請求 ≤ 1500  
  - 驗證：log 或請求體
  - 證據：
- [ ] **C3-5** 單次 generate input token 遠低於 7.3 萬（目標 < 5k）  
  - 驗證：DeepSeek 後台
  - 證據：
- [ ] **C3-6** `model_used` 仍為 Pro  
  - 驗證：同 C1-5
  - 證據：
- [ ] **C3-7** `facebook_shell` 有測試或手動 in/out 樣例  
  - 驗證：pytest 或工作記錄
  - 證據：
- [ ] **C3-8** 靈感／assist **未**被 gateway 誤擋  
  - 驗證：靈感頁載入 TC
  - 證據：
- [ ] **C3-9** Middleware 讀 body 後 generate 仍可 `await request.json()`（無 Request Timeout／非誤判 400）  
  - 驗證：`curl -X POST .../contents/{topic_id}/generate -H "Authorization: Bearer …" -H "Content-Type: application/json" -d '{"llm_input":"應被剝除的長文…"}'` → **200** 或業務 4xx（非連線逾時）；後端 log 有 `[TOKEN_GATEWAY_PASSED]`；路由 handler 正常執行完畢  
  - 驗證：對照 Phase 1 **C1-4** 同一 curl，掛 gateway 前後皆通  
  - 證據：

---

## Phase 4 — 前端體驗與可觀測性（P2）

**目標**：TopicCard skeleton + fade；cache-first 體感；文件對齊。

**依賴**：Phase 2 API 穩定。

**實作基礎**：Phase 4 結案前 **[`v7_implementation_basics.md`](../../../../v7_implementation_basics.md) BF-UI-1～BF-UI-4 必須 `[x]`**（與 **P4-03／P4-04** 對齊 README 按鈕／i18n）。

**結案判定**：**C4-1、C4-2、C4-4 必須 `[x]`**；**BF-UI-1～BF-UI-4 必須 `[x]`**。

### 工作明細

- [x] **P4-01** TopicCard：standard 載入 skeleton → fade-in  
  - 產出：`TopicCard.tsx`
- [x] **P4-02** kol_style 按鈕：延遲請求、獨立 loading  
  - 產出：`TopicTranslateDisplayButton.tsx`
- [x] **P4-03** `data-testid` 對照 [`按鈕測試ID架構表.md`](../../../按鈕測試ID架構表.md)（若有新按鈕；README 規則 3、4）  
  - 產出：架構表更新 + 元件屬性
- [x] **P4-04** i18n 三語（**禁止硬編碼**；README 規則 6）  
  - 產出：`frontend/src/i18n/index.ts`
- [x] **P4-05** `/health` 文件與 cost_controls 一致  
  - 產出：README / v7 需求（VM-3／Phase 2 已就緒）
- [x] **P4-06** 工作記錄：三主線 Token 收口  
  - 產出：`工作記錄.md`

### Phase 4 完成檢查清單

- [ ] **C4-1** `/topics` 切 ja：skeleton → 譯文 fade-in  
  - 驗證：瀏覽器 375px + desktop
  - 證據：
- [ ] **C4-2** 快取命中後再切語系：Network **0** 翻譯 API  
  - 驗證：DevTools Network
  - 證據：
- [ ] **C4-3** 僅「網紅風格」才出現 Flash 請求  
  - 驗證：點擊前後 Network
  - 證據：
- [x] **C4-4** `npm run build` PASS  
  - 驗證：終端
  - 證據：`V7-4_Phase4_session_log.md`（2026-06-06 build exit 0）
- [ ] **C4-5** 工作記錄含 Phase 1～4 證據摘要  
  - 驗證：人工審閱
  - 證據：

---

## Phase 5 — 合規（非程式主線 · P3）

- [x] **P5-01** Privacy Policy / APPI 跨境披露（法務）  
  - 證據：`Privacy.tsx` + i18n 頻道區塊 7（DeepL／DeepSeek／APPI）；`V7-5_Phase5_session_log.md` — **草稿**待法務覆核
- [x] **P5-02** 確認 **不做** NLLB（架構 + repo 審計）  
  - 驗證：`grep -i nllb` 無新增依賴
  - 證據：`V7-5_Phase5_session_log.md` — 程式／requirements **0 命中**；僅文件禁止敘述

---

## 跨 Phase 總驗收（上線前）

- [ ] **X-1** 10 則收集：DeepSeek ≈ 10 次 Flash summary，**0** 次收集翻譯  
  - 驗證：後台統計
  - 證據：
- [ ] **X-2** 瀏覽 20 張已預載卡：DeepSeek **0**、DeepL **0**  
  - 驗證：Network
  - 證據：
- [ ] **X-3** 1 次 generate：Pro **1** 次，input token < 5k  
  - 驗證：後台
  - 證據：
- [ ] **X-4** 24h 日誌：僅 channel 流水線，無三類、無 kol  
  - 驗證：scheduler log
  - 證據：
- [ ] **X-5** `專案完整架構表_v7.md` 與本檔 Phase 勾選一致  
  - 驗證：文件審閱
  - 證據：
- [ ] **X-6** v6 凍結檔未被修改  
  - 驗證：`git diff docs/archives/` 空
  - 證據：

---

## 證據記錄模板（貼至工作記錄）

```text
## v7 Token Phase {N} 結案 — {日期}
- 分支／commit：
- 檢查清單：（複製本檔該 Phase 區塊，將 [ ] 改為 [x] 或 [!]）
- 指令／查詢：
- 日誌片段：
- DeepSeek 後台：
- 已知限制／下一 Phase：
```

---

## 版本

| 日期 | 說明 |
|------|------|
| 2026-06-05 | 初版：Phase 0～5 工作明細 + 檢查清單 |
| 2026-06-05 | 格式統一：全檔 `[ ]` / `[x]` PASS / `[!]` FAIL |
| 2026-06-05 | 補丁：C1-4/C3-9 FastAPI body 重放；C2-11 in-flight 鎖；C3-3 DB Context SoT |
