# Looker Studio ＋ Google Sheet（行銷週卡）

欄位 SoT：[`marketing_period_sheet_fields.md`](./marketing_period_sheet_fields.md)。  
週報節奏：[`marketing_weekly_ops_runbook.md`](./marketing_weekly_ops_runbook.md)。

## 1. 匯出 CSV（本機／WorkBuddy）

```bash
python scripts/marketing_period_export_sheet.py --all --out docs/evidence/marketing/ops_weekly.csv
# 或單週：
python scripts/marketing_period_export_sheet.py --period-start 2026-10-20 --out docs/evidence/marketing/ops_weekly.csv
```

- UTF-8 BOM，可直接「檔案 → 匯入」Google Sheet。  
- **禁**貼 email 名單。

## 2. Google Sheet

**已建（2026-10-28 · info@）**：[`AlterEgo_ops_weekly`](https://docs.google.com/spreadsheets/d/1uttJA5MwwV7pH8a30bSeDlMBOWfVm0eD3foJVugkxUI/edit)（帳號 **`info@ai-alterego.com`**；分頁 `ops_weekly` 已貼首週列）。  
（勿用 a.adam 那張舊表。）

1. 開新試算表，分頁名 **`ops_weekly`**（或沿用上列）。  
2. 匯入／貼上 `ops_weekly.csv`（含表頭）。  
3. 每週一覆寫或追加一列（與 upsert 同一週）。

## 3. Looker Studio

**已建（2026-10-28 · info@）**：報表 **[Alter Ego Weekly Ops](https://lookerstudio.google.com/reporting/5d96e560-baf9-40da-9ad3-cae35c528cbe)**（資料源＝上列 Sheet／`ops_weekly`）。  
已上評量表：`external_new_users`、`ads_spend_hkd`、`ads_clicks`、`traffic_light`（畫布可再拖排；可選再加 `ads_impr`／GA4 欄）。

補建／擴充步驟：

1. [Looker Studio](https://lookerstudio.google.com/) → 建立報表 → 資料來源 **Google 試算表** → 選 `ops_weekly`。  
2. 建議分數卡（本週篩 `period_start` 最新一列；對照上一列＝WoW）：  
   - Mongo：`external_new_users`、`valid_members`、`email_subscribers_total`  
   - Ads：`ads_spend_hkd`、`ads_clicks`、`ads_impr`  
   - GA4：`ga4_sign_up`、`ga4_generate_post`、`ga4_purchase`  
3. GA4 流量圖可另加原生 GA4 連線；**人數卡必須走 Sheet**（合約：人＝Mongo）。  
4. 燈號：用 `traffic_light` 文字／條件格式（黃／綠／紅）。

## 4. Ads 來源提醒

有 Developer Token → `fetch_ads` API；否則 `--handfill` 後再 upsert＋重匯 CSV。
