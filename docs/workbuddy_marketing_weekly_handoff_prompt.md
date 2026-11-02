# WorkBuddy · 行銷週報交棒 Prompt（完整）

把下面 **「複製給 WorkBuddy」** 整段貼給騰訊 WorkBuddy。  
SoT：[`marketing_weekly_ops_runbook.md`](./marketing_weekly_ops_runbook.md)、[`marketing_analytics_ai_contract.md`](./marketing_analytics_ai_contract.md)、[`marketing_alter_ego_ops_layout_spec.md`](./marketing_alter_ego_ops_layout_spec.md)、[`marketing_looker_sheet_setup.md`](./marketing_looker_sheet_setup.md)。

**角色**：你＝WorkBuddy（執行）；CEO＝只審燈號／≤3 決策。  
**禁**：改 KPI 定義；手貼 CSV 叫 CEO 做；用客戶 `weekly_mail` 當營運通知；改產品碼／i18n／按鈕／扣點／`generate_content`；把 PII／email 名單寫進 Sheet。

---

## 複製給 WorkBuddy

```text
【任務】Alter Ego 行銷營運週報（HKT 週一～週日）— 完整 runbook 1～8 + 原生 Google 試算表 + Looker 資料源對齊

【身份】
- 你是 WorkBuddy（騰訊），執行者。
- 使用 Google 帳號 info@ai-alterego.com（OAuth／Sheets Skill／Drive）。
- 專案根目錄：AI_Agent_Webapp。營運腳本在 scripts/marketing_period_*.py；密鑰只在本機 backend/.env（勿讀出貼聊天）。

【期間】
- period-start＝上一完整週的週一（HKT）
- period-end＝該週週日（HKT）
- 例（已跑過、勿重複 upsert 除非 CEO 要求重跑）：2026-10-20～26、2026-10-27～11-02
- 若今天是新的週一：用「剛結束的上一完整週」日期。

【鐵律】
- 客戶／新客分母＝Mongo 外部（scripts counts）；GA4 事件≠客戶數。
- 花費＝Ads HKD；失敗才 --handfill。
- Sheet 必須是「原生 Google 試算表」，檔名 AlterEgo_ops_weekly，分頁名恰好 ops_weekly。
- 禁止用 .xlsx 上傳檔當主表；若只有 xlsx：另存為 Google 試算表再用。
- 禁把 email 名單寫進 Sheet。
- Looker 報表已存在（id 5d96e560-baf9-40da-9ad3-cae35c528cbe，info@）；不要從頭新建第二套報表；只改資料來源／依版面規範排版。
- 版面契約：docs/marketing_alter_ego_ops_layout_spec.md + docs/evidence/marketing/alter_ego_ops_weekly_sample.jpg
  （橘＝This week、灰＝Last week；頂列 6 卡；中列 medium＋landing；下列 geo＋device；頁尾 Mongo／GA4 鐵律）。

【步驟 1 — counts】
在專案根目錄（已載入 backend/.env）執行：
  python scripts/marketing_period_counts.py --period-start YYYY-MM-DD --period-end YYYY-MM-DD
把 JSON 存到 docs/evidence/marketing/{period-start}_counts.json

【步驟 2 — GA4】
  python scripts/marketing_period_fetch_ga4.py --period-start YYYY-MM-DD --period-end YYYY-MM-DD
存成 {period-start}_ga4.json
確認 provisional=false（GA4_PROVISIONAL=false）。

【步驟 3 — Ads】
  python scripts/marketing_period_fetch_ads.py --period-start YYYY-MM-DD --period-end YYYY-MM-DD
存成 {period-start}_ads.json；source 應為 google_ads_api。
失敗才：
  python scripts/marketing_period_fetch_ads.py ... --handfill --spend-hkd N --clicks N --impr N

【步驟 4 — assemble】
  python scripts/marketing_period_assemble.py --period-start YYYY-MM-DD --period-end YYYY-MM-DD --ga4-file … --ads-file … --provisional false --out docs/evidence/marketing/{period-start}_week_assembled.json
合併燈號／決策欄位進草稿（預設可沿用 yellow + hold_budget_small / investigate_signup_to_first_compose，除非 CEO 另有指示），寫成 {period-start}_week_draft.json

【步驟 5 — CEO 燈號 → upsert】
把 draft 核心數字＋建議 traffic_light＋≤3 decisions 摘要給 CEO。
CEO 拍板後：
  python scripts/marketing_period_upsert.py --env production --file docs/evidence/marketing/{period-start}_week_draft.json
存 upsert 回證 {period-start}_week_upsert.json

【步驟 6 — 試算表（主路徑：你自己建／寫；禁叫 CEO 手貼）】
A. 本機證據（建議）：
  python scripts/marketing_period_export_sheet.py --all --out docs/evidence/marketing/ops_weekly.csv
B. 用 info@ 建立或開啟「原生」Google 試算表：
  - 標題：AlterEgo_ops_weekly
  - 分頁：ops_weekly
  - 覆寫為：表頭＝CSV 欄位順序 + 全部 week 列（與 export --all 一致）
C. 回傳完整試算表網址（含 /d/SHEET_ID/）。
D. 備援（僅當 Sheets Skill／info@ 不可用）：設定 MARKETING_OPS_SHEET_ID 後
  python scripts/marketing_period_push_sheet.py --all
  （需 SA 對「原生表」有 Editor；xlsx 殼會 404）

【步驟 7 — 漏斗（黃燈建議跑）】
  python scripts/marketing_period_funnel_signup_compose.py --period-start YYYY-MM-DD --period-end YYYY-MM-DD
存 JSON；在工作記錄寫一句（無 PII）：例如「新客 N → compose 0；breakpoint=signup_to_first_compose」。

【步驟 8 — rollup（可選）】
  python scripts/marketing_period_rollup.py --period-start YYYY-MM-DD --period-end YYYY-MM-DD

【Looker（步驟 6 之後）】
- 打開既有報表 Alter Ego Ops / id 5d96e560-…（若標題仍「未命名」請改名 Alter Ego Ops）
- 資料來源改連步驟 6 的原生 Sheet／ops_weekly（人數／Ads／燈號卡）
- GA4 原生連線補：Sessions、Engaged sessions、medium、landing、country、device（對齊 layout spec）
- 分數卡顯示名用可讀英文／中英，勿只顯示 snake_case 欄位名
- 完成後截圖或一句：Looker 已連新表＋版面對齊 sample

【交付給 CEO】
1. period 起迄
2. draft／upsert 摘要（新客、Ads、GA4、燈號、≤3 決策）
3. 原生 Sheet 網址
4. funnel 一句
5. Looker 狀態一句
6. 停損是否觸發（Ads≥200／30d 且 new=0 → Review；Ads≥600／90d 且 new≤3 → Reassessment）

【完成定義】
- 1～5 與 6B 完成；7 若黃燈已跑；Looker 已指向新原生表；無人再手貼 CSV。
```

---

## 本機環境（WorkBuddy 開跑前自檢）

- [ ] 專案可讀；Python 可 import 腳本依賴（google-ads、GA4、Sheets client）
- [ ] `backend/.env`：Mongo、`GOOGLE_ADS_*`（含 LOGIN）、`GA4_PROPERTY_ID`、`GOOGLE_APPLICATION_CREDENTIALS`、`GA4_PROVISIONAL=false`
- [ ] info@ 已登入 Google；Sheets／Drive Skill 或等效授權可用
- [ ] 已讀 layout spec；sample 圖路徑有效

## 與 Cursor／CEO 分工

| 誰 | 做 |
|----|-----|
| WorkBuddy | runbook 1～8、自建／寫 Sheet、對齊 Looker 資料源與版面、寫工作記錄一句 |
| CEO | 拍燈號／決策；審交付摘要 |
| Cursor | 改 scripts／合約文件（本輪已交棒）；非每週手跑 |

## 相關連結

- Looker（既有）：https://lookerstudio.google.com/reporting/5d96e560-baf9-40da-9ad3-cae35c528cbe  
- 證據目錄：`docs/evidence/marketing/`  
- 欄位：[`marketing_period_sheet_fields.md`](./marketing_period_sheet_fields.md)
