# Vercel 環境變數設置指南

## 問題診斷

生產環境無法連接到後端 API，因為缺少 `VITE_API_URL` 環境變數。

當前代碼邏輯：
```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
```

如果沒有設置 `VITE_API_URL`，生產環境會嘗試連接到 `localhost`，這會導致連接失敗。

---

## 解決方案：在 Vercel 設置環境變數

### 步驟 1：訪問 Vercel 環境變數設置

1. 訪問 Vercel Dashboard：
   - https://vercel.com/adams-projects-f29f05d1/ai-agent-webapp/settings/environment-variables

2. 或通過以下路徑：
   - 登入 Vercel → 選擇專案 `ai-agent-webapp`
   - 點擊「Settings」→「Environment Variables」

---

### 步驟 2：添加環境變數

#### 2.1 添加 `VITE_API_URL`

**變數名稱：** `VITE_API_URL`

**變數值：** `https://gentle-enchantment-production-1865.up.railway.app/api/v1`

**環境：** 
- ✅ Production（生產環境）
- ✅ Preview（預覽環境）
- ✅ Development（開發環境，可選）

**說明：**
- 這是後端 API 的完整 URL
- 必須包含 `/api/v1` 後綴
- 確保後端 URL 正確（檢查 Railway Dashboard）

---

### 步驟 3：驗證設置

#### 3.1 檢查環境變數

在 Vercel Environment Variables 頁面確認：
- [ ] `VITE_API_URL` 已添加
- [ ] 值為：`https://gentle-enchantment-production-1865.up.railway.app/api/v1`
- [ ] 已選擇 Production 環境

#### 3.2 觸發重新部署

**方法 1：自動觸發**
- 環境變數設置後，Vercel 會自動觸發重新部署
- 等待部署完成（約 1-2 分鐘）

**方法 2：手動觸發**
- 如果沒有自動觸發，可以：
  1. 訪問 Deployments 頁面
  2. 點擊最新部署右側的「...」選單
  3. 選擇「Redeploy」

---

### 步驟 4：驗證修復

#### 4.1 檢查部署日誌

1. 訪問 Vercel Deployments：
   - https://vercel.com/adams-projects-f29f05d1/ai-agent-webapp/deployments

2. 點擊最新部署記錄

3. 檢查 Build Logs：
   - 確認構建成功
   - 確認環境變數已正確讀取

#### 4.2 測試生產環境

1. 訪問生產環境：
   - https://ai-agent-webapp-ten.vercel.app

2. 打開瀏覽器開發者工具（F12）→ Console

3. 檢查是否有 API 連接錯誤：
   - ❌ 如果看到 `Failed to fetch` 或 `CORS` 錯誤 → 檢查後端 CORS 設置
   - ✅ 如果沒有錯誤 → 環境變數設置成功

4. 測試功能：
   - 訪問 Dashboard
   - 檢查是否能載入主題列表
   - 檢查是否能生成內容

---

## 後端 URL 確認

### 如何確認後端 URL？

1. 訪問 Railway Dashboard：
   - https://railway.app/dashboard

2. 選擇專案：`gentle-enchantment`

3. 點擊「Settings」→「Networking」

4. 查看「Public Domain」：
   - 應該顯示：`gentle-enchantment-production-1865.up.railway.app`
   - 如果不同，請使用實際顯示的 URL

5. 確認後端健康檢查：
   - 訪問：`https://gentle-enchantment-production-1865.up.railway.app/health`
   - 應該返回 JSON 響應

---

## 常見問題

### Q1: 設置環境變數後，網站仍然無法連接後端

**可能原因：**
1. 環境變數未正確設置（檢查拼寫和值）
2. 後端 URL 不正確（檢查 Railway Dashboard）
3. CORS 設置問題（檢查後端 CORS 配置）
4. 需要重新部署（環境變數更改需要重新部署）

**解決方案：**
1. 確認環境變數設置正確
2. 確認後端 URL 正確
3. 檢查後端 CORS 設置（應該允許 `https://ai-agent-webapp-ten.vercel.app`）
4. 觸發重新部署

---

### Q2: 如何確認環境變數是否生效？

**方法 1：檢查構建日誌**
- 在 Vercel Build Logs 中，環境變數會在構建時被讀取
- 注意：`VITE_*` 變數會在構建時被內嵌到代碼中

**方法 2：在代碼中輸出（僅開發環境）**
```typescript
if (import.meta.env.DEV) {
  console.log('API URL:', import.meta.env.VITE_API_URL)
}
```

**方法 3：檢查 Network 請求**
- 打開瀏覽器開發者工具 → Network
- 查看 API 請求的 URL
- 確認是否指向正確的後端 URL

---

### Q3: 不同環境使用不同的後端 URL

**設置方式：**
- **Production：** `https://gentle-enchantment-production-1865.up.railway.app/api/v1`
- **Preview：** 可以使用相同的 URL，或設置為測試環境 URL
- **Development：** `http://localhost:8000/api/v1`（本地開發）

在 Vercel Environment Variables 頁面，可以為每個環境設置不同的值。

---

## 檢查清單

### 設置前檢查
- [ ] 確認後端 URL（Railway Dashboard）
- [ ] 確認後端服務正常運行（訪問 `/health` 端點）
- [ ] 確認後端 CORS 設置正確

### 設置時檢查
- [ ] 變數名稱：`VITE_API_URL`（必須以 `VITE_` 開頭）
- [ ] 變數值：完整的後端 URL（包含 `/api/v1`）
- [ ] 環境選擇：至少選擇 Production

### 設置後檢查
- [ ] 觸發重新部署
- [ ] 檢查部署日誌
- [ ] 測試生產環境功能
- [ ] 檢查瀏覽器 Console 是否有錯誤

---

## 相關文件

- **前端 API 配置：** `frontend/src/api/client.ts`
- **後端 CORS 配置：** `backend/app/config.py`
- **Vercel 配置：** `frontend/vercel.json`

---

## 下一步

設置完成後：
1. 等待部署完成
2. 測試生產環境功能
3. 確認所有 API 請求正常
4. 檢查 Dashboard 是否能正常載入數據

