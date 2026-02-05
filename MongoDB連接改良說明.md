# MongoDB 連接改良說明

## 📋 改良內容

已根據專家建議和改良版代碼，對 `backend/app/database.py` 進行了全面改良。

## ✅ 主要改進

### 1. 重試機制
- **預設重試 3 次**，每次間隔 2 秒
- 避免因暫時性網路問題導致系統直接崩潰
- 可配置的重試參數（`max_retries`, `delay`）

### 2. 環境區分
- **開發環境**：連接失敗時允許系統繼續啟動（方便測試其他功能）
- **生產環境**：連接失敗則阻止啟動，避免資料不一致
- 根據 `settings.ENVIRONMENT` 自動判斷

### 3. 詳細錯誤處理
- **認證失敗**：詳細說明可能原因（用戶名密碼錯誤、權限不足等）
- **連接超時**：說明可能原因（服務未啟動、IP 白名單、防火牆等）
- **配置錯誤**：檢查連接字串格式
- **錯誤分類**：區分不同類型的錯誤，提供針對性的解決建議

### 4. 安全處理
- **連接字串驗證**：在連接前驗證格式
- **日誌安全**：使用 `_sanitize_url_for_logging()` 隱藏密碼
- **敏感資訊保護**：日誌中不輸出完整連接字串

### 5. 連接池配置
- `maxPoolSize=50`：最大連接池大小
- `minPoolSize=10`：最小連接數
- 優化連接性能

### 6. 健康檢查機制
- `check_connection()`：定期檢查連接狀態
- `get_connection_info()`：取得連接資訊（用於診斷和監控）

### 7. 改進的 `get_database()` 函數
- 開發環境中自動嘗試重新連接
- 更好的錯誤處理和提示

## 🔧 新增函數

### `_validate_connection_string(url: str) -> bool`
驗證 MongoDB 連接字串格式

### `_sanitize_url_for_logging(url: str) -> str`
清理連接字串用於日誌記錄（隱藏密碼）

### `get_connection_info() -> dict`
取得連接資訊（用於診斷和監控）

## 📝 使用方式

### 基本使用
```python
from app.database import connect_to_mongo, get_database

# 連接 MongoDB（自動重試）
await connect_to_mongo(max_retries=3, delay=2)

# 取得資料庫實例
db = await get_database()
```

### 健康檢查
```python
from app.database import check_connection, get_connection_info

# 檢查連接狀態
is_connected = await check_connection()

# 取得連接資訊
info = get_connection_info()
```

## 🎯 錯誤處理範例

### 開發環境
- 連接失敗時：記錄警告，系統繼續啟動
- 資料庫功能無法使用，但其他功能正常

### 生產環境
- 連接失敗時：記錄錯誤，阻止系統啟動
- 確保資料一致性

## 📊 日誌輸出範例

### 成功連接
```
INFO: 嘗試連接 MongoDB (第 1/3 次)...
INFO: ✅ 成功連接到 MongoDB: ai_agent_webapp
INFO: 連接字串: mongodb+srv://user:***@cluster.mongodb.net/...
INFO: 連接嘗試次數: 1
```

### 認證失敗
```
ERROR: ❌ MongoDB 認證失敗 (第 1 次嘗試)
ERROR: 可能原因：
ERROR:   1. 用戶名或密碼錯誤
ERROR:   2. 用戶權限不足
ERROR:   3. 資料庫名稱與用戶授權不一致
ERROR:   4. 連接字串中的特殊字符未正確 URL 編碼
WARNING: ⚠️ 開發環境：MongoDB 連接失敗，但允許系統繼續啟動
```

### 連接超時
```
ERROR: ❌ MongoDB 連接超時 (第 1 次嘗試)
ERROR: 可能原因：
ERROR:   1. MongoDB 服務未啟動（本地）
ERROR:   2. 網路連接問題
ERROR:   3. IP 白名單未包含當前 IP（Atlas）
ERROR:   4. 防火牆阻擋連接
```

## 🔍 與現有代碼的整合

### `main.py` 的 `lifespan` 函數
已更新為：
- 調用改良版的 `connect_to_mongo()`
- 處理開發環境連接失敗的情況
- 添加連接狀態驗證

## 📚 相關文件

- 問題報告：`問題報告_MongoDB認證失敗.md`
- 專家建議：已整合到代碼中
- 改良版範例：已實現

## 🎉 完成狀態

✅ 重試機制  
✅ 環境區分  
✅ 詳細錯誤處理  
✅ 安全處理  
✅ 連接池配置  
✅ 健康檢查機制  
✅ 改進的 `get_database()` 函數  
✅ 與 `main.py` 整合  

---

**改良完成時間：** 2026-01-16  
**狀態：** ✅ 已完成並測試

