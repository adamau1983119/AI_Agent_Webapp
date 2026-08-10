# v8 正式域 — 日常運作與客戶體驗（CX／OPS）

> **狀態（2026-08-10）**：產品**已正式上架**。預設工作＝**真實客戶體感**＋**日常運作煙霧**，不再預設 v7 Day／PD／程式段。  
> **觸發**：`專案開始，正式域日常運作，客戶體驗優先 @AGENTS.md`  
> **證據**：`docs/evidence/v8/YYYY-MM-DD/`（截圖或 Network 一句才可勾）  
> **改碼**：僅 **CX／OPS FAIL 阻塞客戶** 才開 `feature/v8-*`＋PR；禁止為測試改預設架構。  
> **逐頁改善程序**：[`v8_page_by_page_cx.md`](./v8_page_by_page_cx.md)（Discuss→Inventory→Atom→Verify→Record；**確認原子後才改碼**）。  
> **OBS／日報 SoT**：[`v8_observability_alerting.md`](./v8_observability_alerting.md) · 備份 [`2026-08-10_ops_digest_smtp_block_snapshot`](./backups/2026-08-10_ops_digest_smtp_block_snapshot/SNAPSHOT_README.md)

---

## 代號總表（現行）

| 族 | 代號 | 客戶／營運問題 | 最短驗法 |
|----|------|----------------|----------|
| **CX** | **CX-LOGIN** | 能登入正式域、語系可切 | `ai-alterego.com` 登入 → Dashboard |
| **CX** | **CX-AE** | Alter Ego 主路可用 | extract／skip／regenerate 其一＋截圖 |
| **CX** | **CX-TOPIC** | 主題卡隨介面語系（尤其 **en／ja**） | 切 en／ja → 標題摘要對語系 |
| **CX** | **CX-MC** | My Channel 真實 feed | `/my-channel` 有卡或可解鎖 |
| **CX** | **CX-PK** | Post Kit 可仿文／複製 | 詳情 Post Kit copy＋toast |
| **OPS** | **OPS-HEALTH** | API／DB 活著 | `api…/health` → 200、`database: connected` |
| **OPS** | **OPS-CARD** | 當日有自動產卡 | Dashboard／Mongo 今日新 topic |
| **OPS** | **OPS-I18N** | 新卡含三語預寫 | 新 topic 有 `titles_i18n.en`＋`.ja` |
| **OPS** | **OPS-DIGEST** | 正式域每日營運報告進信箱 | Deploy log `digest_sent` **或** 信箱自動收到（**非**本機手動） |
| **OPS** | **OPS-COST** | 成本未失控 | DeepSeek／DeepL 用量或告警一句 |
| **FIX** | **FIX-*** | 上列 FAIL 且阻塞客戶 | 最小 PR；結案對回 CX／OPS |

---

## OPS-DIGEST 現況（2026-08-10）

| 項 | 狀態 | 一句 |
|----|------|------|
| Watchdog／digest loop | ✅ | `WATCHDOG_START digest=True` |
| 本機強制寄（樣式） | ✅ | `digest_sent`；信箱已收 |
| **正式域自動進信箱** | ❌ **FAIL** | `smtp.gmail.com:587` timeout（Hobby 擋 SMTP） |
| 正式解 | ⏳ | Railway **Pro** 或改 `EmailService` **HTTPS**（旁路 GHA／本機排程 **不作正式解**） |
| checklist | **PD-OBS-TL-07b `[!]`** | 見 observability 檔 |

---

## 每日建議順序（約 45′～90′）

1. **OPS-HEALTH**（正式域）  
2. **OPS-CARD**＋**OPS-I18N**（今日新卡）  
3. 任選 **1～2 個 CX-***（用**真實帳號**，勿訪客當 PASS）  
4. **OPS-DIGEST**／**OPS-COST**（有則勾；DIGEST 須正式域自動，勿用本機代勾）  
5. 有 FAIL → 記 **FIX-***；無則不改碼  

---

## 與舊代號對照（封存 · 勿作預設）

| 舊 | 新 |
|----|-----|
| Day1／E0-AE-*／CD-AE-* | **CX-AE**（煙霧） |
| Day2／E0-MC／PK* | **CX-MC**／**CX-PK** |
| Day3／Discover CD-4 | 上線後選測；非每日必過 |
| PD-*／程式段 Phase | **禁止**再開；僅 FIX 最小修 |
| VM-*／全量 C* | **OPS-COST** 煙霧即可 |

---

## 當日勾選（複製到工作記錄）

```text
日期：
OPS-HEALTH：
OPS-CARD：
OPS-I18N：
CX-（選）：
OPS-DIGEST／COST：
FAIL／FIX：
明日第一步：
```
