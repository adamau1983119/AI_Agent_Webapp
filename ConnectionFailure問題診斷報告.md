# ConnectionFailure 問題診斷報告

## 📋 問題現狀

### 錯誤訊息
```
啟動生成任務失敗: name 'ConnectionFailure' is not defined
```

### 錯誤位置
- **API 端點**: `POST /api/v1/schedules/generate-today`
- **錯誤發生在**: `get_scheduler_service()` 調用時
- **狀態碼**: 500 Internal Server Error

---

## ✅ 已確認的修復

### 1. 導入檢查
所有相關文件都已正確導入 `ConnectionFailure`：

- ✅ `backend/app/api/v1/schedules.py` (第 13 行)
- ✅ `backend/app/services/repositories/base_repository.py` (第 10 行)
- ✅ `backend/app/api/v1/topics.py` (第 21 行)
- ✅ `backend/app/database.py` (第 8-13 行)

### 2. 緩存清除
- ✅ Python 緩存已清除（`__pycache__` 目錄數量 = 0）

### 3. 日誌增強
- ✅ 已在 `get_scheduler_service()` 中添加詳細日誌
- ✅ 已在 `SchedulerService.__init__()` 中添加詳細日誌
- ✅ 已在 `AutomationWorkflow.__init__()` 中添加詳細日誌

---

## 🔍 問題分析

### 可能原因

1. **後端服務器未完全重啟**
   - 雖然已清除緩存，但服務器可能仍在使用舊代碼
   - 需要完全停止並重新啟動

2. **導入順序問題**
   - 雖然所有文件都已導入，但可能存在循環導入
   - `ConnectionFailure` 在導入時可能尚未定義

3. **作用域問題**
   - 錯誤可能發生在某個內部函數或閉包中
   - 該作用域可能無法訪問導入的 `ConnectionFailure`

4. **Python 模組緩存問題**
   - 即使清除了 `__pycache__`，Python 可能仍在使用內存中的模組
   - 需要完全重啟 Python 進程

---

## 🔧 建議解決方案

### 方案 1：完全重啟後端服務器（最優先）

1. **停止所有 Python 進程**
   ```powershell
   Get-Process python | Stop-Process -Force
   ```

2. **等待 5 秒**
   ```powershell
   Start-Sleep -Seconds 5
   ```

3. **重新啟動後端服務器**
   ```powershell
   cd backend
   .\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### 方案 2：檢查後端日誌

查看後端 console 輸出，應該會看到我們添加的詳細日誌：
- `正在初始化 SchedulerService...`
- `初始化 TopicRepository...`
- `初始化 AutomationWorkflow...`

這些日誌會幫助定位錯誤發生的確切位置。

### 方案 3：驗證導入

在 Python 交互式環境中測試：
```python
cd backend
.\venv\Scripts\python.exe
>>> from app.services.repositories.base_repository import BaseRepository
>>> from pymongo.errors import ConnectionFailure
>>> print(ConnectionFailure)
```

---

## 📊 當前狀態

- **代碼層面**: ✅ 所有文件都已正確導入
- **緩存層面**: ✅ 已清除
- **運行層面**: ❌ 錯誤仍然存在
- **日誌層面**: ✅ 已添加詳細日誌

---

## 🎯 下一步行動

1. **查看後端 console 日誌**
   - 應該會看到我們添加的詳細初始化日誌
   - 確認錯誤發生的確切位置

2. **完全重啟後端服務器**
   - 停止所有 Python 進程
   - 等待幾秒
   - 重新啟動

3. **如果問題仍然存在**
   - 檢查是否有其他文件也需要導入 `ConnectionFailure`
   - 檢查導入順序是否有問題
   - 考慮在 `get_scheduler_service()` 中直接導入 `ConnectionFailure`

---

## 💡 臨時解決方案

如果問題持續存在，可以在 `get_scheduler_service()` 函數中直接導入：

```python
def get_scheduler_service() -> SchedulerService:
    """獲取排程服務實例（單例）"""
    from pymongo.errors import ConnectionFailure  # 臨時導入
    global _scheduler_service
    if _scheduler_service is None:
        try:
            logger.info("正在初始化 SchedulerService...")
            _scheduler_service = SchedulerService()
            logger.info("SchedulerService 初始化成功")
        except Exception as e:
            import traceback
            logger.error(f"SchedulerService 初始化失敗: {e}")
            logger.error(f"完整錯誤堆疊:\n{traceback.format_exc()}")
            raise
    return _scheduler_service
```

但這只是臨時方案，根本問題需要找到並修復。

