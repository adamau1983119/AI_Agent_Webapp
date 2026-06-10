# v7 監控與紀律 — Checklist（CTO 鎖定 · 2026-06-05）

> **本檔 = 監察專用可勾選清單**（`[ ]`／`[x]` PASS／`[!]` FAIL）。  
> **Token 全線 Phase 0～4** → [`v7_token_cost_phase_checklist.md`](./v7_token_cost_phase_checklist.md)（含 **P0-06／P0-07** 與 **E0**、**C0～C4**）。  
> **截圖怎麼拍** → [`v7_evidence_screenshot_guide.md`](./v7_evidence_screenshot_guide.md)。  
> **監察週每日 45′（VM-1～4 · 2026-06-09～12）** → [`v7_monitoring_week_daily_checklist.md`](./v7_monitoring_week_daily_checklist.md)。  
> **觸發** → [`AGENTS.md`](../AGENTS.md)「專案開始（v7）」。  
> **實作基礎守則（i18n／按鈕 testid）** → [`v7_implementation_basics.md`](./v7_implementation_basics.md)（本檔僅後端監控時 **BF-UI-*** 可 ➖）。

---

## 勾選符號（與主 checklist 相同）

| 符號 | 意義 |
|:----:|------|
| `[ ]` | 未驗證 |
| `[x]` | PASS（√）；**須有證據** |
| `[!]` | FAIL（×）；寫原因 |

**證據欄必填**：`證據：截圖 <檔名> — …` 或 `證據：PR #… 行數 …`；**MD-M3** 類不得僅貼終端 log 取代瀏覽器截圖。

---

## 對照表（本檔 ↔ 主 checklist）

| 本檔 | 主 checklist [`v7_token_cost_phase_checklist.md`](./v7_token_cost_phase_checklist.md) |
|------|----------------------------------------------------------------------------------------|
| **MD-E0-*** | **E0-B、E0-F、E0-N**（每日開工） |
| **MD-M1-*** | **P0-06**（Loguru / `log_cost_event`） |
| **MD-M2-*** | **P0-07**（新檔 ≤150 行） |
| **MD-M3-*** | 頂部「截圖政策」+ 各 Phase **C*-* ** |

---

## 每日開工 — 環境與監察前置（MD-E0）

> 未完成 **MD-E0-B、MD-E0-F** 前，勿勾 **MD-M1** 中依賴本機服務的項。  
> 詳細拍攝方式 → [`v7_evidence_screenshot_guide.md`](./v7_evidence_screenshot_guide.md) §2。

- [ ] **MD-E0-B** 後端 `http://localhost:8000/health` 整段 JSON（含 `cost_controls`）  
  - 驗證：瀏覽器可開；欄位與 `.env` 一致  
  - 證據：截圖 `YYYY-MM-DD_v7_E0-B_….png` —
- [ ] **MD-E0-F** 前端 `http://localhost:3000` 已登入 P0 頁；Console 無未處理紅錯  
  - 證據：截圖 `YYYY-MM-DD_v7_E0-F_….png` —
- [ ] **MD-E0-N** DevTools → Network → **Fetch/XHR** + **Preserve log**（可併入 E0-F）  
  - 證據：截圖或註明併入 E0-F —

**MD-E0 結案**：**MD-E0-B、MD-E0-F 必須 `[x]`**。

---

## M1 — Loguru only（拒絕 Pino）· 驗收清單

### 政策（不可改）

| 禁止 | 必須 |
|------|------|
| `pino`、`pino-pretty` | [`backend/app/utils/logger.py`](../backend/app/utils/logger.py) **Loguru** |
| `vercel dev` 作本機後端 | `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` |
| `/server/utils/logger.js` | 僅擴充 Python `logger.py` |

**官方 `tag`（僅准這五個字串作為 `log_cost_event` 的 `tag`）**

| tag | 用途 |
|-----|------|
| `SUMMARY_FLASH_SUCCESS` | Flash 寫入 `summary_flash` |
| `I18N_CACHE_HIT` | 快取命中 |
| `CACHE_MISS` | 快取未命中 |
| `TRANSLATION_FALLBACK_TRIGGERED` | DeepL Fallback |
| `TOKEN_GATEWAY_PASSED` | generate 通過 gateway |

**輸出格式（強制 · 內建 Key-Value 結構化）**

- 單行：`[{tag}] k1=v1 k2=v2`（空格分隔；**禁止**手拼 f-string／`str(dict)` 導致排版錯亂）。
- `log_cost_event` **內部**須將 `**fields` 轉為工整 `key=value`（建議：**key 排序**、`str(v)`）。
- 範例：`[SUMMARY_FLASH_SUCCESS] chars=245 topic_id=123`

**實作規格（Cursor · 防 async 陷阱）**

- 函數保持**同步**；在 `async def` 內直接呼叫，**函數內不 `await`、不做 I/O**。
- 可選 `level: str = "info"`，其餘一律 kwargs 進 `fields`。

```python
def log_cost_event(tag: str, level: str = "info", **fields) -> None:
    parts = [f"{k}={fields[k]}" for k in sorted(fields)]
    message = f"[{tag}] " + " ".join(parts)
    getattr(logger, level.lower(), logger.info)(message)
```

### M1 完成檢查清單（= 主檔 P0-06）

- [ ] **MD-M1-1** `requirements.txt`／環境**無**新增 `pino` 依賴  
  - 驗證：`grep -i pino backend/` 無新增  
  - 證據：
