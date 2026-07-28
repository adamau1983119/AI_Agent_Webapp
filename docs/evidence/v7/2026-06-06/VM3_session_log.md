# VM-3 執行記錄 — MD-M2 + C0 契約（2026-06-06 接續 · 排程漂移）

> **分支**：`feature/v7-cost-pipeline`  
> **完成判定**：MD-M2-1、M2-2；C0-1、C0-2、C0-4（文件／JSON 證據）

## MD-M2 PR 紀律

| 項 | 結果 |
|----|------|
| MD-M2-1 無 `CRITICAL ENGINE` | `grep CRITICAL ENGINE backend/app` → **0 筆** |
| MD-M2-2 v7 新檔 ≤150 行 | `logger.py`：**133 行**（含 `log_cost_event` 區塊） |

## 程式變更（VM-3）

| 檔案 | 變更 |
|------|------|
| `backend/app/main.py` | 根路由 `GET /health` 併入 `cost_controls_summary()`（解鎖 E0-B 嚴格項） |
| `backend/.env`（本機，**不提交**） | Phase 0 省 Token 組：`ENABLE_SCHEDULED_TOPIC_COLLECTION=false`、`ENABLE_AI_TOPIC_TRANSLATION=false`、`AUTO_START_SCHEDULER=false` |

## C0 驗證（重啟 uvicorn 後）

**指令**：`Invoke-RestMethod http://localhost:8000/health`

**JSON 證據**：`2026-06-06_v7_VM3_health_cost_controls.json`

| 項 | 欄位 | 值 | 結果 |
|----|------|-----|------|
| **C0-1** | `cost_controls.scheduled_topic_collection` | `false` | PASS |
| **C0-2** | `cost_controls.ai_topic_translation` | `false` | PASS |
| **C0-3** | `cost_controls.deepseek_model` | `deepseek-v4-flash` | PASS（非 production 全站 Pro） |
| **C0-4** | 架構表 v7 D1～D5 | `專案完整架構表_v7.md` L104～L164 | PASS（文件存在） |

### `cost_controls` 摘錄

```json
{
  "auto_start_scheduler": false,
  "scheduled_topic_collection": false,
  "ai_topic_translation": false,
  "ai_topic_fallback": false,
  "ai_service": "deepseek",
  "deepseek_model": "deepseek-v4-flash"
}
```

啟動 log：`成本開關: {...}`（`main.py` lifespan）

## MD-M3-2 今日勾選項 + 證據檔名

| Checklist 項 | 證據 |
|--------------|------|
| MD-M2-1 | 本檔 MD-M2；grep 0 筆 |
| MD-M2-2 | 本檔；`logger.py` 133 行 |
| C0-1 / C0-2 | `2026-06-06_v7_VM3_health_cost_controls.json` |
| C0-4 | `專案完整架構表_v7.md` D1～D5 |
| E0-B 嚴格項 | 同上 JSON（根 `/health` 含 `cost_controls`） |

## 待辦

- [ ] 瀏覽器補拍 **E0-B** PNG（可選；JSON 已滿足 VM-3 完成判定）
- [ ] **commit** `main.py` + `logger.py`（使用者確認後）
- [ ] **VM-4**：MD-ALL + **V7-0 ☑**
