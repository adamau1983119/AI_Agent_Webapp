# v7 程式段總表（index · SoT）

> **日期 SoT**：2026-07-21（週二）— 見 [`工作記錄.md`](../../工作記錄.md) 頂部  
> **閘門**：[`_GATE.md`](./_GATE.md)（每次 `專案開始` 第一步）  
> **策略**：程式段已結 → **上架衝刺測試**（07-22～24 · 每日 1.5h）  
> **測試 SoT**：[`launch_test_sprint_2026-07-22.md`](./launch_test_sprint_2026-07-22.md)  
> **備份**：[`2026-07-21_launch-sprint-trigger_snapshot`](../backups/2026-07-21_launch-sprint-trigger_snapshot/SNAPSHOT_README.md) · [`2026-06-25_f05-mychannel-program_snapshot`](../backups/2026-06-25_f05-mychannel-program_snapshot/SNAPSHOT_README.md)

---

## Active（進行中）

| Phase | 排程 | PD | CD／PK | Checklist | 結案 Python | 最後證據 |
|-------|------|----|--------|-----------|-------------|----------|
| **上架衝刺測試** | **07-22～24** · 每日 **1.5h** | — | 見三日表 | [`launch_test_sprint_2026-07-22.md`](./launch_test_sprint_2026-07-22.md) | 手測 + 截圖 | 待 Day1 |

> **程式段主線已結**（含 **2026-07-21**）：Post Kit L0；**AE-0～AE-2（程式）**；**MC-1～6**。  
> **下一步**：依上架衝刺三日表跑 CD／E0／PK；**勿**再開新 PD 主線。  
> **觸發**：`專案開始，先讀 …/_GATE.md 與 launch_test_sprint_2026-07-22.md 當日 Day，再開測 @AGENTS.md`

---

## 上架衝刺 · 三日總覽（2026-07-22～24）

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
