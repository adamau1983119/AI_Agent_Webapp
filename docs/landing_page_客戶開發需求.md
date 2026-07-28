# 登入前介紹頁（Landing Page）— 客戶開發需求

> **文件版本**：v1.0  
> **建立日期**：2026-06-02  
> **狀態**：📋 需求定稿（待設計／開發排程）  
> **優先級**：🔴 P0（對外第一印象；目前根路徑無介紹頁）  
> **產品**：Influencers AI（網紅 AI 助手）  
> **相關文件**：[landing_page_feature_brief.md](./landing_page_feature_brief.md)（功能盤點／第三方討論）、[landing_page_feature_brief.html](./landing_page_feature_brief.html)（可讀＋複製）、[專案完整架構表.md](../專案完整架構表.md)、[publish_post_kit_spec.md](./publish_post_kit_spec.md)、[品牌設計規範.md](../品牌設計規範.md)、[按鈕測試ID架構表.md](../按鈕測試ID架構表.md)

---

## 📋 需求概述

### 核心（一句）

**新增登入前的「第一頁」**：向未註冊訪客介紹產品核心價值與功能好處，並以明確 CTA **引導註冊／登入**。

### 現況與問題

| 項目 | 現況 | 問題 |
|------|------|------|
| 根路徑 `/` | `RootRedirect`：有 token → `/dashboard`；無語言 → `/language`；否 → `/login` | 訪客**看不到**產品介紹，直接進登入流程 |
| 對外敘事 | 功能分散在登入後 Sidebar | 新用戶**不理解**站內能做什麼、為何要註冊 |
| 行銷／第三方 | 僅有內部 brief | 需正式**客戶開發需求**供設計與工程估工 |

### 目標

1. **吸引**：3 秒內讓訪客理解「這是給網紅／創作者的 AI 內容助手」  
2. **說服**：以 **6 項主打功能** + 每項 **≤20 字** 好處說明價值  
3. **轉換**：主 CTA 導向 **註冊或登入**  
4. **對齊 MVP**：強調 **Post Kit + 複製發文**（站內產素材 → 貼到 FB／IG），**非站內代發**

---

## 1. 使用者與情境

### 1.1 目標使用者

- 網紅、KOL、自媒體創作者  
- 需定期發 Fashion／Food／Trend 等主題內容者  
- 希望減少選題、寫稿、找圖時間者  

### 1.2 使用情境

| # | 情境 | 期望行為 |
|---|------|----------|
| U1 | 朋友分享連結，首次進站 | 閱讀介紹 → 點「免費開始」→ 註冊 |
| U2 | 搜尋或廣告進站，尚未決定 | 瀏覽 6 功能卡 → 點「登入」 |
| U3 | 已選語言、未登入 | 從 Landing 進 `/login` 或 `/register` |
| U4 | 已登入舊用戶誤開 `/` | **不**看 Landing，直接進 `/dashboard` |

---

## 2. 頁面資訊架構（IA）

### 2.1 建議區塊（由上而下）

| 順序 | 區塊 | 目的 | 必填 |
|:----:|------|------|:----:|
| 1 | **Header** | Logo、語言切換、登入／註冊 | ✅ |
| 2 | **Hero** | 一句價值主張 + 副標 + 主 CTA + 次 CTA | ✅ |
| 3 | **功能卡 ×6** | 主打功能 + 好處（≤20 字） | ✅ |
| 4 | **進階功能（折疊）** | 平台連線、排程等次要能力 | 建議 |
| 5 | **Footer** | `/terms`、`/privacy`、版權 | ✅ |

### 2.2 不放在首屏主視覺

- Meta OAuth／平台連線細節  
- 排程、偏好權重技術說明  
- 導師模式（**規劃中，未上線**—若提及須標「即將推出」）  
- API 代發（L2，**非 MVP**）

---

## 3. 內容需求 — 主打 6 項（SoT）

> 文案原則：**繁中好處每項 ≤20 字**；英文／日文由 i18n 對等翻譯，長度可略調但語意一致。

| # | 功能名稱 | 好處（繁中，≤20字） | 圖示建議 |
|---|----------|---------------------|----------|
| 1 | **主題趨勢** | 自動收時尚美食熱點，選題省時間 | 趨勢／報紙 |
| 2 | **AI 寫稿／重生** | 一鍵產文配圖，少花構思時間 | 魔法筆／文件 |
| 3 | **建立頻道（AI 助手）** | 用說話建頻道，不必懂 RSS | 對話／頻道 |
| 4 | **靈感策劃** | 搜尋加 AI 對話，找企劃靈感 | 燈泡 |
| 5 | **風格學習** | 按讚踩學偏好，越用越像你 | 星星／調色 |
| 6 | **複製發文（Post Kit）** | 標題內文標籤複製，貼平台即發 | 複製／火箭 |

