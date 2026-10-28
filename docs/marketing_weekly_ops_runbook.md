# 行銷週報操盤（WorkBuddy · 週一～週日 HKT）

合約：[`marketing_analytics_ai_contract.md`](./marketing_analytics_ai_contract.md)。  
**禁**改 KPI 定義；**禁**用客戶 `weekly_mail` 當營運通知。

## 每週一（上一完整週）

1. `python scripts/marketing_period_counts.py --period-start YYYY-MM-DD --period-end YYYY-MM-DD`
2. GA4：`GA4_PROPERTY_ID`＋`GOOGLE_APPLICATION_CREDENTIALS` → `marketing_period_fetch_ga4.py`  
   - 內部篩選器＝**有效** 時設 `GA4_PROVISIONAL=false`
3. Ads：有 Developer Token／探索層級 → `marketing_period_fetch_ads.py`  
   - 否則 Ads 後台抄該週費用／點擊／曝光 → `--handfill --spend-hkd … --clicks … --impr …`
4. `marketing_period_assemble.py … --ga4-file … --ads-file … --out draft.json`
5. 補燈號／≤3 決策（CEO）→ `marketing_period_upsert.py --env production --file draft.json`
6. 可選：`marketing_period_rollup.py`；Looker／Sheet 對 [`marketing_period_sheet_fields.md`](./marketing_period_sheet_fields.md)

## Looker

一頁：GA4 事件卡＋Mongo 外部／Valid／Email＋Ads HKD；本週橙／上週灰。決策＝六段稿＋快照，不另開第二套 KPI。

## 停損提醒

Ads≥HKD200／30 日且 external_new＝0 → Review。Ads≥HKD600／90 日且 external_new≤3 → Reassessment。
