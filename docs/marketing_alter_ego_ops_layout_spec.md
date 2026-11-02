# Alter Ego Ops · 週報版面規範（SoT）

**用途**：WorkBuddy／Looker 交付「每週營運週報」時的**視覺與結構契約**。  
**不**從頭重建報表；對齊已建 Looker **Alter Ego Weekly Ops**，版面以本檔＋sample 為準。  
**Sample 圖**：[`evidence/marketing/alter_ego_ops_weekly_sample.jpg`](./evidence/marketing/alter_ego_ops_weekly_sample.jpg)（mock；非正式數）。

相關：[`marketing_weekly_ops_runbook.md`](./marketing_weekly_ops_runbook.md)、[`marketing_looker_sheet_setup.md`](./marketing_looker_sheet_setup.md)、[`marketing_analytics_ai_contract.md`](./marketing_analytics_ai_contract.md)。

---

## 1. 頁面身份

| 項 | 規範 |
|----|------|
| 品牌主標 | **Alter Ego Ops**（最大、粗） |
| 副標 | **Weekly Report** |
| 區間 | **This Week vs Last Week** · HKT **Mon–Sun** |
| 頁尾 | `Mongo denominator for customers · GA4 for traffic only`；並標 **Report Schema Version: v1.0**（顯示用，不升 `schema_version`） |
| 正式版 | **禁止**留「Sample mock, not live data」 |

---

## 2. 色票

| Token | 用途 | 建議色碼 |
|-------|------|----------|
| `brand.orange` | This week、Desktop 環、強調 | `#E85D04` |
| `brand.orangeSoft` | 淺強調／地圖低熱力 | `#F4A261` |
| `neutral.grey` | Last week、Mobile 環 | `#9CA3AF` |
| `neutral.greyDark` | 軸線／次要標籤 | `#6B7280` |
| `surface.page` | 畫布底 | `#F3F4F6` |
| `surface.card` | 分數卡底 | `#FFFFFF` |
| `text.primary` | 主數字、標題 | `#111827` |
| `text.muted` | 卡標、頁尾 | `#6B7280` |
| `delta.up` | WoW 上升 | `#16A34A` |
| `delta.down` | WoW 下降 | `#DC2626` |
| `light.yellow` | `traffic_light=yellow` | `#EAB308` |
| `light.green` | `traffic_light=green` | `#16A34A` |
| `light.red` | `traffic_light=red` | `#DC2626` |

**圖例固定**：This week＝**orange**；Last week＝**grey**。Looker 色票選最接近即可，勿改成紫系／深色主題。

---

## 3. 字級／層級

Looker 無專屬品牌字檔時用**系統無襯線**（近似 Inter／Roboto）。重點＝層級，不鎖 font 檔名。

| 元素 | 層級 |
|------|------|
| Alter Ego Ops | 最大、粗 |
| Weekly Report／區間說明 | 次級 |
| 分數卡主數字 | 大、粗、`text.primary` |
| 卡標題（Sessions 等） | 小、`text.muted` |
| WoW％與 last-week 對照 | 更小；升=`delta.up`、降=`delta.down` |
| 圖表標題 | 中小、粗 |
| 頁尾 | 最小、`text.muted` |

Traffic light 卡：主顯示 **YELLOW／GREEN／RED**（或中英對照），可附短註（如 Normal／Warning）；顏色跟 `light.*`。

---

## 4. 排版結構（固定）

由上到下，**一頁講完**：

```
[ 標題區：Alter Ego Ops / Weekly Report / This Week vs Last Week ]
[ 分數卡 × 6 橫排（窄屏可折 2×3）]
[ 第二列：Valid members | Email subscribers | Revenue（Stripe USD）]
[ 中列：Sessions by medium | Top landing pages ]
[ 下列：Sessions by country（地圖＋Top） | Device category ]
[ 頁尾鐵律 ]
```

### 4.1 頂列分數卡（必備 6）

| 順序 | 卡名 | 資料來源 |
|------|------|----------|
| 1 | Sessions | GA4 原生 |
| 2 | Engaged sessions | GA4 原生 |
| 3 | External new users (Mongo) | Sheet ← Mongo |
| 4 | Ads spend HKD | Sheet ← Ads |
| 5 | GA4 sign_up (events) | Sheet 或 GA4（事件≠客戶） |
| 6 | Traffic light | Sheet ← CEO |

卡樣式：`surface.card` 底、細邊或輕陰影、小圓角；主數字偏上；WoW 在下。

頂列維持 6 張。不把 Valid members 插進這列。

### 4.1b 第二列（人與錢，不進頂列）

與頂列同一張卡樣式，左起：

| 順序 | 卡名 | 資料來源 |
|------|------|----------|
| 1 | Valid members | Sheet ← Mongo：外部 ∧ 期間成功生成 ∧ 期間至少 1 筆扣點。≠ GA4 `sign_up` |
| 2 | Email subscribers | Sheet ← Mongo：`email_subscribers_total`；註 total／new。訂閱者 ≠ 客戶 |
| 3 | Revenue (Stripe USD) | Stripe USD；無資料顯示 —。HK$ 僅顯示（×7.8），禁 ROI 混幣，不用 `ga4_purchase` |

### 4.2 中列圖

- **Sessions by medium**：橫條；Last week 灰／This week 橘（organic／cpc／referral／(none) 等）。
- **Top landing pages**：橫條；至少涵蓋 `/language`、`/welcome`、`/en`、`/ja`（有數才顯示）。

### 4.3 下列圖

- **Sessions by country**：世界地圖熱力＋Top countries 橫條（常見 HK／US／JP／KR／TW）。註記必須含 **Learning Signal Only**（樣本過小，勿用單週值做市場結論）。
- **Device category**：甜甜圈；Desktop＝橘、Mobile＝灰（有 tablet 時另用淺灰，勿搶主色）。

### 4.4 禁改

- 不把人數卡改成只讀 GA4 users。
- 不新增第一屏雜訊（多餘 KPI 條、促銷貼紙）。
- 不另開第二套「從頭設定」的 Looker 報表取代本契約（沿用既有報表 ID 擴充）。

---

## 5. 資料鐵律（與合約一致）

- **人／客戶分母**＝Mongo 外部（Sheet 卡）。
- **流量**＝GA4（sessions、medium、landing、geo、device）。
- **花費**＝Ads HKD。
- GA4 `sign_up` **不可**當成外部新客數。

---

## 6. WorkBuddy 交付檢查

每週交付前對照：

- [ ] 版面結構符合第 4 節（頂列 6 卡＋第二列 Valid／Email／Revenue＋四圖區＋頁尾 schema v1.0）
- [ ] 色／圖例符合第 2 節（橘＝本週、灰＝上週）
- [ ] 人數／Ads／燈號來自當週 Sheet／快照（非手貼過期 CSV）
- [ ] 頁尾無 mock 字樣；數為當週 production
- [ ] 六段分析稿另交（合約）；本檔只管儀表版面

---

## 7. 變更

改色票或增刪第一屏模組＝改本檔並知會 CEO；**禁**私改 KPI 定義（見合約）。
