# 全專案架構測試對照表（對齊 `專案完整架構表.md`）

> **用途**：補足 **[channel_create_new_scheme_checklist.md](./channel_create_new_scheme_checklist.md)** 範圍外之模組—依 **`專案完整架構表.md`** 路由、API、服務與 Mongo 集合，排定 **煙霧／迴歸** 勾選，方便 **測試週**（`AGENTS.md` 第 10～14 工作天、**2026-05-12 起**）逐日執行。  
> **建立／更新**：2026-05-20（**§H** H1～H2 Meta Facebook OAuth **PASS**，實曆 2026-05-20）  
> **規則**：勾選前須有證據（URL、status、截圖或紀錄一句）；與 **#11** 一致—不虛報。  
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
| 1 | 第 10 天 | Meta + 詳情 2.6 | **§H** 社交連線、**§C** 主題詳情 API |
| 2 | 第 11 天 | 詳情 RWD | **§C**、**§A** viewport |
| 3 | 第 12 天 | 頻道助手 42 點 | **§E** + 建立頻道清單 **I.1** |
| 4 | 第 13 天 | 靈感 28 點 | **§F** |
| 5 | 第 14 天 | 匯總 | 本表全區 **未完成項** 掃尾 + **§E** #32/#33 |

---

## §A — 全域與導覽（`App.tsx`／`Sidebar.tsx`）

**對齊架構表**：「前端路由結構」「Sidebar 導航」。

| # | 項目 | 驗證方式（摘要） | 結果 | 證據／備註 |
|:-:|------|------------------|:----:|------------|
| A1 | 已登入時 `/` 導向預期（如 `/topics`） | 手動／Network | [ ] | |
| A2 | Sidebar 每一 `path` 可進入、與路由一致 | 逐項點擊 | [ ] | 對照架構表路徑表 |
| A3 | 語言切換後導覽標籤仍正確（i18n） | Header 語言 | [ ] | |
| A4 | `data-testid`：側邊欄至少抽樣 2 連結 | DevTools | [ ] | 見 `按鈕測試ID架構表.md` |

---

## §B — 認證與帳號（`auth` API／登入註冊流程）

**對齊架構表**：「認證流程」、`api/v1/auth.py`、`middleware/jwt_auth`。

| # | 項目 | 驗證方式 | 結果 | 證據／備註 |
|:-:|------|----------|:----:|------------|
| B1 | Google 登入成功 → 進入主功能 | 手動 | [ ] | |
| B2 | Email 登入／註冊（若啟用） | 手動 | [ ] | |
| B3 | 無效 token 或過期 → 導回登入或錯誤提示 | 可選 | [ ] | |
| B4 | `PATCH /profile` 或同等更新個人資料 | Network | [ ] | 對照架構表 auth |

---

## §C — 主題列表與詳情（`topics`／`contents`／`images`）

**對齊架構表**：「主題卡生成」「Topic 模型」、路由 `/topics`、`/topics/:id`。

| # | 項目 | 驗證方式 | 結果 | 證據／備註 |
|:-:|------|----------|:----:|------------|
| C1 | `/topics` 列表載入、分類 Tab／無限滾動 | 手動 | [ ] | 可對照 v4 Phase 1 TC |
| C2 | **詳情 2.6**：固定 `topic_id` 開 `/topics/:id`，觸發 1～2 個後端操作 | Network 記 status | [ ] | 對齊 AGENTS 第 1 天腳本 |
| C3 | `contents` 無資料時非 500（預期 404） | Network | [ ] | |
| C4 | 圖片區／預覽（若有）無阻擋錯誤 | 目視 + Console | [ ] | |
| C5 | **RWD 375px**：詳情頁無橫向捲動、主按鈕可點 | DevTools | [ ] | 對齊 AGENTS 第 11 天 |

---

## §D — 我的頻道列表與維護（非建立頁）

**對齊架構表**：`/channels`、`channels.py` 更新／刪除；**清單 H** 已盤點 API，本表補 **UI 行為**。

| # | 項目 | 驗證方式 | 結果 | 證據／備註 |
|:-:|------|----------|:----:|------------|
| D1 | `/channels` 列表與後端一致 | 手動 | [ ] | |
| D2 | 編輯頻道（若有 UI）儲存成功 | Network | [ ] | |
| D3 | 刪除頻道（若有）列表同步、無幽靈項 | 手動 | [ ] | 對齊清單 **H** |
| D4 | 與 **§E** 新建頻道後列表出現新項目 | 端到端 | [ ] | |

---

## §E — 建立頻道 `/channels/create`（交叉引用）

**對齊架構表**：「建立頻道 Step 2／RSS」①～⑤。

| # | 項目 | 驗證方式 | 結果 | 證據／備註 |
|:-:|------|----------|:----:|------------|
| E1 | **助手主導** Phase B～D | 逐項 | [ ] | **[channel_create_new_scheme_checklist.md](./channel_create_new_scheme_checklist.md)** |
| E2 | **I.1～I.3**（E2E、無障礙、429、離線…） | 測試週 | [ ] | 同檔 **I 節** |
| E3 | **#32/#33** 建議名稱／描述 → 套用 | 手動 | [ ] | `btn-channels-assist-apply-naming` |
| E4 | **D.1** 表單主路（關閉助手後仍可建立） | 手動 | [ ] | 建立頻道清單 **D.1** |

