# Looker／Google Sheet 欄位（對齊合約 schema_version 1）

WorkBuddy／人工每週將 `marketing_period_counts.py` 輸出＋Ads／GA4 手填寫入 Sheet，供 Looker 分數卡（本週橙／上週灰）。

## 建議分頁 `ops_weekly`

| 欄 | 來源 | 說明 |
|----|------|------|
| period_start / period_end | script | HKT 週一～日 |
| schema_version | script | 1 |
| external_new_users | script | Mongo |
| external_total_users | script | Mongo |
| valid_members | script | 生成成功＋扣點 |
| active_users_30d | script | |
| successful_generations | script | ae_compose* |
| email_subscribers_total / _new | script | ≠ customer |
| ads_spend_hkd / ads_clicks / ads_impr | Ads 手填 | HKD |
| ga4_sign_up / generate_post / purchase | `fetch_ga4.py`（Data API）或暫手填 | 事件≠客戶；Property ID≠G-ID |
| ads_spend_hkd / clicks / impr | `fetch_ads.py`（API 或 `--handfill`） | HKD；等 Token 前用手填 |
| revenue_usd | Stripe／books | USD |
| revenue_hkd_equiv | 可選 | USD×7.8 |
| founder_noise | 手填 | low／medium／high |
| provisional | 手填 | GA4 篩選未有效＝true |
| traffic_light | CEO 拍板後 | |
| prev_* 同名欄 | 上週列或並排 | WoW |

## 注意

- 禁止把 email 名單貼進 Sheet。  
- GA4 圖表可直接連 GA4；Mongo 卡必須走本 Sheet。  
- 詳見 [`marketing_analytics_ai_contract.md`](./marketing_analytics_ai_contract.md)。
