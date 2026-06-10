# v7 A 軌自動驗收 — 2026-06-11（重跑）

> **執行者**：Cursor Agent（A 軌；非 U 軌手測）  
> **分支**：`feature/v7-cost-pipeline`  
> **政策**：禁止 `collect`／`generate-today`／assist 迴圈；允許單次診斷 POST（無 LLM 之 400）

---

## 總覽

| 區塊 | 結果 | 備註 |
|------|------|------|
| E0-B `/health` | **PASS** | Mongo **connected**；`cost_controls` 六開關 **false** |
| `npm run build` | **PASS** | exit 0，~4.9s |
| `GET /docs` | **PASS** | 200 |
| 公共 feed API | **PASS** | `GET /public/topics/feed?lang=zh-TW` → 200，`count=0` |
| C3-3 gateway | **PASS** | 無 `summary_flash` → `POST …/generate` **400** |
| 靜態檢查 | **PASS** | gateway、`article_prompt`、Discover、i18n、無 NLLB／SQLAlchemy |
| `pytest` | **SKIP** | venv 無 pytest |
| C1 資料面 | **DEFER** | DB **0**／96 筆具 `summary_flash`；刻意未跑 collect |
| U 軌 | **待做** | 登入煙霧 5 步（用家） |

---

## E0-B — GET /health

- **URL**：`http://localhost:8000/health` → **200**
- **database**：`connected`
- **cost_controls**：`auto_start_scheduler`、`scheduled_topic_collection`、`ai_topic_translation`、`ai_topic_fallback`、`channel_prefetch_pipeline`、`public_feed_pipeline` 皆 **false**
- **models**：`deepseek_model_flash` = `deepseek-v4-flash`；`deepseek_model_pro` = `deepseek-v4-pro`

**對照**：C0-1、C0-2、C0-3 → **PASS**

---

## 靜態檢查

| 項 | 結果 |
|----|------|
| `article_prompt.py` 僅 `summary_flash`（無 `original_content[:2000]`） | PASS |
| `TokenGatewayMiddleware` @ `main.py` L367-368 | PASS |
| `Topic.summary_flash` 欄位 | PASS |
| `App.tsx` `/discover` 路由 | PASS |
| i18n `nav.discover`、`discover.*` 三語 | PASS |
| `backend/app` 無 NLLB | PASS |
| `backend/app` 無 SQLAlchemy | PASS |

---

## API 煙霧

| 請求 | 狀態 | 說明 |
|------|------|------|
| `GET /api/v1/public/topics/feed?lang=zh-TW` | 200 | `{"data":[],"lang":"zh-TW","cached":false,"count":0}` |
| `POST /api/v1/contents/topic_fashion_20260313020033_0/generate` | **400** | 缺 `summary_flash`（C3-3；未觸發 Pro LLM） |

---

## Mongo 快照

| 指標 | 值 |
|------|-----|
| `topics` 總數 | 96 |
| 非空 `summary_flash` | **0** |

> C1-1～C1-7 完整驗收需 **新 collect** 或測試段 **06-16**；本輪 A 軌不跑。

---

## 前端建置

```
npm run build → exit 0 (~4.87s)
```

---

## 本輪未執行（政策）

- `POST …/collect`
- `POST …/schedules/generate-today`
- 批次 `translate-display`／assist 迴圈
- U 軌瀏覽器截圖

---

## 結論

**A 軌本輪 PASS**（環境 + 建置 + 靜態 + 公共 API + C3-3 400）。  
**阻塞 commit 前**：U 軌煙霧、（可選）`git commit`；**C\*** 截圖項留 **06-16 起**。
