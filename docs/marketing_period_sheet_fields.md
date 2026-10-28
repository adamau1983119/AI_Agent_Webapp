# Looker／Google Sheet 欄位（對齊合約 schema_version 1）

WorkBuddy 每週：`export_sheet.py` → Sheet 分頁 `ops_weekly` → Looker。  
設定步驟：[`marketing_looker_sheet_setup.md`](./marketing_looker_sheet_setup.md)。

## 建議分頁 `ops_weekly`

| 欄 | 來源 | 說明 |
|----|------|------|
| period_start / period_end | snapshot | HKT 週一～日 |
| schema_version | snapshot | 1 |
| provisional | snapshot | Internal Traffic 有效後 false |
| traffic_light | CEO | yellow／green／red |
| external_new_users | Mongo counts | |
| external_total_users | Mongo | |
| valid_members | Mongo | 生成成功＋扣點 |
| active_users_30d | Mongo | |
| successful_generations | Mongo | ae_compose* |
| email_subscribers_total / _new | Mongo | ≠ customer |
| ads_spend_hkd / ads_clicks / ads_impr | `fetch_ads` API 或 `--handfill` | HKD |
| ga4_sign_up / generate_post / purchase | `fetch_ga4` | 事件≠客戶 |
| revenue_usd / revenue_hkd_equiv | Stripe／×7.8 | |
| founder_noise | 手填 | low／medium／high |

匯出：

```bash
python scripts/marketing_period_export_sheet.py --all --out docs/evidence/marketing/ops_weekly.csv
```

## 注意

- 禁止把 email 名單貼進 Sheet。  
- GA4 圖表可直接連 GA4；**人數卡必須走本 Sheet**。  
- 詳見 [`marketing_analytics_ai_contract.md`](./marketing_analytics_ai_contract.md)。
