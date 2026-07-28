# V7-5 Phase 5 Session Log

> **日期**：2026-06-06  
> **分支**：`feature/v7-cost-pipeline`  
> **目標**：合規—Privacy Policy 跨境／APPI 揭露；NLLB repo 審計

---

## P5-01 Privacy Policy / APPI 跨境披露

| 項 | 產出 | 狀態 |
|----|------|------|
| 新增 頻道區塊 7 | `frontend/src/i18n/index.ts` — 跨境傳輸、DeepL／DeepSeek、APPI、**不使用 NLLB** | ✅ |
| 聯繫 頻道區塊 8 | 原 頻道區塊 7 聯繫我們改為 頻道區塊 8 | ✅ |
| 頁面 | `frontend/src/pages/Privacy.tsx` — 渲染 頻道區塊 7 列表 + 頻道區塊 8 | ✅ |
| 三語 | zh-TW／en／ja 齊 | ✅ |
| 更新日期 | `lastUpdate` → 2026 年 6 月 | ✅ |

**備註**：文案為 **v7 技術揭露草稿**；正式上線前建議 PM／法務覆核 DeepL／DeepSeek DPA 與 APPI 境外提供程序。

---

## P5-02 NLLB 審計（架構 + repo）

```text
grep -i nllb 程式與依賴檔（*.py, *.txt, *.json, *.ts, *.tsx）→ 0 筆
grep -i nllb 全 repo → 僅文件／政策禁止敘述 + 隱私政策揭露句（非依賴）
grep sqlalchemy backend/*.py → 0 筆
backend/requirements.txt → 無 nllb／transformers／torch 翻譯堆疊
```

| 檔案類 | NLLB 命中 | 性質 |
|--------|-----------|------|
| `backend/`、`frontend/src/`（除 i18n 揭露句） | 0 | — |
| `專案完整架構表_v7.md`、`AGENTS.md`、checklist | 3 處 | **禁止**政策文字 |
| `i18n` 頻道區塊 7 | 3 語各 1 句 | 使用者揭露「不使用 NLLB」 |

**結論**：v7 翻譯路徑為 **DeepL + 字串 Fallback**（D4）；**未引入** NLLB-200 或自架模型依賴。✅

---

## 驗證

- `npm run build` exit 0（Phase 5 動前端後）

---

## 待辦

- [ ] 瀏覽器 `/privacy` 三語截圖（可併 C4 或獨立證據）
- [ ] 法務覆核 P5-01 定稿
- [ ] **commit** 待使用者指示
