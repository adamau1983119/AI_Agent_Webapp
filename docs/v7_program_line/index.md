# v7 程式段總表（index · SoT）

> **日期 SoT**：2026-07-30（星期四）— 見 [`工作記錄.md`](../../工作記錄.md) 頂部  
> **閘門**：[`_GATE.md`](./_GATE.md)  
> **策略**：**v7 已 code-freeze** → 後續測試／上架走 **v8**（`feature/v8-launch`）  
> **v7 保全**：[`../archives/v7.0.0_CODE_FREEZE_MANIFEST.md`](../archives/v7.0.0_CODE_FREEZE_MANIFEST.md) · tag `v7.0.0-code-freeze`  
> **v8 架構 SoT**：[`../../專案完整架構表_v8.md`](../../專案完整架構表_v8.md)  
> **上架 DNS**：[`../alter_ego_launch_dns_checklist.md`](../alter_ego_launch_dns_checklist.md)

---

## Active（進行中）

| Phase | 排程 | PD | CD／PK | Checklist | 結案 Python | 最後證據 |
|-------|------|----|--------|-----------|-------------|----------|
| **v8 上架** | **07-29～** · DNS／正式域 | — | 真實運行 | [`../alter_ego_launch_dns_checklist.md`](../alter_ego_launch_dns_checklist.md) · 架構表 v8 | 線上 health + DNS | **07-30**：api health ✅；Vercel API URL ✅；Google Console／登入 E2E ⏳ · 備份 `2026-07-30_v8_hosting_b_day2_snapshot` |

> **v7 程式段＋上架衝刺主路已結**（07-28 補測；07-29 freeze＋PR #17 → `main`）。  
> **禁止**再開 v7 功能 PD；**禁止**改 archives v7 凍結檔。  
> **觸發（上架）**：在 `feature/v8-launch` 工作；對照架構表 **v8** + DNS checklist。

---

## Completed（封存 · 含上架衝刺）

| Phase | 結果 | 錨點 |
|-------|------|------|
| **v7 code-freeze** | ✅ | tag `v7.0.0-code-freeze` · `9556ea7` · PR #17 |
| **上架衝刺 Day1～3** | ✅ 條件上架 | [`launch_test_sprint_2026-07-22.md`](./launch_test_sprint_2026-07-22.md) |

---

## 上架衝刺 · 三日總覽（歷史 · 2026-07-22～24／補測 07-28）

| 日期 | 週 | 時長 | 主題 | 必過（摘要） |
|------|-----|------|------|--------------|
| **07-22** | 三 | 1.5h | **Day1** 環境 + AE 主路 | E0-B/F；E0-AE-1～3；CD-AE-C1／C3 |
| **07-23** | 四 | 1.5h | **Day2** MyChannel + Post Kit | E0-MC；CD-MC2/3；PK1～4 |
| **07-24** | 五 | 1.5h | **Day3** Discover + 煙霧 + 收口 | CD-4-1/2；PD-AE2-03；Token 煙霧；上架判決 |

**延後／N/A（不阻塞可上架）**：CD-DNS0、KPI 基線、staging 30 批（無 DT-5）、全量 C*/X* 細項、Post Kit P1/P2 API。

---

## Completed（程式段 · 近期）

| Phase | 程式 | CD／C* | 檔案 | 證據 |
|-------|------|--------|------|------|
| **AE-2** | ✅ PD-01/02/04 | ⏳ PD-AE2-03 → Day3 | [`v7_alter_ego_checklist.md`](../v7_alter_ego_checklist.md) | weekly_batch + feedback + reextract |
| **MC-6 熱門模板** | ✅ PD-MC4-03 | ⏳ CD-MC4-* → Day2 餘裕 | [`v7_mychannel_checklist.md`](../v7_mychannel_checklist.md) | templates JSON + UI |
| **Post Kit L0 + F05～F07** | ✅ | ⏳ PK* → Day2 | [`publish_post_kit_spec.md`](../publish_post_kit_spec.md) | `check_postkit_bf_ui` + `check_ae_bf_ui` 22/22 |
| **AE-0～AE-1d** | ✅ PD 全線 | ⏳ CD-AE-C*／E0 → Day1 | [`v7_alter_ego_checklist.md`](../v7_alter_ego_checklist.md) | static + live |
| **MC-1～5** | ✅ PD | ⏳ CD-MC*／E0-MC → Day2 | [`v7_mychannel_checklist.md`](../v7_mychannel_checklist.md) | `check_mychannel_bf_static` |
| **Token V7-0～5** | ✅ | ⏳ C* 煙霧 → Day3 | [`_completed/token_cost.md`](./_completed/token_cost.md) | `bebf6d0` |
| **Discover PF-B/M** | ✅ | ⏳ CD-4／B → Day3 | [`v7_discover_public_feed_checklist.md`](../v7_discover_public_feed_checklist.md) | `check_pf_b_*` |
| **Landing** | ✅ | ⏳ 煙霧 → Day3 | — | `check_landing_bf_ui` 11/11 |

---

## 日曆（06-25 起 · 07-21 補記 · 07-22 衝刺鎖定）

| 日期 | 週 | 主題 |
|------|-----|------|
| **06-25** | 四 | ✅ AE-1c/d + F05～F07 + MC-1～5 程式段 |
| **06-26** | 五 | staging 真批／緩衝（未記） |
| **06-30** | 二 | 建議整批測試週起（當時未開跑） |
| **07-21** | 二 | ✅ AE-2 程式 + MC-6 模板；Active → 測試 |
| **07-22** | 三 | **上架衝刺 Day1**（1.5h）— AE |
| **07-23** | 四 | **上架衝刺 Day2**（1.5h）— MC + Post Kit |
| **07-24** | 五 | **上架衝刺 Day3**（1.5h）— Discover + 收口／上架判決 |

---

## 外部（尚未遷入專區 · 仍有效）

- **上架衝刺明細**：[`launch_test_sprint_2026-07-22.md`](./launch_test_sprint_2026-07-22.md)
- Discover 全文：[`v7_discover_public_feed_checklist.md`](../v7_discover_public_feed_checklist.md)
- 測試週每日（舊／全量）：[`test_week_daily_checklist.md`](../test_week_daily_checklist.md)
