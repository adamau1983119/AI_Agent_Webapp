# v8 正式域 — 日常運作與客戶體驗（CX／OPS）

> **狀態（2026-09-02）**：產品**已正式上架**；公眾主題卡**產出時契約**與全站正文截斷已合 `main`（PR #51／#52）；第一批新卡驗收＝**9/3 04:00 HKT**。  
> **觸發**：`專案開始，正式域日常運作，客戶體驗優先 @AGENTS.md`  
> **證據**：`docs/evidence/v8/YYYY-MM-DD/`（截圖或 Network／信箱一句才可勾）  
> **改碼**：僅 **CX／OPS FAIL 阻塞客戶** 才開 `feature/v8-*`＋PR。  
> **OBS／日報 SoT**：[`v8_observability_alerting.md`](./v8_observability_alerting.md) · 備份 [`2026-09-02_topic-card-cx_snapshot`](./backups/2026-09-02_topic-card-cx_snapshot/SNAPSHOT_README.md) · [`2026-08-20_source-article-translation-and-guardrails_snapshot`](./backups/2026-08-20_source-article-translation-and-guardrails_snapshot/SNAPSHOT_README.md)

---

## 代號總表（現行）

| 族 | 代號 | 客戶／營運問題 | 最短驗法 |
|----|------|----------------|----------|
| **CX** | **CX-LOGIN** | 能登入正式域、語系可切 | 登入 → **`/dashboard`**（AE pending 仍進 onboarding） |
| **CX** | **CX-AE** | Alter Ego 主路可用 | extract／skip／regenerate 其一＋截圖 |
| **CX** | **CX-TOPIC** | 主題卡隨介面語系（尤其 **en／ja**） | Dashboard 切 en／ja → 標題摘要對語系 |
| **CX** | **CX-MC** | My Channel 真實 feed | `/my-channel` 有卡或可解鎖 |
| **CX** | **CX-PK** | Post Kit 可仿文／複製 | 詳情 Post Kit copy＋toast |
| **CX** | **CX-IMAGE** | 主題詳情可搜圖（Google） | 詳情 → 搜尋圖片 → 有結果；Network `images/search` 200 |
| **OPS** | **OPS-HEALTH** | API／DB 活著 | `api…/health` → 200、`database: connected` |
| **OPS** | **OPS-CARD** | 當日有自動產卡 | Dashboard **今日主題 N/15**、底部 TopicCard 網格；或 Mongo `generated_at` HKT 當日 |
| **CX** | **CX-ARTICLE-BODY** | 詳情只見報導正文、無購物／相關閱讀附錄 | **9/3 04:00 新卡**詳情；舊卡不回填 |
| **OPS** | **OPS-I18N** | 新卡含三語預寫 | 新 topic 有 `titles_i18n.en`＋`.ja`（需 `ENABLE_TOPIC_TRIPLE_PRELOAD=true`） |
| **OPS** | **OPS-DIGEST** | 正式域每日營運報告進信箱 | Deploy log `Email 發送成功 (resend)` 或信箱自動收到 |
| **OPS** | **OPS-COST** | 成本未失控 | DeepSeek／DeepL 用量或告警一句 |
| **OPS** | **OPS-ENV** | Railway 變數對齊 v6 本機 | `validate/images` google=true；OAuth 正式域 URL |
| **FIX** | **FIX-*** | 上列 FAIL 且阻塞客戶 | 最小 PR；結案對回 CX／OPS |

---

## 2026-09-02 公眾主題卡產出時契約＋正文截斷（PR #51／#52）