**Post Kit 表述（待客戶確認）**：

- **方案 A**：寫「即將推出」— 因 L0 UI 尚未完整交付  
- **方案 B**：寫「已可從主題詳情產出素材」— 弱化 Post Kit 品牌詞  
- **預設建議**：方案 A，避免過度承諾  

### 3.1 Hero 文案（草案，可交設計潤飾）

| 元素 | 繁中草案 |
|------|----------|
| **主標** | 你的 AI 內容助手，從靈感到發文 |
| **副標** | 自動收熱點、AI 寫稿配圖，複製貼上就能發 |
| **主 CTA** | 免費開始 → `/register` |
| **次 CTA** | 已有帳號？登入 → `/login` |

### 3.2 進階功能（折疊區，可選）

| 功能 | 好處（≤20字） |
|------|----------------|
| 多語言 | 繁中英日，海外網紅也能用 |
| 自動收集 | 背景抓 RSS，不用自己刷新聞 |
| 來源驗證 | 推薦來源較可靠，少亂連 |

---

## 4. 功能需求

### 4.1 路由與導向（待決，預設方案如下）

**建議預設（待客戶拍板）**：

```text
未登入 + 已選語言：
  GET / 或 GET /welcome → Landing 頁

已登入（有 token）：
  GET / → /dashboard（維持現狀）

未選語言（首次）：
  維持 /language → 選完語言 → Landing 或 /login（二選一，見待決項）
```

| ID | 需求 | 優先 |
|----|------|:----:|
| FR-1 | 新增 Landing 路由（`/welcome` **或** 未登入時 `/` 顯示 Landing） | P0 |
| FR-2 | 已登入使用者訪問 Landing 路由時 **302 → `/dashboard`** | P0 |
| FR-3 | Hero／Header CTA：主按鈕 → `/register`；次按鈕 → `/login` | P0 |
| FR-4 | Footer 連結 → `/terms`、`/privacy`（既有靜態頁） | P0 |
| FR-5 | Header 語言切換：zh-TW／en／ja（對齊全站 i18n） | P0 |
| FR-6 | 功能卡可選：點擊錨點捲動或連到登入後對應路由說明（**登入前不開功能頁**） | P1 |

### 4.2 與現有登入前頁面關係

| 既有路由 | 與 Landing 關係 |
|----------|-----------------|
| `/language` | 首次進站語言選擇；選完後導向 Landing（建議）或 `/login` |
| `/login`、`/register` | Landing CTA 目標；Landing **不取代** 登入表單 |
| `/forgot-password`、`/verify-email` | 維持不變；由登入／註冊頁進入 |

### 4.3 國際化（i18n）

| ID | 需求 |
|----|------|
| I18N-1 | 所有使用者可見字串寫入 `frontend/src/i18n/index.ts`（zh-TW／en／ja） |
| I18N-2 | **禁止**硬編碼可見中文（品牌名 Influencers AI 除外） |
| I18N-3 | Hero、6 功能卡、CTA、Footer 皆需三語 key |

**建議 key 前綴**：`landing.hero.*`、`landing.features.*`、`landing.cta.*`、`landing.footer.*`

### 4.4 UI／品牌

| ID | 需求 |
|----|------|
| UI-1 | 對齊 [品牌設計規範.md](../品牌設計規範.md)（Lane Crawford 風格基調） |
| UI-2 | RWD：375px 無橫向捲動；功能卡小螢幕 **單欄** 或 **橫向滑動**（設計定案） |
| UI-3 | 主 CTA 觸控區 **≥44px** |
| UI-4 | 新增按鈕須有 `data-testid`（對照 [按鈕測試ID架構表.md](../按鈕測試ID架構表.md)） |

**建議 testid（草案）**：

| testid | 元素 |
|--------|------|
| `btn-landing-register` | 主 CTA「免費開始」 |
| `btn-landing-login` | 次 CTA「登入」 |
| `link-landing-terms` | 使用條款 |
| `link-landing-privacy` | 隱私政策 |

---

## 5. 非功能需求

| ID | 項目 | 標準 |
|----|------|------|
| NFR-1 | 首屏載入 | 靜態資源為主；目標 **< 3s**（本機 dev 參考） |
| NFR-2 | SEO（選配 P1） | `<title>`、`<meta description>` 三語或依語言切換 |
| NFR-3 | 無需後端新 API | Landing 為**純前端**靜態內容頁（除非日後 CMS） |
| NFR-4 | 無需登入即可瀏覽 | 公開頁，不呼叫需 Bearer 的 API |

