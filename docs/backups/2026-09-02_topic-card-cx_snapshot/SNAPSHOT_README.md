# Snapshot — 2026-09-02 公眾主題卡產出時契約＋全站正文截斷

## 1. 摘要與目標

本快照封存 **PR #51／#52 已合 `main`**（`7d55dc3`）之公眾主題卡 CX 契約：

1. **產出時寫滿契約**（`finalize_produced_cards`，04:00 HKT 與手動 generate-today）：清洗後 `original_content`、`summary_flash`、三語 `titles_i18n`／`description_i18n`／`source_content_i18n`、`pipeline_version`。
2. **詳情 GET 不重抓**：`on_demand=False`，只 overlay 已產快取。舊卡（9/1–9/2）不回填。
3. **全站正文截斷**（`article_boilerplate`）：不依來源／分類寫特例。文中分享列刪行；購物／最新影片／相關閱讀／Newsletter 等整行結束標記起截斷。
4. **My Channel** 本輪不改收集；之後接同一產出契約。

**Git**：先 `feature/v8-topic-card-cx` → PR → `main` → Railway。改碼前備份 `backup/2026-09-02-pre-topic-card-cx`；合入後本分支 `backup/2026-09-02-topic-card-cx-merged`。

**正式域（2026-09-02 12:12）**：Railway `alert-emotion` 重啟成功；`ensure_today_topics` 15/15 略過補產（今日卡已存在）。第一批新契約卡 = **9/3 04:00 HKT**。

---

## 2. 備份檔案清單

| 檔案名稱 | 說明 |
|:---|:---|
| `article_boilerplate.py` | 全站抽取出口：刪 chrome 行＋結束標記截斷 |
| `article_extractor.py` | 抽取後呼叫 boilerplate |
| `topic_card_finalize.py` | 產出時寫滿三語與 summary_flash |
| `source_article_translator.py` | GET 路徑 `on_demand=False` |
| `test_ops_alert_card_fix.py` | 購物附錄＋非時裝 Related Stories 截斷測試 |

---

## 3. Git／PR

| 項 | 值 |
|:---|:---|
| 程式基線 | `main` `7d55dc3`（#52）含 `922b8ce`（#51） |
| 備份分支 | `backup/2026-09-02-topic-card-cx-merged` |
| 改碼前備份 | `backup/2026-09-02-pre-topic-card-cx` |
| PR | [#51](https://github.com/adamau1983119/AI_Agent_Webapp/pull/51) · [#52](https://github.com/adamau1983119/AI_Agent_Webapp/pull/52) |
