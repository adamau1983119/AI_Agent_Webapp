# v8 開通產卡前檢查表（最小成本 · DT-5）

> **分支**：`feature/v8-observability-alerting`（產卡閘自 `feature/v8-collection-min-cost-gate`）  
> **備份**：`backup/2026-07-31-daily-ops-ready` · [`docs/backups/2026-07-31_v8_daily_ops_ready_snapshot/`](./backups/2026-07-31_v8_daily_ops_ready_snapshot/SNAPSHOT_README.md)  
> **配方 SoT**：[`backend/app/config/collection_min_cost_recipe.json`](../backend/app/config/collection_min_cost_recipe.json)  
> **日期**：2026-07-31（五）  
> **本輪狀態**：**A～D ✅**；Railway Deploy ✅；進入 **日常運作測試**（E 對齊明日自動產卡）

---

## A. DT-5（必過）— ✅ 已結

- [x] DeepSeek **用量信息** → **余额预警设置** 已 **保存**
- [x] 人民幣餘額預警：**開**；閾值 **¥20**
- [x] 通知信箱：平台寄至帳號綁定信箱
- [x] 帳上預付可接受（開通初期）

---

## B. 最小成本 Variables — ✅ 已結

| Variable | 目標值 | 正式域 |
|----------|--------|--------|
| `ENABLE_SCHEDULED_TOPIC_COLLECTION` | `true` | ✅ |
| `ENABLE_AI_TOPIC_TRANSLATION` | `false` | ✅ |
| `ENABLE_AI_TOPIC_FALLBACK` | `false` | ✅ |
| `ENABLE_CHANNEL_PREFETCH_PIPELINE` | `false` | ✅ |
| `ENABLE_PUBLIC_FEED_PIPELINE` | `false` | ✅ |

- [x] recipe／`check_collection_min_cost.py`  
- [x] Railway 已套用 + Deploy（使用者 2026-07-31 確認）

---

## C. 開通前 before — ✅ 已結

- [x] `--phase before` PASS（開通前）

---

## D. 開通 after — ✅ 已結

- [x] `--phase after` PASS；`scheduled_topic_collection=true`

---

## E. 日常運作煙霧（自動產卡 · 不手動觸發）

- [ ] **08-01 ≥04:15 HKT** Dashboard：fashion／food／trend 約各 5（合計約 15）
- [ ] 同日 DeepSeek 用量無異常尖峰
- [x] 成本「每日報表」改由 Observability **每日營運報告**（見 [`v8_observability_alerting.md`](./v8_observability_alerting.md)）

---

## F. 相關／非產卡

| 項目 | 狀態 |
|------|------|
| Observability 紅燈＋每日 digest | Railway 旗標已開；須映像含 `observability` 程式 |
| Discover public feed pipeline | 維持關 |
| 密鑰輪換（曾外洩） | ⏳ 獨立安全項 |

---

## 結案 Python

| 指令 | 結果 |
|------|------|
| `check_collection_min_cost.py` | ✅ |
| `--phase before` | ✅ |
| `--phase after` | ✅ |
