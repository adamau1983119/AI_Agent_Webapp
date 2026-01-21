# 修復 Elasticsearch HTTP 連接問題

## 問題

Elasticsearch 8.11.0 預設啟用了 HTTPS，但應用程式使用 HTTP 連接，導致連接失敗。

## 解決方案

### 方案 1：配置 Elasticsearch 使用 HTTP（推薦用於開發環境）

編輯 `D:\Users\Ophelia Chan\Desktop\elasticsearch-8.11.0\config\elasticsearch.yml`，添加或修改：

```yaml
# 禁用 HTTPS（僅用於開發環境）
xpack.security.http.ssl.enabled: false
```

**注意**：修改後需要重啟 Elasticsearch。

### 方案 2：更新應用程式以支援 HTTPS

更新 `.env` 文件：

```env
ELASTICSEARCH_HOSTS=https://localhost:9200
ELASTICSEARCH_USE_SSL=true
```

並更新 `elasticsearch_service.py` 以支援 SSL 證書驗證。

### 方案 3：使用 HTTP（如果已配置）

如果 Elasticsearch 已配置為使用 HTTP，確保 `.env` 文件配置正確：

```env
ELASTICSEARCH_HOSTS=http://localhost:9200
ELASTICSEARCH_USE_SSL=false
```

## 當前狀態

從日誌中看到：
- IK Analyzer 插件已成功載入 ✅
- Elasticsearch 已啟動 ✅
- 但連接使用 HTTP 時被拒絕（因為預設啟用 HTTPS）❌

## 建議

**開發環境**：使用方案 1，禁用 HTTPS
**生產環境**：使用方案 2，配置 HTTPS 連接

