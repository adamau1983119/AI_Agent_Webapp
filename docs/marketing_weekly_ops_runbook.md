# 行銷週報操盤（**WorkBuddy 執行** · HKT 週一～週日）

合約：[`marketing_analytics_ai_contract.md`](./marketing_analytics_ai_contract.md)。  
**執行者＝WorkBuddy**（填表、跑 script、記錄、營運電郵）。  
**CEO**＝審燈號／≤3 決策；**不**申請 Ads Developer Token、**不**開 MCC、**不**手跑 API。

**禁**改 KPI 定義；**禁**用客戶 `weekly_mail` 當營運通知。

## Ads 方針

- **目標**：`fetch_ads` **API**（Developer Token＋OAuth refresh；GCP 探索層級）。  
- 客戶帳 `970-864-5947`；MCC `730-946-6170` **已掛**（2026-10-29）。本機設 `GOOGLE_ADS_LOGIN_CUSTOMER_ID=7309466170`。`fetch_ads` 掛帳後煙霧 **PASS**（週 10/20～26＝35.17／19／2196）。  
- `GOOGLE_ADS_*` 只放本機 `.env`（勿進 Git）；授權腳本：`marketing_period_ads_oauth.py`。  
- 每週一：優先 API；失敗才 `--handfill`。

## 每週一（WorkBuddy 清單）

上一完整週：`period-start`＝週一、`period-end`＝週日（HKT）。

1. `marketing_period_counts.py --period-start … --period-end …`
2. GA4：`fetch_ga4.py`（`GA4_PROPERTY_ID`＋服務帳戶；`GA4_PROVISIONAL=false`）
3. Ads：`fetch_ads.py …`（API）→ 存 `ads.json`；失敗才  
   `--handfill --spend-hkd N --clicks N --impr N`
4. `assemble.py … --ga4-file … --ads-file … --out draft.json`
5. 草稿給 CEO 拍燈號／決策 → WorkBuddy：  
   `upsert.py --env production --file draft.json`
6. `export_sheet.py --period-start … --out docs/evidence/marketing/ops_weekly.csv` → 匯入 Sheet（Looker 見 [`marketing_looker_sheet_setup.md`](./marketing_looker_sheet_setup.md)）
7. 黃燈可跑：`funnel_signup_compose.py`（無 PII）→ 結果一句寫工作記錄
8. 可選：`rollup.py`

## 停損提醒

Ads≥HKD200／30 日且 external_new＝0 → Review。Ads≥HKD600／90 日且 external_new≤3 → Reassessment。
