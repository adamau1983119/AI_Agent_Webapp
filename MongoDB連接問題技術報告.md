# MongoDB 連接問題技術報告

## 📋 問題摘要

**問題描述**：FastAPI 應用程序在啟動時成功連接到 MongoDB Atlas，健康檢查端點顯示連接正常，但特定 API 端點（`POST /api/v1/schedules/generate-today`）仍然返回「資料庫客戶端未初始化」錯誤。

**影響範圍**：影響主題生成功能，無法通過 API 生成主題。

**嚴重程度**：中等（功能無法使用，但系統可以啟動）

---

## 🔍 當前狀態

### ✅ 正常工作的部分

1. **服務器啟動**：服務器成功啟動，無錯誤
2. **MongoDB 連接**：啟動時成功連接到 MongoDB Atlas
   - 連接字串格式正確
   - 認證成功
   - 資料庫名稱正確：`ai_agent_webapp`
3. **健康檢查端點**：`GET /api/v1/health` 返回 `"database": "connected"`
4. **配置**：`.env` 文件配置正確，包含有效的用戶名和密碼

### ❌ 問題部分

1. **API 端點**：`POST /api/v1/schedules/generate-today` 返回 400 錯誤
   - 錯誤訊息：`"資料庫客戶端未初始化"`
   - 即使健康檢查顯示已連接

---

## 🛠️ 已嘗試的解決方案

### 1. 配置修復
- ✅ 創建並配置 `.env` 文件
- ✅ 驗證 MongoDB Atlas 連接字串格式
- ✅ 確認用戶名和密碼正確
- ✅ 驗證資料庫名稱

### 2. 代碼修復

#### 2.1 修復 `check_connection()` 函數
- **位置**：`backend/app/database.py:279-320`
- **修改**：添加自動重新連接功能
- **邏輯**：如果 `client` 或 `database` 為 `None`，自動調用 `connect_to_mongo()` 重新連接
- **結果**：健康檢查端點正常工作，但 API 端點仍有問題

#### 2.2 修復健康檢查端點
- **位置**：`backend/app/api/v1/health.py:13-28`
- **修改**：正確解包 `check_connection()` 的返回值 `(bool, str)`
- **結果**：健康檢查正確顯示連接狀態

#### 2.3 增強 API 端點
- **位置**：`backend/app/api/v1/schedules.py:256-415`
- **修改**：在 `generate_today_all_topics()` 中添加自動重新連接邏輯
- **結果**：問題仍然存在

### 3. 診斷測試

#### 3.1 直接連接測試
```python
# 測試結果：連接成功
✅ 成功連接到 MongoDB: ai_agent_webapp
```

#### 3.2 獨立進程測試
```python
# 測試 check_connection() 函數
結果: (True, 'connected')
但全局變數: client = None, database = None
```

**關鍵發現**：`check_connection()` 返回 `True`，但全局變數 `client` 和 `database` 仍然是 `None`

---

## 🔬 技術細節

### 代碼結構

#### 全局變數定義
```python
# backend/app/database.py:23-26
client: AsyncIOMotorClient = None
database: AsyncIOMotorDatabase = None
_connection_attempts = 0
```

#### 連接函數
```python
# backend/app/database.py:81-238
async def connect_to_mongo(max_retries: int = 3, delay: int = 2):
    global client, database, _connection_attempts
    # ... 連接邏輯
    client = AsyncIOMotorClient(...)
    database = client[settings.MONGODB_DB_NAME]
    return database
```

#### 檢查連接函數
```python
# backend/app/database.py:279-320
async def check_connection() -> tuple[bool, str]:
    global client, database
    if client is None or database is None:
        # 嘗試重新連接
        await connect_to_mongo(max_retries=1, delay=1)
        if client is None or database is None:
            return False, "資料庫客戶端未初始化，且重新連接失敗"
    # 執行 ping
    await client.admin.command("ping")
    return True, "connected"
```

### 觀察到的行為

1. **服務器啟動時**：
   - `connect_to_mongo()` 成功執行
   - 全局變數 `client` 和 `database` 被正確設置
   - 日誌顯示：`✅ 成功連接到 MongoDB: ai_agent_webapp`

2. **健康檢查端點調用時**：
   - `check_connection()` 返回 `(True, "connected")`
   - 端點返回 `"database": "connected"`

3. **API 端點調用時**：
   - `check_connection()` 可能返回 `(False, "資料庫客戶端未初始化")`
   - 即使嘗試重新連接，全局變數可能仍未更新

### 可能的根本原因

1. **模組重載問題**：
   - 使用 `uvicorn --reload` 時，模組可能被重載
   - 全局變數可能在不同模組實例之間不同步

