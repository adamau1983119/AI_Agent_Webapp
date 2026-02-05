# MongoDB 認證失敗解決方案

## 🔴 錯誤訊息
```
pymongo.errors.OperationFailure: bad auth : authentication failed
```

## 📋 問題診斷

錯誤顯示：**認證失敗**，這意味著：
- ✅ 連接字串格式正確（能連接到 MongoDB Atlas）
- ❌ 用戶名或密碼不正確

## ✅ 解決步驟

### 步驟 1：確認 MongoDB Atlas 中的用戶名

在 MongoDB Atlas Dashboard 中：
1. 點擊 **"Security"** → **"Database Access"**
2. 查看您的資料庫用戶列表
3. 確認用戶名是否為：`aadam1983119_db_user`

### 步驟 2：確認密碼

**選項 A：使用現有密碼**
- 如果您記得密碼，確認是否為 `Adam91599957`
- 如果忘記，需要重置密碼

**選項 B：重置密碼（推薦）**
1. 在 **"Database Access"** 頁面
2. 找到用戶 `aadam1983119_db_user`
3. 點擊 **"Edit"** 或 **"..."** → **"Edit User"**
4. 點擊 **"Edit Password"**
5. 設置新密碼（記住這個密碼）
6. 點擊 **"Update User"**

### 步驟 3：更新 .env 文件

更新 `backend/.env` 文件中的連接字串：

```env
MONGODB_URL=mongodb+srv://aadam1983119_db_user:新密碼@adamau1983119.yyykp09.mongodb.net/?appName=adamau1983119&retryWrites=true&w=majority
```

**重要：**
- 將 `新密碼` 替換為實際密碼
- 如果密碼包含特殊字符，需要 URL 編碼

### 步驟 4：驗證連接

運行測試腳本：
```powershell
cd backend
.\venv\Scripts\python.exe test_mongo_connection.py
```

## 🔍 常見問題

### Q: 如何確認用戶名是否正確？

在 MongoDB Atlas Dashboard：
- **Security** → **Database Access**
- 查看用戶列表中的用戶名

### Q: 如何確認密碼是否正確？

**方法 1：重置密碼（最簡單）**
- 在 Database Access 中重置密碼
- 使用新密碼更新 .env 文件

**方法 2：使用 MongoDB Compass 測試**
- 下載 MongoDB Compass
- 使用連接字串測試連接
- 如果連接成功，密碼正確

### Q: 連接字串中的用戶名和密碼在哪裡？

連接字串格式：
```
mongodb+srv://用戶名:密碼@集群地址/資料庫?選項
```

例如：
```
mongodb+srv://aadam1983119_db_user:Adam91599957@adamau1983119.yyykp09.mongodb.net/?appName=adamau1983119&retryWrites=true&w=majority
```

## 🎯 快速修復

1. **登入 MongoDB Atlas Dashboard**
2. **Security** → **Database Access**
3. **找到用戶** `aadam1983119_db_user`
4. **重置密碼**（設置一個新密碼，記住它）
5. **更新 .env 文件**中的密碼
6. **重啟服務器**

## ✅ 驗證修復

修復後，應該看到：
```
✅ MongoDB connection successful!
Connection status: True
Reason: connected
```

---

**需要幫助？** 如果重置密碼後仍然失敗，請檢查：
- 網絡訪問是否已配置（IP 白名單）
- 用戶權限是否正確
- 連接字串格式是否正確

