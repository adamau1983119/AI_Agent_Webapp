# MongoDB Atlas 連接配置步驟

## 📋 當前狀態

您已經有：
- ✅ MongoDB Atlas 帳號
- ✅ 項目 ID: `6948c5c9fcd51e1e52696159`
- ✅ 集群名稱: `adamau1983119`
- ✅ 數據大小: 117.23 MB

## 🔧 配置步驟

### 步驟 1：獲取連接字串

1. **在 MongoDB Atlas Dashboard 中**：
   - 找到您的集群 `adamau1983119`
   - 點擊 **"Connect"** 按鈕

2. **選擇連接方式**：
   - 選擇 **"Connect your application"**（連接應用程式）

3. **選擇驅動程式**：
   - Driver: **Python**
   - Version: **3.11 or later**（或最新版本）

4. **複製連接字串**：
   - 格式類似：`mongodb+srv://<username>:<password>@adamau1983119.xxxxx.mongodb.net/?retryWrites=true&w=majority`
   - 點擊 **"Copy"** 複製完整連接字串

### 步驟 2：配置資料庫用戶（如果還沒有）

1. **在 Atlas Dashboard 中**：
   - 點擊左側 **"Security"** → **"Database Access"**

2. **創建資料庫用戶**：
   - 點擊 **"Add New Database User"**
   - 選擇認證方式：**"Password"**
   - 輸入用戶名和密碼（記住這些資訊，稍後需要）
   - 用戶權限：選擇 **"Read and write to any database"**
   - 點擊 **"Add User"**

### 步驟 3：配置網絡訪問（如果還沒有）

1. **在 Atlas Dashboard 中**：
   - 點擊左側 **"Security"** → **"Network Access"**

2. **添加 IP 地址**：
   - 點擊 **"Add IP Address"**
   - 選擇 **"Allow Access from Anywhere"**（開發用，IP: `0.0.0.0/0`）
   - 或添加您的當前 IP 地址
   - 點擊 **"Confirm"**

### 步驟 4：更新連接字串

將連接字串中的 `<username>` 和 `<password>` 替換為實際值：

**原始格式：**
```
mongodb+srv://<username>:<password>@adamau1983119.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

**替換後格式：**
```
mongodb+srv://your_username:your_password@adamau1983119.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

**⚠️ 重要：如果密碼包含特殊字符，需要 URL 編碼：**
- `@` → `%40`
- `:` → `%3A`
- `/` → `%2F`
- `#` → `%23`
- `?` → `%3F`
- `&` → `%26`
- `%` → `%25`

### 步驟 5：創建 `.env` 文件

在 `backend` 目錄下創建或更新 `.env` 文件：

```env
# MongoDB Atlas 配置
MONGODB_URL=mongodb+srv://your_username:your_password@adamau1983119.xxxxx.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=ai_agent_webapp

# 環境設定
ENVIRONMENT=development
```

**範例（請替換為您的實際值）：**
```env
MONGODB_URL=mongodb+srv://admin:MyPassword123@adamau1983119.abc123.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=ai_agent_webapp
ENVIRONMENT=development
```

### 步驟 6：驗證連接

重啟後端服務器：

```powershell
cd "F:\Adam 2025\Myproject\AI_Agent_Wbbapp_for_Social_Media_Content_Generation\backend"
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**成功連接的標誌：**
```
✅ 成功連接到 MongoDB: ai_agent_webapp
MongoDB URL: mongodb+srv://...
```

### 步驟 7：測試查詢

連接成功後，可以查詢資源：

```powershell
.\venv\Scripts\python.exe query_resource_id.py 6948c5c9fcd51e1e52696159
```

## 🔍 使用 Data Explorer 驗證數據

在 MongoDB Atlas Dashboard 中：
1. 點擊左側 **"DATABASE"** → **"Data Explorer"**
2. 選擇您的集群和資料庫
3. 查看集合（collections）：
   - `topics` - 主題
   - `contents` - 內容
   - `images` - 圖片

## ⚠️ 常見問題

### Q: 連接失敗怎麼辦？

**檢查清單：**
1. ✅ 連接字串格式是否正確
2. ✅ 用戶名和密碼是否正確
3. ✅ 網絡訪問是否已配置（IP 白名單）
4. ✅ 集群是否正在運行
5. ✅ 密碼中的特殊字符是否已 URL 編碼

### Q: 如何驗證連接字串是否正確？

可以使用 MongoDB Compass 或命令行工具測試：

```bash
# 使用 mongosh（如果已安裝）
mongosh "your_connection_string"
```

### Q: 連接字串中的資料庫名稱在哪裡？

連接字串中的資料庫名稱是可選的。如果沒有指定，可以在連接後選擇資料庫。我們在 `.env` 中使用 `MONGODB_DB_NAME` 來指定。

## 📝 快速參考

**連接字串格式：**
```
mongodb+srv://[username]:[password]@[cluster].mongodb.net/[database]?[options]
```

**必要組件：**
- `username`: 資料庫用戶名
- `password`: 資料庫密碼（URL 編碼）
- `cluster`: 集群名稱（如 `adamau1983119.xxxxx`）
- `database`: 資料庫名稱（可選，我們使用 `MONGODB_DB_NAME`）
- `options`: 連接選項（如 `retryWrites=true&w=majority`）

## ✅ 配置完成後

配置完成後，您應該能夠：
- ✅ 連接 MongoDB Atlas
- ✅ 查詢和創建主題
- ✅ 生成內容
- ✅ 保存圖片
- ✅ 使用所有資料庫相關功能

---

**需要幫助？** 如果遇到任何問題，請檢查：
1. MongoDB Atlas Dashboard 中的集群狀態
2. 網絡訪問配置
3. 資料庫用戶權限
4. 連接字串格式

