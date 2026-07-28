# DeepSeek Key 輪換 + 雙軌驗收 — 2026-06-11

> **分支**：`feature/v7-cost-pipeline`  
> **不含**：完整 `sk-…`（僅尾碼稽核）

---

## 6/6 帳單根因（CSV 核對）

| 來源 | 6/6 Flash |
|------|-----------|
| `ai-agent-webapp-production`（`sk-9995d…`） | **17,828** 次、~7.16 億 tokens、**主因 ¥62.68** |
| `ai-agent-webapp-production 2`（`sk-c5be0…`） | 188 次 |
| `wts-fortune-app-v30` | **0**（6 月 CSV 無列） |

**程式根因（6/6）**：VM-1 啟動時 `.env` 排程＋AI 翻譯 **全開**；同日 V7-1 落地 **雙 Flash**（翻譯 + `summary_flash`）。見 `VM1_session_log.md`。

---

## Key 輪換（使用者操作）

| 步驟 | 狀態 |
|------|------|
| 刪除 `ai-agent-webapp-production`／`production 2` | ✅ |
| 新建 dev key（尾碼 **ebe36**） | ✅ |
| 更新 `backend/.env` + Ctrl+S | ✅ |
| 重啟 uvicorn；runtime 尾碼 `ebe36` | ✅ |
| `/health` cost_controls 全 false | ✅ |
| DeepSeek 每日預算告警 | ⏳ 使用者後台 |

**保留**：`wts-fortune-app-v30`（另一專案；與 6/6 尖峰無關）。

---

## 雙軌驗收（決策 2026-06-10）

| 軌 | 負責 | 內容 |
|----|------|------|
| **A 軌** | 助手 | `/health`、build、靜態 grep、curl（**不** collect／generate-today） |
| **U 軌** | 用家 | 登入驗證 ~20～30′（5 步） |

證據 A 軌：`docs/evidence/v7/2026-06-10/A-track_agent_session_log.md`、本日重跑 `A-track_agent_session_log.md`

---

## 待辦（不變）

- ✅ `feature/v7-cost-pipeline` **commit** `bebf6d0`（排除 `.env`）
- ⏳ 測試段 **整批測試週**（C*／CD*；U 軌 E2E可併任一日）
