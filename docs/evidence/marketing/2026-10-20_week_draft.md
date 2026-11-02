# 行銷營運週報（已拍板 · 2026-10-29 完整重跑）

依 `docs/marketing_analytics_ai_contract.md`。禁止改 KPI 定義。

## 1. 期間／環境／provisional

| 項 | 值 |
|----|-----|
| period | week · 2026-10-20～2026-10-26 HKT（一～日） |
| prev_week | 2026-10-13～2026-10-19 |
| env | production |
| schema_version | 1 |
| provisional | **false**（GA4 Internal Traffic＝有效） |
| focus.theme | hygiene |
| 執行日 | 2026-10-29（四）提前跑完整週一 runbook |

## 2. Core 數字

| 指標 | 值 | 來源 |
|------|-----|------|
| external_new_users | **2** | Mongo counts |
| external_total_users | **7** | Mongo counts |
| valid_members | **0** | Mongo（生成成功＋扣點） |
| active_users_30d | **4** | Mongo |
| successful_generations | **0** | ledger ae_compose* |
| email_subscribers_total | **6** | Mongo（≠ customer） |
| email_subscribers_new | **2** | Mongo |
| ads_spend_hkd / clicks / impr | **35.17／19／2196** | Ads API（LOGIN MCC `7309466170`） |
| ga4_sign_up / generate_post / purchase | **7／11／0** | GA4 Data API property `557136140` |
| revenue_usd | **null／0** | 本週無 Stripe |
| founder_noise | **medium** | CEO 同意 |
| traffic_light | **yellow** | CEO 同意 2026-10-28；2026-10-29 重 upsert |

## 3. 對帳

- 客戶／新客分母只認 Mongo：本週外部新客 **2**，存量 **7**。  
- GA4 `sign_up`＝7 **不可**當成 7 個外部客戶。  
- 有新客但 **valid_members＝0**、**successful_generations＝0** → 註冊未換成產文／扣點。  
- 漏斗：新客 2 → compose 0；breakpoint＝`signup_to_first_compose`。

## 4. Focus（hygiene）

- 到達維持 `/language`；持續搜尋字詞清理。  
- 本週不設 japan（Ads 未拆；無真實 JP 花費）。  
- 優先：註冊→首次 compose 摩擦（產品側 #127／#128 已合；下週再看漏斗是否改善）。

## 5. 燈號與 ≤3 決策（已拍板）

- 燈號：**yellow**  
- 停損：未觸發 30 日 Review（Ads 週花費 35.17 ≪ 200；new≠0）。  
- D1：不加薪預算（`hold_budget_small`）。  
- D2：查註冊→首次產文（`investigate_signup_to_first_compose`）。  
- D3：GA4 provisional 已清；Ads API 取代 handfill；MCC LOGIN 已確認。

## 6. 快照

- 草稿：`2026-10-20_week_draft.json`  
- upsert：`2026-10-20_week_upsert.json`（production · 2026-10-29）  
- Sheet 匯出：`ops_weekly.csv` → 貼入 `AlterEgo_ops_weekly`（Looker 自動刷新）
