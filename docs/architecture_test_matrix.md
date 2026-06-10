# 全專案架構測試對照表（對齊 `專案完整架構表.md`）

> **用途**：補足 **[channel_create_new_scheme_checklist.md](./channel_create_new_scheme_checklist.md)** 範圍外之模組—依 **`專案完整架構表.md`** 路由、API、服務與 Mongo 集合，排定 **迴歸 TC** 勾選，方便 **測試週**（`AGENTS.md` 第 10～14 工作天、**2026-05-12 起**）逐日執行。  
> **建立／更新**：2026-06-03（**NW-2**：矩陣 **I1～I3**、**A3**、**B1/B4**、**D1**、**E1**、**J1** 補勾；頻道 **33/42**）  
> **命名**：本檔 **矩陣 A～K**＝大區（對應下方標題）；**A1、C2**＝該區內列號。**禁止**使用分節符號。**頻道 42 點**用 **頻道區塊 N**（見 `test_week_daily_checklist`）。  
> **非本表範圍**：**`/channels/create` 助手主導** 之 B～D 細項—請用 **建立頻道清單**；**I.1～I.3** 與 **清單 H** 仍為 SoT。

**本機檢測預設**：前端 **`http://localhost:3000`**（`vite.config.ts`）、後端 **`http://localhost:8000`**、API Base **`…/api/v1`**—詳表見 [test_week_gap_closure_plan.md](./test_week_gap_closure_plan.md) 第二節。**按日排程**：[test_week_daily_checklist.md](./test_week_daily_checklist.md)。

---

## 與其他文件怎麼搭配

| 文件 | 角色 |
|------|------|
| [專案完整架構表.md](../專案完整架構表.md) | 路由／目錄／集合／靈感架構之 **單一導覽** |
| [channel_create_new_scheme_checklist.md](./channel_create_new_scheme_checklist.md) | **建立頻道** 交付與 **I 節** 工單 |
| [AGENTS.md](../AGENTS.md) | **第 10～14 天** 日程與完成判定 |
| [v4.0.0_Checklist_TestList.md](../v4.0.0_Checklist_TestList.md) | 歷史 Phase 1～5 **細項 TC**；本表為 **架構覆蓋矩陣**，可指向該檔 Phase |
| **[test_week_gap_closure_plan.md](./test_week_gap_closure_plan.md)** | **架構複核 12 類缺口** → 測試週 **日別／P0／DoD**（與本表 **#2** 對齊） |

---

## 建議測試週執行順序（可對照 AGENTS）

| 次序 | 建議日 | AGENTS 對齊 | 本表區段（優先） |
|:----:|--------|-------------|------------------|
| 1 | 第 10 天 | Meta + 詳情 2.6 | **矩陣 H** 社交連線、**矩陣 C** 主題詳情 API |
| 2 | 第 11 天 | 詳情 RWD | **矩陣 C**、**矩陣 A** viewport |
| 3 | 第 12 天 | 頻道助手 42 點 | **矩陣 E** + 建立頻道清單 **I.1** |
| 4 | 第 13 天 | 靈感 28 點 | **矩陣 F** |
| 5 | 第 14 天 | 匯總 | 本表全區 **未完成項** 掃尾 + **矩陣 E** #32/#33 |

---

## 矩陣 A — 全域與導覽（`App.tsx`／`Sidebar.tsx`）

**對齊架構表**：「前端路由結構」「Sidebar 導航」。

| # | 項目 | 驗證方式（摘要） | 結果 | 證據／備註 |
|:-:|------|------------------|:----:|------------|
| A1 | 已登入時 `/` 導向預期（如 `/topics`） | 手動／Network | [ ] | |
| A2 | Sidebar 每一 `path` 可進入、與路由一致 | **S4 逐項 TC**（UI + Network；見 `test_week_daily_checklist` **S4 表**） | [ ] | 對照架構表 9 路由；**禁止**僅「能開頁」 |
| A3 | 語言切換後導覽標籤仍正確（i18n） | Header 語言 | [x] | **2026-06-02 NW-1**：ja/en Sidebar 無裸 key（NW1-3a/b） |
| A4 | `data-testid`：側邊欄至少抽樣 2 連結 | DevTools | [ ] | 見 `按鈕測試ID架構表.md` |

