# Welcome／主題卡改版 · GA4 中檢 Day4

> **撰寫**：2026-11-16（星期一）  
> **改版日**：2026-11-12（PR #132～#136 訪客入口／禮遇卡／CTA）  
> **性質**：中檢（非整段 Day14）。正式 Day14 對照約 **2026-11-26**。  
> **SoT**：[docs/marketing_welcome_ga4_measurement.md](../../marketing_welcome_ga4_measurement.md)

## §1 上週改動簽查（定稿）

| 日 | PR／項 | 範圍 | 對訪客可見行為 |
|----|--------|------|----------------|
| 11-09 | **#131** | 產卡多樣性空報告 KeyError | 穩定每日 15；非 Welcome UI |
| 11-12 | **#132** 等 A0–A9 | Welcome 1大+2小×三類；`/`→Dashboard；詳情同分類小卡；`topic_open`／dwell | 進站先看卡 |
| 11-12 | 全寬度／Hero→Dashboard | 桌面也顯示卡；`btn-landing-register`→`/dashboard` | 逛卡路徑 |
| 11-12 | `before_date` 舊卡 | TopicDetail 相關 3 小卡 | 詳情留存 |
| 11-12 | 扣點彈窗 Option B | 速度向文案 | 生成才要登入 |
| 11-12 | **#134／#135** | Welcome 黑卡／詳情白卡 | CTA 視覺 |
| 11-12 | **#136** | `welcome_cta_click`／`guest_charge_cta_click`＋`cta_id` | 量測上線 |

不計入：#138 i18n 稽核、#139 GSC。

## §2 對照窗（HKT）

| 窗 | 日期 | 天數 | 證據 |
|----|------|------|------|
| 改版前 | 2026-11-02～11-11 | 10 | `2026-11-02_pre_ship_ga4_traffic.json`／`_ga4.json` |
| 改版後 | 2026-11-12～11-15 | 4 | `2026-11-12_post_ship_ga4_traffic.json`／`_ga4.json` |
| 事件摘錄 | 同上 | — | `2026-11-16_welcome_midcheck_events.json` |

`provisional=false`；property `557136140`。

## §3 流量與 Core 事件

| 指標 | 前（10 日） | 後（4 日） | 粗日均 前→後 |
|------|------------:|----------:|-------------|
| sessions | 28 | 14 | 2.8 → 3.5 |
| engaged_sessions | 14 | 5 | 1.4 → 1.25 |
| page_views | 94 | 22 | 9.4 → 5.5 |
| ga4_sign_up | 1 | 0 | — |
| ga4_generate_post | 10 | 0 | — |
| ga4_purchase | 0 | 0 | — |

### 落地頁（sessions）

| Landing | 前 | 後 |
|---------|---:|---:|
| `/language` | 23 | （後窗未進前三） |
| `/welcome` | 2 | 1 |
| `/dashboard` | 1（含 `?tab=food`） | **9** |
| `/ja` | — | 4 |
| `/en` | 1 | — |

### 來源 medium（sessions）

| medium | 前 | 後 |
|--------|---:|---:|
| cpc | 19 | 1 |
| (none) | 6 | 7 |
| referral | 3 | 4 |
| organic | — | 2 |

後窗付費幾乎停（cpc 1），與前窗不可直接比轉換率。

## §4 CTA／主題事件（Data API）

| 事件 | 前 | 後 |
|------|---:|---:|
| `welcome_cta_click` | 0 | **1** |
| `guest_charge_cta_click` | 0 | 0 |
| `topic_open`／`topic_dwell` 等 | 未見 | 未見 |

- 自訂維度 `cta_id`：**尚未**在 GA4 註冊（API：`customEvent:cta_id` invalid）。Explore 細拆 `hero_start`／`offer_register` 需先建 Event-scoped 維度。  
- 正式域 11-12 Network 手測曾 PASS（`offer_register`）；後窗總量僅 1 次 click。

## §5 中檢一句

**樣本不足僅觀察**：落地已明顯從 `/language` 轉向 **`/dashboard`（9/14）**，符合訪客入口改版；但後窗付費冷、`sign_up`＝0、`generate_post`＝0、CTA 幾乎無量。**不**判健康／註冊掉。正式 **Day14（2026-11-26 星期四）** 再跑完整 14 日前後＋Explore `cta_id`。

## §6 待人手（GA4 UI）

1. 管理 → 自訂定義：Event-scoped **`cta_id`**（參數名 `cta_id`）  
2. Explore：後窗 `welcome_cta_click` 依 `cta_id`  
3. **11-19 前勿**標 Key event
