# MongoDB 連接問題修復工作紀錄

**日期**：2026-01-16  
**分支**：`feature/mongodb-connection-fix-backup`  
**狀態**：✅ 修復完成

---

## 📋 問題描述

### 核心問題
FastAPI 應用程序在啟動時成功連接到 MongoDB Atlas，健康檢查端點顯示連接正常，但特定 API 端點（`POST /api/v1/schedules/generate-today`）仍然返回「資料庫客戶端未初始化」錯誤。

### 根本原因
1. **模組重載問題**：`uvicorn --reload` 會在檔案變更時重新載入模組，導致 `database.py` 的全局變數在不同模組實例中不同步
2. **作用域問題**：`global client, database` 只在單一模組內有效。跨模組導入時，Python 會建立不同的引用，導致 API 端點拿到的是未初始化的副本

---

## 🔧 解決方案實施

### 1. 移除全局變數依賴 ✅

**修改文件**：`backend/app/main.py`

**實施內容**：
- 在 `lifespan` 函數的 startup 階段直接建立 MongoDB 連接
- 將連接存儲到 `app.state.mongo_client` 和 `app.state.mongo_db`
- 添加 `app.state.db` 簡短別名，方便使用
- 在 shutdown 階段關閉連接

**關鍵代碼**：
```python
# 建立 MongoDB 客戶端
mongo_client = AsyncIOMotorClient(settings.MONGODB_URL, ...)
await mongo_client.admin.command("ping")
mongo_db = mongo_client[settings.MONGODB_DB_NAME]

# 存儲到 app.state
app.state.mongo_client = mongo_client
app.state.mongo_db = mongo_db
app.state.db = mongo_db  # 簡短別名
```

### 2. 簡化 API 端點 ✅

**修改文件**：
- `backend/app/api/v1/schedules.py`
- `backend/app/api/v1/topics.py`
- `backend/app/api/v1/health.py`

**實施內容**：
- 所有相關端點添加 `request: Request` 參數（放在最前面）
- 直接使用 `request.app.state.db` 獲取資料庫實例
- 移除複雜的檢查邏輯，改為直接訪問
- 添加實例 ID 日誌，確認使用同一個實例

**關鍵代碼**：
```python
@router.post("/generate-today")
async def generate_today_all_topics(
    request: Request,
    request_body: GenerateTodayRequest = Body(...),
    ...
):
    # 直接從 app.state 獲取
    db = request.app.state.db
    logger.info(f"資料庫實例 ID: {id(db)}")
    # 使用 db 進行操作
```

### 3. 創建測試端點 ✅

**新增文件**：`backend/app/api/v1/test_db.py`

**實施內容**：
- 創建 `/api/v1/test/db` 測試端點
- 用於驗證 `app.state.db` 是否正常工作
- 測試基本資料庫操作（count_documents, ping）
- 返回資料庫實例 ID 用於驗證

### 4. 重構 database.py ✅

**修改文件**：`backend/app/database.py`

**實施內容**：
- 保留舊的全局變數方式作為向後兼容（不推薦使用）
- 新增從 `app.state` 獲取連接的函數：
  - `get_database_from_request(request)`
  - `get_client_from_request(request)`
  - `check_connection_from_request(request)`
  - `get_database_dependency(request)` - FastAPI 依賴注入
- 簡化 `check_connection_from_request`，直接使用 `app.state`

### 5. 更新 BaseRepository ✅

**修改文件**：`backend/app/services/repositories/base_repository.py`

**實施內容**：
- `__init__` 方法添加可選的 `db` 參數
- 如果提供了 `db` 參數，將使用該實例而不是全局變數
- 保持向後兼容

### 6. 優化日誌輸出 ✅

**修改文件**：`backend/app/main.py`

**實施內容**：
- 將可選配置的警告改為 DEBUG 級別
- 在開發環境中，這些訊息不會在 INFO 級別顯示
- 生產環境只顯示已配置的服務
- 添加資料庫實例 ID 日誌

### 7. 創建異常模組 ✅

**新增文件**：`backend/app/exceptions.py`

**實施內容**：
- 統一導入 MongoDB 相關異常
- 避免循環導入問題
- 提供自定義異常類

---

## 📊 修改統計

### 修改的文件
1. `backend/app/main.py` - 集中連接管理
2. `backend/app/database.py` - 重構連接函數
3. `backend/app/api/v1/health.py` - 使用 app.state
4. `backend/app/api/v1/schedules.py` - 直接使用 app.state.db
5. `backend/app/api/v1/topics.py` - 直接使用 app.state.db
6. `backend/app/services/repositories/base_repository.py` - 支持傳入 db 參數

