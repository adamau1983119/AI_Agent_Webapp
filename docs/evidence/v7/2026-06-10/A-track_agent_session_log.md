# v7 A 軌自動驗收 — 2026-06-10

> **執行者**：Cursor Agent（非用家手測）  
> **分支**：`feature/v7-cost-pipeline`  
> **後端**：本 session 啟動 `uvicorn` @ `127.0.0.1:8000`  
> **前端**：未啟動（U 軌 E2E留用家）

---

## 總覽

| 區塊 | 結果 | 備註 |
|------|------|------|
| 環境啟動 | PASS | Mongo connected；Redis 未連（降級，非阻擋） |
| E0-B `/health` | PASS | `cost_controls` 六開關 false + Flash/Pro 分離 |
| 靜態／程式存在 | PASS | gateway、summary_flash、Discover、i18n |
| `npm run build` | PASS | exit 0，5.76s |
| `pytest` | SKIP | venv 未安裝 pytest |
| 公共 API | PASS | `GET /public/topics/feed?lang=zh-TW` → 200 空陣列 |
| C3-3 gateway | PASS | 無 `summary_flash` → generate **400** |
| C2 translate-display | PARTIAL | 200 + `[Fallback-JA]`（DeepL key 空或失敗，符合 D4 fallback） |
| C1 資料面 | DEFER | DB **0** 筆 `summary_flash`（96 筆舊資料）；需新 collect（耗 Token，本輪未跑） |
| U 軌 | 待做 | 登入後 5 步 E2E（約 20～30′） |

---

## E0-B — GET /health

```json
{
  "status": "healthy",
  "environment": "development",
  "database": { "status": "connected" },
  "cost_controls": {
    "auto_start_scheduler": false,
    "scheduled_topic_collection": false,
    "ai_topic_translation": false,
    "ai_topic_fallback": false,
    "channel_prefetch_pipeline": false,
    "public_feed_pipeline": false,
    "ai_service": "deepseek",
    "deepseek_model": "deepseek-v4-flash",
    "deepseek_model_flash": "deepseek-v4-flash",
    "deepseek_model_pro": "deepseek-v4-pro"
  }
}
```

**對照**：C0-1、C0-2、C0-3 → **PASS**（省 Token 組）

---

## 靜態檢查

| 項 | 結果 | 證據 |
|----|------|------|
| C1-3 `article_prompt` 無 `original_content[:2000]` | PASS | `backend/app/prompts/article_prompt.py` 僅 summary_flash |
| C1-9 無 SQLAlchemy | PASS | `backend/app` grep 無命中 |
| C2-10 無 NLLB | PASS | `backend/app` grep 無命中 |
| TokenGateway 已掛載 | PASS | `main.py` L367-368 |
| Topic.summary_flash 欄位 | PASS | `models/topic.py` |
| topic_translations 唯一索引 | PASS | `uniq_topic_lang_type` |
| Discover 路由／API | PASS | `App.tsx` `/discover`；`publicFeed.ts`；feed **200** |
| i18n discover 三語 | PASS | `i18n/index.ts` nav.discover、discover.* |

---

## API 健康檢查

| 請求 | 狀態 | 說明 |
|------|------|------|
| `GET /docs` | 200 | Swagger 可開 |
| `GET /api/v1/public/topics/feed?lang=zh-TW` | 200 | `{"data":[],"count":0}` |
| `POST .../contents/topic_fashion_20260313020033_0/generate` | **400** | 缺 `summary_flash`（C3-3 PASS） |
| `POST .../topics/.../translate-display` (ja, standard) | **200** | `cached: false`；標題含 `[Fallback-JA]`（C2-5 路徑觸發） |

---

## Mongo 快照

| 指標 | 值 |
|------|-----|
| `topics` 總數 | 96 |
| 含非空 `summary_flash` | **0** |
| `topic_translations` 筆數 | 0 |
| 索引 | `_id_`, `uniq_topic_lang_type` |

**結論**：程式已支援 summary_flash；**舊資料未回填**。C1-1／C1-2 需一次 **collect**（會呼叫 DeepSeek Flash）— 本輪刻意不跑以免未授權耗 Token。

---

## 建置

```
npm run build → ✓ built in 5.76s (exit 0)
```

---

## 警告（非 FAIL）

- **Redis** `localhost:6379` 未連 — 快取降級；公共 feed `cached: false` 屬預期
- **Elasticsearch** import 警告 — 回退 Mongo 搜尋
- **pytest** 未安裝 — 若需 CI 級回歸可 `pip install pytest` 後重跑

---

## Checklist 代理勾選建議

| 代號 | 建議 | 理由 |
|------|------|------|
| C0-1～C0-3 | `[x]` | health JSON |
| C1-3, C1-9, C2-10 | `[x]` | 靜態 grep |
| C3-3 | `[x]` | generate 400 實測 |
| C2-5 | `[x]` | Fallback-JA 實測 |
| C1-1, C1-2, C1-5, C1-7 | `[ ]` | 需 collect／generate 成功／後台計數 |
| C4-* | `[ ]` | 需 :3000 瀏覽器（U 軌） |
| CD-* / E0-PF | `[ ]` | 需 `/discover` UI |

---

## 用家 U 軌（僅剩）

1. 登入 → 儀表板（無紅錯）
2. 主題列表切語系一次
3. （可選）詳情 generate — 舊主題預期 400 提示
4. `/discover` 空狀態或卡片
5. `/channels/create` 助手可開

回報：**PASS** 或 **第 N 步 FAIL + 一句描述** 即可。
