# v7 程式段專區 — 進入閘門（每次 `專案開始` 必讀）

> **位置**：[`docs/v7_program_line/`](./)  
> **未讀本檔** → **禁止**修改 `active/` 內 checklist、**禁止**宣稱 Phase 結案。

---

## 1. 目錄規則

| 目錄 | 用途 |
|------|------|
| [`index.md`](./index.md) | **總表 SoT**：排程、Active / Completed、證據一行 |
| [`active/`](./active/) | **進行中** Phase checklist（助手改碼日只動這裡 + 程式） |
| [`_completed/`](./_completed/) | **程式段已結案**（含 Token）；**不移出**本專區樹 |
| [`_TEMPLATE.md`](./_TEMPLATE.md) | `active/` 新 Phase 統一骨架 |

**封存**：僅當 **程式段 100%**（該 Phase 所有 **PD** 或歷史 **P\*** `[x]` + 結案 Python 全 PASS）→ 由 `active/` 移至 `_completed/`；**C\*/CD\*** 可仍 `[ ]`（標「留整批測試週」）。

---

## 2. 結案鐵律（BF-CLOSE）

1. **禁止**在未跑完當 Phase **結案 Python** 前：說「已完成」「今日構建結案」「checklist 全勾」。
2. **禁止**程式段勾 **CD-\***、**PK\***、**C\***、**E0 截圖項**（整批測試週才勾）。
3. 回覆末尾 **必附 Python 結案證據表**（腳本 → exit code → N/N PASS）。
4. **共通**（任何改碼日）：`python scripts/validate_structure.py`、`python scripts/fix_test_doc_wording.py`。
5. 勾 `[x]` 前須**可重現**（規則 #11、#12）；見 [`v7_implementation_basics.md`](../v7_implementation_basics.md)。

---

## 3. 助手流程（固定順序）

1. 讀 **本檔 `_GATE.md`**
2. 讀 [`index.md`](./index.md) **當日 Phase** 列
3. 打開 `active/{phase}.md` 或 `_completed/{phase}.md`（測試週勾 C* 時）
4. 改 **程式檔案**（見該 Phase `### 程式檔案`）
5. 跑 **結案 Python**
6. 只更新 **PD / P\*** 與 `index.md` 證據列
7. [`工作記錄.md`](../../工作記錄.md) 頂部一句

---

## 4. 命名

| 區域 | 工作項 | 驗收項 |
|------|--------|--------|
| `active/` 新 Phase | **PD-{SKU}-NN** | **CD-{SKU}-NN** |
| `_completed/` 封存 | 允許歷史 **P\*/C\***（Token） | 測試週改 C* 仍在本檔 |

---

## 5. 觸發詞（2026-07-29 修訂 · v8 上架）

**現用（上架／正式域）**

```
專案開始，v8 上架，先讀 docs/archives/v7.0.0_CODE_FREEZE_MANIFEST.md 與 專案完整架構表_v8.md @AGENTS.md
```

→ 確認 **v7 已隔離** → 只在 **`feature/v8-launch`** 改碼／測正式域；**禁止**改 archives v7 凍結檔。

**封存（上架衝刺測試 · 07-22～24）**

```
專案開始，先讀 docs/v7_program_line/_GATE.md 與 launch_test_sprint_2026-07-22.md 當日 Day，再開測 @AGENTS.md
```

→ 歷史三日表；主路已過，勿重開 v7 PD。

**封存（程式段）**：`專案開始，並先讀 docs/v7_program_line/_GATE.md，再對照 index 當日 Phase @AGENTS.md`
