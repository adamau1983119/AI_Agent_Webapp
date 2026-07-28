# Alter Ego — 技術規格（AE-0 SoT）

> **版本**：v1.0  
> **日期 SoT**：2026-06-24（週三）  
> **對照**：[`v7.0.0_需求文件.md`](./v7.0.0_需求文件.md) 頻道區塊 14 · [`v7_alter_ego_checklist.md`](./v7_alter_ego_checklist.md) · [`專案完整架構表_v7.md`](../專案完整架構表_v7.md) **Alter Ego SKU**  
> **程式映射**：`backend/app/models/alter_ego_dna.py`、`backend/app/services/shells/`、`backend/app/api/v1/alter_ego.py`

---

## 1. 範圍與分界

| 項目 | 決策 |
|------|------|
| 產品 | 新用戶貼 **1～3 篇範文** → 結構化 **文字 DNA** → **Soul（Flash）→ Shell（YAML）→ Post Kit** |
| LLM | Alter Ego 全路徑 **Flash-only**；詳情 `contents/generate` 仍 **Pro**（分路由） |
| 護城河 MVP | DNA JSON + exemplar + 週 batch Flash patch；**不做 fine-tune** |
| 隔離 | **禁止**讀寫 `public_feed:feed:*`、`my_channel:feed:*` |
| 驗收 | **禁止 Mock**；schema fail → 重试 ≤2 或 UX 重贴 |

---

## 2. DNA 扁平 Pydantic（`AlterEgoDnaJson`）

實作：`backend/app/models/alter_ego_dna.py`

### 2.1 必填最小集

| 欄位 | 型別 | 說明 |
|------|------|------|
| `lexicon` | `list[str]` | 1～20 個特徵詞／口頭禪（每項 ≤40 字） |
| `tone_descriptors` | `list[str]` | 1～8 個語氣形容（例：`親切`、`犀利`） |
| `voice_persona` | `str` | 一句話人設摘要（≤120 字） |
| `language_primary` | `str` | `zh-TW` \| `en` \| `ja`（與範文主語一致） |
| `exemplar_snippets` | `list[str]` | 1～3 段 **摘錄**（每段 ≤280 字；**不得**存全文範文） |

### 2.2 選填（建議 extract 盡量填）

| 欄位 | 型別 | 說明 |
|------|------|------|
| `sentence_rhythm` | `str` | `short_punchy` \| `mixed` \| `long_flowing` |
| `emoji_style` | `str` | `none` \| `sparse` \| `moderate` |
| `opening_patterns` | `list[str]` | 常見開場句式（≤5） |
| `closing_patterns` | `list[str]` | 常見結尾句式（≤5） |
| `hashtag_style` | `str` | 標籤習慣描述（≤80 字） |
| `avoid_list` | `list[str]` | 應避免的詞／語氣（≤10） |
| `cta_style` | `str` | 行動呼籲習慣（≤80 字） |

### 2.3 驗證鐵律

- **strict**：`model_config = ConfigDict(extra="forbid")` — LLM 多欄位即 fail  
- 日誌：`[ALTER_EGO_DNA_EXTRACT_FAIL]`；**禁止** log 全文範文  
- 壓縮注入 Pro generate：`ContentStyleService.compress_for_generate()` → ≤500 字 one-liner + `dna_version_id`

---

## 3. Mongo 資料模型

### 3.1 `alter_ego_dna`

| 欄位 | 說明 |
|------|------|
| `user_id` | 唯一 |
| `dna_json` | `AlterEgoDnaJson` 序列化 |
| `dna_status` | `pending` \| `active` \| `skipped` \| `legacy_only` |
| `current_dna_version_id` | UUID hex；每次寫入 bump |
| `updated_at` | ISO datetime |

### 3.2 `alter_ego_dna_snapshots`

| 欄位 | 說明 |
|------|------|
| `snapshot_id` | = 寫入時 `version_id` |
| `user_id`, `dna_json`, `created_at` | |
| `reason` | `extract` \| `manual` \| `weekly_batch` \| `rollback` |

### 3.3 `user_feedback_logs`

採用／👍👎 Diff → 週 batch 輸入（AE-2）。

---

## 4. ContentStyleService（唯一風格入口）

實作規劃：`backend/app/services/content_style_service.py`

```python
class StyleContext(TypedDict):
    route: Literal["ae", "contents_generate", "assist"]
    dna_status: DnaStatus
    compressed_dna: str          # Pro generate 用
    dna_version_id: Optional[str]
    legacy_style_hint: str       # legacy_only 時 one-liner

async def resolve_for_route(user_id: str, route: str) -> StyleContext: ...
```

