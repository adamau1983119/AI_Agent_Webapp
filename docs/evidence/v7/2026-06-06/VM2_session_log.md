# VM-2 執行記錄 — log_cost_event（2026-06-06 接續 · 排程漂移）

> **分支**：`feature/v7-cost-pipeline`  
> **檔案**：`backend/app/utils/logger.py`（新增 `log_cost_event`、`COST_EVENT_TAGS`）

## MD-M1 自測

| 項 | 結果 |
|----|------|
| MD-M1-1 無 pino | `grep -i pino backend/` → **無** |
| MD-M1-2 `log_cost_event` + `colorize=True` | 已實作；`setup_logging` 未改 `colorize` |
| MD-M1-3 終端輸出 | `[SUMMARY_FLASH_SUCCESS] chars=245 topic_id=t1`（key 排序） |
| MD-M1-5 E0 已收 | 沿用 VM-1 E0-B/F 截圖（06-06） |

### 驗證指令（可重現）

```powershell
cd backend
.\venv\Scripts\python.exe -c "from app.utils.logger import log_cost_event; log_cost_event('SUMMARY_FLASH_SUCCESS', topic_id='t1', chars=245)"
```

### 終端摘錄（2026-06-09 自測）

```text
[SUMMARY_FLASH_SUCCESS] chars=245 topic_id=t1
[CACHE_MISS] topic_id=abc
```

## 待辦

- [ ] **commit** 本變更至 `feature/v7-cost-pipeline`（使用者確認後）
- [ ] **E0-B 嚴格項**：`/health` 補 `cost_controls`（Phase 0 C0-4，可 VM-3 前）
- [ ] **VM-3**：MD-M2 + C0 截圖
