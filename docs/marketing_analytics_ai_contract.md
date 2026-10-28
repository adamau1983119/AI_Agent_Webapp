# 行銷分析 AI 合約（SoT · schema_version 1）

**觸發句（給 Cursor／Gemini／WorkBuddy）**  
`依 docs/marketing_analytics_ai_contract.md 產出上一完整週行銷分析；禁止改 KPI 定義。`

專家核實：**PASS（2026-10-28）**。未拍板前 AI 稿＝草稿。Mock ≠ 正式數據。

## 角色

| 角色 | 做 | 不做 |
|------|----|------|
| CEO | 審稿、拍板燈號／≤3 決策 | 手算分母 |
| WorkBuddy | 每週 counts／GA4／Ads**手填**／assemble／upsert／export Sheet、記錄、營運電郵 | 自創 KPI；寫 users；用客戶 weekly_mail 當營運通知；逼 CEO 申請 Ads Token |
| Cursor／Gemini | 依本合約分析 | 私改定義 |
| Python scripts | counts／fetch_ga4／fetch_ads／assemble／export_sheet／funnel／upsert／rollup | 行銷 FastAPI；改扣點／生成管線 |

## SoT 鐵律

- **人**＝Mongo 外部（排除 `staff_identity`）  
- **事件**＝GA4（≠ 客戶數）  
- **花費**＝Ads **HKD**  
- **營收**＝Stripe **USD**；可選 `revenue_hkd_equiv = USD × 7.8`（僅顯示；**禁混幣 ROI**）

## 週界

HKT **週一 00:00～週日 23:59**。上週＝上一完整週。首週無上週 → `prev_week: n/a`。

## Core 定義（v1）

| 欄位 | 定義 |
|------|------|
| `external_new_users` | 期間內新建外部帳 |
| `external_total_users` | 截至 `period_end` 外部帳存量 |
| `valid_members` | 外部 ∧ 期間成功生成（見下）∧ 期間至少 1 筆扣點 |
| `active_users_30d` | 外部 ∧（近 30 日 `last_login_at` 或成功生成） |
| `successful_generations` | ledger `action` ∈ `ae_compose`｜`ae_compose_part`（Post Kit／發文成功扣點）；排除瀏覽／失敗／重試 |
| `email_subscribers_total` | 外部 ∧ `email_verified` ∧ `weekly_mail_opt_out`≠true（現有產品信 opt-in SoT；≠ Customer） |
| `email_subscribers_new` | 上列且 `created_at`／驗證落在期間內（能辨則辨；否則 `source_notes`） |
| `founder_noise` | low｜medium｜high |
| `provisional` | GA4 內部篩選未「有效」時 true |
| `schema_version` | **1** |

手填／後台：`revenue_usd`、燈號、決策。  
`ga4_*`：`marketing_period_fetch_ga4.py`。  
`ads_*`：`marketing_period_fetch_ads.py`（API 或 `--handfill`）。週報節奏見 [`marketing_weekly_ops_runbook.md`](./marketing_weekly_ops_runbook.md)。

## Focus／Segments

每週可換 `focus.theme`（如 hygiene｜japan）。日本無拆 Ads 時只用代理指標，禁偽 JP 花費。

## 停損

- **30 日**：Ads≥HKD200 且 external_new＝0 → Review；只准關鍵字／文案／落地；禁大功能。  
- **90 日**：Ads≥HKD600 且 external_new≤3 → Product Reassessment。

## 快照

集合 `marketing_period_snapshots`。唯一鍵 `(period_type, period_start)` upsert。禁 PII（無 email 列表）。只寫 `--env production`。

## 呼叫約定

```bash
python scripts/marketing_period_counts.py --period-start YYYY-MM-DD --period-end YYYY-MM-DD
# 需 GA4_PROPERTY_ID + GOOGLE_APPLICATION_CREDENTIALS（見 backend/.env.example）
python scripts/marketing_period_fetch_ga4.py --period-start YYYY-MM-DD --period-end YYYY-MM-DD
python scripts/marketing_period_fetch_ads.py --period-start YYYY-MM-DD --period-end YYYY-MM-DD
# 或：… --handfill --spend-hkd N --clicks N --impr N
python scripts/marketing_period_assemble.py --period-start YYYY-MM-DD --period-end YYYY-MM-DD --ga4-file ga4.json --ads-file ads.json
python scripts/marketing_period_upsert.py --env production --file draft.json
python scripts/marketing_period_export_sheet.py --period-start YYYY-MM-DD --out docs/evidence/marketing/ops_weekly.csv
python scripts/marketing_period_funnel_signup_compose.py --period-start YYYY-MM-DD --period-end YYYY-MM-DD
python scripts/marketing_period_rollup.py --period-start YYYY-MM-DD --period-end YYYY-MM-DD
```

stdout＝JSON（export＝CSV）。Sheet／Looker：[`marketing_looker_sheet_setup.md`](./marketing_looker_sheet_setup.md)。  
Measurement ID `G-F38Q4L6CPV` ≠ Property ID；後者為數字。

## 分析稿六段

1. 期間／env／provisional／schema_version  
2. core 表（含來源）  
3. 對帳（Mongo vs GA4）  
4. focus  
5. 燈號＋≤3 決策（待拍板）＋停損旗標  
6. 擬寫入 JSON  

## 呈現

Looker 一頁：GA4 流量＋強制 Mongo／Valid／Email／Ads 卡；本週橙／上週灰 WoW。決策層＝六段稿＋快照。
