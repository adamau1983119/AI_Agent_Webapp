# v7 監察週 — 每日 Checklist（VM-1～VM-4）

> **排程**：**2026-06-09（二）～06-12（五）**；每天 **45′**（含記錄）。**06-06～08 週末／一不排**。  
> **確認日**：2026-06-05（使用者同意 VM 四日安排）。  
> **週目標**：監察線驗收結案 → **`工作記錄` V7-0 ☑**；**不開 Token Phase 1**。  
> **政策**：[`v7_dev_monitoring_discipline.md`](./v7_dev_monitoring_discipline.md)、[`v7_evidence_screenshot_guide.md`](./v7_evidence_screenshot_guide.md)、[`v7_token_cost_phase_checklist.md`](./v7_token_cost_phase_checklist.md)（E0、P0-06/07、C0-*）。  
> **日曆 SoT**：[AGENTS.md](../AGENTS.md)「下週日曆 VM-1～VM-4」。  
> **實作基礎守則**：[`v7_implementation_basics.md`](./v7_implementation_basics.md)（**BF-***；VM 週預設後端，動前端須 **BF-UI-***）。

---

## 邏輯（四日分工）

| 日 | 實作 vs 驗收 |
|----|----------------|
| **VM-1** | 僅證據與環境（**無** `log_cost_event` 程式） |
| **VM-2** | **實作** `log_cost_event` + **當日** MD-M1 自測結案 |
| **VM-3** | **局部驗收**：MD-M2 + C0-1/2 瀏覽器截圖 |
| **VM-4** | **總驗收**：MD-ALL + V7-0 ☑ |

**分支**：`feature/v7-cost-pipeline`（**VM-2** 起 commit；VM-1 可僅截圖）。

---

## 每日開工（VM 週每一天）

- [ ] **`專案開始` 前檢查**：已輸出 AGENTS **「專案開始前檢查 — 結果表」**（六必讀 + 啟動檢查）
- [ ] **BF-DAY-1**～**BF-DAY-3**（[`v7_implementation_basics.md`](./v7_implementation_basics.md)；**VM-2+** 後端為主時 **BF-UI-*** 標 ➖）
- [ ] 後端：`http://localhost:8000/health` 可開（當日若已拍 E0-B 可註明沿用）
- [ ] 前端：`http://localhost:3000` 可開
- [ ] 分支非 `main` 直改（建議 `feature/v7-cost-pipeline`）
- [ ] 記錄：日期、VM 代號、證據檔名
- [ ] **若當日改 `.tsx`**：README 規則 **6**（i18n 三語）+ **3／4**（`data-testid`、更新按鈕測試ID架構表）

---

## 2026-06-09（二）｜VM-1｜環境 + E0 + 證據目錄

| 分鐘 | 動作 | ☐ |
|:----:|------|:-:|
| 0～5′ | R Gate：`git branch`；`:8000/docs`、`:3000` **200** | ☐ |
| 5～25′ | 拍 **E0-B** `/health` 全 JSON；拍 **E0-F** 登入 P0 + Network Preserve | ☐ |
| 25～35′ | 建立 `docs/evidence/v7/2026-06-09/`；檔名依 evidence guide | ☐ |
| 35～40′ | 核對 `.env` 省 Token 組與 `cost_controls` 一致（不提交 `.env`） | ☐ |
| 40～45′ | `工作記錄`：E0 檔名 + 明日 **VM-2 log_cost_event** | ☐ |

**完成判定**：**MD-E0-B、MD-E0-F `[x]`**（各附截圖檔名）；**MD-M3-1 `[x]`**。

---

## 2026-06-10（三）｜VM-2｜`log_cost_event`（監察核心 · 實作日）

| 分鐘 | 動作 | ☐ |
|:----:|------|:-:|
| 0～5′ | E0-B 快查（環境未變可註明沿用日期） | ☐ |
| 5～25′ | `logger.py`：`log_cost_event` 同步、kwargs 排序 `key=value` | ☐ |
| 25～35′ | 無 pino；重啟 uvicorn；手測 `SUMMARY_FLASH_SUCCESS` 等多 kwargs | ☐ |
| 35～40′ | 終端截圖（輔助）；確認 E0-B/F 仍有效 | ☐ |
| 40～45′ | commit；主 checklist **P0-06** 證據欄 | ☐ |

**完成判定**：**MD-M1-1、M1-2、M1-3、M1-5 `[x]`**。

---

## 2026-06-11（四）｜VM-3｜MD-M2 + C0 契約（局部驗收）

| 分鐘 | 動作 | ☐ |
|:----:|------|:-:|
| 0～5′ | E0 快查 | ☐ |
| 5～15′ | PR：**無** `CRITICAL ENGINE`；列 `logger.py` 行數 ≤150 | ☐ |
| 15～30′ | 拍 `/health`：**C0-1** 排程關、**C0-2** 收集翻譯關 | ☐ |
| 30～38′ | **C0-3** env／config；**C0-4** 架構表 v7 D1～D5 | ☐ |
| 38～45′ | **MD-M3-2**：今日 `[x]` 項 + 檔名表 | ☐ |

**完成判定**：**MD-M2-1、M2-2 `[x]`**；**C0-1、C0-2、C0-4 `[x]`**（截圖或文件一句）。

---

## 2026-06-12（五）｜VM-4｜監察總驗收（硬截止）

| 分鐘 | 動作 | ☐ |
|:----:|------|:-:|
| 0～10′ | 複核 MD-M1～M3；**P0-06、P0-07 → `[x]`** | ☐ |
| 10～25′ | **C0-5** 基線（DeepSeek 或「無帳單」）；**P0-01** 可標 `[!]` 延後 | ☐ |
| 25～35′ | Phase 0：E0 + C0 **≥4 項 `[x]`** 且含 **C0-4** | ☐ |
| 35～40′ | `工作記錄` 「V7 證據表」；**V7-0 ☑** | ☐ |
| 40～45′ | 監察線結案一句；**下步：V7-1 Phase 1**（不本日開發） | ☐ |

**完成判定**：**MD-ALL-1～3 `[x]`**；**V7-0 ☑**。  
**禁止**：本日新開 `summary_flash`、排程大改（規則 #14）。

---

## 週末收尾模板（複用）

- 今日目標（VM-x）：
- 實際完成：
- 證據（截圖檔名／PR）：
- 明日第一步（一句）：

---

## 維護

日曆變更時：同步 [AGENTS.md](../AGENTS.md) VM 表、`工作記錄.md` **實曆填寫**、本檔日期列。
