# Welcome 改版 · GA4 量測清單（A／B／C）

> **Ship 日（產品 UI）**：2026-11-12 · PR **#134**／**#135**（黑卡禮遇）  
> **CTA 事件上線日**：以本文件合入 `main` 之 merge 日為準（工作記錄再註）  
> **合約**：[`marketing_analytics_ai_contract.md`](./marketing_analytics_ai_contract.md) — **人＝Mongo**；**事件＝GA4**；`sign_up` ≠ 客戶數  
> **Measurement ID**：`G-F38Q4L6CPV`（≠ Property ID）

---

## A. 立刻（GA4 UI · 零改碼／本檔合入後仍須手做）

### A1. Annotations（註記）— ✅ 2026-11-12 已建（info@）

| 日期 | 標題 | 說明 |
|------|------|------|
| 2026-11-12 | `Welcome gift card #134/#135` | `black mono gift card on Welcome` |
| 2026-11-12 | `Welcome GA4 CTA events live #136` | `welcome_cta_click / guest_charge_cta_click` |

### A2. 14 日前後 Explore

Explore → 自由形式：

- **對照窗**：改版前 14 日 vs 改版後 14 日（HKT；勿只比 1～2 天）
- **維度**：Landing page、Session source/medium、Device category
- **指標**：Sessions、Engaged sessions、Event count（`sign_up`、`generate_post`）
- **篩選 Landing**：含 `/welcome`、`/en`、`/ja`、`/language`

### A3. 週報 KPI

**不改** Core 定義與 `marketing_period_fetch_ga4.py` 的 `EVENTS = (sign_up, generate_post, purchase)`。  
CTA 事件先在 Explore 看；**勿**把 `sign_up` 當外部新客。

---

## B. 程式事件（已實作）

| 事件名 | 參數 `cta_id` | 觸發 | 檔案 |
|--------|---------------|------|------|
| `welcome_cta_click` | `hero_start` | Hero「免費開始」→ `/dashboard` | `Welcome.tsx` · `btn-landing-register` |
| `welcome_cta_click` | `offer_register` | 黑卡「立即行動」→ `/register` | `GuestCreditOfferCard` · mono |
| `guest_charge_cta_click` | `register` \| `login` \| `cancel` | 詳情白卡彈窗 | `GuestCreditOfferCard` · modal |

- **Production-only**（`import.meta.env.PROD`）；本機 dev **不送**。  
- **無 PII**（無 email／user id）。  
- **不**觸發 Ads conversion（與 `sign_up` 分離）。  
- `/guest-charge-sample`：`analyticsEnabled={false}`。

### B1. GA4 後台（事件上線後 1～2 日）

1. Reports → Events：確認 `welcome_cta_click`、`guest_charge_cta_click` 出現（管理「事件」列表可能延遲）。  
2. 自訂維度（若尚未有）：Event-scoped `cta_id`（參數名 `cta_id`）。  
3. **7 日內不要**標為 Key event；觀察後再決定（避免污染 Ads `sign_up`）。

### B2. 正式域手測 — ✅ 2026-11-12 PASS

- 網址：`https://www.ai-alterego.com/welcome` → 黑卡「立即行動」  
- DevTools Network：`collect` Payload → **`en=welcome_cta_click`**、**`ep.cta_id=offer_register`**、`dl=…/welcome`（HTTP 204）  
- 注意：勿只看 `page_view`（`/register`）；即時總覽可能為 0（內部流量篩選），以 Network 為準

---

## C. 判讀規則（Day 14 填工作記錄）

| 形狀 | 訊號 | 動作 |
|------|------|------|
| **健康** | Welcome engaged ↑；`offer_register` → `/register` → `sign_up` 比率持平或↑ | 維持；週報一句 PASS |
| **逛卡成功、註冊未動** | `hero_start`／dashboard／topic 瀏覽↑；`sign_up` 平 | 調黑卡位置／文案；**不**改扣點 |
| **註冊掉** | `sign_up`↓ 且 `offer_register` 被 `hero_start` 壓過 | 先調 CTA 優先；**不**先加 Ads 預算 |
| **停損** | 仍走合約 30／90 日 Ads×新客 | 不變 |

### Day 14 模板（貼工作記錄）

```text
Welcome GA4 Day14（HKT YYYY-MM-DD～）：
- landing /welcome sessions／engaged：前 __ → 後 __
- welcome_cta_click hero_start／offer_register：__／__
- guest_charge_cta_click register：__
- ga4 sign_up：前 __ → 後 __
- Mongo external_new_users：前 __ → 後 __
- 一句結論：健康／逛卡未註冊／註冊掉／其他
```

---

## 刻意不做

- 不改扣點金額、每日 15、`generate_content`、凍結 tag  
- 不把 CTA 事件寫進 Core `schema_version`／週報人數卡  
- 不為示範頁灌事件  
