# Google Ads／GA4 設定紀錄（2026-10-20 星期二）

斷線後只跟本檔「現在有效」。下面舊句若與這一節相反，以這一節為準。不要重做已合併的程式。不要另開第二份紀錄。

## 現在有效

- 五個市場這個月繼續投放，用來了解。美國、英國不暫停。日本、台灣不拆開。預算維持小額。
- 到達網址只用 `https://www.ai-alterego.com/language`（**2026-10-28 後台已確認**）。
- 不要改成日本 `/ja`、繁中 `/welcome` 當主到達網址。網站連結可連 `/welcome` `/en` `/ja`。
- `adammidlife.com` 之後才買。這個月不要寫進廣告。
- `sign_up` 是唯一主要轉換。網頁瀏覽已改次要。不要再匯入第二個 `sign_up`。
- **2026-10-28**：正式 Mongo 排除內部後 **外部客戶≈3**。**客戶數 SoT＝Mongo 外部**；GA4 `sign_up`×7 不可當 7 個外部客戶。預設不改程式。
- **2026-10-28 後台已做**：GA4 `sign_up` 重要活動；GA4↔Ads 連結；內部規則 `staff-office`＋篩選器測試中；Ads 網站連結；搜尋字詞排除 5 個。
- 今天不要做：日本圓子帳、自訂報表、BigQuery、客戶名單 100 人、加強型轉換、再開 MCC、促銷圖片衝優化分數。

## 現在停在這裡

2026-10-28：GA4／Ads 量尺與衛生後台項已做完。行銷週期快照／AI 合約已開 [`marketing_analytics_ai_contract.md`](./marketing_analytics_ai_contract.md)（分支 `feature/v8-marketing-period-snapshots`）。下一步可選：篩選器改「有效」、回家 IP、持續字詞清理；Looker 接 Sheet；正式庫首筆 upsert 須核准。

## 廣告帳戶現況

- 帳戶：`970-864-5947`（港幣）。登入 `info@ai-alterego.com`。
- 活動：`AI AlterEgo - Search - Global`。2026-10-16 開始，17 日開始曝光。
- 近窗約 22 點擊／~2083 曝光／CPC ~HK$1.19／費用 ~HK$26（以 Ads 總覽為準）。
- 到達網址：**已確認** `https://www.ai-alterego.com/language`（2026-10-28）。
- 網站連結：Welcome／English／日本語／繁體中文（2026-10-28）。
- 搜尋字詞：首批 5 個泛用 AI 字詞已排除（2026-10-28）。
- **2026-10-20 決定**：這五個市場先跑一個月，用來了解。美國、英國不暫停，也不拆日本、台灣。每日預算維持小額。
- 黃底「客戶名單要滿 100 人」先不做。

## 轉換頁現況（2026-10-20 12:02）

- 目標「註冊」：狀態仍是 **設定錯誤**。
- 轉換動作顯示名稱已改成 **`sign_up`**。來源網站、主要動作、一次轉換、價值 HK$1（只是占位）。狀態 **非運作中**。
- 顯示名稱改成 `sign_up` 不會自動開始記轉換。Tag Assistant 測到正式站登入之後才會變。
- 「網頁瀏覽」12:40 已改成次要動作。目標上的主要轉換動作數是 0。摘要列若仍印「主要」，以設定頁的「次要動作」為準。
- `generate_post`、`purchase` 可以之後匯入，先不要當出價目標。

## 程式已合併

- **PR #116** 已合 `main`，merge `f77a085`。提交 `8f1013a`。登入成功再送廣告轉換 `AW-18489161677/QrRhCJ2z-6IdEM3vqPBE`。
- **PR #115** 已合 `main`，merge `bb1d503`。提交 `7a7a770`。分支 `feature/v8-ga4-events`。
- 正式站成功後才送事件。本機不送。電郵不放進事件。
- `sign_up`：密碼登入、電郵註冊、Google 登入成功。
- `generate_post`：發文套件生成成功。
- `purchase`：點數結帳確認成功。
- 掛點：`frontend/src/lib/analytics.ts`、`frontend/src/stores/authStore.ts`、`frontend/src/pages/OAuthCallback.tsx`、`frontend/src/components/features/PostComposerPanel.tsx`、`frontend/src/components/features/CreditsBillingPanel.tsx`。
- 無新按鈕、無新 i18n 鍵。圖片搜尋、`titles_i18n`、sitemap、canonical 未改。扣點、`generate_content`、每日 15 未改。
- GA4 資源 `G-F38Q4L6CPV`。Ads 代碼 `AW-18489161677`。兩者本來就在正式站載入。
- 工作記錄與 `專案完整架構表_v8.md` 已寫 2026-10-20 這一筆。

## 還沒在後台做完的

轉換動作這一頁今天可以停。`sign_up` 已是網站主要轉換，標籤已由正式站送出。不要再把 GA4 的 `sign_up` 匯入成第二個主要轉換，否則會算兩次。

仍要在廣告活動裡做：

- 到達網址離開 `/ai/generator`。五個市場這一個月先共用一個存在的頁：`https://www.ai-alterego.com/language`。不要按國家拆活動。

這一個月不改地區：

- 美國、英國繼續投放。日本、台灣也不拆開。每日預算維持小額。

之後再做，今天不要開：

- GA4 連到 `970-864-5947`（方便對帳，不是這次轉換的前提）。
- 加強型轉換。事件裡沒有電郵。
- `generate_post`、`purchase` 先不要當出價目標。
- 日本圓子帳、自訂報表、BigQuery、客戶名單 100 人。MCC `373-100-3566` 不要再走一次開管理員。
- `adammidlife.com` 買到之後再換到達網址。這個月不要填。

## 更早、已合併、不要重做

- **PR #114** merge `1399a75`：`/welcome`、`/terms`、`/privacy` 各自 canonical。
- **PR #113** merge `9a4f917`：客人錯誤改「暫時無法使用」，DeepSeek 太忙回 `model_busy`。
