# V7-2 Phase 2 開工記錄（2026-06-06 接續）

> **分支**：`feature/v7-cost-pipeline`  
> **目標**：`topic_translations` + DeepL + cache-first + 夜間港日預載（無 kol_style job）

## 程式變更（P2-01～P2-11）

| 項 | 檔案 | 狀態 |
|----|------|------|
| P2-01 | `models/topic_translation.py` | ✅ |
| P2-02 | `repositories/topic_translation_repository.py`（**58 行**） | ✅ |
| P2-03 | `scripts/ensure_topic_translations_indexes.py`；`main.py` 啟動 ensure | ✅ |
| P2-04 | `services/translation/deepl_provider.py`（**72 行**） | ✅ |
| P2-05/06/13 | `topic_display_translation_service.py` — cache-first、DeepL、in-flight | ✅ |
| P2-07 | `config/channel_prefetch.yaml` | ✅ |
| P2-08/10 | `channel_prefetch_pipeline.py` + `scheduler.py` job | ✅ |
| P2-09 | `cost_controls.channel_prefetch_pipeline` | ✅ |
| P2-11 | `I18N_CACHE_HIT`／`CACHE_MISS`／`TRANSLATION_FALLBACK_TRIGGERED` | ✅ |
| P2-12 前端 | **延後 Phase 4**（後端 API 已支援 `translation_type`） | ⏳ |

## 設定（本機 `.env` · 不提交）

```env
ENABLE_CHANNEL_PREFETCH_PIPELINE=false
DEEPL_API_KEY=
TRANSLATION_TIMEOUT_SEC=5
```

## 待驗收（程式完成後一併測）

| C*-* | 動作 |
|------|------|
| C2-1/2 | `ensure_topic_translations_indexes.py`；重複 upsert |
| C2-3/4 | `POST /topics/{id}/translate-display` 兩次 → HIT/MISS 日誌 |
| C2-5 | 無 DEEPL key → `[Fallback-JA]`／`[Fallback-EN]` |
| C2-6/7/8 | 手動 `run_channel_prefetch_pipeline`；grep 無 `kol_style` job |
| C2-11 | mock 錯誤後第二次請求仍可完成 |

## 下步

- **V7-3 Phase 3**：`token_gateway` + body 重放 + generate 加固
