# Looker Studio ＋ Google Sheet（行銷週卡）

欄位 SoT：[`marketing_period_sheet_fields.md`](./marketing_period_sheet_fields.md)。  
週報節奏：[`marketing_weekly_ops_runbook.md`](./marketing_weekly_ops_runbook.md)。  
**版面／色票／結構 SoT**：[`marketing_alter_ego_ops_layout_spec.md`](./marketing_alter_ego_ops_layout_spec.md)（sample：[`evidence/marketing/alter_ego_ops_weekly_sample.jpg`](./evidence/marketing/alter_ego_ops_weekly_sample.jpg)）。  
**WorkBuddy 交棒 Prompt**：[`workbuddy_marketing_weekly_handoff_prompt.md`](./workbuddy_marketing_weekly_handoff_prompt.md)。

## 1. 推送到 Sheet（WorkBuddy Agent · 每週）

```bash
# 自動覆寫分頁 ops_weekly（表頭＋全部 week 列）— 取代手動貼
python scripts/marketing_period_push_sheet.py --all

# 可選：本機留證 CSV
python scripts/marketing_period_export_sheet.py --all --out docs/evidence/marketing/ops_weekly.csv
```

- `.env`：`GOOGLE_APPLICATION_CREDENTIALS`、`MARKETING_OPS_SHEET_ID`、可選 `MARKETING_OPS_SHEET_TAB=ops_weekly`。  
- **一次設定（GCP＋Sheet）**：  
  1. 在服務帳戶所屬 GCP 專案啟用 **Google Sheets API**。  
  2. 用 `info@` 把試算表「共用」給該服務帳戶 `client_email`（**Editor**）。  
- **禁**貼 email 名單；**禁**每週手貼 CSV（除非 push 失敗臨時降級）。

## 2. Google Sheet

**SoT（2026-11-02 起 · 原生表）**：[`AlterEgo_ops_weekly`](https://docs.google.com/spreadsheets/d/1KCrF-Yi8h3K5RxZ66b2ZNnSy5SoLs1qu0gTrOEMjb8M/edit)（分頁 **`ops_weekly`**；ID `1KCrF-Yi8h…`）。  
**棄用**：`109Xw93X…`、`1wD3zDwW…`、`1uttJA5…`；**勿**用上傳的 `ops_weekly.xlsx`。  
**寫入方式**：使用者 OAuth（`.env` 的 `MARKETING_SHEETS_REFRESH_TOKEN`，scope＝Sheets＋Drive.file）→ 自動覆寫分頁；SA `push_sheet` 為備援（須先共用給 `ga4-marketing-reader@regal-skyline-513006-q6`）。GCP 專案 `562088897382` 已啟用 Sheets API；SA 專案 `regal-skyline-513006-q6` **未**啟 Drive API（SA 無法建表）。

## 3. 視覺報表（WorkBuddy 直接產出 · 每週可重跑）

Looker Studio 無公開 API，改資料源／加 GA4 連線須人工 UI。**要即時可附的視覺報表**改用本機管線：

```bash
# 1) 抓 GA4 流量明細（sessions／engagedsessions／medium／landing／country／device＋每日走勢）
python scripts/marketing_period_fetch_ga4_traffic.py \
  --period-start 2026-10-27 --period-end 2026-11-02 \
  --out docs/evidence/marketing/2026-10-27_ga4_traffic.json

# 2) 產 HTML（讀 counts／ads／ga4／traffic／draft 證據）
python scripts/marketing_period_render_visual.py \
  --period-start 2026-10-27 --period-end 2026-11-02 \
  --prev-start 2026-10-20 --prev-end 2026-10-26 \
  --out docs/evidence/marketing/ops_weekly_visual_2026-11-02.html

# 3) HTML → PNG 附件（Windows Chrome）
chrome --headless=new --hide-scrollbars --force-device-scale-factor=2 \
  --window-size=1290,1010 --screenshot=…/ops_weekly_visual_2026-11-02.png file:///…html
```

- 版面對齊 [`marketing_alter_ego_ops_layout_spec.md`](./marketing_alter_ego_ops_layout_spec.md)：頂列 6 卡、中列 medium＋landing、下列 country（**取代世界地圖**，避免地理資料合規問題）＋device donut；橙＝本週、灰＝上週。
- 依賴：`.wb_marketing_venv`（`google-api-python-client`、`google-auth`、`google-analytics-data`、`tzdata`）。

## 4. Looker Studio
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

## 5. Ads 來源提醒

有 Developer Token → `fetch_ads` API；否則 `--handfill` 後再 upsert＋重匯 CSV。
