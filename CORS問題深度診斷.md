# CORS 問題深度診斷

## 問題描述

錯誤訊息顯示：
- 請求來源：`https://ai-agent-webapp-ten.vercel.app/`
- 允許的來源（從 header）：`https://railway.com`

這表示後端返回的 `Access-Control-Allow-Origin` header 是 `https://railway.com`，而不是我們設定的 `https://ai-agent-webapp-ten.vercel.app`。

## 可能的原因

1. **Railway 代理層覆蓋 CORS header**
   - Railway 可能有自己的代理層在設定 CORS header
   - 這可能覆蓋了應用程式的 CORS 設定

2. **環境變數格式問題**
   - Railway 環境變數可能需要特定格式
   - JSON 格式可能沒有正確解析

3. **中間件順序問題**
   - CORS 中間件可能被其他中間件覆蓋

## 解決方案

### 方案 1：檢查 Railway 環境變數格式

在 Railway Dashboard：

1. 訪問：https://railway.app/dashboard
2. 選擇專案：`AI_Agent_Webapp`
3. 點擊服務：`backend`
4. 點擊 "Variables" 標籤
5. 找到 `CORS_ORIGINS` 環境變數
6. **確認格式**：
   - 應該使用逗號分隔格式（不是 JSON 陣列）
   - 正確格式：`https://ai-agent-webapp-ten.vercel.app,http://localhost:5173,http://localhost:3000`
   - 錯誤格式：`["https://ai-agent-webapp-ten.vercel.app"]`

### 方案 2：使用通配符測試（臨時）

如果問題仍然存在，可以暫時使用通配符 `*` 來測試：

1. 在 Railway Dashboard 中
2. 將 `CORS_ORIGINS` 暫時設為：`*`
3. 保存並等待重新部署
4. 測試前端是否可以連接
5. **重要**：測試完成後，改回正確的格式

### 方案 3：檢查 Railway 網路設定

1. 在 Railway Dashboard 中
2. 點擊服務：`backend`
3. 點擊 "Settings" 標籤
4. 檢查 "Networking" 區塊
5. 確認是否有代理設定影響 CORS

### 方案 4：手動設定 CORS Header（如果其他方案無效）

如果 Railway 的代理層確實覆蓋了 CORS header，我們可能需要手動設定回應 header。

## 診斷步驟

### 步驟 1：檢查 Railway 部署日誌

1. 訪問：https://railway.app/dashboard
2. 選擇專案：`AI_Agent_Webapp`
3. 點擊服務：`backend`
4. 查看 "Deployments" 標籤
5. 點擊最新的部署
6. 查看日誌，確認：
   - `CORS_ORIGINS 設定值: ...`
   - `設定 CORS，允許的來源: ...`

### 步驟 2：測試後端 API

使用 curl 或 Postman 測試：

```bash
curl -H "Origin: https://ai-agent-webapp-ten.vercel.app" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     https://gentle-enchantment-production-1865.up.railway.app/api/v1/topics \
     -v
```

檢查回應 header 中的 `Access-Control-Allow-Origin`。

### 步驟 3：檢查瀏覽器 Network 標籤

1. 打開開發者工具（F12）
2. 點擊 "Network" 標籤
3. 嘗試發送請求
4. 點擊請求，查看：
   - Request Headers 中的 `Origin`
   - Response Headers 中的 `Access-Control-Allow-Origin`

## 當前狀態

- ✅ 後端 CORS 設定正確（從日誌確認）
- ✅ 前端環境變數正確設定
- ❌ 瀏覽器仍顯示 CORS 錯誤
- ❓ 可能原因：Railway 代理層覆蓋 CORS header

## 下一步

1. 檢查 Railway 環境變數格式
2. 嘗試使用通配符 `*` 測試
3. 檢查 Railway 網路設定
4. 如果問題仍然存在，考慮手動設定 CORS header

