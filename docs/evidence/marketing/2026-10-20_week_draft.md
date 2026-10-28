# 行銷營運週報（草稿 · 待 CEO 拍板）

依 `docs/marketing_analytics_ai_contract.md`。禁止改 KPI 定義。

## 1. 期間／環境／provisional

| 項 | 值 |
|----|-----|
| period | week · 2026-10-20～2026-10-26 HKT（一～日） |
| prev_week | 2026-10-13～2026-10-19 |
| env | production（Mongo 唯讀 counts） |
| schema_version | 1 |
| provisional | **true**（GA4 內部篩選仍「測試中」；手填 ga4_* 前維持） |
| focus.theme | hygiene |

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
| ads_spend_hkd / clicks / impr | **null**（無後台 API；下週補） | Ads |
| ga4_sign_up / generate_post / purchase | **null**（下週補） | GA4 |
| revenue_usd | **0** | 本週無 Stripe；US$3 在 10-15 |
| revenue_hkd_equiv | **0**（×7.8） | 僅顯示 |
| founder_noise | **medium** | CEO 同意 |
| traffic_light | **yellow** | CEO 同意 2026-10-28 |

## 3. 對帳

- 客戶／新客分母只認 Mongo：本週外部新客 **2**，存量 **7**。  
- GA4 事件數（待填）**不可**當成外部客戶數。  
- 有新客但 **valid_members＝0**、**successful_generations＝0** → 註冊未換成產品價值（產文／扣點）。

## 4. Focus（hygiene）

- 維持到達 `/language`；持續搜尋字詞清理。  
- 本週不設 japan（Ads 未拆；無真實 JP 花費）。  
- 優先搞清楚：新客為何沒有 generate_post／Post Kit 成功路徑。

## 5. 燈號與 ≤3 建議決策（待拍板）

- 燈號：**yellow**（CEO 同意）  
- 停損：本週 new＝2 → 未觸發 30 日「new＝0」門；Ads null 故 spend 門暫不評。  
- D1：不加薪預算；待 Ads／GA4 補齊再談出價。  
- D2：查「註冊→首次產文」摩擦（本週 0 成功生成）。  
- D3：GA4 篩選改「有效」後取消 provisional。

## 6. 擬寫入快照 JSON

見 `2026-10-20_week_draft.json`。CEO 同意後執行 upsert（production）。
