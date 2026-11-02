# 行銷營運週報（2026-11-02 週一完整 runbook）

依 `docs/marketing_analytics_ai_contract.md`。opsOnly：未改產品碼／i18n／按鈕。Python checking＝N/A。

## 1. 期間／環境

| 項 | 值 |
|----|-----|
| period | week · **2026-10-27～2026-11-02** HKT |
| prev_week | 2026-10-20～2026-10-26 |
| env | production |
| provisional | **false** |
| traffic_light | **yellow**（沿用 hygiene；CEO 可再拍） |
| focus.theme | hygiene |

## 2. Core

| 指標 | 值 |
|------|-----|
| external_new_users | **1** |
| external_total_users | **8** |
| valid_members | **1** |
| active_users_30d | **5** |
| successful_generations | **1** |
| email_subscribers_total／new | **6／0** |
| ads_spend_hkd／clicks／impr | **23.52／18／212**（Ads API） |
| ga4_sign_up／generate_post／purchase | **5／8／0** |

## 3. 對帳／漏斗

- GA4 sign_up＝5 ≠ Mongo 新客 1（人數只認 Mongo）。  
- 本週有 **1** 次成功生成／valid_member（既有外部用戶）；**本週新客 1 人仍 0 compose** → breakpoint 仍 `signup_to_first_compose`。  
- 停損：本週 spend 23.52、new≠0 → 未觸發 30 日 Review。

## 4. 決策（暫沿用）

- D1 `hold_budget_small`  
- D2 `investigate_signup_to_first_compose`  
- D3 `watch_compose_after_pr128`

## 5. 產物

- `2026-10-27_week_draft.json`／`_upsert.json`  
- `ops_weekly.csv`（**2 列**：含上週 10/20）→ 請貼 Sheet 後 Looker 刷新
