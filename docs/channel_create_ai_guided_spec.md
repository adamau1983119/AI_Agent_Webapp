# 建立頻道 — AI 主導三步驟＋動態 RSS（規格 v0.2）

> **對齊**：`專案完整架構表.md` →「建立頻道 Step 2／RSS」第⑤節  
> **原則**：先定 **備援 UX** 與 **檢索 MVP**，再鎖 API 契約與 UI。  
> **更新**：2026-05-08（**E 階段 A** 助手優先版面凍結）  
> **完整願景（一至六節，不依 MVP 砍範圍）**：[channel_create_full_vision_一至四.md](./channel_create_full_vision_一至四.md)（核心體驗目標、IA、前端、後端、**資料生命週期**、**測試／發布／營運**；檔名 `一至四` 為歷史路徑）  
> **新方案檢查清單**：[channel_create_new_scheme_checklist.md](./channel_create_new_scheme_checklist.md)（**A～I**；**H、I**＝第五、六章，預設 **測試階段** 勾選）

---

## A1 — 狀態機（助手主軸 × 現有精靈）

| 精靈步驟 | 使用者目標 | 助手主軸行為（目標） | 與現有 `CreateChannel.tsx` |
|----------|------------|----------------------|----------------------------|
| **Step 1** | 決定「追蹤主題」粗輪廓（類別／地區／一句話） | 開場自我介紹＋三步驟說明；提供 **可點選選項**＋自然語言框 | 已存在：`showAssist`、快捷鈕、`POST /channels/assist` |
| **Step 2** | 選 ≤10 條 RSS（候選池／已選） | 依槽位 **檢索** 動態候選（MVP：白名單）；可「再推薦」排除已選（見架構 ③） | 已存在：`selected_feeds`、`getDefaultRssSources` |
| **Step 3** | 命名／描述並建立 | 可選：建議名稱／描述（需求 #32/#33）；**備援**：一律可手動填 | 已存在：表單＋`POST /channels` |

**並行策略（v0.1 現況）**：助手 **不取代** 右側／下方精靈進度；使用者可隨時 **關閉助手** 僅用表單（備援 UX）。  
**目標版面（v0.2）**：見 **E 階段「助手優先（Assistant-first）」**—預設 **主舞台僅助手**，表單收斂至 **摘要／進階**；備援與「關閉助手」語意由 **L4 進階** 承接。

---

## A4 — 長尾自然語言＋備援 UX

| 情境 | 行為 |
|------|------|
| NL 可解析出 category＋region | 與現有 `parse_user_intent` 相同；信心不足時 `clarification_question` |
| 冷門／槽位填不滿 | **不阻塞**：保留「自行描述」輸入框；**進階**＝關閉助手、直接用 Step1～3 表單與 Step2 池 |
| AI／API 失敗 | Toast＋可重試；表單仍可用 |
| 動態 RSS 無合適候選 | Step2 仍可走「貼 URL／驗證」（架構 ④，另迭代） |

**i18n**：所有使用者可見引導句走 `channels.guided.*`（zh-TW／en／ja）。

---

## B1 — 檢索 MVP（ADR 摘要）

| 方案 | MVP | 後續 |
|------|-----|------|
| **僅站內白名單** | ✅ **採用**：`DEFAULT_RSS_SOURCES`／`list_default_primary_feeds`，可 `exclude_urls` 篩選 | 成本低、無 SSRF 外部放大 |
| 外部搜尋 API | ❌ 本階段 | 成本／濫用需限流與預算 |
| RAG／知識庫 | ❌ 本階段 | 需內容管線與索引 |

**B3 銜接**：動態 URL 須經 **probe／SSRF 防護** 後才進候選池（與架構 ④ 同一路徑）；**本 MVP 僅回傳已在白名單內之 URL**，不主動 crawl 使用者貼上的陌生網域。

---

## A3 — API 契約（已實作端點）

### `POST /api/v1/channels/assist/wizard-options`

**Request（JSON）**

