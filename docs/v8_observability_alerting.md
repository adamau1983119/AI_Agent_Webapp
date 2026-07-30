# v8 Observability／告警（紅綠燈 · 24h Watchdog）

> **SaaS**：Incident Alerting + Uptime Watchdog  
> **分支**：`feature/v8-observability-alerting`  
> **備份**：`backup/2026-07-31-pre-obs-traffic-light`  
> **日期**：2026-07-31  
> **安全**：紅燈即時告警預設「僅紅燈寄」；初期另開 **每日營運報告**（綠燈也寄）  
> **Railway（2026-07-31）**：使用者已開 Gmail／`OBS_ALERT_*`／Watchdog／Digest；Deploy ✅；⏳ 確認部署映像含本分支 Observability 程式

---

## 初期：每日營運報告（綠燈也寄）

| env | 預設 | 說明 |
|-----|------|------|
| `OBS_DAILY_DIGEST_ENABLED` | `false` | `true`＝每天一封報告 |
| `OBS_DAILY_DIGEST_HOUR_HKT` | `8` | 香港時間幾點後才寄（配合 Watchdog 迴圈） |

與紅燈即時告警並行：綠燈安静告警仍保留；另外**每天一封**「每日營運報告」含【綠燈】／【紅燈】。

```bash
python scripts/send_obs_daily_digest_now.py   # 立刻寄一封樣式確認
```

---

## 一眼看懂

| 燈 | 含義 | 電郵 |
|----|------|------|
| **綠燈** | 沒事・系統正常 | 紅燈通道：不寄；**每日報告**：會寄（若開 digest） |
| **紅燈** | 有事・請立即處理 | **立刻寄**＋每日報告也會標紅燈 |

---

## PD

- [x] **PD-OBS-TL-01** `traffic_light.py` 紅／綠判定  
- [x] **PD-OBS-TL-02** mailer 置頂【紅燈】／【綠燈】  
- [x] **PD-OBS-TL-03** `ops_agent` 僅紅燈寄信 + 冷卻  
- [x] **PD-OBS-TL-04** `ops_watchdog` 週期迴圈（env 閘）  
- [x] **PD-OBS-TL-05** `main.py` 閘門掛 Watchdog  
- [x] **PD-OBS-TL-06** `check_obs_traffic_light.py` PASS（live green_quiet）  
- [x] **PD-OBS-TL-07a** Railway：Gmail + OBS 旗標 + Deploy（使用者確認 2026-07-31）  
- [ ] **PD-OBS-TL-07b** 確認正式映像含 Observability（merge／部署來源）；首封自動每日報告（≥08:00 HKT）  
- [ ] **PD-OBS-TL-08** 密鑰輪換（聊天曾外洩之 App Password／API key）

---

## Railway 要開才「正式站 24h」（現況未開＝未全日運作）

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
OBS_OPS_EMAIL=a.adam1983119@gmail.com
GMAIL_USER=…
GMAIL_APP_PASSWORD=…
```

須部署含本功能的映像（目前 Railway 追 `main` 時，需 merge／改部署分支）。

---

## 結案 Python

```bash
python scripts/check_obs_traffic_light.py
python scripts/check_observability_static.py
```
