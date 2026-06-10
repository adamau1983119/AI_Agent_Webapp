# V7-3 Phase 3 開工記錄（2026-06-06 接續）

> **分支**：`feature/v7-cost-pipeline`  
> **目標**：Token Gateway + summary_flash 強制 + Pro max_tokens=1500

## 程式變更（P3-01～P3-07）

| 項 | 檔案 | 狀態 |
|----|------|------|
| P3-01/02 | `middleware/token_gateway.py`（**88 行**）；`main.py` 掛載 | ✅ |
| P3-03 | `contents.py` — `_require_summary_flash` → **400** | ✅ |
| P3-04 | `deepseek.py` — Pro `max_tokens=1500`（`DEEPSEEK_PRO_MAX_TOKENS`） | ✅ |
| P3-05 | `[TOKEN_GATEWAY_PASSED]` on generate/regenerate | ✅ |
| P3-06 | `article_prompt` + `_style_dna_hint`（登入用戶 style_profile） | ✅ |
| P3-07 | `utils/facebook_shell.py`（**35 行**） | ✅ |
| P3-08 | Free/Pro Redis 月額 | ⏳ 延後 P3.1 |

## Gateway 行為

- **路徑**：`POST /api/v1/contents/{id}/generate|regenerate`  only
- **剝除**：`llm_input`、`user_prompt`、`original_content` 等
- **body 重放**：`request._receive` 回灌 JSON
- **超大 body**：>64KB → **413**
- **不擋**：靈感／assist／`/api/v1/generate`（C3-8）

## facebook_shell 手動樣例

```python
from app.utils.facebook_shell import build_facebook_shell
out = build_facebook_shell("標題", "內文段落", ["美食", "香港"], ["https://example.com/a.jpg"])
# out["copy_bundle"] → 可複製字串
```

## 待驗收（程式完成後一併測）

| C*-* | 動作 |
|------|------|
| C3-1 | curl 大 `llm_input` → 剝除／413 |
| C3-2/9 | generate 200 + `[TOKEN_GATEWAY_PASSED]` + `await body` 正常 |
| C3-3 | 無 `summary_flash` topic → **400** |
| C3-4 | log `max_tokens=1500` |
| C3-7 | 上列 `facebook_shell` in/out |

## 下步

- **V7-4 Phase 4**（前端 skeleton／i18n）或 **整線 commit**
