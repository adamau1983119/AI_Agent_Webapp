# V7-4 Phase 4 Session Log

> **日期**：2026-06-06（實曆漂移）  
> **分支**：`feature/v7-cost-pipeline`  
> **目標**：TopicCard skeleton + fade-in；cache-first 體感；kol_style 按需按鈕

---

## 實作摘要

| 項 | 產出 | 狀態 |
|----|------|------|
| P4-01 | `TopicCard.tsx` — 語系切換自動 `standard_translation`；skeleton → fade-in | ✅ |
| P4-02 | `TopicTranslateDisplayButton.tsx` — `kol_style` 獨立 loading、點擊才請求 | ✅ |
| P4-03 | `按鈕測試ID架構表.md` — `btn-topic-card-kol-style`、`btn-topic-detail-kol-style` | ✅ |
| P4-04 | `i18n` — `topics.translateKolStyle`、`topics.kolStyleDone` 三語 | ✅ |
| P2-12 | 卡片 standard 自動；僅「網紅風格」按鈕觸發 kol | ✅ |
| P4-05 | `/health` cost_controls 已於 VM-3／Phase 2 就緒（本輪無改） | ➖ |
| C4-4 | `npm run build` exit 0 | ✅ |

---

## 行為說明

1. **`/topics` 切語系**（介面 ≠ 收集語言）  
   - 有 `titles_i18n[lang]` → 直接顯示譯文 + opacity fade-in（**0 API**）  
   - 無快取 → 自動 `POST translate-display`（`standard_translation`）+ skeleton → fade-in  

2. **網紅風格**  
   - 卡片底部 **`btn-topic-card-kol-style-{id}`**；僅點擊才送 `translation_type=kol_style`  
   - 詳情頁並列 **`btn-topic-detail-kol-style`**  

3. **API**  
   - `topicsAPI.translateDisplay(id, lang, translationType)` 支援 `standard_translation`／`kol_style`  

---

## 變更檔案

- `frontend/src/components/ui/TopicCard.tsx`
- `frontend/src/components/ui/TopicTranslateDisplayButton.tsx`
- `frontend/src/api/topics.ts`
- `frontend/src/lib/topicDisplay.ts`
- `frontend/src/pages/TopicDetail.tsx`
- `frontend/src/i18n/index.ts`
- `按鈕測試ID架構表.md`

---

## 待手測（使用者程式全線完成後）

| 代號 | 驗證 |
|------|------|
| C4-1 | `/topics` 切 ja：skeleton → 譯文 fade-in（375px + desktop） |
| C4-2 | 快取命中後再切語系：Network **0** translate-display |
| C4-3 | 僅點「網紅風格」後出現 Flash 相關請求 |
| C4-5 | 工作記錄 Phase 1～4 證據摘要 |

---

## 下步

- **整線 commit**（待使用者指示）  
- **C1～C4 手測**與截圖（`docs/v7_evidence_screenshot_guide.md`）
