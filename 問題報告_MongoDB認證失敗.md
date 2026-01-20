# 問題報告：MongoDB 認證失敗

## 📋 問題概述

後端服務器在啟動時無法連接到 MongoDB 資料庫，出現認證失敗錯誤。

## 🔴 錯誤訊息

```
pymongo.errors.OperationFailure: bad auth : authentication failed, 
full error: {'ok': 0, 'errmsg': 'bad auth : authentication failed', 
'code': 8000, 'codeName': 'AtlasError'}
```

**錯誤位置：**
- 文件：`backend/app/database.py`
- 函數：`connect_to_mongo()`
- 操作：`await client.admin.command("ping")`

## 📊 當前狀態

### 1. 環境變數驗證
- ✅ 環境變數驗證通過（開發環境）
- ⚠️ `DEEPSEEK_API_KEY` 未設定（已改為警告，不阻止啟動）
- ✅ `GOOGLE_API_KEY` 和 `GOOGLE_SEARCH_ENGINE_ID` 已配置

### 2. MongoDB 配置
- **配置來源：** `backend/app/config_module.py`
- **預設值：** `MONGODB_URL = "mongodb://localhost:27017"`
- **實際使用：** 從環境變數或 `.env` 文件讀取

### 3. 錯誤發生時機
- 在應用啟動的 `lifespan` 階段
- 嘗試連接 MongoDB 時立即失敗
- 阻止整個應用程式啟動

## 🔍 可能的原因

### 原因 1：MongoDB Atlas 認證資訊錯誤
如果使用 MongoDB Atlas（雲端服務），可能的原因：
- ❌ 用戶名或密碼錯誤
- ❌ 連接字串格式不正確
- ❌ IP 白名單未包含當前 IP 地址
- ❌ 資料庫用戶權限不足

### 原因 2：本地 MongoDB 配置問題
如果使用本地 MongoDB：
- ❌ MongoDB 服務未啟動
- ❌ 認證配置與連接字串不匹配
- ❌ 端口被占用或配置錯誤

### 原因 3：連接字串格式問題
- ❌ 特殊字符未正確編碼（如密碼中的 `@`、`:`、`/` 等）
- ❌ 連接字串缺少必要的參數
- ❌ 使用了錯誤的連接協議

## 📝 當前配置檢查清單

請檢查以下項目：

### 1. `.env` 文件位置
- 文件路徑：`backend/.env`
- 確認文件是否存在

### 2. MongoDB 連接字串格式

**MongoDB Atlas 格式：**
```
MONGODB_URL=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<database>?retryWrites=true&w=majority
```

**本地 MongoDB 格式（無認證）：**
```
MONGODB_URL=mongodb://localhost:27017
```

**本地 MongoDB 格式（有認證）：**
```
MONGODB_URL=mongodb://<username>:<password>@localhost:27017/<database>?authSource=admin
```

### 3. 環境變數設定
確認 `.env` 文件中包含：
```env
MONGODB_URL=your_connection_string_here
MONGODB_DB_NAME=ai_agent_webapp
```

## 💡 建議的解決方案

### 方案 1：檢查並修正 MongoDB Atlas 連接字串

1. **登入 MongoDB Atlas 控制台**
   - 確認集群狀態正常
   - 檢查 IP 白名單是否包含當前 IP（或使用 `0.0.0.0/0` 允許所有 IP）

2. **驗證資料庫用戶**
   - 確認用戶名和密碼正確
   - 確認用戶有適當的讀寫權限

3. **獲取正確的連接字串**
   - 在 Atlas 控制台中點擊 "Connect"
   - 選擇 "Connect your application"
   - 複製連接字串
   - 替換 `<password>` 為實際密碼

4. **特殊字符處理**
   - 如果密碼包含特殊字符，需要 URL 編碼：
     - `@` → `%40`
     - `:` → `%3A`
     - `/` → `%2F`
     - `#` → `%23`
     - `?` → `%3F`