| 欄位 | 型別 | 說明 |
|------|------|------|
| `step` | `1 \| 2 \| 3` | 精靈步驟 |
| `category` | optional enum | Step≥2 時建議帶入 |
| `region` | optional enum | Step≥2 時建議帶入 |
| `exclude_urls` | string[] | 已選或排除之 URL（正規化 trim） |

**Response（JSON）**

| 欄位 | 說明 |
|------|------|
| `step` | 回聲 |
| `retrieval_mvp` | 固定 `"whitelist_default_rss"`（便於前端／日誌辨識） |
| `quick_options` | `{ kind: "category"\|"region", value, label_key }[]` — `label_key` 對應前端 i18n |
| `feed_options` | `{ kind: "feed", name, url, role }[]` — 僅 Step2 且 category＋region 皆有效時填充；已扣 `exclude_urls` |

**錯誤**：沿用全域錯誤格式；驗證失敗 422。

---

## B2／B4 — 服務邊界

- **產生候選**：`channel_assist_service.get_wizard_options` → 呼叫 `channel_service.list_default_primary_feeds`（與 `GET .../defaults/rss-sources` 同源）。
- **與 `POST /channels/assist` 關係**：意圖解析維持獨立；精靈選項為 **非 AI** 之結構化列表（可與 AI 建議並列於 UI）。

---

## C1～C4 — 前端（迭代順序）

1. **C1**：助手頂部引導文案＋備援出口（關閉助手）。**版面主從** 以 **E 階段** 為準（Phase B 起「預設即助手」）。
2. **C2**：依 `wizard-options` 渲染 **類別** 列（Step1）；Step2 可於後續在助手或側欄重用 `feed_options`。
3. **C3**：與現有快捷鈕並存；逐步收斂重複 UI。
4. **C4**：`data-testid`：`btn-channels-guided-category-{value}` 等。

---

## D1／D2 — 風險與驗收

- **D1**：本端點無額外 AI 呼叫；仍受全站 rate limit／JWT 保護。
- **D2**：影響檔案：`channels.py`、`channel_assist_service.py`、`channels.ts`、`CreateChannel.tsx`、`i18n/index.ts`。

---

## E — 助手優先版面（Assistant-first）— **Phase A 規格凍結**（2026-05-08）

> **Phase A 定義**：本節只凍結 **產品／資訊架構／驗收文字**；**不承諾** `CreateChannel.tsx` 已改版（Phase B 起才動 UI）。

### E1 — 目標（一句話）

使用者從「我的頻道 → 建立頻道」進入 **`/channels/create`** 後，**預設主版面僅呈現 AI 助手**（對話流、輸入、助手提供的結構化捷徑按鈕）；**無需再點「開啟／喚起 AI 助手」** 即可完成頻道設立（含送出前可理解的確認）。

### E2 — 資訊架構（L0～L4）

| 層級 | 職責 | 使用者可見（目標） |
|:----:|------|-------------------|
| **L0** | 導覽 | 標題、返回；可選極短副標（如「由助手帶你完成」）— **i18n** |
| **L1 主舞台** | 唯一核心 | 助手訊息流、輸入框、**類別／地區／RSS 相關捷徑**（視覺上歸屬助手，非傳統表單主欄） |
| **L2 進度** | 可預期 | **頂部細進度條** 或 **助手內「目前已具備／尚缺」** 二選一或混合—實作於 Phase B 定案 |
| **L3 摘要** | 信任與送出前檢查 | **可展開摘要卡**：頻道名稱、描述要點、已選 RSS 重點（至少覆蓋其一組合，細節 Phase B 對照現有 state） |
| **L4 進階／脫困** | 手動偏好、錯誤 | **折疊區**：極簡表單或「改用手動」；AI／API 失敗時 **重試＋降級** 文案與按鈕（沿用現有 Toast／429 策略） |

### E3 — 設計原則（凍結）

