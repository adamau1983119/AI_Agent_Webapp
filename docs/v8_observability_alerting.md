# v8 Observability／告警（紅綠燈 · 24h Watchdog）

> **SaaS**：Incident Alerting + Uptime Watchdog  
> **正確行為**：正式域 Webapp（Railway）每日 ≥**08:00 HKT** 由 `EmailService` 自動寄「每日營運報告」到 `OBS_OPS_EMAIL`（綠燈也寄）；紅燈另即時告警。  
> **寄信（2026-08-11）**：**Resend HTTPS** 優先（`RESEND_API_KEY`）；本機可回退 Gmail SMTP。禁止以本機排程／GitHub Actions 充當正式解。  
> **日期**：2026-08-11（對照 [`calendar_2026_reference.md`](./calendar_2026_reference.md)）  
> **備份**：`backup/2026-08-11-ops-digest-resend-pass` · [`docs/backups/2026-08-11_ops_digest_resend_pass_snapshot/`](./backups/2026-08-11_ops_digest_resend_pass_snapshot/SNAPSHOT_README.md)  
> **程式**：PR #19 `feat(email): prefer Resend HTTPS…` 已合 `main`

---

## 初期：每日營運報告（綠燈也寄）

| env | 預設 | 說明 |
|-----|------|------|
| `OBS_DAILY_DIGEST_ENABLED` | `false` | `true`＝每天一封報告 |
| `OBS_DAILY_DIGEST_HOUR_HKT` | `8` | 香港時間幾點後才寄（配合 Watchdog 迴圈） |
| `RESEND_API_KEY` | （空） | 正式域必填；走 `https://api.resend.com/emails` |
| `EMAIL_FROM` | （空） | 例：`Alter Ego <noreply@ai-alterego.com>`（網域須 Resend Verified） |

```bash
python scripts/send_obs_daily_digest_now.py   # 本機立刻寄一封（驗設定；≠正式自動）
```

---

## 一眼看懂

| 燈 | 含義 | 電郵 |
|----|------|------|
| **綠燈** | 沒事・系統正常 | 紅燈通道：不寄；**每日報告**：會寄（若開 digest） |
| **紅燈** | 有事・請立即處理 | **立刻寄**＋每日報告也會標紅燈 |

---

## 現況核證（2026-08-11）

| 層 | 項目 | 狀態 | 證據／備註 |
|----|------|------|------------|
| L1 | Railway `OBS_*` 旗標 | ✅ | Watchdog／Digest 已開 |
| L2 | 寄信通道 | ✅ | **Resend HTTPS**（PR #19）；網域 `ai-alterego.com` Verified |
| L3 | 正式域 loop | ✅ | `WATCHDOG_START … digest=True` |
| L4 | **正式域自動日報進信箱** | ✅ **PASS** | `Email 發送成功 (resend)`；08-11 信箱已收 |

曾 FAIL：Hobby 擋 `smtp.gmail.com:587` → 改 Resend 後解除。  
08-11 首封曾標紅燈（health 讀取 timeout）；隨後 `/health` = healthy（短暫誤報）。

---

## PD

- [x] **PD-OBS-TL-01** `traffic_light.py` 紅／綠判定  
- [x] **PD-OBS-TL-02** mailer 置頂【紅燈】／【綠燈】  
- [x] **PD-OBS-TL-03** `ops_agent` 僅紅燈寄信 + 冷卻  
- [x] **PD-OBS-TL-04** `ops_watchdog` 週期迴圈（env 閘）  
- [x] **PD-OBS-TL-05** `main.py` 閘門掛 Watchdog  
- [x] **PD-OBS-TL-06** `check_obs_traffic_light.py` PASS（live green_quiet）  
- [x] **PD-OBS-TL-07a** Railway：OBS 旗標 + Deploy；loop 已啟動  
- [x] **PD-OBS-TL-07b** 正式域自動每日報告進信箱 — **PASS**（2026-08-11 Resend）  
- [ ] **PD-OBS-TL-08** 密鑰輪換（聊天曾外洩之 App Password／API key）  
- [x] **PD-OBS-TL-09** HTTPS `EmailService`（Resend）→ Redeploy → `digest`／信箱 — **PASS**

---

## Railway Variables（正式域）

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
RESEND_API_KEY=re_…
EMAIL_FROM=Alter Ego <noreply@ai-alterego.com>
# Gmail SMTP 僅本機備援（正式域有 Resend 即可）
```

---

## 結案 Python

```bash
python scripts/check_obs_traffic_light.py
python scripts/check_observability_static.py
```
