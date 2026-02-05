# ConnectionFailure 修復方案實施報告

## 📋 修復時間
2026-01-16

## 🎯 問題描述
程式在執行時拋出 `name 'ConnectionFailure' is not defined` 錯誤，雖然在多個檔案已導入，但在執行時仍然沒有被正確解析。

## ✅ 已實施的修復方案

### 1. 創建統一的異常模組 ✅
**文件**: `backend/app/exceptions.py`

創建了統一的異常定義模組，集中導入 MongoDB 相關異常，避免循環導入和導入順序問題：

```python
from pymongo.errors import (
    ConnectionFailure,
    ServerSelectionTimeoutError,
    OperationFailure,
    ConfigurationError
)
```

**優點**:
- 集中管理所有異常導入
- 避免循環導入問題
- 統一的導入點，易於維護

### 2. 在函數內部添加臨時導入 ✅
**文件**: `backend/app/api/v1/schedules.py`

在 `get_scheduler_service()` 函數內部直接導入 `ConnectionFailure`，確保作用域正確：

```python
def get_scheduler_service() -> SchedulerService:
    """獲取排程服務實例（單例）"""
    # 在函數內部導入 ConnectionFailure，確保作用域正確
    from pymongo.errors import ConnectionFailure
    import traceback
    ...
```

**優點**:
- 確保在函數執行時 `ConnectionFailure` 一定存在
- 避免因模組載入順序導致名稱未定義
- 即使頂部導入失敗，函數內部導入仍可正常工作

### 3. 更新相關文件使用統一的異常模組 ✅

更新了以下文件使用統一的 `exceptions` 模組：

- ✅ `backend/app/services/repositories/base_repository.py`
- ✅ `backend/app/api/v1/topics.py`
- ✅ `backend/app/api/v1/schedules.py` (添加了備用導入)

**注意**: `backend/app/database.py` 保持直接從 `pymongo.errors` 導入，因為它是基礎模組，避免循環導入。

### 4. 增強錯誤日誌輸出 ✅

在關鍵位置添加了完整的錯誤堆疊追蹤：

- ✅ `get_scheduler_service()` - 添加了 `ConnectionFailure` 專用錯誤處理
- ✅ `generate_today_all_topics()` - 增強了錯誤日誌輸出

**改進內容**:
- 輸出錯誤類型 (`type(e).__name__`)
- 輸出完整錯誤堆疊 (`traceback.format_exc()`)
- 區分不同類型的錯誤（資料庫連接問題 vs 其他問題）

## 📊 修改文件清單

1. ✅ **新建**: `backend/app/exceptions.py` - 統一的異常模組
2. ✅ **修改**: `backend/app/api/v1/schedules.py` - 添加函數內部導入和增強錯誤處理
3. ✅ **修改**: `backend/app/services/repositories/base_repository.py` - 使用統一的異常模組
4. ✅ **修改**: `backend/app/api/v1/topics.py` - 使用統一的異常模組

## 🔍 修復策略說明

### 雙重保障策略

1. **頂部導入** (模組級別)
   - 從 `pymongo.errors` 直接導入
   - 從統一的 `exceptions` 模組導入（備用）

2. **函數內部導入** (執行時)
   - 在 `get_scheduler_service()` 函數內部直接導入
   - 確保在執行時一定可以訪問 `ConnectionFailure`

### 為什麼這樣設計？

1. **避免循環導入**: 統一的 `exceptions.py` 只導入第三方庫，不導入應用模組
2. **作用域保障**: 函數內部導入確保在執行時名稱一定存在
3. **向後兼容**: 保持頂部導入，不影響現有代碼
4. **易於調試**: 增強錯誤日誌，快速定位問題

## 🚀 後續步驟建議

### 1. 完全重啟後端服務器 ⚠️ **重要**

即使代碼已修復，**必須完全重啟後端服務器**才能生效：

```powershell
# 停止所有 Python 進程
Get-Process python | Stop-Process -Force

# 等待 5 秒
Start-Sleep -Seconds 5

# 重新啟動後端服務器
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 清除 Python 緩存（可選）

如果問題仍然存在，清除 Python 緩存：

```powershell
cd backend
Get-ChildItem -Path . -Filter __pycache__ -Recurse -Directory | Remove-Item -Recurse -Force
```

### 3. 驗證修復

重新測試 API：

```bash
# 測試生成今日主題 API
POST /api/v1/schedules/generate-today
```

**預期結果**:
- ✅ 如果資料庫未連接：返回 **400 Bad Request**，包含友好的錯誤訊息
- ✅ 如果資料庫連接正常：返回 **200 OK**，任務在背景執行
- ✅ 不再出現 `name 'ConnectionFailure' is not defined` 錯誤

### 4. 監控日誌

檢查後端日誌，確認：
- ✅ `ConnectionFailure` 可以正確導入
- ✅ 錯誤堆疊追蹤完整輸出
- ✅ 錯誤類型正確識別

## 📝 技術細節

### 導入順序

1. **模組載入時**:
   ```
   pymongo.errors → ConnectionFailure (定義)
   app.exceptions → ConnectionFailure (重新導出)
   app.api.v1.schedules → ConnectionFailure (導入)
   ```

2. **函數執行時**:
   ```
   get_scheduler_service() → 內部導入 ConnectionFailure
   ```

### 錯誤處理流程

```
API 請求
  ↓
get_scheduler_service()
  ↓
SchedulerService.__init__()
  ↓
TopicRepository() / AutomationWorkflow()
  ↓
BaseRepository._get_collection()
  ↓
get_database() → 可能拋出 ConnectionFailure
  ↓
捕獲 ConnectionFailure → 記錄完整堆疊 → 返回友好錯誤訊息
```

## ✅ 檢查清單

- [x] 創建統一的 `exceptions.py` 模組
- [x] 在 `get_scheduler_service()` 添加函數內部導入
- [x] 更新 `base_repository.py` 使用統一異常模組
- [x] 更新 `topics.py` 使用統一異常模組
- [x] 增強錯誤日誌輸出
- [x] 通過 lint 檢查
- [ ] **待執行**: 完全重啟後端服務器
- [ ] **待執行**: 驗證修復效果

## 🎯 預期效果

修復後，系統應該：

1. ✅ **不再出現** `name 'ConnectionFailure' is not defined` 錯誤
2. ✅ **正確捕獲** 資料庫連接失敗異常
3. ✅ **輸出完整** 錯誤堆疊追蹤，便於調試
4. ✅ **返回友好** 錯誤訊息給前端

## 📚 參考資料

- [Python 導入系統文檔](https://docs.python.org/3/reference/import.html)
- [Pymongo 錯誤處理](https://pymongo.readthedocs.io/en/stable/api/pymongo/errors.html)
- [FastAPI 異常處理](https://fastapi.tiangolo.com/tutorial/handling-errors/)

---

**修復完成時間**: 2026-01-16  
**修復狀態**: ✅ 代碼修復完成，等待重啟服務器驗證

