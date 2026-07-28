# v7 本機驗證 — 截圖證據指南（:8000 / :3000）

> **政策（不變）**：凡在 **`http://localhost:8000`**、**`http://localhost:3000`** 上確認 checklist 是否 PASS，**必須以截圖為證**；助手／編程人員**不得**僅憑口頭、log 複製或「應該可以」勾 `[x]`。  
> **對照**：[`v7_token_cost_phase_checklist.md`](./v7_token_cost_phase_checklist.md)、[`v7_implementation_basics.md`](./v7_implementation_basics.md)（**BF-UI** 與 Phase 4／Discover）、[`工作記錄.md`](../工作記錄.md) 「v7 Token 開發核證（V7）」、[`AGENTS.md`](../AGENTS.md)「專案開始（v7）」。

---

## 1. 為何需要本指南

編程人員在 **8000（後端）** 與 **3000（前端）** 上要對照 checklist 時，常遇到：

- API 結果只在 Network／終端機，難對照 **C*-* 編號**
- 重啟後端前後 **`/health`** 不一致，無留存
- 多語／翻譯／生成要 **同一 session** 才省時間

本指南固定：**怎麼開環境 → 拍什麼 → 檔名怎麼寫 → 貼去哪**。

---

## 2. 固定環境（每次驗收 session 開工）

| 步驟 | URL／指令 | 必截圖代號 | 截圖須含 |
|------|-----------|------------|----------|
| 1 | `http://localhost:8000/health` | **E0-B** | 整段 JSON；**`cost_controls`** 可讀 |
| 2 | `http://localhost:8000/docs` 或首屏 200 | **E0-B2** | 瀏覽器網址列 + Swagger 標題（可與 E0-B 合併一張） |
| 3 | `http://localhost:3000` 登入後任一 P0 頁（如 `/dashboard`） | **E0-F** | 網址列 + 頂部列；Console **無未處理紅錯**（可同圖小窗 Console） |
| 4 | DevTools → **Network → Fetch/XHR**，勾 **Preserve log** | — | 後續操作均保留 |

**E0 未 `[x]` 前**：checklist 內 **C1-*～C4-*** 的 UI／API 驗收**一律不勾**。

---

## 3. 截圖檔名規則（強制）

```text
YYYY-MM-DD_v7_<檢查項代號>_<簡述>.png
```

範例：

- `2026-06-05_v7_E0-B_health_cost_controls.png`
- `2026-06-05_v7_C1-2_collect_summary_flash_network.png`
- `2026-06-05_v7_C3-9_generate_after_gateway.png`

**建議存放**（本機，**勿提交**含 token／密鑰原圖至 git）：

```text
docs/evidence/v7/YYYY-MM-DD/
```

於 `.gitignore` 可忽略 `docs/evidence/`（若含敏感資訊）。**工作記錄**只貼**相對路徑 + 一句話**，不貼完整 JWT。

---

## 4. checklist「證據」欄必填格式

每個改為 `[x]` 的 **C*-* ** 在 checklist 或 `工作記錄` 須有：

```text
證據：截圖 <檔名> — <一句話：看見什麼>
```

可選補充（**不能取代截圖**）：`commit`、`curl` 狀態碼、DeepSeek 後台日期。

**終端彩色日誌（輔助）**：`uvicorn` 視窗可截 **`[SUMMARY_FLASH_SUCCESS]`**、**`[TOKEN_GATEWAY_PASSED]`** 等（見 Loguru 本機設定）；**仍須**瀏覽器／Network 截圖對照 **C*-***，不可只用終端代勾 UI／API 項。

**FAIL `[!]`** 也須截圖（錯誤畫面／Network 紅字／timeout）。

---

## 5. 檢查項 → 建議截圖內容（:8000 / :3000）

> **原則**：能在瀏覽器看到的，用**瀏覽器整屏或 Network 面板**；僅 CLI 的用**終端機視窗**（仍算截圖證據）。

### Phase 0

| 代號 | 建議截圖 |
|------|----------|
| C0-1、C0-2 | **E0-B**：`/health` 內 `cost_controls` 各開關為 false／預期值 |
| C0-3 | **終端**或文字編輯器：`.env` 片段（**馬賽克** API key）顯示 FLASH/PRO 分離 |
| C0-4 | 開著 **`專案完整架構表_v7.md`** D1～D5 的編輯器視窗（文件驗收） |
| C0-5 | DeepSeek 後台統計頁（可非 localhost） |

### Phase 1

| 代號 | 建議截圖 |
|------|----------|
| C1-2 | **Network**：`POST .../channels/.../collect` **200** + 回應摘要；可另附 Mongo Compass `summary_flash` 欄位 |
| C1-4 | **Network**：`POST .../generate` 請求 payload **無** 長 HTML；或後端 log 視窗（終端截圖） |
| C1-5 | 生成成功回應 JSON 含 **`model_used`** 為 pro；或 DeepSeek 後台該次為 Pro |
| C1-7 | DeepSeek 後台「次數」對照（收集前後） |

