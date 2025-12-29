# CORS 錯誤修復指南

## 問題描述

前端訪問後端 API 時出現 CORS 錯誤：
```
Access to fetch at 'https://your-backend-api.railway.app/api/v1/topics' 
from origin 'https://ai-agent-webapp-ten.vercel.app' 
has been blocked by CORS policy: 
Response to preflight request doesn't pass access control check: 
The 'Access-Control-Allow-Origin' header has a value 'https://railway.com' 
that is not equal to the supplied origin.
```

## 解決方案

### 步驟 1：更新 Railway 後端 CORS 設定

1. **訪問 Railway Dashboard**
   - 網址：https://railway.app/dashboard
   - 選擇專案：`AI_Agent_Webapp`
   - 點擊服務：`backend`

2. **設定環境變數**
   - 點擊 "Variables" 標籤
   - 找到或建立 `CORS_ORIGINS` 環境變數
   - 設定值為（逗號分隔）：
     ```
     https://ai-agent-webapp-ten.vercel.app,http://localhost:5173,http://localhost:3000
     ```
   - 保存後，Railway 會自動重新部署

### 步驟 2：確認 Vercel 前端 API URL

1. **訪問 Vercel Dashboard**
   - 網址：https://vercel.com/dashboard
   - 選擇專案：`ai-agent-webapp`
   - 點擊 "Settings" → "Environment Variables"

2. **確認環境變數**
   - 找到 `VITE_API_URL`
   - 確認值為：
     ```
     https://gentle-enchantment-production-1865.up.railway.app/api/v1
     ```
   - 如果不是，請更新並保存
   - 保存後，Vercel 會自動重新部署

### 步驟 3：清除瀏覽器快取

如果環境變數已正確設定，但問題仍然存在，請嘗試：

1. **硬重新載入**
   - Windows: `Ctrl + Shift + R`
   - Mac: `Cmd + Shift + R`

2. **清除快取**
   - 打開開發者工具（F12）
   - 點擊 "Application" 標籤
   - 點擊 "Clear storage"
   - 點擊 "Clear site data"

## 驗證修復

1. **檢查後端 CORS 設定**
   - 訪問：https://gentle-enchantment-production-1865.up.railway.app/health
   - 應該返回 200 狀態碼

2. **檢查前端連接**
   - 訪問：https://ai-agent-webapp-ten.vercel.app/
   - 打開開發者工具（F12）
   - 檢查 Console，應該沒有 CORS 錯誤
   - 檢查 Network 標籤，API 請求應該返回 200 狀態碼

## 重要網址

### 前端
- 網域：https://ai-agent-webapp-ten.vercel.app/
- Vercel Dashboard：https://vercel.com/dashboard

### 後端
- 網域：https://gentle-enchantment-production-1865.up.railway.app
- 健康檢查：https://gentle-enchantment-production-1865.up.railway.app/health
- API 文檔：https://gentle-enchantment-production-1865.up.railway.app/docs
- Railway Dashboard：https://railway.app/dashboard

## 環境變數清單

### Railway 後端環境變數
- `MONGODB_URL`: MongoDB 連接字串
- `MONGODB_DB_NAME`: 資料庫名稱（預設：`ai_agent_webapp`）
- `CORS_ORIGINS`: CORS 允許的來源（逗號分隔）
- `PORT`: 端口（Railway 自動設定）
- `AI_SERVICE`: AI 服務（預設：`ollama`）
- `ENVIRONMENT`: 環境（預設：`production`）
- `DEBUG`: 除錯模式（預設：`false`）

### Vercel 前端環境變數
- `VITE_API_URL`: 後端 API 基礎 URL
- `VITE_USE_MOCK`: 是否使用 Mock 資料（預設：`false`）

