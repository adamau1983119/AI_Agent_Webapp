# V7-1 Phase 1 開工記錄（2026-06-06 接續）

> **分支**：`feature/v7-cost-pipeline`  
> **目標**：`summary_flash` 寫庫；收集零 AI 翻譯；`article_prompt` 斷流；generate 用 Pro

## 程式變更（P1-01～P1-11）

| 項 | 檔案 | 狀態 |
|----|------|------|
| P1-01 | `models/topic.py`、`schemas/topic.py` — `summary_flash` | ✅ |
| P1-02 | `services/summarization/summary_flash_service.py`（**62 行**） | ✅ |
| P1-03 | `channel_collector.py` `_persist_topics`、`topic_collector.py` | ✅ |
| P1-05/06 | `prompts/article_prompt.py`、`prompts/system_constants.py` | ✅ 無 `original_content[:2000]` |
| P1-07 | `config_module.py` — `DEEPSEEK_MODEL_FLASH`／`PRO` | ✅ |
| P1-08 | `services/ai/deepseek.py` — `_call_api(model=)`、`generate()` | ✅ |
| P1-09 | `api/v1/contents.py`、`automation/workflow.py` — DB `summary_flash` SoT + Pro | ✅ |
| P1-10 | 收集翻譯仍由 `cost_controls.ai_topic_translation_enabled()` 關閉 | ✅（沿用 Phase 0） |
| P1-11 | `log_cost_event('SUMMARY_FLASH_SUCCESS', …)` | ✅ |

## 本機驗證（可重現）

```powershell
cd backend
.\venv\Scripts\python.exe -c "from app.prompts.article_prompt import build_article_prompt; p=build_article_prompt('t','fashion',[],summary_flash='x'); assert 'original_content' not in p"
# 預期：無輸出即 PASS

grep "original_content\[:2000\]" app/prompts/article_prompt.py
# 預期：0 筆
```

## 待驗收（需瀏覽器／DeepSeek 後台）

| C*-* | 動作 |
|------|------|
| C1-1 | Compass／mongo：`topics.summary_flash` 存在 |
| C1-2 | `POST /channels/{id}/collect` → 新 topic 有 `summary_flash` + 終端 `[SUMMARY_FLASH_SUCCESS]` |
| C1-4/5 | `POST /contents/{id}/generate` → 200；`model_used=deepseek-v4-pro` |
| C1-7 | collect 10 則 ≈ 10 次 Flash（非 20+ 翻譯） |

## 待辦

- [ ] 使用者手測 collect + generate 截圖
- [ ] **commit** `feature/v7-cost-pipeline`
- [ ] C1-6 assist 仍 Flash（回歸一筆）