---

## 矩陣 B — 認證與帳號（`auth` API／登入註冊流程）

**對齊架構表**：「認證流程」、`api/v1/auth.py`、`middleware/jwt_auth`。

| # | 項目 | 驗證方式 | 結果 | 證據／備註 |
|:-:|------|----------|:----:|------------|
| B1 | Google 登入成功 → 進入主功能 | 手動 | [x] | **2026-05-19 R-3**／環境 Gate；持續用於測試週 |
| B2 | Email 登入／註冊（若啟用） | 手動 | [ ] | |
| B3 | 無效 token 或過期 → 導回登入或錯誤提示 | 可選 | [ ] | |
| B4 | `PATCH /profile` 或同等更新個人資料 | Network | [x] | **2026-06-02 NW-1**：`/settings` 表單 NW1-6；S9 API 曾 PASS（W-3） |

---

## 矩陣 C — 主題列表與詳情（`topics`／`contents`／`images`）

**對齊架構表**：「主題卡生成」「Topic 模型」、路由 `/topics`、`/topics/:id`。

| # | 項目 | 驗證方式 | 結果 | 證據／備註 |
|:-:|------|----------|:----:|------------|
| C1 | `/topics` 列表載入、分類 Tab／無限滾動 | 手動 | [ ] | 可對照 v4 Phase 1 TC |
| C2 | **詳情 2.6**：固定 `topic_id` 開 `/topics/:id`，觸發 1～2 個後端操作 | Network 記 status | [x] | **2026-05-21 T-10**：`topic_trend_20260519212108_9` GET 200；重新生成 POST 200；interactions 200 |
| C3 | `contents` 無資料時非 500（預期 404） | Network | [x] | **2026-05-05** 修復；T-10 未再現 500 |
| C4 | 圖片區／預覽（若有）無阻擋錯誤 | 目視 + Console | [ ] | |
| C5 | **RWD 375px**：詳情頁無橫向捲動、主按鈕可點 | DevTools | [x] | **2026-05-21 T-11**：375×747 五項 **PASS** |
| C6 | **方案 C 顯示多語**：收集語言主標；介面語言 ≠ 收集語言時 **「譯為目前語言」**；`POST …/translate-display`；詳情切換收集時標題 | 手動 + Network | [ ] | **2026-06-03** 程式交付；testid：`btn-topic-card-translate`、`btn-topic-detail-translate-display`；需 **重啟 uvicorn**／建議重新收集 |

---

## 矩陣 D — 我的頻道列表與維護（非建立頁）

**對齊架構表**：`/channels`、`channels.py` 更新／刪除；**清單 H** 已盤點 API，本表補 **UI 行為**。

| # | 項目 | 驗證方式 | 結果 | 證據／備註 |
|:-:|------|----------|:----:|------------|
| D1 | `/channels` 列表與後端一致 | 手動 | [x] | **2026-05-21** E2E；**2026-06-03 NW2-7**：**1/3** 列表 + **GET /channels 200** |
| D2 | 編輯頻道（若有 UI）儲存成功 | Network | [ ] | |
| D3 | 刪除頻道（若有）列表同步、無幽靈項 | 手動 | [ ] | 對齊清單 **H** |
| D4 | 與 **矩陣 E** 新建頻道後列表出現新項目 | 端到端 | [x] | **2026-05-21**：**親切香港美食** 於 `/channels` 可見 |

---

## 矩陣 E — 建立頻道 `/channels/create`（交叉引用）

**對齊架構表**：「建立頻道 Step 2／RSS」①～⑤。