| route | 行為 |
|-------|------|
| `ae` | 僅 `active` 用 DNA；`skipped`／`pending` 用預設 Soul；**不** fallback `style_profiles` |
| `contents_generate` | `active` → compressed DNA + version_id；`legacy_only` → one-liner；`skipped` → preset／空 |
| `assist` | CreateChannel 貼範文 → 同一 `extract` API |

**version_tag**：任何 DNA 更新 bump `current_dna_version_id` 並寫 snapshot；`generation_meta.dna_version_id` 凍結當次 generate 所用版本。

---

## 5. Shell 層（YAML + ShellManager）

實作：`backend/app/config/shells/*.yaml`、`backend/app/services/shells/shell_manager.py`

### 5.1 平台 v1

| 檔案 | 平台 | v1 重點約束 |
|------|------|-------------|
| `facebook.yaml` | Facebook | 首段 ≤90 字；hashtag **4～6** 個 |
| `threads.yaml` | Threads | hashtag **0～1** |
| `x.yaml` | X（Twitter） | 單則 ≤280 字；可選 thread |

**IG v1 不做**（無 `instagram.yaml`）。

### 5.2 ShellManager 介面

```python
class ShellRule(BaseModel): ...  # 自 YAML 載入

class ShellManager:
    def list_platforms(self) -> list[str]: ...
    def load(self, platform: str) -> ShellRule: ...
    def build_prompt_constraints(self, platform: str) -> str: ...
```

Soul（Flash + DNA）產出中性正文 → Shell（Flash + YAML 約束）產出平台仿文。

---

## 6. API 契約

Router：`/api/v1/alter-ego`（與 `contents/generate` **物理隔離**）

### 6.1 `POST /extract`

**Request**

```json
{
  "exemplars": ["範文1全文…", "範文2…"],
  "language": "zh-TW"
}
```

- `exemplars`：1～3 篇；每篇 ≤8000 字（HTTP gateway 另限 body 64KB）  
- 需 `Authorization: Bearer`

**Response**

```json
{
  "dna_json": { "...": "AlterEgoDnaJson" },
  "dna_version_id": "uuid",
  "dna_status": "active"
}
```

- Flash-only；schema fail → 重试 ≤2；仍 fail → **422** + `[ALTER_EGO_DNA_EXTRACT_FAIL]`

### 6.2 `POST /preview`（AE-1a）

Soul + Shell 仿文預覽；`platform`: `facebook` \| `threads` \| `x`。

### 6.3 `POST /dna/rollback`（AE-1）

回滾至指定 `snapshot_id`。

---

## 7. 雙層 LLM 防禦

| 層 | 作法 |
|----|------|
| HTTP | `AlterEgoBodyGateway` 限 body；獨立 router |
| Factory | `get_llm_client(namespace="alter_ego")` **assert Flash-only** |
| 灰區 | `contents/generate` 可讀 compressed DNA，**必須** Pro |

---

## 8. 首登動線（前端 · AE-1d）

- `dna_status=pending` → `/onboarding/alter-ego`（必含 **Skip**）  
- Skip → `skipped` → `/my-channel`  
- Settings「建立我的 Alter Ego」供 Skip 用戶回補  

---

## 9. 檔案清單

| 路徑 | 用途 |
|------|------|
| `docs/ALTER_EGO_SPEC.md` | 本檔（AE-0 SoT） |
| `backend/app/models/alter_ego_dna.py` | DNA Pydantic |
| `backend/app/schemas/alter_ego.py` | API schemas |
| `backend/app/api/v1/alter_ego.py` | Router |
| `backend/app/services/alter_ego_service.py` | extract／preview 邏輯 |
| `backend/app/services/ai/llm_factory.py` | namespace Flash 防禦 |
| `backend/app/services/shells/shell_manager.py` | Shell YAML 載入 |
| `backend/app/config/shells/*.yaml` | 平台規則 |
| `backend/app/middleware/alter_ego_body_gateway.py` | HTTP 閘門（AE-1） |
| `frontend/src/pages/AlterEgoOnboarding.tsx` | Onboarding（AE-1d） |

---

## 10. 版本

| 版本 | 日期 | 說明 |
|------|------|------|
| v1.0 | 2026-06-24 | AE-0 初版：DNA 扁平 schema、Shell YAML、API 契約、ContentStyleService 介面 |
