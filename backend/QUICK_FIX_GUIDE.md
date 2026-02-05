# 🚀 快速修復指南

## ⚡ 立即執行（3 步驟）

### 步驟 1：停止所有後端進程

```powershell
# 在 PowerShell 中執行
taskkill /F /IM python.exe
```

### 步驟 2：等待 3 秒

```powershell
Start-Sleep -Seconds 3
```

### 步驟 3：重新啟動後端

```powershell
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🔍 如果仍然無法啟動

### 檢查 1：端口是否被佔用

```powershell
netstat -ano | findstr ":8000"
```

如果看到輸出，記下 PID，然後：
```powershell
taskkill /PID <PID> /F
```

### 檢查 2：測試模組導入

```powershell
cd backend
.\venv\Scripts\python.exe -c "from app.main import app; print('OK')"
```

如果出現錯誤，請查看錯誤訊息並修復。

### 檢查 3：檢查 MongoDB 連接

確認 MongoDB 服務正在運行：
```powershell
# 檢查 MongoDB 服務狀態
Get-Service | Where-Object {$_.Name -like "*mongo*"}
```

---

## 📋 常見錯誤及解決方法

### 錯誤 1：`Address already in use`

**原因：** 端口 8000 已被佔用

**解決：**
```powershell
# 查找佔用端口的進程
netstat -ano | findstr ":8000"

# 終止進程（替換 <PID> 為實際 PID）
taskkill /PID <PID> /F
```

### 錯誤 2：`ModuleNotFoundError`

**原因：** 缺少 Python 套件

**解決：**
```powershell
cd backend
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 錯誤 3：`ConnectionFailure`

**原因：** MongoDB 無法連接

**解決：**
1. 確認 MongoDB 服務正在運行
2. 檢查 `.env` 文件中的 `MONGODB_URL`
3. 測試連接：
   ```python
   from motor.motor_asyncio import AsyncIOMotorClient
   client = AsyncIOMotorClient("mongodb://localhost:27017")
   # 測試連接
   ```

### 錯誤 4：`TimeoutError` 或 RSS Feed 請求超時

**原因：** RSS Feed 無法訪問或響應太慢

**解決：**
- 這是正常的，系統會自動跳過無法訪問的 RSS Feed
- 如果影響啟動，可以暫時註釋掉有問題的 RSS Feed URL

---

## ✅ 驗證服務正常運行

### 測試 1：健康檢查

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET
```

應該返回：
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "..."
}
```

### 測試 2：排程端點

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/schedules" -Method GET
```

應該返回排程列表（即使為空也是正常的）。

---

## 📞 需要幫助？

如果以上步驟都無法解決問題，請提供：

1. **完整的錯誤訊息**（從啟動到錯誤發生）
2. **執行環境**：
   - Python 版本
   - 作業系統版本
   - MongoDB 版本
3. **重現步驟**：詳細描述如何觸發錯誤

---

**最後更新：** 2026-01-21

