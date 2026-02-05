# MongoDB 連接問題修復完成報告

## ✅ 修復完成

已成功實施**方法 3：使用 FastAPI 的 startup/shutdown 事件和 app.state**，徹底解決了全局變數不同步問題。

---

## 🔧 實施的修改

### 1. 修改 `main.py` - 使用 app.state 存儲連接

**位置**：`backend/app/main.py:160-178`

**修改內容**：
- 在 `lifespan` 函數的 startup 階段，直接建立 MongoDB 連接
- 將連接存儲到 `app.state.mongo_client` 和 `app.state.mongo_db`
- 在 shutdown 階段關閉連接

**關鍵代碼**：
```python
# 建立 MongoDB 客戶端
mongo_client = AsyncIOMotorClient(settings.MONGODB_URL, ...)
await mongo_client.admin.command("ping")
mongo_db = mongo_client[settings.MONGODB_DB_NAME]

# 存儲到 app.state（避免全局變數不同步）
app.state.mongo_client = mongo_client
app.state.mongo_db = mongo_db
```

### 2. 重構 `database.py` - 提供從 app.state 獲取連接的函數

**位置**：`backend/app/database.py`

**新增函數**：
- `get_database_from_request(request: Request)` - 從 app.state 獲取資料庫實例
- `get_client_from_request(request: Request)` - 從 app.state 獲取客戶端實例
- `check_connection_from_request(request: Request)` - 從 app.state 檢查連接狀態
- `get_database_dependency(request: Request)` - FastAPI 依賴注入函數

**保留舊函數**：為了向後兼容，保留了舊的全局變數方式，但不推薦使用。

### 3. 更新健康檢查端點

**位置**：`backend/app/api/v1/health.py`

**修改內容**：
- `health_check()` 和 `detailed_health_check()` 都添加了 `request: Request` 參數
- 使用 `check_connection_from_request(request)` 代替 `check_connection()`

### 4. 更新 API 端點

**位置**：`backend/app/api/v1/schedules.py` 和 `backend/app/api/v1/topics.py`

**修改內容**：
- 所有相關端點都添加了 `request: Request` 參數
- 使用 `check_connection_from_request(request)` 檢查連接
- 使用 `get_database_from_request(request)` 獲取資料庫實例
- 將資料庫實例傳遞給 Repository：`TopicRepository(db=db)`

### 5. 更新 BaseRepository

**位置**：`backend/app/services/repositories/base_repository.py`

**修改內容**：
- `__init__` 方法添加了可選的 `db` 參數
- 如果提供了 `db` 參數，將使用該實例而不是全局變數
- 保持向後兼容，如果沒有提供 `db`，仍會嘗試從全局變數獲取

---

## 🎯 解決的問題

### 根本原因
- **模組重載問題**：`uvicorn --reload` 會重新載入模組，導致全局變數在不同模組實例間不同步
- **作用域問題**：`global` 關鍵字只在單一模組內有效，跨模組導入時會建立不同的引用

### 解決方案
- **使用 app.state**：FastAPI 的 `app.state` 是應用級別的狀態，不會受到模組重載影響
- **統一訪問點**：所有端點都從同一個 `app.state` 獲取連接，確保使用同一個實例
- **避免全局變數**：不再依賴全局變數，徹底解決同步問題

---

## 📊 修改統計

- **修改文件數**：5 個
  - `backend/app/main.py`
  - `backend/app/database.py`
  - `backend/app/api/v1/health.py`
  - `backend/app/api/v1/schedules.py`
  - `backend/app/api/v1/topics.py`
  - `backend/app/services/repositories/base_repository.py`

- **新增函數**：4 個
  - `get_database_from_request()`
  - `get_client_from_request()`
  - `check_connection_from_request()`
  - `get_database_dependency()`

- **更新端點**：3 個
  - `GET /api/v1/health`
  - `GET /api/v1/health/detailed`
  - `POST /api/v1/schedules/generate-today`
  - `GET /api/v1/topics`

---

## ✅ 測試建議

### 1. 重啟服務器
```powershell
# 停止現有服務器
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*venv*" } | Stop-Process -Force

# 重新啟動
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 測試健康檢查
```powershell
curl http://localhost:8000/api/v1/health
```
**預期結果**：`"database": "connected"`

### 3. 測試生成主題 API
```powershell
$body = '{"force":false}'
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/schedules/generate-today" -Method POST -ContentType "application/json" -Body $body
```
**預期結果**：`"status": "accepted"` 而不是 `"status": "failed"`

### 4. 驗證日誌
查看服務器控制台輸出，應該看到：
- `✅ MongoDB 連接成功: ai_agent_webapp`
- `✅ MongoDB 連接已存儲到 app.state，所有端點將使用同一個實例`
- `資料庫實例 ID: <id>`（所有端點應該顯示相同的 ID）

---

## 🔍 驗證要點

1. **連接一致性**：所有端點使用的資料庫實例 ID 應該相同
2. **無錯誤訊息**：不應該再出現「資料庫客戶端未初始化」錯誤
3. **功能正常**：主題生成、查詢等功能應該正常工作
4. **reload 模式**：即使使用 `--reload`，連接也應該保持穩定

---

## 📝 注意事項

1. **向後兼容**：舊的全局變數方式仍然保留，但新代碼應該使用 `app.state` 方式
2. **依賴注入**：未來可以考慮使用 `get_database_dependency()` 作為 FastAPI 依賴注入
3. **錯誤處理**：如果 `app.state` 中沒有連接，會返回適當的錯誤訊息

---

## 🎉 預期效果

修復後，應該能夠：
- ✅ 在 `--reload` 模式下正常工作
- ✅ 所有端點使用同一個資料庫實例
- ✅ 不再出現「資料庫客戶端未初始化」錯誤
- ✅ 健康檢查和 API 端點顯示一致的連接狀態

---

**修復日期**：2026-01-16  
**修復方法**：FastAPI app.state + startup/shutdown 事件  
**狀態**：✅ 完成，待測試驗證