| 項 | 狀態 | 一句 |
|----|------|------|
| **OPS-CARD-PRODUCE-CONTRACT** | ✅ 程式 | 04:00／generate-today 呼叫 `finalize_produced_cards`；三語＋`summary_flash`＋清洗正文 |
| **CX-ARTICLE-GET-OVERLAY** | ✅ 程式 | 詳情 GET 不重抓、不 Flash；只 overlay `source_content_i18n` |
| **CX-ARTICLE-BODY-CUTOFF** | ✅ 程式 | `article_boilerplate` 全站截斷購物／影片／相關閱讀；不依來源特例 |
| **OPS-CARD-DEPLOY-912** | ✅ | Railway `alert-emotion` 12:12 重啟；`/health` 200；15/15 略過補產（今日已足） |
| **CX-ARTICLE-BODY** | ⏳ 9/3 04:00 | 新公眾卡詳情無商品清單／Related Stories；**不回填** 9/1–9/2 |
| **CX-MC-PRODUCE** | ⏳ 之後 | 頻道收集暫不改；接同一產出契約時再驗 |
| **備份** | ✅ | `backup/2026-09-02-topic-card-cx-merged` · [snapshot](./backups/2026-09-02_topic-card-cx_snapshot/SNAPSHOT_README.md) |

---

## 2026-08-20 主題卡事實錨定＋源文章完整新聞翻譯＋5 道實體硬門禁

| 項 | 狀態 | 一句 |
|----|------|------|
| **OPS-CARD-FACT-ANCHOR** | ✅ | 公共主題卡 `generate_content=false`；按需生成 JIT；Soul/Article Prompt 事實錨定防跨領域污染 |
| **CX-ARTICLE-TRANSLATION** | ✅ | `resolve_source_article_translation` 完整新聞報道翻譯；支援三語快取與查看原文/譯文即時切換 |
| **FIX-SOURCE-ARTICLE-EXTRACTION** | ✅ | 升級 ArticleExtractor 支援 RSS `content:encoded` 解析、正則降級與 On-Demand 即時正文補抓，解決「NO 源文 SHOW」 |
| **CX-TOPIC-LAYOUT** | ✅ | TopicDetail 1:1 草圖排版；150/300/500 黃金字數；純化互動（移除編輯按鈕、保留👍👎） |
| **FIX-I18N-LANGUAGE-SCRIPT** | ✅ | 修復日語純漢字誤判為日文之漏洞；`titles_i18n` 快取嚴格驗收目標語系腳本 |
| **GATE-PHYSICAL-ENFORCEMENT** | ✅ | Git Pre-Commit 實體綁定 5 道門禁（結構＋i18n＋管線＋2 組單元測試）；全部 100% PASS |
| **備份** | ✅ | `backup/2026-08-20-source-article-translation-and-guardrails` · [snapshot](./backups/2026-08-20_source-article-translation-and-guardrails_snapshot/SNAPSHOT_README.md) |

---

## 2026-08-12 Railway env ＋ 圖片搜尋 ＋ 主題去重（PR #38）

| 項 | 狀態 | 一句 |
|----|------|------|
| **OPS-ENV-GOOGLE-IMAGE** | ✅ | Railway `GOOGLE_API_KEY`＋`GOOGLE_SEARCH_ENGINE_ID`；API 搜圖 PASS |
| **OPS-ENV-OAUTH-META** | ✅ 使用者已設 | 正式域 `BACKEND_URL`／`FRONTEND_URL`／`CORS`／OAuth redirect／`META_*` |
| **FIX-TOPIC-DEDUP** | ✅ **PR #38** | 補生成只填缺口；Dashboard 去重；merge `4819e99` |
| **FIX-IMAGE-GOOGLE-ONLY** | ✅ PR #39 | `main` `6fa295d` — Google 優先、移除 DuckDuckGo |
| **CX-IMAGE** | ⏳ 手測 | 瀏覽器 Topic 詳情搜圖截圖 |
| **備份** | ✅ | `backup/2026-08-12-railway-env-image-ops` · [snapshot](./backups/2026-08-12_railway_env_image_ops_snapshot/SNAPSHOT_README.md) |
| **範本** | ✅ | `backend/.env.railway.example` |

**說明**：v6 圖片搜尋在 **本機 `.env`** 已驗證；`.env` 不進 Git，**Railway 須手動複製**。先前靠 DuckDuckGo 掩蓋未設 Google。

---

## PR #24 主題卡修復（2026-08-11 · 已 merge `main`）

