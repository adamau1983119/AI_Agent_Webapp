# DeepSeek 費用調查（2026-05）— 根因與防護

> **建立**：2026-05-28  
> **狀態**：調查結案（文件）；**待執行**：API Key 輪換、`AUTO_START_SCHEDULER` 本機關閉  
> **證據檔**（使用者本機，勿提交 git）：`Desktop\cost-2026-5.csv`、`Desktop\amount-2026-5.csv`

---

## 1. 結論（一句）

**2026-05 帳單 ¥63.43** 主要來自 **`ai-agent-webapp-production` / `production 2` 兩把 API Key** 的 **`deepseek-v4-pro`** 大量呼叫；**不是** Railway `gentle-enchantment`（已 **offline／REMOVED 約 5 個月**）；**5/13 無消費**；**¥16 尖峰日為 5/3（非 5/13）**；**5/24（週日）仍有 552 次 API 請求**，多數為 **production 第一把 key**，本機 `.env` 僅綁 **production 2**。

---

## 2. 證據對照表

| 來源 | 內容 |
|------|------|
| `cost-2026-5.csv` | 帳號級日費用；全月 **¥63.43**；模型 **v4-pro／v4-flash**；**無 5/13**；**5/3 ¥16.30**、**5/24 ¥11.28** |
| `amount-2026-5.csv` | 分 Key 日用量；**v4-pro**；**5/3** 約 **1,779 request**；**5/24** **552 request**；**5/13 = 0** |
| Railway `gentle-enchantment` | **Trial expired**、**Service offline**、Deployments **REMOVED**、最後 deploy **~5 months ago** → **不解釋 2026-05 用量** |
| 本機 `backend/.env` | `AI_SERVICE=deepseek`；Key = **production 2**（`sk-c5be…`）；**無 `DEEPSEEK_MODEL`**（程式預設 `deepseek-chat`）；**`AUTO_START_SCHEDULER=true`** |
| 收口測試 W-2（5/27） | 僅 **73 request**／日 → **非月帳單主因** |

---

## 3. 尖峰日明細

| 日期（UTC） | 費用 (CNY) | production 請求數 | production 2 請求數 | 備註 |
|-------------|------------|-------------------|---------------------|------|
| **2026-05-03** | **16.30** | 1,138 | 638 | 全月最高；疑似批量／自動任務 |
| **2026-05-13** | **0** | 0 | 0 | AGENTS T-11 排程日≠帳單日 |
| **2026-05-24** | **11.28** | 469 | 83 | 週日；使用者稱未開電腦；**仍有 API 流量** |
| 2026-05-27 | ~0.68 | — | 73（flash） | W-2 手測量級 |

---

## 4. 根因假設（優先序）

| # | 假設 | 佐證 |
|---|------|------|
| 1 | **非 Railway 的程式** 使用兩把 production key（腳本、他機、舊環境） | Railway offline；amount 仍有數百～千次/日 |
| 2 | **本機曾開 `uvicorn` 且 `AUTO_START_SCHEDULER=true`** | 開發環境也會啟動排程；但本機 key 僅 **production 2** |
| 3 | **API Key 曾外洩**（截圖／對話）被第三方刷 | 5/24 週日無人仍可發生 |
| 4 | **計費模型顯示 v4-pro** vs 程式預設 `deepseek-chat` | 須輪換 key 後再驗 `model` 欄位 |

**已排除**：Railway production 服務在 **2026-05 仍在跑**（Deployments 顯示長期 REMOVED）。

---

## 5. 防護清單（測試期必做）

- [x] **DeepSeek**：作廢 `ai-agent-webapp-production`、`production 2`；新建 **僅本機測試** key（**2026-06-13**；尾碼 **ebe36**，勿 commit `.env`）  
- [x] **勿**將完整 `sk-…` 貼入對話／截圖（政策持續）  
- [x] 本機 `.env`（**2026-06-03 程式預設**）：`AUTO_START_SCHEDULER=false`、`ENABLE_SCHEDULED_TOPIC_COLLECTION=false`、`ENABLE_AI_TOPIC_TRANSLATION=false`、`ENABLE_AI_TOPIC_FALLBACK=false`  
- [x] **2026-06-03**：程式預設 **`DEEPSEEK_MODEL=deepseek-v4-flash`**（全功能統一 Flash）；`.env` 若仍寫 v3-pro 會覆寫預設，請改為 flash  
- [ ] DeepSeek 後台：每日預算／用量告警（**新 key** 須重設）  
- [x] 調查 **production 第一把 key** 6/6 尖峰 → 見 **§8**（本機後端常駐 + 排程全開 + V7-1 雙 Flash）  
- [x] 程式（2026-06-03）：`app/utils/cost_controls.py`；排程收集／`generate-today` 受 `ENABLE_SCHEDULED_TOPIC_COLLECTION` 控制；收集翻譯受 `ENABLE_AI_TOPIC_TRANSLATION` 控制  
- [x] 驗證：`GET /health` 回傳 `cost_controls` 皆為預期 false（**2026-06-13** 重驗）

---

## 6. 與本專案程式的關係

| 高風險路徑 | 說明 |
|------------|------|
| `POST /schedules/generate-today` | 30 主題 × 2 次 DeepSeek／輪 |
| `trigger_manual_generation` | `auto_generate_content=True` |
| `ensure_today_topics` | **僅 `ENVIRONMENT=production`** 啟動時自動補主題 |
| 排程每 6h 收集 | RSS 失敗時 AI 補標題（較輕） |
| 靈感／頻道 assist、詳情 regenerate | 手測量級（5/27 已證） |

---

## 7. 相關文件

- [`工作記錄.md`](../工作記錄.md)「DeepSeek 費用調查（2026-05）」＋ **6/6 尖峰（2026-06-13）**  
- [`docs/環境重建指南與Checklist.md`](./環境重建指南與Checklist.md)  
- [`docs/test_week_daily_checklist.md`](./test_week_daily_checklist.md)「測試期 DeepSeek」  
- [`docs/v7_token_cost_phase_checklist.md`](./v7_token_cost_phase_checklist.md) **雙軌驗收（A／U）**  
- 備份：`docs/backups/2026-05-28_deepseek-cost-investigation_snapshot/`、`docs/backups/2026-06-13_deepseek-key-rotation_snapshot/`

---

## 8. 附錄 — 2026-06-06 Flash 尖峰（結案 2026-06-13）

| 項目 | 數據 |
|------|------|
| 帳單 | Flash **¥62.68**；**18,016** 次；約 **7.3 億** tokens |
| 元兇 Key | **`ai-agent-webapp-production`**（`sk-9995d…`）約 **99%** |
| `wts-fortune-app-v30` | 6 月 CSV **0 筆**（非元兇） |

**根因鏈**：

1. **06-06 VM-1**：本機 `.env` 曾 **排程 + AI 翻譯全開**（`VM1_session_log.md`）。  
2. **同日 V7-1**：收集管線改為 **翻譯 Flash + `summary_flash` Flash**（雙呼叫）。  
3. **後端常駐**：uvicorn 持續跑 → 6h 收集／翻譯累積。

**處置**：刪除兩把 production key；新 dev key（尾碼 **ebe36**）；`cost_controls` 六開關維持 **false**；助手 **A 軌** 禁止 `generate-today`／大量 `collect`（見 `A-track_agent_session_log.md`）。
