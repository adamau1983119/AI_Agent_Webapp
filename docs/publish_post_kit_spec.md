# 發文套件（Post Kit）— 產品規格與 Checklist

> **版本**：v0.1  
> **建立日期**：2026-05-27  
> **狀態**：📋 **產品主路（L0）— 待開發**  
> **取代／降級**：多平台 **API 代發** 為 **L2 選配**（見 [`social_connect_publish_verify_gate.md`](./social_connect_publish_verify_gate.md)）

**相關**：[`工作記錄.md`](../工作記錄.md)「產品主路—Post Kit」、[`test_week_daily_checklist.md`](./test_week_daily_checklist.md)、[`專案完整架構表.md`](../專案完整架構表.md)

---

## 1. 核心（一句）

**本網站核心 = 給網紅「可發一篇貼文」的素材與選擇**（標題候選、內文、Hashtag、照片）；每項附 **複製 icon**，使用者 **貼到自有平台**（FB／IG 等）發布——**不在站內代發**。

---

## 2. 產品定位

### 2.1 我們做什麼

| 做 | 不做（MVP） |
|----|-------------|
| 策展趨勢／主題 **資料** 供選擇 | 嵌入各平台發布 iframe |
| 產出與編輯 **Post Kit** 四類元件 | 多平台 OAuth + Graph **代發**（L2） |
| **一鍵複製** 到剪貼簿 | 代替使用者在平台 **裁圖、排程、音樂** |
| 字數／Hashtag **建議**（規則提示） | 保證各平台演算法成效 |

### 2.2 兩個畫面（使用者心模型）

```text
【畫面 A】Influencers AI（本專案）
  靈感 → 主題 → 詳情 Post Kit → 逐項 Copy

【畫面 B】Facebook / Instagram / …（使用者自己的 App）
  貼上標題、內文、Hashtag，上傳／選圖，用平台原生工具發布
```

**我們只負責 A；B 由使用者操作。** 價值在 **選得對、複製快**，不在 **代發中介**。

### 2.3 與 Phase 5（分發）的關係

| 層級 | 名稱 | 說明 |
|:----:|------|------|
| **L0（MVP 主路）** | **Post Kit + Copy** | 本文件 |
| **L1** | 半自動 | 複製 +「在 Facebook 開啟」深連結（仍不代發） |
| **L2（選配）** | API 代發 + 連線 Gate | [`social_connect_publish_verify_gate.md`](./social_connect_publish_verify_gate.md) |

---

## 3. Post Kit 四類元件

每類：**預覽 + 選擇（若適用）+ 複製 icon**；複製成功 → toast（i18n 三語）。

| # | 元件 | 內容 | UI 要點 | 複製輸出 |
|:-:|------|------|---------|----------|
| **1** | **標題** | **2～3 個候選**（不同鉤子：好奇／利益／問題） | 並列或 Tab；標示「建議 1／2／3」 | 純文字單標題 |
| **2** | **內文** | 短文（`article`）；可選 **腳本**（`script`） | 字數提示（如「約 300 字」）；與生成設定連動 | 純文字 |
| **3** | **Hashtag** | 建議 tag 列表（可編輯後再 copy） | 顯示 `#tag` chips；可增刪 | `#a #b #c` 或換行 |
| **4** | **照片** | 主題圖 + 搜圖候選（1～N） | 縮圖格；每張 **copy 連結** 或 **下載** | URL 或提示「長按儲存」 |

### 3.1 可選：一鍵複製全文

次要按鈕 **「複製全部文字」** = 標題（已選）+ 內文 + Hashtag 合併；**圖片不包含**（各平台上傳流程不同）。

### 3.2 資料來源（對齊現有後端）

| 元件 | 現有 API／欄位 |
|------|----------------|
| 標題候選 | **待開發**（可先 UI  mock：主題 `title` + AI 變體端點） |
| 內文／腳本 | `GET/POST /api/v1/contents/{topic_id}`、`regenerate` |
| Hashtag | 主題 `keywords`、助手／`generate` 擴充 |
| 照片 | `GET /api/v1/images/{topic_id}`、詳情圖片區 |

---

## 4. 主舞台與路由

| 優先 | 路由 | 角色 |
|:----:|------|------|
| **P0** | **`/topics/:id`** | **Post Kit 主舞台**（詳情頁內區塊或右欄） |
| P1 | `/publish` | 改名 **「發布助手」**：僅 Post Kit 摘要 + copy（**隱藏** API 發布按鈕） |
| P2 | `/inspiration` | 進主題後進入 Post Kit（維持現流） |
| — | `/social-connect` | MVP **隱藏** 或標「進階／稍後」 |

```text
/topics/:id
  ├─ 主題標題（現有）
  ├─ 生成設定 / 重新生成（現有）
  └─ 【Post Kit】← 新增
        ├─ 標題候選 [copy]×3
        ├─ 內文 [copy]  腳本 [copy]
        ├─ Hashtag [copy]
        └─ 圖片 [copy link] [download]
```

---

## 5. UI／UX 規範