| 項 | 狀態 | 一句 |
|----|------|------|
| **FIX-TOPIC-HKT** | ✅ **已部署** | Dashboard HKT 今日 filter；`N/15`；Vercel Ready |
| **FIX-TOPIC-UX** | ✅ | 空狀態「準備中」；schedules 失敗不清空卡 |
| **CX-LOGIN** | ✅ **對齊程式** | AE 完成 → `/dashboard`（pending → onboarding） |
| **OPS-I18N 預載** | ⏳ **env** | 需 Railway `ENABLE_TOPIC_TRIPLE_PRELOAD=true` + DeepL key |
| **回歸腳本** | ✅ | `python scripts/check_topic_core_regression.py` |
| **備份** | ✅ | `backup/2026-08-11-topic-dashboard-hkt-pr24` · snapshot README |

--- 

### 本日異常（PR #27 部署檔案路徑）— 已修

| 項 | 狀態 | 一句 |
|----|------|------|
| **FIX-TOPIC-I18N-CONFIG** | ✅ merged | `backend/config/topic_languages.json` + Railway Root=`backend/` |
| **FIX-TOPIC-DEEPL-FALLBACK** | ⏳ PR | Fallback 禁止寫 `titles_i18n`；前端忽略 `[Fallback-` |
| **FIX-TOPIC-V8-CUTOVER** | ⏳ PR | 列表預設只顯示 `pipeline_version>=8`；舊卡留 DB |
| **FIX-TOPIC-LIST-PERF** | ⏳ PR | `/topics` 批量 image／word count |
| **OPS-DIGEST 雙軌** | ⏳ PR | 主旨「每日基本檢查」vs「即時告警」 |

**明日 OPS 第一步**：merge 後確認 DeepL key → 產新卡（generate-today 或等 04:00）→ Dashboard 無舊 Fallback 卡；信箱搜「每日基本檢查」。

---

| 項 | 狀態 | 一句 |
|----|------|------|
| Watchdog／digest loop | ✅ | `WATCHDOG_START digest=True` |
| 寄信 | ✅ | **Resend HTTPS**（PR #19）；網域 Verified |
| **正式域自動進信箱** | ✅ **PASS** | 08-11 信箱已收；`Email 發送成功 (resend)` |
| From | ✅ | `noreply@ai-alterego.com` |
| checklist | **PD-OBS-TL-07b／09 `[x]`** | 見 observability 檔 |

---

## 每日建議順序（約 45′～90′）

1. **OPS-HEALTH**（正式域）  
2. **OPS-CARD**＋**OPS-I18N**（今日新卡；僅 v8 世代）  
3. 任選 **1～2 個 CX-***（真實帳號）  
4. **OPS-DIGEST**／**OPS-COST**（搜主旨「每日基本檢查」；紅燈另看「即時告警」）  
5. 有 FAIL → 記 **FIX-***；無則不改碼  

**OPS-CARD 證據句範例**：`Dashboard 今日 12/15；GET /topics 200；pipeline_version=8`  
**OPS-I18N 證據句範例**：`抽樣無 [Fallback-；切 ja 標題為日文`  
**回滾首登 landing**：Vercel 設 `VITE_POST_LOGIN_PATH=/my-channel`（預設不設＝Dashboard）

---

## 當日勾選（複製到工作記錄）

```text
日期：2026-08-12
OPS-HEALTH：PASS（healthy／connected）
OPS-ENV：PASS（Google 圖片 key；OAuth／Meta 正式域 URL 已貼 Railway）
OPS-CARD：⏳ PR #38 部署後觀察是否仍重複卡
CX-IMAGE：⏳ API PASS；瀏覽器手測待截圖
CX-LOGIN／CX-TOPIC：⏳ Google 登入／三語切換
OPS-DIGEST／COST：維持 PASS
FAIL／FIX：FIX-TOPIC-DEDUP ✅ #38；FIX-IMAGE-GOOGLE ✅ #39
明日第一步：瀏覽器 CX-IMAGE 截圖；Dashboard 確認無重複卡
```
