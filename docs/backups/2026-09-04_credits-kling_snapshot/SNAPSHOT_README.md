# Snapshot — 2026-09-04 登入點數＋Stripe 一次購買（PR #59）

## 1. 摘要

本快照封存 **PR #59 已合 `main`**（merge `72b18a0`，程式 `71869e6`）之金流：

1. **帳本 SoT** = Mongo `credit_wallets`（免費 lots + 已購）。正式域無 Redis 不擋點數。
2. **免費**：歡迎 3 次登入各 +10（舊戶 `initial_grant` 先 +5 補滿第一檔）；之後每日 HKT +5；免費未到期帽 10；每筆 7 日到期。
3. **購買**：Stripe Checkout `mode=payment` US$3=180／US$5=350／US$10=800；已購不過期。未設金鑰 → Checkout **503**。
4. **扣點**：未過期免費 FIFO → 已購。Compose／My Channel unlock 仍 1 點。
5. **未改**：翻譯核心、`generate_content`、每日 15 張公眾卡。

**精選照片 4 張 2×2** 仍在 `feature/v8-featured-photos`（`d3b5b1e`），**未合 main**。

## 2. Git／PR

| 項 | 值 |
|:---|:---|
| 程式基線 | `main` `72b18a0`（PR #59） |
| 改碼前備份 | `backup/2026-09-04-pre-credits` |
| 合入後備份 | `backup/2026-09-04-credits-kling-merged` |
| 照片 WIP 備份 | `backup/2026-09-04-featured-photos-wip`（未合 main） |
| PR | [#59](https://github.com/adamau1983119/AI_Agent_Webapp/pull/59) |

## 3. 正式域（Railway · 2026-09-04 02:52 UTC）

| 項 | 狀態 |
|:---|:---|
| 容器／Uvicorn | ✅ `0.0.0.0:8080` startup complete |
| Mongo | ✅ `ai_agent_webapp` ping 成功 |
| 排程 | ✅ 04:00 HKT；`ensure_today_topics` **15/15 略過補產** |
| Redis | ⚠️ `localhost:6379` 拒連＝正式機無 Redis（預期；點數走 Mongo） |
| `AUTO_START_SCHEDULER` env 警告 | ⚠️ 假警報（隨後排程已啟動） |
| Stripe env | ⏳ 啟動 log 未證實；未設則 Checkout 503 |
| Mongo URI 打進 log | ⚠️ `main.py` 印 URI 前 50 字含帳密開頭 — **請 Atlas 輪換密碼**；勿把連線字串貼聊天 |

## 4. 備份檔案清單

| 檔案 | 說明 |
|:---|:---|
| `billing.py` | packs／balance／checkout／webhook |
| `credit_ledger_service.py` | 公開帳本 API（wallet SoT） |
| `credit_grants.py` | 歡迎 10×3、每日 +5、帽 10 |
| `credit_wallet.py` | 到期、FIFO |
| `credit_packs.py` | 三檔常數 |
| `credit_stripe.py` | Checkout；無金鑰不 ready |
| `credit_store.py` | Mongo wallets |
| `credit_ledger_io.py` | ledger 冪等 |
| `check_mychannel_bf_static.py` | PD-MC1-02 改認歡迎／每日常數 |

## 5. Railway 金流 env（值勿進 git）

```env
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
```

Webhook：`https://api.ai-alterego.com/api/v1/billing/webhook`

## 6. 回滾

- 金流：revert PR #59（`72b18a0`）或切回 `backup/2026-09-04-pre-credits`。
- 照片：尚未在 main，無需回滾。
