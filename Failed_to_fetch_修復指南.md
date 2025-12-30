# Failed to Fetch 錯誤修復指南

## 🔍 問題診斷

"Failed to fetch" 錯誤通常表示前端無法連接到後端 API。可能的原因：

1. **後端服務未運行**
2. **API URL 設定錯誤**
3. **CORS 設定問題**
4. **網路連接問題**

---

## ✅ 快速修復步驟

### 步驟 1: 檢查後端服務狀態

訪問後端健康檢查端點：
```
https://your-backend-domain.railway.app/health
```

**預期回應**：
```json
{
  "status": "healthy",
  "environment": "production"
}
```

**如果無法訪問**：
- 後端服務可能未運行
- 檢查 Railway 部署狀態
- 查看 Railway 日誌

---

### 步驟 2: 檢查前端 API URL 設定

**在 Vercel Dashboard**：

1. 訪問：https://vercel.com/dashboard
2. 選擇專案：`ai-agent-webapp`
3. 點擊 "Settings" → "Environment Variables"
4. 檢查 `VITE_API_URL`：
   - 應該設為：`https://your-backend-domain.railway.app/api/v1`
   - 確認沒有多餘的斜線
   - 確認使用 `https://`（不是 `http://`）

**如果未設定或錯誤**：
- 更新 `VITE_API_URL` 為正確的後端網域
- 保存後，Vercel 會自動重新部署

---

### 步驟 3: 檢查後端 CORS 設定

**在 Railway Dashboard**：

1. 訪問：https://railway.app/dashboard
2. 選擇專案：`AI_Agent_Webapp`
3. 點擊服務：`backend`
4. 點擊 "Variables" 標籤
5. 檢查 `CORS_ORIGINS`：
   - 應該包含：`https://ai-agent-webapp-ten.vercel.app`
   - 格式：逗號分隔或 JSON 陣列

**正確格式（逗號分隔）**：
```
https://ai-agent-webapp-ten.vercel.app,http://localhost:5173,http://localhost:3000
```

**正確格式（JSON 陣列）**：
```
["https://ai-agent-webapp-ten.vercel.app","http://localhost:5173","http://localhost:3000"]
```

**如果未設定或錯誤**：
- 添加或更新 `CORS_ORIGINS`
- 保存後，Railway 會自動重新部署

---

### 步驟 4: 清除瀏覽器快取

1. **硬重新載入**：
   - Windows: `Ctrl + Shift + R`
   - Mac: `Cmd + Shift + R`

2. **清除快取**：
   - 打開開發者工具（F12）
   - 點擊 "Application" 標籤
   - 點擊 "Clear storage"
   - 點擊 "Clear site data"

---

## 🔧 詳細診斷

### 診斷 1: 檢查瀏覽器 Console

1. 打開開發者工具（F12）
2. 點擊 "Console" 標籤
3. 查看錯誤訊息：

**如果是 CORS 錯誤**：
```
Access to fetch at '...' from origin '...' has been blocked by CORS policy
```
→ 解決：檢查後端 CORS 設定

**如果是網路錯誤**：
```
Failed to fetch
NetworkError when attempting to fetch resource
```
→ 解決：檢查後端服務是否運行

**如果是 404 錯誤**：
```
404 Not Found
```
→ 解決：檢查 API URL 是否正確

---

### 診斷 2: 檢查 Network 標籤

1. 打開開發者工具（F12）
2. 點擊 "Network" 標籤
3. 刷新頁面
4. 查看 API 請求：

**檢查項目**：
- **Request URL**：是否指向正確的後端網域
- **Status Code**：
  - `200` = 成功
  - `404` = API URL 錯誤
  - `500` = 後端錯誤
  - `CORS error` = CORS 設定問題
- **Response Headers**：檢查 `Access-Control-Allow-Origin`

---

### 診斷 3: 測試後端 API

使用 curl 或瀏覽器直接訪問：

```bash
# 測試健康檢查
curl https://your-backend-domain.railway.app/health

# 測試 API 端點
curl https://your-backend-domain.railway.app/api/v1/topics?page=1&limit=1

# 測試 CORS（使用 OPTIONS 請求）
curl -X OPTIONS \
  -H "Origin: https://ai-agent-webapp-ten.vercel.app" \
  -H "Access-Control-Request-Method: GET" \
  https://your-backend-domain.railway.app/api/v1/topics \
  -v
```

---

## 🚨 常見問題和解決方案

### 問題 1: 後端服務未運行

**症狀**：
- 無法訪問後端健康檢查端點
- Railway 日誌顯示錯誤

**解決**：
1. 檢查 Railway 部署狀態
2. 查看 Railway 日誌
3. 確認環境變數已正確設定
4. 重新部署後端

---

### 問題 2: API URL 設定錯誤

**症狀**：
- 瀏覽器 Network 標籤顯示 404 錯誤
- Console 顯示 "Failed to fetch"

**解決**：
1. 確認 `VITE_API_URL` 格式正確
2. 確認後端網域正確
3. 確認路徑包含 `/api/v1`
4. 清除瀏覽器快取

---

### 問題 3: CORS 設定問題

**症狀**：
- Console 顯示 CORS 錯誤
- Network 標籤顯示 CORS 相關錯誤

**解決**：
1. 確認 `CORS_ORIGINS` 包含前端網域
2. 確認格式正確（逗號分隔或 JSON）
3. 重新部署後端
4. 清除瀏覽器快取

---

### 問題 4: 環境變數未更新

**症狀**：
- 環境變數已更新，但問題仍然存在

**解決**：
1. 確認 Vercel/Railway 已重新部署
2. 等待部署完成（通常 1-2 分鐘）
3. 清除瀏覽器快取
4. 硬重新載入頁面

---

## 📋 檢查清單

### 後端檢查
- [ ] 後端服務運行中（Railway Dashboard）
- [ ] 健康檢查端點可訪問（`/health`）
- [ ] API 文檔可訪問（`/docs`）
- [ ] `CORS_ORIGINS` 包含前端網域
- [ ] `ENVIRONMENT=production` 已設定
- [ ] 日誌中沒有錯誤訊息

### 前端檢查
- [ ] `VITE_API_URL` 已正確設定
- [ ] `VITE_USE_MOCK=false`（生產環境）
- [ ] Vercel 已重新部署
- [ ] 瀏覽器快取已清除

### 網路檢查
- [ ] 後端網域可訪問
- [ ] 前端網域可訪問
- [ ] 沒有防火牆阻擋
- [ ] DNS 解析正常

---

## 🎯 快速測試命令

### 測試後端健康狀態
```bash
curl https://your-backend-domain.railway.app/health
```

### 測試 API 端點
```bash
curl https://your-backend-domain.railway.app/api/v1/topics?page=1&limit=1
```

### 測試 CORS
```bash
curl -X OPTIONS \
  -H "Origin: https://ai-agent-webapp-ten.vercel.app" \
  -H "Access-Control-Request-Method: GET" \
  https://your-backend-domain.railway.app/api/v1/topics \
  -v
```

---

## 📞 需要幫助？

如果以上步驟都無法解決問題，請提供：

1. **瀏覽器 Console 錯誤訊息**（完整錯誤）
2. **Network 標籤截圖**（顯示請求詳情）
3. **後端日誌**（Railway 日誌）
4. **環境變數設定**（隱藏敏感資訊）

---

**最後更新**：2025-12-30

