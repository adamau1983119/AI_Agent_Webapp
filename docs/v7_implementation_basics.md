# v7 實作基礎守則（BF · 改碼前必讀）

> **適用**：**2026-06-09 起** v7 監察週（VM-1～4）、Token Phase 0～4、Discover SKU（PF-*）之**任何程式 commit**。  
> **觸發**：對話 **`專案開始`**／**`專案開始 v7`** → 須先完成 [`AGENTS.md`](../AGENTS.md) **「專案開始前檢查」**（六必讀 + 啟動檢查），**再**勾本檔當日適用之 **BF-***。  
> **SoT**：[`README.md`](../README.md) 規則 **3、4、6、8、11～14**；[`開發人員必讀規則.md`](../開發人員必讀規則.md)。

---

## 規則對照（一句收斂）

| 代號 | 內容 | 必讀／工具 |
|------|------|------------|
| **BF-1** | 改碼前讀相關檔、`grep` 影響範圍；禁止未讀就改 | README 規則 **8** |
| **BF-2** | **禁止硬編碼**可見 UI 字串；三語 **zh-TW／en／ja** | README 規則 **6** → [`frontend/src/i18n/index.ts`](../frontend/src/i18n/index.ts) |
| **BF-3** | **新按鈕／連結**須 `data-testid`；ID 與架構表一致 | README 規則 **3、4** → [`按鈕測試ID架構表.md`](../按鈕測試ID架構表.md)、[`按鈕架構表.md`](../按鈕架構表.md) |
| **BF-4** | 動 **路由／頁面** 對照 [`專案完整架構表_v7.md`](../專案完整架構表_v7.md)（或凍結版架構表） | README 規則 **4** |
| **BF-5** | 動 **版面／元件樣式** 對照 [`品牌設計規範.md`](../品牌設計規範.md) | 僅 UI 變更 |
| **BF-6** | 勾選前**查實際程式**；禁止未測即勾 | README 規則 **11、12** |
| **BF-7** | **禁止**為 ngrok／本機 HTTPS 等測試**擅自改**既有架構與預設 | README 規則 **14**、AGENTS |

---

## 每日開工（有 commit 當日必勾）

- [ ] **BF-DAY-1** 已輸出 **「專案開始前檢查 — 結果表」**（含分支非 `main` 直改）
- [ ] **BF-DAY-2** 本日若動**前端**：已讀 [`按鈕測試ID架構表.md`](../按鈕測試ID架構表.md)（有新增／修改按鈕時）
- [ ] **BF-DAY-3** 本日若動**前端**：已確認 i18n key 存在或**同日**補齊三語（BF-2）

---

## 前端結案前（Phase 4、Discover PF-4、任何 `.tsx` 可見字串）

- [ ] **BF-UI-1** `npm run build` exit 0
- [ ] **BF-UI-2** 新增可見字串皆為 `t('…')`；**無**新增硬編碼中文／英文／日文（品牌名例外依 README）
- [ ] **BF-UI-3** 新增／修改按鈕已加 **`data-testid`**，且已更新 [`按鈕測試ID架構表.md`](../按鈕測試ID架構表.md)
- [ ] **BF-UI-4** 更新測試結果前已 `grep`／`read_file` 核對 testid、i18n key **確實存在**（BF-6）

---

## 後端為主當日（VM-2 log_cost_event、Phase 0～2）

- **BF-UI-*** 標 **➖ 本輪不涉及**（僅改 `backend/`）。
- 仍須 **BF-DAY-1**、**BF-1**、**BF-6**、**BF-7**。

---

## 與各 checklist 的掛鉤

| 工作流 | 額外必過項 |
|--------|------------|
| Token Phase 4 | 本檔 **BF-UI-*** + [`v7_token_cost_phase_checklist.md`](./v7_token_cost_phase_checklist.md) **P4-03、P4-04** |
| Discover PF-4 | 本檔 **BF-UI-*** + **PD-4-04、CD-4-5**（[`v7_discover_public_feed_checklist.md`](./v7_discover_public_feed_checklist.md)） |
| 監察週 VM-1～4 | 每日開工見 [`v7_monitoring_week_daily_checklist.md`](./v7_monitoring_week_daily_checklist.md)；**VM-2+** 後端為主 |

---

## 助手回覆（`專案開始` 時）

結果表須多一列：

| 類別 | 項目 | 狀態 | 備註 |
|------|------|------|------|
| v7 | `v7_implementation_basics.md` 當日 BF | ✅／➖ | 一句：本日是否動前端；已勾 BF-DAY / BF-UI |
