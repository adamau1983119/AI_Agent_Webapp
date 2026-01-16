# MongoDB 配置指南

## 📋 當前狀態

您收到的錯誤訊息是**正常的預期行為**：

```json
{
    "status": "failed",
    "message": "資料庫未連接，無法生成主題",
    "detail": "資料庫客戶端未初始化",
    "suggestion": "請配置 MONGODB_URL 並確保 MongoDB 服務正在運行"
}
```

這表示：
- ✅ 系統正確檢測到資料庫未連接
- ✅ 錯誤處理正常工作
- ✅ API 返回了友好的錯誤訊息（400 Bad Request，不是 500）

## 🔧 配置 MongoDB

### 選項 1：本地 MongoDB（推薦用於開發）

#### 步驟 1：安裝 MongoDB

**Windows:**
```powershell
# 使用 Chocolatey（如果已安裝）
choco install mongodb

# 或下載安裝程式
# https://www.mongodb.com/try/download/community
```

**驗證安裝:**
```powershell
# 檢查 MongoDB 服務狀態
Get-Service MongoDB

# 或手動啟動
mongod --dbpath "C:\data\db"
```

#### 步驟 2：創建 `.env` 文件

在 `backend` 目錄下創建 `.env` 文件：

```env
# MongoDB 配置（本地）
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=ai_agent_webapp

# 環境設定
ENVIRONMENT=development
```

#### 步驟 3：重啟服務器

```powershell
# 停止當前服務器（Ctrl+C）
# 然後重新啟動
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

### 選項 2：MongoDB Atlas（雲端，推薦用於生產）

#### 步驟 1：註冊 MongoDB Atlas

1. 訪問 https://cloud.mongodb.com
2. 註冊帳號（免費層可用）
3. 創建集群（選擇免費 M0 層）

#### 步驟 2：配置網絡訪問

1. 在 Atlas Dashboard 中，點擊 **"Network Access"**
2. 點擊 **"Add IP Address"**
3. 選擇 **"Allow Access from Anywhere"**（開發用）或添加您的 IP
4. 點擊 **"Confirm"**

#### 步驟 3：創建資料庫用戶

1. 在 Atlas Dashboard 中，點擊 **"Database Access"**
2. 點擊 **"Add New Database User"**
3. 設置用戶名和密碼
4. 選擇權限：**"Read and write to any database"**
5. 點擊 **"Add User"**

#### 步驟 4：獲取連接字串

1. 在 Atlas Dashboard 中，點擊 **"Connect"**
2. 選擇 **"Connect your application"**
3. 選擇驅動程式：**Python**，版本：**3.11 or later**
4. 複製連接字串，格式如下：
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

#### 步驟 5：配置 `.env` 文件

在 `backend` 目錄下創建或更新 `.env` 文件：

```env
# MongoDB 配置（Atlas）
MONGODB_URL=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=ai_agent_webapp

# 環境設定
ENVIRONMENT=development
```

**重要提示：**
- 將 `<username>` 替換為您的資料庫用戶名
- 將 `<password>` 替換為您的資料庫密碼
- 如果密碼包含特殊字符，需要 URL 編碼：
  - `@` → `%40`
  - `:` → `%3A`
  - `/` → `%2F`
  - `#` → `%23`
  - `?` → `%3F`

#### 步驟 6：重啟服務器

```powershell
# 停止當前服務器（Ctrl+C）
# 然後重新啟動
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## ✅ 驗證連接

配置完成後，重啟服務器，您應該看到：

```
✅ 成功連接到 MongoDB: ai_agent_webapp
```

如果連接失敗，檢查：
1. MongoDB 服務是否運行（本地）或集群是否正常（Atlas）
2. `.env` 文件是否在 `backend` 目錄下
3. 連接字串格式是否正確
4. 網絡訪問是否配置（Atlas）

---

## 🚫 暫時不配置 MongoDB（開發模式）

如果您暫時不需要資料庫功能，系統會：
- ✅ 正常啟動（開發環境）
- ✅ API 返回友好的錯誤訊息
- ✅ 其他功能正常運行（不依賴資料庫的部分）

**注意：** 以下功能需要資料庫：
- ❌ 生成主題
- ❌ 保存主題
- ❌ 查詢主題列表
- ✅ API 正常響應（返回錯誤訊息）

---

## 📝 快速檢查清單

- [ ] `.env` 文件存在於 `backend` 目錄
- [ ] `MONGODB_URL` 已配置
- [ ] `MONGODB_DB_NAME` 已配置
- [ ] MongoDB 服務正在運行（本地）或集群正常（Atlas）
- [ ] 網絡訪問已配置（Atlas）
- [ ] 已重啟服務器

---

## 🆘 常見問題

### Q: 如何檢查 MongoDB 是否運行？

**本地 MongoDB:**
```powershell
Get-Service MongoDB
```

**Atlas:**
- 登入 Atlas Dashboard
- 檢查集群狀態（應該是綠色）

### Q: 連接字串格式錯誤怎麼辦？

確保格式正確：
- 本地：`mongodb://localhost:27017`
- Atlas：`mongodb+srv://username:password@cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority`

### Q: 密碼包含特殊字符怎麼辦？

使用 URL 編碼：
- `@` → `%40`
- `:` → `%3A`
- `/` → `%2F`
- `#` → `%23`
- `?` → `%3F`

### Q: 如何測試連接？

重啟服務器後，查看日誌：
- ✅ 成功：`成功連接到 MongoDB: ai_agent_webapp`
- ❌ 失敗：會顯示具體錯誤訊息

---

**配置完成後，重新測試 API 即可正常生成主題！** 🎉

