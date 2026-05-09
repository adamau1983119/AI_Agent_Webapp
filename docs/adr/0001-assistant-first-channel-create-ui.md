# ADR 0001 — 建立頻道改為助手優先（Assistant-first）

## 狀態

Accepted（2026-05-09）

## 情境

建立頻道原以三步表單為主；產品要降低冷啟動摩擦，並與 §E（`channel_create_ai_guided_spec.md`）對齊。

## 決策

- 進入 `/channels/create` **預設展開 AI 助手**（`showAssist` 預設 `true`）。
- **大螢幕**下三步表單預設 **收合**，以摘要＋助手為主；使用者可 **展開完整表單**（進階／備援 L4）。
- 保留「收起助手」「關閉助手，改用表單」等出口，避免單一路徑卡死。

## 後果

- 前端主檔：`frontend/src/pages/CreateChannel.tsx`。
- 驗收對照：`docs/channel_create_new_scheme_checklist.md` **B～D**。
- 功能開關：目前 **無** 後端 env；若日後要漸進放量，見清單 **I.2**。