### Phase 2

| 代號 | 建議截圖 |
|------|----------|
| C2-3 | **Network**：`translate-display` **200** + Response 譯文；日誌 `[I18N_CACHE_HIT]`（終端截圖） |
| C2-4 | 同上路徑 **CACHE_MISS** 後第二次命中 |
| C2-5 | Response body 含 **`[Fallback-JA]`** 或 **`[Fallback-EN]`** |
| C2-6、C2-7 | 終端 scheduler log 或手動觸發 job 輸出（**無** kol_style 字樣） |

### Phase 3

| 代號 | 建議截圖 |
|------|----------|
| C3-1 | **Network**：超大 body 被拒 **400/413** 或 gateway 剝除後仍 **200** |
| C3-2 | 終端 log **`[TOKEN_GATEWAY_PASSED]`** |
| C3-3 | 無 `summary_flash` 時 UI／API **錯誤訊息**；成功時產文與 DB 一致（對照 Compass + 產文預覽） |
| C3-9 | **同一 curl／UI generate**：掛 middleware 前後 **皆 200**（兩張或標註前後） |

### Discover（PF-3／PF-4／PF-B）

| 代號 | 建議截圖 |
|------|----------|
| E0-PF | **`:3000/discover`** 首屏 + Network **僅** `GET …/public/topics/feed` **200** |
| CD-3-1 | Postman 或瀏覽器：`feed?lang=zh-TW` JSON ≥1 卡 |
| CD-3-2 | Redis 停用後同一 feed 仍 **200** |
| CD-4-1 | `/discover` ≥1 張卡可讀 |
| CD-4-2 | Network：**無** `assist`／`generate`／`translate-display`／DeepL 網域 |
| **E0-Discover-i18n** | **前置 PF-B**；zh-TW／ja；Network 翻譯 API **= 0** |
| **E0-MC** | MyChannel：feed 免費層 + unlock 1 點 + URL 可點 — 見 [`v7_mychannel_checklist.md`](./v7_mychannel_checklist.md) |
| CD-B-2 | 併入 **E0-Discover-i18n**（港日同質結案必備） |

### Phase 4

| 代號 | 建議截圖 |
|------|----------|
| C4-1 | **375px** DevTools：`/topics` 切語系 **skeleton → 譯文**（可短錄影改為連拍 2 張） |
| C4-2 | **Network**：第二次切語系 **無** DeepL 請求 |
| C4-3 | 僅點「網紅風格」後出現 Flash 相關請求 |
| C4-4 | 終端 **`npm run build` exit 0** 最後幾行 |

---

## 6. 批次截圖（一 session 多項，沿用 v6 做法）

| 批次 | 一次操作 | 可勾選（須同圖可辨識） |
|------|----------|------------------------|
| **B-E0** | 開 `:8000/health` + `:3000` 首頁 | E0-B、E0-F |
| **B-TOPIC** | `/topics` 列表 + 切 **ja** + Network | C4-1、C4-2（Phase 4） |
| **B-GEN** | 詳情頁按生成 + Network payload | C1-4、C1-5、C3-2（若 Phase 3 已上線） |

檔名可用 **`2026-06-05_v7_B-TOPIC_topics_ja_network.png`**，在證據句列出涵蓋的 **C*-* 編號**。

---

## 7. 禁止與安全

- **禁止**：無截圖勾 `[x]`；用助手對話代替本機畫面；同一張圖分日重複勾不同日期（須註明 **複核 PASS + 日期**）。
- 截圖須**馬賽克**：`sk-…`、`Bearer eyJ…`、`.env` 密碼、他人個資。
- **Mongo Atlas**、**DeepSeek** 後台截圖允許，但帳號資訊請打碼。

---

## 8. 與 R+T 的關係

| 體系 | 證據 |
|------|------|
| **R-2～R-3**（重建） | 仍可用 **:8000/docs**、**:3000** 截圖（與 v6 相同） |
| **T-10～T-14**（v6 封存） | 沿用 [`test_week_daily_checklist.md`](./test_week_daily_checklist.md) **批次↔截圖** |
| **V7-0～V7-4** | **本檔 + v7 checklist**；**截圖政策相同，不變** |

---

## 版本

| 日期 | 說明 |
|------|------|
| 2026-06-05 | 初版：v7 本機 :8000/:3000 截圖證據強制政策與 C* 對照表 |
| 2026-06-11 | 增 Discover／E0-Discover-i18n（PF-B 硬門檻）／PF-S mock 截圖對照 |
| 2026-06-11 | CD-H-4：須重啟 uvicorn 後 `/health` 含 `safe_batch_size` |
