# 測試週架構缺口收口計劃（2026-05-12 起）

> **用途**：將複核所見 **12 項「架構／驗證尚未完善」** 對應到 **可執行工單**（含建議日、優先級、完成定義），與 **`AGENTS.md` 第 10～14 工作天** 並行；**不取代** [channel_create_new_scheme_checklist.md](./channel_create_new_scheme_checklist.md) **I 節** 與 [architecture_test_matrix.md](./architecture_test_matrix.md) 逐列勾選。  
> **建立**：2026-05-09  
> **最後修訂**：2026-05-21 — **#3** Meta PASS（2026-05-20）；**#7** 建立→列表 PASS（2026-05-21）；**#8** 詳情 **22/35** 已更新。  
> **規則**：勾選須附證據（URL／status／截圖／一句結論）；禁止虛報 **PASS**。  
> **每日可勾清單（已排好第 10～14 天）** → **[test_week_daily_checklist.md](./test_week_daily_checklist.md)**

### 測試週前記錄（非 #1～#12 收口項）

- **2026-05-09**：文件快照 `docs/backups/2026-05-09_test_week_docs_snapshot`；`frontend` **`npm run build`** 通過 — 詳 **`工作記錄.md`（2026-05-09 補）**、[channel_create_new_scheme_checklist.md](./channel_create_new_scheme_checklist.md) **I.0**、[test_week_daily_checklist.md](./test_week_daily_checklist.md) **測試週前已完成**。
- **2026-05-20**：**#3 Meta #39** 瀏覽器完整授權回呼 **PASS**（Facebook、`target=facebook`）；**PR #14** 合併 **`main`**（`51ba68c`）。Instagram 另流程。
- **2026-05-21**：**T-10 詳情 2.6 PASS**；**T-11 2.7 RWD PASS**（**22/35**）；**#7** 建立頻道 **親切香港美食** 列表可見；**I.1 E2E** 煙霧 PASS；**T-12** 頻道 **31/42**（與 E2E 併記，主線區塊 PASS）。

---

## 本機檢測週預設：3000（前端）與 8000（後端）

| 項目 | 預設值 | 依據／備註 |
|------|--------|------------|
| **前端開發伺服器** | **`http://localhost:3000`** | `frontend/vite.config.ts` 已設定 **`server.port: 3000`**（非 Vite 預設 5173） |
| **後端 API** | **`http://localhost:8000`** | `backend/.env.example` **`PORT=8000`**；啟動例見 `README.md` |
| **前端 → API Base** | **`http://localhost:8000/api/v1`** | `frontend/.env.example` **`VITE_API_URL`**；未設時程式碼同預設 |
| **OpenAPI** | **`http://localhost:8000/docs`** | 手動／契約驗證用 |
| **健康檢查** | **`http://localhost:8000/health`** 或 **`http://localhost:8000/api/v1/health`** | 根路徑與 v1 路由並存；詳細版 **`/api/v1/health/detailed`** |
| **CORS** | 後端須允許 **`http://localhost:3000`** | `backend/.env.example` **`CORS_ORIGINS`** 已含 `3000`（及歷史用的 `5173`） |
| **Meta OAuth 開發** | **`BACKEND_URL=http://localhost:8000`** | 回呼路徑 `…/api/v1/social/meta/callback`；ngrok 時見 `NGROK_SETUP.md` |

**檢測週開跑前**：兩埠皆可連（瀏覽器開 **3000**、`/docs` 或 health 開 **8000**）；若前端改埠，須同步 **CORS** 與 **`.env`**。舊文件若仍寫「僅 5173」，**以本 repo `vite.config.ts` 3000 為準**。

---

## 一週總覽（建議對照）

| 建議日（AGENTS） | 主線 | 本檔優先收口項（見下表 #） |
|------------------|------|---------------------------|
| **第 10 天** 2026-05-12 | Meta + 詳情 2.6 | **#3**、**#8**（詳情）、**#4**（Redis 可選 smoke）、**#12**（SoT 抽樣起頭） |
| **第 11 天** 2026-05-13 | 詳情 RWD | **#8**、**architecture_test_matrix §A／§C** |
| **第 12 天** 2026-05-14 | 頻道助手 42 點 | **#1**（I.1 與建立頻道 E2E／429／效能）、**#7** |
| **第 13 天** 2026-05-15 | 靈感 28 點 | **#8**、**architecture_test_matrix §F** |
| **第 14 天** 2026-05-21 | 匯總 | **#1**（I.1／I.2 剩餘）、**#2**（矩陣掃尾）、**#9**、**#10**、**#11**、**#12**（全文對照簽核） |

---

## 缺口收口表（12 項）

**欄位**：`[ ]` 於測試週由執行人勾選；**證據**填連結或 `工作記錄` 錨點。