### 方案 2：使用本地 MongoDB（開發環境）

如果不需要使用 Atlas，可以切換到本地 MongoDB：

1. **安裝並啟動本地 MongoDB**
   ```bash
   # Windows (使用 Chocolatey)
   choco install mongodb
   
   # 或下載安裝程式
   # https://www.mongodb.com/try/download/community
   ```

2. **更新 `.env` 文件**
   ```env
   MONGODB_URL=mongodb://localhost:27017
   MONGODB_DB_NAME=ai_agent_webapp
   ```

3. **確認 MongoDB 服務運行**
   ```powershell
   # 檢查服務狀態
   Get-Service MongoDB
   ```

### 方案 3：在開發環境中允許 MongoDB 連接失敗（臨時方案）

如果只是為了測試其他功能，可以暫時允許應用在 MongoDB 連接失敗時繼續啟動：

**修改位置：** `backend/app/main.py` 的 `lifespan` 函數

**建議邏輯：**
- 在開發環境中，如果 MongoDB 連接失敗，記錄警告但不阻止啟動
- 在生產環境中，MongoDB 連接失敗則阻止啟動

### 方案 4：添加更詳細的錯誤處理和診斷

在 `backend/app/database.py` 中添加：
- 連接字串格式驗證
- 更詳細的錯誤訊息（不暴露密碼）
- 連接重試機制
- 開發環境的降級處理

## 🔧 診斷步驟

### 步驟 1：檢查當前配置
```powershell
# 檢查 .env 文件是否存在
Test-Path "backend\.env"

# 查看 MONGODB_URL（不顯示完整內容以保護敏感資訊）
Get-Content "backend\.env" | Select-String "MONGODB"
```

### 步驟 2：測試 MongoDB 連接
```python
# 使用 Python 測試連接
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv("backend/.env")
uri = os.getenv("MONGODB_URL")
print(f"連接字串前 20 個字符: {uri[:20]}...")

try:
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("✅ MongoDB 連接成功")
except Exception as e:
    print(f"❌ MongoDB 連接失敗: {e}")
```

### 步驟 3：驗證連接字串格式
- 確認連接字串以 `mongodb://` 或 `mongodb+srv://` 開頭
- 確認包含必要的參數
- 確認沒有多餘的空格或換行符

## 📌 需要第三方協助的資訊

為了更好地診斷問題，請提供以下資訊（**請隱藏敏感資訊**）：

1. **MongoDB 類型**
   - [ ] MongoDB Atlas（雲端）
   - [ ] 本地 MongoDB

2. **連接字串格式（隱藏敏感部分）**
   ```
   mongodb+srv://user:***@cluster.***.mongodb.net/...
   或
   mongodb://localhost:27017
   ```

3. **錯誤發生的完整堆疊追蹤**
   - 已包含在上方

4. **環境資訊**
   - 作業系統：Windows 10
   - Python 版本：Python 3.13
   - pymongo 版本：需要確認

5. **`.env` 文件相關配置（隱藏敏感資訊）**
   ```env
   MONGODB_URL=***
   MONGODB_DB_NAME=ai_agent_webapp
   ENVIRONMENT=development
   ```

## 🎯 優先處理建議

1. **立即處理：** 檢查 MongoDB Atlas IP 白名單和用戶認證資訊
2. **短期方案：** 如果只是開發測試，考慮使用本地 MongoDB
3. **長期方案：** 添加更完善的錯誤處理和診斷機制

## 📚 相關文件

- MongoDB Atlas 連接指南：https://docs.atlas.mongodb.com/getting-started/
- PyMongo 連接字串格式：https://pymongo.readthedocs.io/en/stable/examples/authentication.html
- MongoDB 連接字串規範：https://docs.mongodb.com/manual/reference/connection-string/

---

**報告生成時間：** 2026-01-16  
**問題狀態：** 🔴 待解決  
**影響範圍：** 阻止後端服務器啟動

