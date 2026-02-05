# 更新 .env 文件以支援 HTTPS

## 📝 HTTPS 配置步驟

### 1. 更新 .env 文件

在 `backend` 目錄下找到或創建 `.env` 文件，添加或更新以下配置：

```env
# Elasticsearch 配置（HTTPS）
ELASTICSEARCH_ENABLED=true
ELASTICSEARCH_HOSTS=https://localhost:9200
ELASTICSEARCH_INDEX=topics
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=xP*87btATBNvn9FfsfrZ
ELASTICSEARCH_TIMEOUT=30
ELASTICSEARCH_MAX_RETRIES=3
ELASTICSEARCH_USE_SSL=true
```

### 2. 配置說明

- **ELASTICSEARCH_HOSTS**: 使用 `https://localhost:9200`（注意是 `https` 不是 `http`）
- **ELASTICSEARCH_USE_SSL**: 設為 `true` 啟用 SSL
- **ELASTICSEARCH_USERNAME**: Elasticsearch 用戶名（預設：`elastic`）
- **ELASTICSEARCH_PASSWORD**: Elasticsearch 密碼（從啟動日誌中獲取）

### 3. 自動檢測

應用程式會自動檢測 URL 協議：
- 如果 URL 以 `https://` 開頭，會自動啟用 SSL
- 如果 URL 以 `http://` 開頭，會使用 HTTP（除非明確設置 `ELASTICSEARCH_USE_SSL=true`）

### 4. SSL 證書驗證

**開發環境**：預設不驗證證書（`verify_certs=False`），因為 Elasticsearch 使用自簽名證書

**生產環境**：建議配置正確的證書並啟用驗證

## ✅ 驗證配置

配置完成後，重啟應用程式，系統會：
1. 自動連接到 Elasticsearch（使用 HTTPS）
2. 檢查 IK Analyzer 是否可用
3. 如果連接失敗，自動回退到 MongoDB 搜尋

## 🔄 HTTP vs HTTPS

### 使用 HTTPS（推薦，Elasticsearch 8.11.0 預設）
```env
ELASTICSEARCH_HOSTS=https://localhost:9200
ELASTICSEARCH_USE_SSL=true
```

### 使用 HTTP（如果已禁用 HTTPS）
```env
ELASTICSEARCH_HOSTS=http://localhost:9200
ELASTICSEARCH_USE_SSL=false
```

## 📝 注意事項

1. **Elasticsearch 8.11.0 預設啟用 HTTPS**
2. **必須配置用戶名和密碼**才能連接
3. **開發環境不驗證證書**（使用自簽名證書）
4. **生產環境建議配置正確的證書**

## 🧪 測試連接

配置完成後，可以測試連接：

```python
# Python 測試腳本
from app.services.elasticsearch_service import es_service
import asyncio

async def test():
    await es_service.connect()
    health = await es_service.health_check()
    print(health)

asyncio.run(test())
```