---

## §F — 靈感策劃 v5.0（`Inspiration.tsx`／`inspiration.py`）

**對齊架構表**：「v5.0 靈感策劃 AI 助手架構」、集合 `inspiration_sessions` 等。

| # | 項目 | 驗證方式 | 結果 | 證據／備註 |
|:-:|------|----------|:----:|------------|
| F1 | `/inspiration` 進頁、模式切換（搜尋／助手） | 手動 | [ ] | |
| F2 | 開始對話 → 問題顯示 → 回答流程 | 手動 | [ ] | 對照架構表流程圖 |
| F3 | 生成內容：驗證狀態／來源連結可讀 | 手動 | [ ] | |
| F4 | 成本／偏好 API（若暴露於 UI）無 500 | Network | [ ] | |
| F5 | 28 點清單（專案既有）逐項結果 | 文件 | [ ] | 對齊 `工作記錄` 靈感測試段 |

---

## §G — 風格檔案、評分、內容面板（Phase 4 一線）

**對齊架構表**：`StyleProfile`、`RatingPanel`、`ContentGenerationPanel`、對應 API。

| # | 項目 | 驗證方式 | 結果 | 證據／備註 |
|:-:|------|----------|:----:|------------|
| G1 | `/style-profile` 載入與儲存 | 手動 | [ ] | |
| G2 | 主題詳情或內容區 **評分** 👍／👎 | 手動 | [ ] | |
| G3 | 內容生成面板：語言／風格選項與請求 | Network | [ ] | |

---

## §H — 發布與社交連線（`Publish`／`SocialConnect`／`social.py`）

**對齊架構表**：`/publish`、`/social-connect`、`distribution_service`、集合 `social_connections`。

| # | 項目 | 驗證方式 | 結果 | 證據／備註 |
|:-:|------|----------|:----:|------------|
| H1 | `/social-connect` 取得 `oauth_url`（Meta） | Network | [x] | **2026-05-20 PASS**：`GET …/meta/connect?target=facebook` → 200；scope 無 `instagram_basic`；`check_meta_config.py` OK |
| H2 | 可進入供應商授權頁（環境允許時） | 手動 | [x] | **2026-05-20 PASS**：Facebook dialog「Adam Au 已與 Influencers AI Agents 連結」 |
| H3 | `/publish` 導流與錯誤顯示（i18n） | 手動 | [ ] | |
| H4 | 回呼／token 儲存失敗時使用者可理解 | 可選 | [ ] | |

---

## §I — 偏好、排程、設定

**對齊架構表**：`/preferences`、`/schedule`、`/settings`。

| # | 項目 | 驗證方式 | 結果 | 證據／備註 |
|:-:|------|----------|:----:|------------|
| I1 | `/preferences` 可開、儲存不報錯 | 手動 | [ ] | |
| I2 | `/schedule` 列表或操作（依現行 MVP） | 手動 | [ ] | |
| I3 | `/settings` 基本項可及 | 手動 | [ ] | |

---

## §J — 後端橫向與維運（非單頁功能）

**對齊架構表**：`feeds` 健康、`automation` 排程、`middleware`。

| # | 項目 | 驗證方式 | 結果 | 證據／備註 |
|:-:|------|----------|:----:|------------|
| J1 | `GET /health`（或專案約定健康端點） | curl／瀏覽器 | [ ] | |
| J2 | RSS 健康／管理 API（若 QA 有權限）抽樣 | API | [ ] | v4 Phase 1.3 |
| J3 | 全站 rate limit／CSRF：不誤擋主流程 | 可選 | [ ] | 對齊架構表 middleware |
| J4 | **收集排程**（6h／清理）：staging／日誌知情即可 | 文件／日誌 | [ ] | 非必手動 |

---

## §K — MongoDB 集合煙霧對照（架構表「資料庫集合」）

**說明**：下列為「功能用到時資料一致」之 **抽樣**；不必逐集合寫入測試，除非當日劇本觸及。

| 集合 | 本週建議觸發劇本 | 已查／備註 |
|------|------------------|------------|
| `users` | 登入／註冊 | [ ] | |
| `topics` / `contents` / `images` | §C 詳情 | [ ] | |
| `channels` | §D、§E | [ ] | |
| `ratings` | §G2 | [ ] | |
| `style_profiles` | §G1 | [ ] | |
| `social_connections` | §H | [x] | **2026-05-20**：Facebook **@Adam Au** 已連接（`/social-connect?success=true`） |
| `schedules` | §I2 | [ ] | |
| `feed_health` | §J2 | [ ] | |
| `inspiration_sessions` / `user_inspiration_preferences` / `cost_records` | §F | [ ] | |

---

## 測試週收尾（第 14 天可貼入 `工作記錄.md`）

- **本表未完成列數**：___  
- **建立頻道清單 I 節未完成列數**：___  
- **下一輪修復（P0）**：___  

---

**維護**：架構表大改路由或新增頁面時，同步增刪本表 § 與列；建立頻道行為變更以 **channel_create_new_scheme_checklist.md** 為先。