### 5.1 複製互動

- 每項使用 **icon 按鈕**（如 Lucide `Copy`）；`data-testid` 前綴 `btn-postkit-copy-*`。
- 使用 `navigator.clipboard.writeText`；失敗時 fallback `document.execCommand('copy')`。
- 成功：`toast.success(t('postKit.copied'))`；可選顯示「請到您的平台貼上」。

### 5.2 i18n（須三語）

建議 key 前綴 `postKit.*`（`frontend/src/i18n/index.ts`）：

- `postKit.sectionTitle` — 發文套件
- `postKit.titleOptions` — 標題選擇
- `postKit.copy` / `postKit.copied` / `postKit.copyAll`
- `postKit.body` / `postKit.script` / `postKit.hashtags` / `postKit.photos`
- `postKit.hint.pasteOnPlatform` — 請到 Facebook／Instagram 貼上發布

### 5.3 無障礙

- 複製鈕 `aria-label` 含元件名稱；觸控區 **≥44px**（對齊 RWD checklist）。

---

## 6. 開發 Checklist

### 6.1 後端（最小）

- [ ] （P1）`GET /api/v1/contents/{topic_id}/post-kit` 聚合：內文、腳本、keywords、image URLs、主題 title
- [ ] （P2）`POST …/title-suggestions` 回傳 2～3 標題候選（AI 或模板）
- [ ] 不新增發布 API 依賴

### 6.2 前端

- [ ] 元件 `PostKitPanel.tsx`（四區 + copy）
- [ ] 嵌入 `TopicDetail.tsx`（主舞台）
- [ ] `/publish`：隱藏 `socialApi.publishContent` 主按鈕；改 Post Kit 導向詳情或內嵌同款面板
- [ ] feature flag（可選）：`VITE_ENABLE_API_PUBLISH=false` 預設關閉 L2
- [ ] i18n zh-TW／en／ja
- [ ] `data-testid` 對照 [`按鈕測試ID架構表.md`](../按鈕測試ID架構表.md) 補登

### 6.3 文件

- [x] 本規格 v0.1
- [ ] 更新 [`專案完整架構表.md`](../專案完整架構表.md) `/publish` 說明為「發布助手」
- [ ] [`README.md`](../README.md) 頂部產品一句對齊 Post Kit

---

## 7. 測試 Checklist

> **禁止模糊簽收**：不得僅「詳情能開」；須 **每個 copy 按鈕** 驗證剪貼簿內容。

### 7.1 Post Kit 專項（建議截圖 PK1～PK4）

| # | 步驟 | PASS 標準 | ☐ |
|:-:|------|-----------|:-:|
| PK1 | 開 `/topics/{固定 topic_id}` | 看見 **發文套件** 四區 | ☐ |
| PK2 | 點 **標題候選 1** 的 copy | 剪貼簿 = 該標題純文字 | ☐ |
| PK3 | 點 **內文** copy | 剪貼簿含短文（與畫面一致） | ☐ |
| PK4 | 點 **Hashtag** copy | 剪貼簿含 `#` 開頭 tags | ☐ |
| PK5 | 點 **圖片** copy 連結 | 剪貼簿為可開之 https URL | ☐ |
| PK6 | 375×747 RWD | 四區可讀、copy 鈕可點、無橫向捲動 | ☐ |

### 7.2 測試週對照（修訂 2026-05-27）

| 原項 | 新標準 |
|------|--------|
| **詳情 2.x** | 併 **PK1～PK6**（Post Kit 為詳情核心驗收） |
| **S4-6** `/publish` | **發布助手** 頁可開、無裸 key；**或** 詳情 Post Kit **PK** 全過即視為覆蓋 |
| **S4-7** `/social-connect` | **N/A（L0）** 或僅記錄「頁面隱藏／進階」 |
| **S11** `/publish` | 同 S4-6；**不要求** `POST …/social/publish` |
| **矩陣 H3** | 改為 **Post Kit copy**；H1～H2 OAuth **N/A（L0）** 除非做 L2 |

### 7.3 記錄格式（貼 `工作記錄.md`）

```text
Post Kit PASS — /topics/…：標題×3 copy OK；內文、Hashtag、圖片連結 copy OK（375×747 截圖 PK）
S4-6 N/A（L0）— 產品主路 Post Kit；/publish 無 API 代發
S4-7 N/A（L0）— 不要求 Facebook 連線
```

---

## 8. 決策紀錄

| 日期 | 決策 |
|------|------|
| 2026-05-27 | **MVP 主路 = Post Kit + Copy**；放棄以 API 代發為核心驗收 |
| 2026-05-27 | 主舞台 **`/topics/:id`**；`/social-connect` 不阻測試週結案 |
| 2026-05-27 | L2 API 發布保留程式但 **feature flag 關閉**，文件見 Gate 規格 |

---

## 9. 修訂紀錄

| 日期 | 版本 | 說明 |
|------|------|------|
| 2026-05-27 | v0.1 | 初稿：產品定位、四元件、UI、開發／測試 Checklist |