| # | 缺口摘要 | P | 建議執行日 | 對照文件／段落 | 完成定義（DoD） | 證據 |
|---|----------|---|------------|----------------|-----------------|------|
| 1 | 建立頻道 **I.1／I.2** 未執行（E2E、a11y、三語全流、429、離線、效能；開關／放量／回滾） | P0 | 第 12～14 天 | [channel_create_new_scheme_checklist.md](./channel_create_new_scheme_checklist.md) **I.1、I.2** | 各列改 `[x]` 或明確 **N/A+理由**；I.2 若本輪不開 feature flag，於 `工作記錄` 寫「採固定 UI、無 env 開關」並產品簽名 | [ ] |
| 2 | **architecture_test_matrix** 全表未簽 | P0 | 第 10～14 天（按 § 拆） | [architecture_test_matrix.md](./architecture_test_matrix.md) **§A～§K** | 每節至少 **煙霧** 跑過一輪；**結果**欄由 `[ ]` 改 `[x]` 並填備註 | [ ] |
| 3 | **Meta #39** 瀏覽器完整授權回呼未結案 | P0 | 第 10 天（**實曆 2026-05-20**） | **§H**、`backend/check_meta_config.py`、AGENTS 第 6 天 | 記錄 **進入授權頁** 與 **callback 結果**（成功／error_code／BLOCK 原因） | [x] **PASS 2026-05-20**：授權頁 OK；`/social-connect?success=true`；**@Adam Au** 已連接；scope 僅粉專權限 |
| 4 | **Redis** 多實例限流／生產 key 未驗 | P1 | 第 10 或 12 天 | `工作記錄` Redis 列案、`docker-compose` redis | **Staging 或本機**：啟 Redis 後重複觸發 validate／search 限流，確認 **429** 與 **detail.code**；無 Redis 則記 **「僅驗記憶體回退」** | [ ] |
| 5 | **feeds/search** 僅白名單、**外部搜尋**未做 | — | 本輪 | [專案完整架構表.md](../專案完整架構表.md) **④** | **文件收口**：在 `工作記錄` 標 **「願景項／下輪」**；**不列為本測試週 PASS 條件** | [ ] |
| 6 | **L5 草稿 API／channel_drafts** 未交付 | — | 本輪 | 清單 **E** **➖** | 確認維持 **N/A**；無需執行測試，僅 **產品／文件** 重申範圍 | [ ] |
| 7 | 頻道 **UI CRUD／幽靈資料** E2E 未封口 | P0 | 第 12～14 天 | 清單 **H**、matrix **§D** | 建立 → 列表可見 → 編輯／刪除（若有 UI）後列表一致；或 **BLOCK** 建 issue | [x] **PASS 2026-05-21**：助手主路建立 **親切香港美食**；`/channels` 列表可見（**I.1**）；編輯／刪除迴歸待 T-14 |
| 8 | 主線通過率未滿（詳情／頻道助手／靈感） | P0 | 第 10～13 天 | `工作記錄` 頂部統計 | 更新 **分數+分母** 與日期；未測項 **≤3** 須註原因（對齊 AGENTS） | [x] **部分 2026-05-21**：詳情 **22/35**；頻道 **31/42**；靈感 **24/28**—T-13 續更新 |
| 9 | **v4.0.0_Checklist** 剩餘 QA／DOC | P1 | 第 14 天 | [v4.0.0_Checklist_TestList.md](../v4.0.0_Checklist_TestList.md) | 掃 **與本版本相關** 之未勾列，能勾則勾；其餘 **延後** 並寫一句 | [ ] |
| 10 | **README** 與 **工作記錄** 日期不同步 | P1 | 第 14 天 | [README.md](../README.md) 頂部 | 「更新日期／最後更新」與 `工作記錄.md` **最後更新** 對齊（或註「以工作記錄為準」並更新表內日期） | [ ] |
| 11 | **助手優先** 無 **feature flag** 矩陣 | P1 | 第 14 天 | 清單 **I.2**、清單 **G** | **二選一**：(a) 補 **環境變數／開關** 設計稿 + 預設表；(b) 文件宣告 **固定 `showAssist` 預設 true**、本輪不開關，**I.2** 標 **N/A+簽名** | [ ] |
| 12 | **規格全文對照（SoT）** 未做一次簽核 | P1 | 第 14 天 | 清單 **I.3**、`channel_create_ai_guided_spec`、願景、`專案完整架構表` **⑤** | 產出 **一段話**：三檔與實裝 **無矛盾** 或列出 **漂移項+負責人** | [ ] |

---

## 與兩份主清單的關係（勿重複造輪子）

- **建立頻道細項**：仍以 **[channel_create_new_scheme_checklist.md](./channel_create_new_scheme_checklist.md)** **I.1～I.2** 為 **SoT**；本檔 **#1** 只負責 **排程與 DoD 一句話**。  
- **全站路由／模組**：仍以 **[architecture_test_matrix.md](./architecture_test_matrix.md)** 為 **SoT**；本檔 **#2** 負責 **分段排程**。  
- **本檔**：給 PM／QA **一頁**看清「架構複核剩餘 12 類」如何塞進 **五天測試週**。

---

## 第 14 天匯總模板（貼 `工作記錄.md`）

```text
【測試週收口 2026-05-12～05-21】
- test_week_gap_closure_plan：12 項中已收口 ___ 項；N/A ___ 項；延後 ___ 項。
- channel_create I.1/I.2：…
- architecture_test_matrix：§A-K 完成度 …
- 下一輪 P0：…
```

---

**維護**：若 AGENTS 日曆再調整，僅改「一週總覽」表之日期列；缺口表 **#** 維持穩定以利跨年比對。
