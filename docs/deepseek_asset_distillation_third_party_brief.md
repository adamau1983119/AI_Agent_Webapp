# DeepSeek 蒸餾成「珍貴資料」— 第三方溝通簡介

> **用途**：與技術顧問、翻譯服務商、投資人或合作方說明 **AI 成本策略** 與 **資料資產** 設計  
> **版本**：v7.0.0 對齊  
> **更新**：2026-06-04  
> **可複製 HTML**：[`deepseek_asset_distillation_third_party_brief.html`](./deepseek_asset_distillation_third_party_brief.html)（瀏覽器開啟，一鍵複製）  
> **詳規**：[`v7.0.0_需求文件.md`](./v7.0.0_需求文件.md)、[`deepseek_cost_investigation_2026-05.md`](./deepseek_cost_investigation_2026-05.md)

---

## 1. 一句話（給第三方）

**Influencers AI 只把 DeepSeek 用在「使用者主動要的發文素材」；RSS 標題翻譯改零成本或便宜機器翻譯，且所有 AI 產出一律寫入資料庫快取，避免重複付費。**

---

## 2. 為什麼要「蒸餾」

| 問題 | 說明 |
|------|------|
| 成本不可擴展 | 測試期曾出現：極少主題收集卻觸發大量 **DeepSeek** 呼叫（多為收集時「每則標題翻譯一次」+ 排程自動收集） |
| 浪費 | 同一標題重翻、同一主題無故「重新生成」，等於丟棄已付費的輸出 |
| 混淆 | 把「看懂標題」與「寫可發布的短文／腳本」混用同一套高價 prompt |

**蒸餾**＝把 DeepSeek 從低價值、高頻流程中抽離，只留下高價值、低頻、可留存、可稽核的產出。

---

## 3. 什麼算「珍貴資料」（要留、要版本化）

| 資產 | 存哪裡 | 為何珍貴 |
|------|--------|----------|
| **短文 + 腳本** | MongoDB `contents`（`article`、`script`） | 使用者要拿去 IG／小紅書發文；含 `model_used`、`prompt_version` |
| **版本歷史** | `contents.versions[]` | 每次重新生成不覆蓋舊稿，可回溯、可選用 |
| **卡片譯文（快取）** | `topics.titles_i18n`、`description_i18n` | 使用者按「譯為目前語言」後**永久快取**，第二次不再呼叫 API |
| **收集主標** | `topics.title`、`original_title` | 來自 RSS，**不應**被翻譯 API 覆寫（方案 C） |
| **（規劃）呼叫日誌** | `ai_generations` | 稽核：哪個 topic、翻譯或生成、是否快取、用哪個 model |

**不算珍貴、不應燒 DeepSeek**：背景排程替每則 RSS 自動改寫標題、無人點開就批量生成全文。

---

## 4. 四層策略（L0～L3）

| 層級 | 做什麼 | 用什麼 | 成本 |
|------|--------|--------|------|
| **L0** | 收集主題卡：保留 RSS／來源語言標題 | 無 AI | ≈ 0 |
| **L1** | 介面顯示：主標＝收集語言；必要時顯示「譯為目前語言」按鈕 | UI only | ≈ 0 |
| **L2** | 使用者按鈕才翻譯標題／短摘要 | Google／Azure 等 **機器翻譯**（規劃） | 低 |
| **L3** | 需要「社群風格」標題改寫 | DeepSeek **Flash**（可選） | 按次 |
| **生成** | 主題詳情：短文、腳本、重新生成 | DeepSeek **Flash**（核心） | 按次、需限流 |

**原則**：主題卡瀏覽 **不必** DeepSeek；**必須** DeepSeek 的是使用者明確觸發的 **內容生成**。

---

## 5. 正式環境建議開關（可給維運／第三方看）

```env
DEEPSEEK_MODEL=deepseek-v4-flash
ENABLE_SCHEDULED_TOPIC_COLLECTION=false
ENABLE_AI_TOPIC_TRANSLATION=false
ENABLE_AI_TOPIC_FALLBACK=false
AUTO_START_SCHEDULER=false
# 規劃
TRANSLATION_PROVIDER=none   # 或 google / azure / deepseek_flash
```

`GET /health` 可回傳 `cost_controls` 供監控對照。

---

## 6. 產品主路（MVP，與蒸餾一致）

```
頻道 RSS 收集 (L0)
    → 主題卡閱讀 (L1，按需 L2/L3 譯)
    → 進詳情 → 使用者按「生成內容」(DeepSeek Flash)
    → Post Kit 複製發文（站外 FB／IG）
```

---

## 7. 給第三方討論題（7 項）

1. **翻譯供應商**：L2 優先接 **Google Cloud Translation** 還是 **Azure Translator**？免費額度與繁中品質要求？  
2. **是否接受「標題僅機翻、不改寫」**作為預設，改寫僅進階選項？  
3. **DeepSeek 預算**：單用戶每月 API 上限（例如 USD）？超過時降級或排隊？  
4. **重新生成**：是否強制二次確認，避免誤觸燒量？  
5. **資料保留**：生成內容與譯文快取保留幾天？是否符合私隱／刪除帳號要求？  
6. **稽核**：是否需要匯出 `ai_generations` 給財務對帳？  
7. **排程**：正式上線是否 **完全關閉**「每 6 小時自動收三類主題」？

---

## 8. 技術錨點（給工程第三方）

| 項目 | 路徑 |
|------|------|
| 成本開關 | `backend/app/utils/cost_controls.py` |
| 收集翻譯 | `backend/app/services/automation/topic_collector.py` → `_translate_title` |
| 按需卡片翻譯 | `backend/app/services/topic_display_translation_service.py` |
| 內容生成 | `backend/app/api/v1/contents.py` |
| 內容版本 | `backend/app/services/repositories/content_repository.py` |
| v7 規格 | `docs/v7.0.0_需求文件.md`、`專案完整架構表_v7.md` |

---

## 9. 參考數據（測試期，非承諾）

- 歷史帳單調查見 `deepseek_cost_investigation_2026-05.md`（多為 **v4-pro** + 高頻 API，非現行 Flash 預設目標）。  
- v7 目標：新用戶首週 DeepSeek 成本較「收集開翻譯」情境 **降 ≥ 80%**（待實測驗證）。

---

**文件維護**：開發團隊 · 2026-06-04