- [ ] **MD-M1-2** 已實作 **`log_cost_event`**（kwargs **內建**格式為 `key=value`）；`setup_logging` 仍 **`colorize=True`**  
  - 驗證：讀 `logger.py` 確認非呼叫端手拼字串；uvicorn 終端彩色  
  - 證據：可選終端截圖 `…_v7_MD-M1-2_….png` —
- [ ] **MD-M1-3** 手動或測試呼叫 `log_cost_event("SUMMARY_FLASH_SUCCESS", topic_id="t1", chars=245)` 終端出現 **`[SUMMARY_FLASH_SUCCESS]`** 且 **kwargs 工整為 `key=value`**  
  - 驗證：重啟 uvicorn 後執行；終端單行須類似 `[SUMMARY_FLASH_SUCCESS] chars=245 topic_id=t1`（**多個關鍵字參數**皆為 `key=value`，無逗號雜湊、無 dict 原樣噴出）  
  - 證據：終端截圖（**輔助**）—
- [ ] **MD-M1-4** 本機啟動指令**僅** `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`（文件／README 未改為 vercel dev）  
  - 證據：工作記錄或 README 一句 —
- [ ] **MD-M1-5** **MD-E0-B、MD-E0-F 已 `[x]`**（瀏覽器主證據齊全）  
  - 證據：檔名 —

**M1 結案判定**：**MD-M1-1、MD-M1-2、MD-M1-3、MD-M1-5 必須 `[x]`**。

---

## M2 — 新檔 ≤150 行 · 驗收清單

### 政策（不可改）

| 禁止 | 必須 |
|------|------|
| 全 repo 頂部 `// CRITICAL…150` 註解 | **v7 新建** `.py` **≤150 行** |
| 對 `scheduler.py` 等舊檔補註解 | 將超 150 行則**拆檔** |
| — | **PR 說明**列檔名 + 行數 |

**適用檔名（例）**：`summary_flash_service.py`、`deepl_provider.py`、`topic_translation_repository.py`、`token_gateway.py`。

### M2 完成檢查清單（= 主檔 P0-07）

- [ ] **MD-M2-1** 本 PR **無**任何 `.py` 頂部 `CRITICAL ENGINE`／`// CRITICAL` 類註解  
  - 驗證：`grep -r "CRITICAL ENGINE" backend/app` 無新增  
  - 證據：
- [ ] **MD-M2-2** 本 PR 新增之 v7 模組**每一檔** ≤150 行（`wc -l` 或 IDE 行數）  
  - 驗證：PR 說明列表：`<檔名> <N> 行`  
  - 證據：PR 連結或截圖 —
- [ ] **MD-M2-3** 若有檔 >150，已拆成獨立 helper／prompts 模組（非硬塞單檔）  
  - 證據：PR 說明 —

**M2 結案判定**：**MD-M2-1、MD-M2-2 必須 `[x]`**（每個含 v7 新檔的 PR 都要過）。

---

## M3 — 證據界線 · 驗收清單

### 政策（不可改）

| 類型 | 角色 |
|------|------|
| **:8000` Network / `:3000` UI 截圖** | **主證據** → 無則不得對應 **C*-* **`[x]`** |
| **終端 `[TAG]` 彩色 log** | **當日對照輔助** |

### M3 完成檢查清單（開發人員紀律 · 每個驗收日）

- [ ] **MD-M3-1** 已讀 [`v7_evidence_screenshot_guide.md`](./v7_evidence_screenshot_guide.md) 並建立 `docs/evidence/v7/YYYY-MM-DD/`（本機）  
  - 證據：資料夾存在或路徑一句 —
- [ ] **MD-M3-2** 今日勾選之 **C*-* / MD-*** 項，**每一項 `[x]` 皆有「截圖檔名」**（非僅終端 log）  
  - 驗證：對照主 checklist 證據欄  
  - 證據：工作記錄貼表 —
- [ ] **MD-M3-3** 未用「助手已測過」代替本人 **:8000 / :3000** 截圖  
  - 證據：自勾選 —

**M3 結案**：與 Phase 結案綁定；**MD-M3-2** 在貼 Phase 證據時必須 `[x]`。

---

## 總驗收（監察線 · 可選獨立勾）

- [x] **MD-ALL-1** M1～M3 各結案判定已滿足  
- [x] **MD-ALL-2** 主 checklist **P0-06、P0-07** 已改 `[x]`（與 MD-M1、MD-M2 同步）  
- [x] **MD-ALL-3** 證據已貼 `工作記錄.md` § v7 Token 開發核證（V7）或 Phase 結案段  

---

## 政策原文（助手參考 · 無需逐項勾）

<details>
<summary>M1～M3 敘述（展開）</summary>

**M1**：`log_cost_event` 唯一出口；**內建** kwargs→`[TAG] k=v`；同步、不 await；Loguru `colorize=True`。

**M2**：v7 新檔 ≤150；禁頂部 JS 風格註解；PR Review。

**M3**：終端輔、瀏覽器截圖主；見 evidence guide。

</details>

---

## 助手執行順序

1. 開發人員／編程：**先 MD-E0 → 再 MD-M1～M3**。  
2. **程式**：`log_cost_event`（MD-M1-2～3）→ 對照主 checklist **Phase 1+** 逐步接 tag。  
3. **禁止**：引入 pino；用終端 log 代勾 UI／Network 項。

---

## 版本

| 日期 | 說明 |
|------|------|
| 2026-06-05 | 初版：M1～M3 政策 |
| 2026-06-05 | **補齊本檔 Checklist**：MD-E0、MD-M1～M3、MD-ALL；對照主 checklist |
| 2026-06-05 | **VM 監察週**：06-09～12 四日表 → `v7_monitoring_week_daily_checklist.md`（使用者確認） |
