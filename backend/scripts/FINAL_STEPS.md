# 🚀 最後步驟 - 啟動應用程式

## ✅ 已完成

1. ✅ IK Analyzer 已安裝
2. ✅ Elasticsearch 已啟動
3. ✅ 應用程式已更新以支援 HTTPS
4. ✅ .env 文件已配置
5. ✅ 依賴已安裝

## 🎯 現在啟動應用程式

### 方法 1：使用啟動腳本（推薦）

```powershell
cd "F:\Adam 2025\Myproject\AI_Agent_Wbbapp_for_Social_Media_Content_Generation"
.\backend\scripts\start_app_with_elasticsearch.ps1
```

### 方法 2：手動啟動

```powershell
cd "F:\Adam 2025\Myproject\AI_Agent_Wbbapp_for_Social_Media_Content_Generation\backend"
uvicorn app.main:app --reload
```

## 📋 啟動後檢查清單

應用程式啟動時，請檢查日誌中是否出現：

### ✅ 成功標誌

```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Elasticsearch 認證已啟用
INFO:     Elasticsearch SSL/HTTPS 已啟用
INFO:     ✅ Elasticsearch 連接成功: elasticsearch
INFO:     ✅ IK Analyzer 插件已安裝
INFO:     ✅ IK Analyzer 正常工作
INFO:     ✅ 創建 Elasticsearch 索引: topics
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### ⚠️ 如果看到錯誤

如果看到以下訊息，這是正常的（會自動回退到 MongoDB）：
```
WARNING: Elasticsearch 連接失敗: ...，將回退到 MongoDB 搜尋
```

**解決方法**：
1. 確認 Elasticsearch 正在運行
2. 檢查 `.env` 配置是否正確
3. 確認用戶名和密碼正確

## 🧪 測試搜尋功能

應用程式啟動後，在另一個終端測試：

### 測試 1：基本搜尋

```bash
curl -X GET "http://localhost:8000/api/v1/topics/search?q=測試&page=1&limit=10" \
  -H "X-User-Role: user"
```

### 測試 2：檢查熱門查詢

```bash
curl -X GET "http://localhost:8000/api/v1/topics/search/hot-queries"
```

### 測試 3：檢查 Elasticsearch 健康狀態

```bash
curl -X GET "http://localhost:8000/api/v1/topics/search/health"
```

## 📊 預期結果

### 搜尋 API 回應範例

```json
{
  "source": "elasticsearch",
  "results": [
    {
      "id": "...",
      "title": "...",
      "summary": "...",
      "_score": 1.5
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 100,
    "total_pages": 10
  }
}
```

## 🔍 故障排除

### 問題 1：Elasticsearch 連接失敗

**症狀**：日誌顯示連接失敗

**解決方案**：
1. 確認 Elasticsearch 正在運行：
   ```powershell
   curl https://localhost:9200 -SkipCertificateCheck
   ```
2. 檢查 `.env` 文件配置
3. 確認用戶名和密碼正確

### 問題 2：IK Analyzer 未工作

**症狀**：連接成功但 IK Analyzer 測試失敗

**解決方案**：
1. 確認插件已安裝：
   ```powershell
   cd "D:\Users\Ophelia Chan\Desktop\elasticsearch-8.11.0"
   .\bin\elasticsearch-plugin list
   ```
2. 重啟 Elasticsearch

### 問題 3：應用程式無法啟動

**症狀**：啟動時出現錯誤

**解決方案**：
1. 檢查 Python 版本：`python --version`（需要 3.8+）
2. 確認依賴已安裝：`pip list | findstr elasticsearch`
3. 查看完整錯誤訊息

## 📝 配置確認

您的當前配置：

```env
ELASTICSEARCH_ENABLED=true
ELASTICSEARCH_HOSTS=https://localhost:9200
ELASTICSEARCH_INDEX=topics
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=xP*87btATBNvn9FfsfrZ
ELASTICSEARCH_TIMEOUT=30
ELASTICSEARCH_MAX_RETRIES=3
ELASTICSEARCH_USE_SSL=true
```

## 🎉 完成！

如果看到所有成功標誌，您的搜尋系統已完全配置並可以使用了！

### 功能清單

- ✅ Elasticsearch 中文全文搜尋（IK Analyzer）
- ✅ MongoDB 備援搜尋
- ✅ Redis 快取
- ✅ 熱門查詢統計
- ✅ HTTPS 安全連接
- ✅ 自動回退機制

## 📚 參考文檔

- `backend/scripts/QUICK_SETUP_COMPLETE.md` - 完整設置指南
- `backend/scripts/update_env_https.md` - HTTPS 配置詳情
- `backend/scripts/install_ik_analyzer.md` - IK Analyzer 安裝指南

