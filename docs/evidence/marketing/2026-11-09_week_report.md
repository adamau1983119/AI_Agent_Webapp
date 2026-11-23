# 行銷營運週報（2026-11-09～11-15）＋Welcome 中檢

> **撰寫**：2026-11-16（星期一）· Cursor 代 WorkBuddy（本機 script；零產品碼）  
> **期間**：HKT 週一～週日 **2026-11-09～2026-11-15**  
> **SoT**：[`docs/marketing_weekly_ops_runbook.md`](../../marketing_weekly_ops_runbook.md)  
> **視覺**：[`ops_weekly_visual_2026-11-16.html`](./ops_weekly_visual_2026-11-16.html)／[`.png`](./ops_weekly_visual_2026-11-16.png)  
> **中檢全文**：[`2026-11-16_welcome_ga4_midcheck.md`](./2026-11-16_welcome_ga4_midcheck.md)

## 1. 期間／燈號／一句總結

| 項 | 值 |
|----|-----|
| period | week · **2026-11-09～2026-11-15** HKT |
| 對照視覺上週 | **2026-10-27～11-02**（11-02～08 本輪不補跑） |
| env | production |
| provisional | **false** |
| traffic_light | **yellow**（沿用 hygiene；**production upsert ⏳ 待你確認燈號**） |
| focus.theme | hygiene |
| 停損 | `review_30d=false`／`reassess_90d=false`（trailing30d Ads ≈ **93.38** HKD；new＝0 但未達 200 門檻） |

**一句**：流量仍在（sessions **24**／engaged **10**；Ads **26.63／18／808**），但 Mongo 外部新客與 compose 皆 **0**；落地已見 Welcome 改版訊號（`/dashboard`＝**9** 與 `/language`＝**9** 並列），轉換仍薄——維持黃燈、不加薪預算。

## 2. KPI

| 指標 | 本週 | 來源 |
|------|-----:|------|
| external_new_users | **0** | Mongo counts |
| external_total_users | **8** | Mongo |
| valid_members | **0** | Mongo |
| active_users_30d | **5** | Mongo |
| successful_generations（compose） | **0** | Mongo |
| email_subscribers_total／new | **6／0** | Mongo |
| ga4_sign_up | **1** | GA4 Data API（≠ 外部新客） |
| ga4_generate_post | **5** | GA4 |
| ga4_purchase | **0** | GA4 |
| ads_spend_hkd／clicks／impr | **26.63／18／808** | Ads API `9708645947` |
| sessions／engaged_sessions | **24／10** | GA4 traffic |
| page_views | **71** | GA4 traffic |
| revenue_usd | — | 無資料 |

## 3. 落地／來源（traffic）

### Landing（sessions）

| Landing | sessions |
|---------|---------:|
| `/dashboard` | **9** |
| `/language` | **9** |
| `/ja` | 4 |
| `/dashboard?tab=food` | 1 |
| `/welcome` | 1 |

### Medium（sessions）

| medium | sessions |
|--------|---------:|
| (none) | 8 |
| cpc | 8 |
| referral | 6 |
| organic | 2 |

### Device／Country（摘要）

- Device：mobile **19**／desktop **5**  
- Country 前段：Taiwan 8、Hong Kong 6、Afghanistan 3、Japan 3、United States 2

## 4. Welcome／主題卡改版中檢（併入）

改版落點 **2026-11-12**（PR #132～#136）落在本週期內。中檢 Day4（非 Day14）：

| 對照 | 前 11-02～11-11（10 日） | 後 11-12～11-15（4 日） |
|------|------------------------:|-----------------------:|
| sessions | 28 | 14 |
| engaged | 14 | 5 |
| 主落地 | `/language` **23** | **`/dashboard` 9** |
| ga4_sign_up | 1 | **0** |
| ga4_generate_post | 10 | **0** |
| `welcome_cta_click` | 0 | **1** |
| 後窗 cpc | — | **1**（付費冷，不可硬比轉換） |

**中檢一句**：落地已明顯改偏 `/dashboard`，符合訪客入口改版；CTA＝1、`sign_up`＝0——**樣本不足僅觀察**。正式 **Day14＝2026-11-26（星期四）**。  
細節與簽查表 → [`2026-11-16_welcome_ga4_midcheck.md`](./2026-11-16_welcome_ga4_midcheck.md)。

## 5. 漏斗（黃燈）

| 項 | 值 |
|----|-----|
| external_new_in_period | **0** |
| new_with_compose_in_period | **0** |
| breakpoint | `none_or_n_a`（本週無新外部客可追） |
| 延續觀察 | 既有外部池仍 **0** ever-composed；決策保留 `investigate_signup_to_first_compose` |

證據：`2026-11-09_funnel_signup_compose.json`。

## 6. 決策（暫沿用 yellow）

- D1 `hold_budget_small`（不加薪）  
- D2 `investigate_signup_to_first_compose`  
- D3 `watch_compose_after_pr128`  
- D4 `watch_welcome_dashboard_landing`（本週新增觀察）

**未**觸發停損加預算／砍預算。production **upsert ⏳**——確認燈號後再跑 `marketing_period_upsert.py`。

## 7. 缺口／下一步

| 項 | 狀態 |
|----|------|
| GA4 Event-scoped `cta_id` | ⏳ 人手註冊（API 仍 invalid） |
| Key event 標註 | ⏳ **11-19 前勿標** |
| Day14 完整前後窗 | **2026-11-26（四）** |
| 11-02～11-08 週報補跑 | **另開**（本輪刻意不混窗） |
| Mongo production upsert | ⏳ 待確認 yellow |
| Sheet | ✅ 本機 CSV 已含 11-09；SA 覆寫 `ops_weekly` **5** 列（含本週）；user OAuth `write_sheet` refresh **400** 降級已避開 |
| Looker | 刷新資料源即可；未改產品碼 |

## 8. 產物清單

| 檔 | 狀態 |
|----|------|
| `2026-11-09_counts.json` | ✅ |
| `2026-11-09_ga4.json` | ✅ |
| `2026-11-09_ga4_traffic.json` | ✅ |
| `2026-11-09_ads.json` | ✅ Ads API |
| `2026-11-09_week_assembled.json` | ✅ |
| `2026-11-09_week_draft.json` | ✅ yellow |
| `2026-11-09_week_upsert_PENDING.json` | ⏳ 非 production upsert |
| `2026-11-09_funnel_signup_compose.json` | ✅ |
| `ops_weekly_visual_2026-11-16.html`／`.png` | ✅ |
| `ops_weekly.csv`／`ops_weekly_2026-11-09.csv` | ✅ |
| `2026-11-09_week_report.md` | ✅ 本檔 |

❌ 未改 i18n／按鈕／產卡／扣點／`api/v1`。
