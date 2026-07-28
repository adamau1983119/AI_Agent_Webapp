# Phase 區塊模板（複製至 `active/{name}.md`）

```markdown
## Phase {ID} — {標題}

**目標**：一句  
**結案判定**：程式段 = 所有 **PD-*** `[x]` + `### 結案 Python` 全 PASS  
**排程日**：YYYY-MM-DD  

### 程式檔案
- [ ] `path/to/file`（待寫）
- [x] `path/to/file`（已落地 · 日期）

### PD — 程式段工作項
- [ ] **PD-{SKU}-01** 描述
  - 產出：…
  - 證據：…

### 結案 Python（程式段收工必跑）
1. `python scripts/validate_structure.py`
2. `python scripts/fix_test_doc_wording.py`
3. `python scripts/check_{sku}_*.py`（若有）
4. `cd frontend && npm run build`（若動 `.tsx`）

### CD — 測試週驗收（禁止程式段勾 `[x]`）
- [ ] **CD-{SKU}-01** 描述
  - 驗證：…
  - 證據：截圖路徑 —
```

**SKU 範例**：`PK`（Post Kit）、`AE`（Alter Ego）、`MC`（MyChannel）、`PF`（Discover）