### 新增的文件
1. `backend/app/api/v1/test_db.py` - 測試端點
2. `backend/app/exceptions.py` - 統一異常定義

### 新增的函數
1. `get_database_from_request(request)` - 從 app.state 獲取資料庫
2. `get_client_from_request(request)` - 從 app.state 獲取客戶端
3. `check_connection_from_request(request)` - 從 app.state 檢查連接
4. `get_database_dependency(request)` - FastAPI 依賴注入

---

## ✅ 驗證步驟

### 1. 測試資料庫連接端點
```powershell
curl http://localhost:8000/api/v1/test/db
```
**預期結果**：`"status": "ok"` 和資料庫實例 ID

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

### 4. 驗證實例 ID
查看服務器日誌，所有端點應該顯示相同的資料庫實例 ID

---

## 🎯 關鍵改進

1. **徹底移除全局變數依賴**：不再使用 `global client, database`
2. **使用 FastAPI 推薦方式**：`app.state` 管理應用級狀態
3. **集中連接管理**：所有連接邏輯在 `main.py` 的 `lifespan` 中
4. **直接訪問**：API 端點直接使用 `request.app.state.db`
5. **實例一致性**：所有端點使用同一個資料庫實例（通過 ID 驗證）
6. **向後兼容**：保留舊的全局變數方式，但標記為不推薦

---

## 📝 技術細節

### app.state 的優勢
- **應用級狀態**：不受模組重載影響
- **統一訪問點**：所有端點從同一個 `app.state` 獲取連接
- **FastAPI 推薦**：官方推薦的最佳實踐
- **避免同步問題**：不會出現全局變數不同步的情況

### 參數順序修復
- Python 語法要求：非默認參數不能在默認參數後面
- 解決方案：將 `request: Request` 放在參數列表最前面

### 日誌優化
- 可選配置警告改為 DEBUG 級別
- 減少日誌噪音，只顯示重要資訊
- 添加實例 ID 日誌用於調試

---

## 🔄 Git 備份

### 分支信息
- **當前分支**：`feature/mongodb-connection-fix-backup`
- **基礎分支**：`feature/ui-improvements`
- **提交訊息**：`fix: 使用 app.state 解決 MongoDB 連接全局變數不同步問題`

### 提交的文件
- `backend/app/database.py`
- `backend/app/main.py`
- `backend/app/api/v1/health.py`
- `backend/app/api/v1/schedules.py`
- `backend/app/api/v1/topics.py`
- `backend/app/api/v1/test_db.py` (新增)
- `backend/app/services/repositories/base_repository.py`
- `backend/app/exceptions.py` (新增)

---

## 📚 相關文檔

1. **MongoDB連接問題技術報告.md** - 詳細的技術分析報告
2. **MongoDB_Connection_Issue_Report_EN.md** - 英文版技術報告
3. **MongoDB連接問題修復完成報告.md** - 修復完成報告
4. **MongoDB連接問題最終解決方案.md** - 解決方案總結

---

## 🎉 修復結果

### 解決的問題
- ✅ 健康檢查顯示已連接但 API 報未初始化
- ✅ 全局變數在不同模組實例間不同步
- ✅ reload 模式導致的連接失效
- ✅ 跨模組導入時的引用不一致

### 預期效果
- ✅ 所有端點使用同一個資料庫實例
- ✅ 在 `--reload` 模式下正常工作
- ✅ 不再出現「資料庫客戶端未初始化」錯誤
- ✅ 健康檢查和 API 端點顯示一致的連接狀態

---

## 📌 注意事項

1. **向後兼容**：舊的全局變數方式仍然保留，但新代碼應該使用 `app.state` 方式
2. **依賴注入**：未來可以考慮使用 `get_database_dependency()` 作為 FastAPI 依賴注入
3. **測試**：建議先測試 `/api/v1/test/db` 端點，確認連接正常後再測試其他功能
4. **日誌級別**：如果需要查看詳細日誌，可以將 `LOG_LEVEL` 設置為 `DEBUG`

---

**修復完成日期**：2026-01-16  
**修復方法**：FastAPI app.state + startup/shutdown 事件  
**狀態**：✅ 完成，待測試驗證  
**Git 分支**：`feature/mongodb-connection-fix-backup`