| # | 項目 | 驗證方式 | 結果 | 證據／備註 |
|:-:|------|----------|:----:|------------|
| E1 | **助手主導** Phase B～D | 逐項 | [x] | **2026-05-09** 清單 **B～D** 開發結案；**2026-05-21** E2E |
| E2 | **I.1～I.3**（E2E、無障礙、429、離線…） | 測試週 | [ ] | **I.1 E2E ☑**；**離線 toast ☑**（**2026-06-02 NW-1 S7**）；375/a11y/429 待 |
| E3 | **#32/#33** 建議名稱／描述 → 套用 | 手動 | [x] | **2026-05-21 E2E**：`btn-channels-assist-apply-naming` |
| E4 | **D.1** 表單主路（關閉助手後仍可建立） | 手動 | [ ] | 建立頻道清單 **D.1** |

---

## 矩陣 F — 靈感策劃 v5.0（`Inspiration.tsx`／`inspiration.py`）

**對齊架構表**：「v5.0 靈感策劃 AI 助手架構」、**「導師／同伴模式（規劃）」**、集合 `inspiration_sessions` 等。  
**規格**：[`v5.0_靈感策劃_導師模式_流程與改動清單.md`](./v5.0_靈感策劃_導師模式_流程與改動清單.md)（2026-05-22）。

| # | 項目 | 驗證方式 | 結果 | 證據／備註 |
|:-:|------|----------|:----:|------------|
| F1 | `/inspiration` 進頁、模式切換（搜尋／助手） | 手動 | [x] | **2026-05-22**：進頁、搜尋／類別／列表 **PASS** |
| F2 | 開始對話 → 問題顯示 → 回答流程 | 手動 | [ ] | 現行助手流程；**導師模式**待實作後重測 |
| F3 | 生成內容：驗證狀態／來源連結可讀 | 手動 | [ ] | 本輪未測助手生成 |
| F4 | 成本／偏好 API（若暴露於 UI）無 500 | Network | [ ] | |
| F5 | 28 點清單（專案既有）逐項結果 | 文件 | [x] | **27/28（96.4%）**；**3.7 PASS** 2026-05-26；**#37** 已知限制；見 `工作記錄` T-13 |

---

## 矩陣 G — 風格檔案、評分、內容面板（Phase 4 一線）

**對齊架構表**：`StyleProfile`、`RatingPanel`、`ContentGenerationPanel`、對應 API。

| # | 項目 | 驗證方式 | 結果 | 證據／備註 |
|:-:|------|----------|:----:|------------|
| G1 | `/style-profile` 載入與儲存 | 手動 | [ ] | |
| G2 | 主題詳情或內容區 **評分** 👍／👎 | 手動 | [ ] | |
| G3 | 內容生成面板：語言／風格選項與請求 | Network | [ ] | |

---

## 矩陣 H — 發布與社交連線（`Publish`／`SocialConnect`／`social.py`）

**對齊架構表**：`/publish`、`/social-connect`、`distribution_service`、集合 `social_connections`。  
**產品分層（2026-05-27）**：**L0** = [`publish_post_kit_spec.md`](./publish_post_kit_spec.md) **PK1～PK6**（詳情 Post Kit + copy）；**L2** = [`social_connect_publish_verify_gate.md`](./social_connect_publish_verify_gate.md)（OAuth／`POST …/social/publish`）。測試週 **預設驗 L0**；H1～H2／H4 標 **N/A** 或 **PARTIAL** 即可。