2. **作用域問題**：
   - `global` 關鍵字可能沒有正確更新所有引用
   - 不同模組導入的 `client` 和 `database` 可能是不同的對象

3. **異步執行問題**：
   - 多個異步任務可能同時訪問全局變數
   - 可能存在競態條件

4. **連接池問題**：
   - Motor 客戶端可能在不同進程/線程中有不同的實例
   - 連接可能被關閉或重置

---

## 📊 環境信息

### 系統環境
- **操作系統**：Windows 10 (Build 18363)
- **Python 版本**：Python 3.13
- **Shell**：PowerShell

### 依賴版本
- **FastAPI**：最新版本
- **Motor**：3.7.1
- **PyMongo**：最新版本
- **Uvicorn**：使用 `--reload` 模式

### MongoDB 配置
- **服務提供商**：MongoDB Atlas
- **連接方式**：`mongodb+srv://`
- **認證方式**：SCRAM-SHA-1
- **資料庫名稱**：`ai_agent_webapp`
- **用戶名**：`aadam1983119_db_user`
- **環境變數**：從 `.env` 文件讀取

### 服務器配置
- **啟動命令**：`uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- **環境模式**：`development`
- **日誌級別**：`INFO`

---

## 📝 日誌和錯誤訊息

### 服務器啟動日誌（成功）
```
2026-01-16 16:46:51 | INFO | app.database:connect_to_mongo:112 - 嘗試連接 MongoDB (第 1/3 次)...
2026-01-16 16:46:53 | INFO | app.database:connect_to_mongo:131 - ✅ 成功連接到 MongoDB: ai_agent_webapp
2026-01-16 16:46:53 | INFO | app.main:lifespan:167 - ✅ MongoDB 連接驗證成功
```

### API 調用錯誤響應
```json
{
    "status": "failed",
    "message": "資料庫未連接，無法生成主題",
    "detail": "資料庫客戶端未初始化",
    "categories": ["fashion", "food", "trend"],
    "expected_count": 9,
    "existing_count": 0,
    "suggestion": "請配置 MONGODB_URL 並確保 MongoDB 服務正在運行"
}
```

### 健康檢查響應（正常）
```json
{
    "status": "healthy",
    "environment": "development",
    "version": "1.0.0",
    "database": "connected",
    "timestamp": "2026-01-16T08:47:35.187019Z"
}
```

---

## 🎯 需要幫助的部分

### 1. 根本原因分析
- 為什麼健康檢查顯示已連接，但 API 端點顯示未連接？
- 為什麼 `check_connection()` 返回 `True`，但全局變數仍然是 `None`？
- 是否存在模組重載或作用域問題？

### 2. 解決方案建議
- 如何確保全局變數在所有模組實例之間同步？
- 是否應該使用單例模式或依賴注入來管理資料庫連接？
- 是否需要修改連接管理策略？

### 3. 最佳實踐
- 在 FastAPI + Motor + Uvicorn 環境中，管理 MongoDB 連接的最佳實踐是什麼？
- 如何避免模組重載導致的全局變數不同步問題？

---

## 🔧 建議的調試步驟

### 1. 添加詳細日誌
在以下位置添加日誌：
- `check_connection()` 函數中記錄全局變數的實際值
- `connect_to_mongo()` 函數中記錄全局變數的更新
- API 端點中記錄連接檢查的詳細過程

### 2. 驗證全局變數同步
- 檢查不同模組導入的 `client` 和 `database` 是否是同一個對象
- 使用 `id()` 函數比較對象身份

### 3. 測試不同場景
- 不使用 `--reload` 模式啟動服務器
- 測試生產環境模式
- 測試多個並發請求

### 4. 考慮替代方案
- 使用 FastAPI 的依賴注入系統管理資料庫連接
- 使用單例模式封裝資料庫連接
- 使用連接池管理器

---

## 📎 相關文件

1. **連接管理代碼**：`backend/app/database.py`
2. **API 端點代碼**：`backend/app/api/v1/schedules.py`
3. **健康檢查代碼**：`backend/app/api/v1/health.py`
4. **配置文件**：`backend/.env`
5. **主應用文件**：`backend/app/main.py`

---

## 📞 聯繫信息

**報告日期**：2026-01-16  
**報告版本**：1.0  
**狀態**：待解決

---

## 🔄 更新記錄

- **2026-01-16 16:50**：創建初始問題報告
- **2026-01-16 16:46**：服務器成功啟動並連接 MongoDB
- **2026-01-16 16:47**：健康檢查顯示已連接，但 API 端點仍返回錯誤

---

**備註**：此報告旨在幫助第三方開發者或技術支持團隊快速了解問題情況，並提供有效的解決方案。所有代碼修改都已提交並被接受，但問題仍然存在，需要進一步的技術分析。

