# v8 Observability／告警（紅綠燈 · 24h Watchdog）

> **SaaS**：Incident Alerting + Uptime Watchdog  
> **正確行為**：正式域 Webapp（Railway）每日 ≥**08:00 HKT** 由 `EmailService` 自動寄「每日營運報告」到 `OBS_OPS_EMAIL`（綠燈也寄）；紅燈另即時告警。**不依賴**本機排程／GitHub Actions。  
> **日期**：2026-08-10（對照 [`calendar_2026_reference.md`](./calendar_2026_reference.md)）  
> **備份**：`backup/2026-08-10-ops-digest-smtp-block` · [`docs/backups/2026-08-10_ops_digest_smtp_block_snapshot/`](./backups/2026-08-10_ops_digest_smtp_block_snapshot/SNAPSHOT_README.md)  
> **分支（歷史）**：`feature/v8-observability-alerting`（程式已合／Deploy）；當日診斷分支勿當正式解  

---

## 初期：每日營運報告（綠燈也寄）

| env | 預設 | 說明 |
|-----|------|------|
| `OBS_DAILY_DIGEST_ENABLED` | `false` | `true`＝每天一封報告 |
| `OBS_DAILY_DIGEST_HOUR_HKT` | `8` | 香港時間幾點後才寄（配合 Watchdog 迴圈） |

與紅燈即時告警並行：綠燈安静告警仍保留；另外**每天一封**「每日營運報告」含【綠燈】／【紅燈】。

```bash
python scripts/send_obs_daily_digest_now.py   # 本機立刻寄一封（驗 Gmail／程式；≠正式域自動）
```

---

## 一眼看懂

| 燈 | 含義 | 電郵 |
|----|------|------|
| **綠燈** | 沒事・系統正常 | 紅燈通道：不寄；**每日報告**：會寄（若開 digest） |
| **紅燈** | 有事・請立即處理 | **立刻寄**＋每日報告也會標紅燈 |

---

## 現況核證（2026-08-10）

| 層 | 項目 | 狀態 | 證據／備註 |
|----|------|------|------------|
| L1 | Railway `OBS_*` 旗標 | ✅ | Variables 已對齊程式鍵名 |
| L2 | 本機 Gmail 寄信 | ✅ | `send_obs_daily_digest_now.py` → `digest_sent`；信箱已收 |
| L3 | 正式域 loop | ✅ | `WATCHDOG_START … digest=True`；`WATCHDOG_TICK green_quiet` |
| L4 | **正式域自動日報進信箱** | ❌ | `DIGEST_TICK digest_failed` → `Timed out connecting to smtp.gmail.com on port 587`（Railway Hobby／非 Pro **擋出站 SMTP**） |

**正式解（二選一 · 禁止旁路充當營運）**

1. **Railway 升 Pro** → Redeploy → 沿用現有 Gmail SMTP（程式不改）  
2. **改 `EmailService` 走 HTTPS 寄信**（平台允許的出站）→ Variables 對齊  

~~GitHub Actions／本機 Task Scheduler~~：**不作正式解**（非正式 Webapp 寄信路徑）。

---

## PD

- [x] **PD-OBS-TL-01** `traffic_light.py` 紅／綠判定  
- [x] **PD-OBS-TL-02** mailer 置頂【紅燈】／【綠燈】  
- [x] **PD-OBS-TL-03** `ops_agent` 僅紅燈寄信 + 冷卻  
- [x] **PD-OBS-TL-04** `ops_watchdog` 週期迴圈（env 閘）  
- [x] **PD-OBS-TL-05** `main.py` 閘門掛 Watchdog  
- [x] **PD-OBS-TL-06** `check_obs_traffic_light.py` PASS（live green_quiet）  
- [x] **PD-OBS-TL-07a** Railway：OBS 旗標 + Deploy；loop 已啟動（2026-08-10 log）  
- [!] **PD-OBS-TL-07b** 正式域自動每日報告進信箱 — **FAIL**（SMTP:587 timeout；見上「正式解」）  
- [ ] **PD-OBS-TL-08** 密鑰輪換（聊天曾外洩之 App Password／API key）  
- [ ] **PD-OBS-TL-09** 選正式解 ① Pro 或 ② HTTPS `EmailService` → Redeploy → log `digest_sent`＋信箱自動收到  

---

## Railway 要開才「正式站 24h」

```
OBS_WATCHDOG_ENABLED=true
OBS_DAILY_DIGEST_ENABLED=true
OBS_DAILY_DIGEST_HOUR_HKT=8
OBS_ALERTING_ENABLED=true
OBS_ALERT_EMAIL_SEND=true
OBS_ALERT_CRASH=true
OBS_ALERT_ONLY_ON_RED=true
OBS_WATCHDOG_INTERVAL_SEC=300
OBS_ALERT_COOLDOWN_SEC=3600
OBS_OPS_EMAIL=…
GMAIL_USER=…
GMAIL_APP_PASSWORD=…
```

旗標已開仍不夠：出站 SMTP 必須可達（Pro）或改 HTTPS 寄信。

---

## 結案 Python

```bash
python scripts/check_obs_traffic_light.py
python scripts/check_observability_static.py
```