---

## 6. 範圍外（本需求不做）

- 站內 Meta／Facebook **代發**（L2）  
- Post Kit **完整 UI** 開發（另見 `publish_post_kit_spec.md`）  
- 導師／同伴模式  
- 付費方案、價格表（除非客戶另開需求）  
- CMS 後台編輯 Landing 文案（v1 以 i18n 檔維護）  
- 為 Landing 擅自改 `.env`、ngrok、HTTPS 預設（README 規則 #14）

---

## 7. 驗收標準（Definition of Done）

### 7.1 必過（P0）

- [ ] 未登入使用者可開啟 Landing，看見 Hero + **6 功能卡** + CTA  
- [ ] 主 CTA 可進 `/register`；次 CTA 可進 `/login`  
- [ ] 已登入使用者開 `/`（或 Landing 路由）→ **`/dashboard`**  
- [ ] Footer 可開 `/terms`、`/privacy`  
- [ ] **zh-TW／en／ja** 切換後文案無裸 key、無硬編碼  
- [ ] 375px RWD：無橫向捲動；CTA 可點  
- [ ] `npm run build` **exit 0**  
- [ ] 新增 `data-testid` 已登記或更新架構表  

### 7.2 建議（P1）

- [ ] 進階功能折疊區  
- [ ] `<meta description>` 三語  
- [ ] 設計稿／截圖存檔供 `工作記錄.md` 引用  

---

## 8. 待客戶／第三方決策

| # | 議題 | 選項 | 建議 |
|---|------|------|------|
| D1 | Landing 路由 | A) `/welcome` B) 未登入 `/` 即 Landing | **B**（SEO 友善） |
| D2 | 選語言後導向 | A) Landing B) 直接 `/login` | **A** |
| D3 | Post Kit 對外文案 | A) 即將推出 B) 已可用（弱化） | **A** |
| D4 | 主 CTA 目標 | `/register` vs `/login` | **`/register`** |
| D5 | 社會證明區 | 有／無 testimonial、截圖 | **v1 無**（缺素材） |
| D6 | Footer 位置 | 首屏可見 vs 僅頁尾 | **僅頁尾**（Hero 簡潔） |

---

## 9. 技術影響範圍（開發參考）

| 層 | 檔案／模組 | 變更類型 |
|----|-----------|----------|
| 前端路由 | `frontend/src/app/App.tsx` | 新增 Landing route；調整 `RootRedirect` |
| 新頁面 | `frontend/src/pages/Landing.tsx`（或 `Welcome.tsx`） | **新增** |
| i18n | `frontend/src/i18n/index.ts` | **新增** landing.* keys |
| 架構表 | `專案完整架構表.md` | 補路由列、移除「缺口」註記 |
| 測試 | `docs/test_week_daily_checklist.md` **L5～L6** | 實作後勾選 |

**分支**：依 [Git分支策略與版本管理.md](../Git分支策略與版本管理.md) — **`feature/landing-page`** → PR，**不直推 `main`**。

---

## 10. 附錄 — 全站功能一覽（登入後，供文案延伸）

> 詳細盤點見 [landing_page_feature_brief.md](./landing_page_feature_brief.md) 頻道區塊 3～頻道區塊 5。

| 功能 | 路由 | 好處（≤20字） |
|------|------|----------------|
| 儀表板 | `/dashboard` | 今日排程熱門一覽，進站知要做什麼 |
| 主題列表 | `/topics` | 自動收趨勢內容，選題不漏拍 |
| 主題詳情 | `/topics/:id` | 內文配圖重生稿，一頁準備發文 |
| 我的頻道 | `/channels` | 自訂類別地區，最多三條內容線 |
| 建立頻道 | `/channels/create` | AI 助手帶設定，不必懂技術 |
| 靈感策劃 | `/inspiration` | 搜尋加 AI，找企劃靈感 |
| 風格檔 | `/style-profile` | 評分學偏好，語氣越來越貼你 |

---

## 11. 修訂紀錄

| 版本 | 日期 | 說明 |
|------|------|------|
| v1.0 | 2026-06-02 | 初版：自 `landing_page_feature_brief` 升級為客戶開發需求 |

---

*本文件為 Landing 頁開發之客戶需求 SoT；討論用摘要與複製工具仍維護於 `landing_page_feature_brief.md`／`.html`。*