| # | 項目 | 驗證方式 | 結果 | 證據／備註 |
|:-:|------|----------|:----:|------------|
| H0 | **Post Kit**（`/topics/:id` 或發布助手）**PK1～PK6** copy | 手動 | [ ] | UI **待開發**；規格 SoT 見 `publish_post_kit_spec.md`；**禁止**以 `POST …/social/publish` 200 當 L0 PASS |
| H1 | `/social-connect` 取得 `oauth_url`（Meta）**【L2】** | Network | [x] | **2026-05-20 PASS**；**L0 不要求**複測 |
| H2 | 可進入供應商授權頁（環境允許時）**【L2】** | 手動 | [x] | **2026-05-20 PASS**；**L0 N/A** |
| H3 | `/publish` 發布助手可開、無裸 i18n key（L0） | 手動 | [ ] | 併入 **H0** 或 S4-6；勿僅「能開頁」 |
| H4 | 回呼／token 儲存失敗時使用者可理解 **【L2】** | 可選 | [ ] | 啟用 `VITE_ENABLE_API_PUBLISH` 時再驗 |

---

## 矩陣 I — 偏好、排程、設定

**對齊架構表**：`/preferences`、`/schedule`、`/settings`。

| # | 項目 | 驗證方式 | 結果 | 證據／備註 |
|:-:|------|----------|:----:|------------|
| I1 | `/preferences` 可開、儲存不報錯 | 手動 | [x] | **2026-06-02 NW-1**：S4-8 UI+API（NW1-1） |
| I2 | `/schedule` 列表或操作（依現行 MVP） | 手動 | [x] | **2026-06-02 NW-1**：S4-9 UI+API（NW1-2） |
| I3 | `/settings` 基本項可及 | 手動 | [x] | **2026-06-02 NW-1**：S9 UI（NW1-6） |

---

## 矩陣 J — 後端橫向與維運（非單頁功能）

**對齊架構表**：`feeds` 健康、`automation` 排程、`middleware`。

| # | 項目 | 驗證方式 | 結果 | 證據／備註 |
|:-:|------|----------|:----:|------------|
| J1 | `GET /health`（或專案約定健康端點） | curl／瀏覽器 | [x] | **2026-06-03 NW-2**：`database=connected`（助手 curl） |
| J2 | RSS 健康／管理 API（若 QA 有權限）抽樣 | API | [ ] | v4 Phase 1.3 |
| J3 | 全站 rate limit／CSRF：不誤擋主流程 | 可選 | [ ] | 對齊架構表 middleware |
| J4 | **收集排程**（6h／清理）：staging／日誌知情即可 | 文件／日誌 | [ ] | 非必手動 |

---

## 矩陣 K — MongoDB 集合抽樣對照（架構表「資料庫集合」）

**說明**：下列為「功能用到時資料一致」之 **抽樣**；不必逐集合寫入測試，除非當日劇本觸及。

| 集合 | 本週建議觸發劇本 | 已查／備註 |
|------|------------------|------------|
| `users` | 登入／註冊 | [ ] | |
| `topics` / `contents` / `images` | 矩陣 C 詳情 | [ ] | |
| `channels` | 矩陣 D、矩陣 E | [ ] | |
| `ratings` | 矩陣 G2 | [ ] | |
| `style_profiles` | 矩陣 G1 | [ ] | |
| `social_connections` | 矩陣 H | [x] | **2026-05-20**：Facebook **@Adam Au** 已連接（`/social-connect?success=true`） |
| `schedules` | 矩陣 I2 | [ ] | |
| `feed_health` | 矩陣 J2 | [ ] | |
| `inspiration_sessions` / `user_inspiration_preferences` / `cost_records` | 矩陣 F | [ ] | |

---

## 測試週收尾（第 14 天可貼入 `工作記錄.md`）

- **本表未完成列數**：約 **30+**（矩陣 A～J 多數待 W-3；矩陣 C／矩陣 D4／矩陣 E3／矩陣 F／矩陣 H 部分已勾—見 `工作記錄`「測試週收口匯總」）  
- **建立頻道清單 I 節未完成列數**：I.1 子項 **6** + I.2 **3**（I.3 全文簽核待 W-3）  
- **下一輪修復（P0）**：見 `工作記錄.md` 匯總節「下一輪 P0」  

---

**維護**：架構表大改路由或新增頁面時，同步增刪本表章節與列；建立頻道行為變更以 **channel_create_new_scheme_checklist.md** 為先。
