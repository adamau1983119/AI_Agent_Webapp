# ADR 0002 — 建立頻道「檢索 MVP」邊界：站內 RSS 白名單

## 狀態

Accepted（2026-05-09）

## 情境

助手需動態列出可選 RSS；完整「外部探索＋索引」尚未就緒。

## 決策

- **MVP**：`wizard-options`、搜尋、再推薦等路徑以 **站內 DEFAULT_RSS_SOURCES／白名單** 為邊界。
- 使用者 **貼上 URL** 仍走 `POST /channels/feeds/validate`（`feed_url_probe_service`、SSRF 防護、限流 429 `detail.code`）。
- 外部搜尋 API／RAG 等 **不** 納入本 MVP DoD；見 `channel_create_ai_guided_spec.md` 檢索 MVP 段。

## 後果

- 前後端契約：`channels.py`、`channel_assist_service.py`、`CreateChannel.tsx` Step 2。
- 測試：429／`detail.code` 與前端 i18n 對照見清單 **I.1**。
