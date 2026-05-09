# ngrok 設定指南（僅供「測試 Meta 連接／發文」使用）

**可選方案：** 若不想用 ngrok，可改為**本機 HTTPS 自簽憑證**測試，見專案根目錄 **LOCAL_HTTPS_META_TEST.md**（不需帳號、網址固定為 localhost）。

---

**重要：請勿把 ngrok 當成預設設定。**  
此流程僅在你要**測試 Meta 平台連接或一鍵發文**時使用（因 Meta 要求回調網址為 https）。  
**測完後請依下方「測完後還原」還原 backend／frontend 的 .env**，否則其餘功能在未開 ngrok 時會無法連線或異常。

Meta 要求 OAuth 回調網址必須為 **https**。本機開發時可**暫時**用 ngrok 將 `http://localhost:8000` 對外成 https 網址。

---

## 一、前置準備

- 已安裝 [ngrok](https://ngrok.com/)（若未安裝：官網下載或 `choco install ngrok`）
- 後端可正常在 8000 埠啟動

---

## 二、每次測試 Meta 連接時的步驟

### 步驟 1：啟動後端

在專案 **backend** 目錄執行（請用 **python -m uvicorn**，不要直接打 `uvicorn`）：

```powershell
cd "f:\Adam 2025\Myproject\AI_Agent_Wbbapp_for_Social_Media_Content_Generation\backend"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

若你有建立虛擬環境（例如 `venv`），可先啟動再執行：
```powershell
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

保持此終端開啟。

---

### 步驟 2：啟動 ngrok

**另開一個終端**，執行：

```powershell
ngrok http 8000
```

終端會顯示類似：

```
Forwarding   https://a1b2c3d4-xx-xx-xx.ngrok-free.app -> http://localhost:8000
```

請複製 **https 開頭的那段網址**（例如 `https://a1b2c3d4-xx-xx-xx.ngrok-free.app`），後面步驟會用到，以下以 `https://YOUR_NGROK_URL` 表示。

> 免費版 ngrok 每次重開網址會變，所以每次重開 ngrok 都要重做步驟 3、4。

---

### 步驟 3：改後端 .env

編輯 **backend\.env**，將 `BACKEND_URL` 改為你的 ngrok https 網址（不要加路徑，不要加結尾斜線）：

```env
BACKEND_URL=https://YOUR_NGROK_URL
```

例如：

```env
BACKEND_URL=https://a1b2c3d4-xx-xx-xx.ngrok-free.app
```

儲存後，**重啟後端**（在跑 uvicorn 的終端按 Ctrl+C，再重新執行步驟 1）。

---

### 步驟 4：改前端 API 網址

讓前端呼叫後端時也走 ngrok，否則登入後回調會錯。

在 **frontend** 目錄建立或編輯 **.env**（若已有 .env 就改其中一行即可）：

```env
VITE_API_URL=https://YOUR_NGROK_URL/api/v1
```

例如：

```env
VITE_API_URL=https://a1b2c3d4-xx-xx-xx.ngrok-free.app/api/v1
```

儲存後，**重啟前端**（Ctrl+C 後重新 `npm run dev`）。

---

### 步驟 5：改 Meta 後台回調網址

1. 開啟 [Meta for Developers](https://developers.facebook.com/) → 你的應用程式「Influencers AI Agents」
2. **應用程式設定** → **進階**
3. 在 **應用程式驗證** 的 **授權回呼網址** 填：
   ```
   https://YOUR_NGROK_URL/api/v1/social/meta/callback
   ```
4. 儲存變更。

---

## 三、測試流程

1. 後端、ngrok、前端皆已啟動，且 .env 與 Meta 皆已改為本次 ngrok 網址。
2. 瀏覽器開啟前端（例如 `http://localhost:3000`）。
3. 到 **平台連接** → 點連接 Meta → 完成 Facebook 授權。
4. 回網站後應顯示已連接；再到 **一鍵發布** 選內容與平台測試發文。

---

## 四、測完後還原（必做，避免影響其他功能）

**測試完 Meta 後請務必還原**，否則平常開發時未開 ngrok 會導致 API 連線失敗：

- **backend\.env**：改回 `BACKEND_URL=http://localhost:8000`
- **frontend**：刪除 `frontend\.env`，或將其中 `VITE_API_URL` 改回 `http://localhost:8000/api/v1`（或刪除該行，使用程式預設）
- Meta 後台：若之後不測 Meta，可改回或刪除 ngrok 回調網址；若正式環境要用 https 則保留正式網域。

---

## 五、常見問題

| 問題 | 處理方式 |
|------|----------|
| ngrok 重開後網址變了 | 再執行步驟 3、4、5，把新網址填進 .env 與 Meta。 |
| 前端仍打 localhost:8000 | 確認 frontend\.env 有 `VITE_API_URL=https://...` 且已重啟前端。 |
| Meta 仍報 redirect_uri 錯誤 | 確認 Meta 的授權回呼網址與 BACKEND_URL 完全一致（含 https、無多餘斜線）。 |