- **預設即助手**：路由進入後 **零次必須點擊** 才能看到助手主介面（不得把「開助手」設為主路徑門檻）。
- **按鈕＝助手動作**：捷徑在資訊架構上屬 **L1**，與「右側大表單」脫鉤（表單退居 L3／L4）。
- **表單不主導**：`name`／`category`／`selected_feeds` 等仍由 state／API 承載；**畫面以對話＋摘要為主**。
- **可完成性**：任一步皆能回答「還缺什麼才能建立」（L2 或助手氣泡明示）。
- **無障礙**：焦點順序、步驟語意（標題層級或 `aria`）— Phase B 實作時對照 `按鈕測試ID架構表.md` 補 `data-testid`。

### E4 — 使用者狀態流（簡化）

`進入` → `蒐集意圖（類別／地區／關鍵字／RSS）` → `助手補齊命名與描述（#32／#33）` → `確認摘要（L3）` → `建立（POST /channels）` → `成功／失敗與下一步`

（與現有 Step1～3 **業務規則對齊**，Phase B 僅改 **預設版面與視覺主從**。）

### E5 — Phase A 驗收標準（文件階段 DoD）

1. 讀完 **E 階段** 能說明：**誰是主畫面**、**表單在哪一層**、**進階何時出現**。  
2. **L2** 呈現形式已列為 **二選一或混合**（未強制實作選項）。  
3. **L3 摘要** 必備欄位至少含：**名稱、描述、RSS 選取狀態** 之最小組合（可展開／可編輯規則留 Phase B）。  
4. **Phase B～D** 已於 **2026-05-09** 交付（見 `channel_create_new_scheme_checklist.md`）；與本節無衝突。

### E6 — 後續階段（本文件標示；**未**承諾排期）

| 階段 | 內容 | 狀態 |
|------|------|:----:|
| **Phase B** | `CreateChannel.tsx`：預設助手、並排主從、摘要、lg 表單收合／展開；`showAssist` 預設 true | ✅ 2026-05-09 |
| **Phase C** | 敘事對齊、429／橫幅／RWD／抽屜／鍵盤循環等 | ✅ 2026-05-09 |
| **Phase D** | `data-testid`、**D.1** 手測腳本、建置驗證；瀏覽器 E2E 見測試週 | ✅ 2026-05-09（開發可驗） |

**與「全集願景」**：核心體驗目標、L0～L5、前後端、**第五節資料生命週期**、**第六節測試／發布／營運** 見 **[channel_create_full_vision_一至四.md](./channel_create_full_vision_一至四.md)**；檢查清單 **H、I** 於測試階段勾選。本檔 Phase B～D 為 **自該全集落地之切片**，非全集本身。

---

## 實作狀態

| 項目 | 狀態 |
|------|------|
| 本規格文件 | ✅ v0.2（E 階段 A 凍結） |
| **助手優先（Assistant-first）版面 UI** | ✅ 2026-05-09；見 **E 階段**、`channel_create_new_scheme_checklist.md` **B～D** |
| `POST .../assist/wizard-options` | ✅ MVP |
| CreateChannel 引導列＋API 類別列 | ✅ MVP（Step1 助手內） |
| Step2 助手：`wizard-options` step=2、地區列＋`feed_options`（扣 exclude） | ✅ MVP |
| Step2 主表單側欄專用「精靈列」（不開助手） | ⏳ 可選 |
| `POST /channels/assist` 之 `exclude_urls`（再推薦） | ✅ MVP |
| `POST /channels/feeds/validate`（SSRF + feedparser） | ✅ MVP；Step2 貼上 URL UI；**per-IP 嚴格限流**（Redis 若可用則多機共享；否則記憶體）；429 `detail.code` |
| `GET /channels/feeds/search?q=`（白名單 AND 關鍵字） | ✅ MVP；Step2 搜尋；同上；429 `detail.code`：`feed_search_rate_limit` |
| assist／wizard **Step3** 建議命名／描述（#32/#33） | ✅ MVP（AI JSON + 後端範本）；Step3 套用 |
