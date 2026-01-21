# 更新 .env 文件以啟用 Elasticsearch

## 📝 配置步驟

### 1. 找到 .env 文件

在 `backend` 目錄下找到或創建 `.env` 文件。

### 2. 添加或更新以下配置

```env
# Elasticsearch 配置（支援 HTTPS）
ELASTICSEARCH_ENABLED=true
ELASTICSEARCH_HOSTS=https://localhost:9200
ELASTICSEARCH_INDEX=topics
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=xP*87btATBNvn9FfsfrZ
ELASTICSEARCH_TIMEOUT=30
ELASTICSEARCH_MAX_RETRIES=3
ELASTICSEARCH_USE_SSL=true
```

**注意**：
- 如果使用 `https://` URL，SSL 會自動啟用
- 如果使用 `http://` URL，請設置 `ELASTICSEARCH_USE_SSL=false`

### 3. 完整的 .env 配置範例

```env
# MongoDB 配置
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=ai_agent_webapp

# Elasticsearch 配置（新增）
ELASTICSEARCH_ENABLED=true
ELASTICSEARCH_HOSTS=http://localhost:9200
ELASTICSEARCH_INDEX=topics
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=xP*87btATBNvn9FfsfrZ
ELASTICSEARCH_TIMEOUT=30
ELASTICSEARCH_MAX_RETRIES=3

# Redis 配置（可選）
REDIS_ENABLED=false
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# 其他配置...
```

## ⚙️ 配置說明

- **ELASTICSEARCH_ENABLED**: 設為 `true` 啟用 Elasticsearch，`false` 使用 MongoDB 搜尋
- **ELASTICSEARCH_HOSTS**: Elasticsearch 服務地址
- **ELASTICSEARCH_INDEX**: 索引名稱（預設：topics）
- **ELASTICSEARCH_USERNAME**: Elasticsearch 用戶名（預設：elastic）
- **ELASTICSEARCH_PASSWORD**: Elasticsearch 密碼（從啟動日誌中獲取）

## 🔄 切換搜尋引擎

### 使用 Elasticsearch（推薦，支援中文分詞）
```env
ELASTICSEARCH_ENABLED=true
```

### 使用 MongoDB（備援方案）
```env
ELASTICSEARCH_ENABLED=false
```

## ✅ 驗證配置

配置完成後，重啟應用程式，系統會：
1. 自動連接到 Elasticsearch
2. 檢查 IK Analyzer 是否可用
3. 如果 Elasticsearch 不可用，自動回退到 MongoDB

## 📝 注意事項

1. **必須重啟應用程式**才能應用新配置
2. **Elasticsearch 必須運行**才能使用 Elasticsearch 搜尋
3. **如果 Elasticsearch 不可用**，系統會自動使用 MongoDB 搜尋
4. **密碼請妥善保管**，不要提交到版本控制系統

