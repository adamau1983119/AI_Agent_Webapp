# MongoDB SSL 握手錯誤解決指南

> **錯誤**：`SSL handshake failed: ... [SSL: TLSV1_ALERT_INTERNAL_ERROR]`  
> **狀態**：應用程式可以找到 MongoDB，但 SSL 握手失敗

---

## 🔍 問題診斷

錯誤訊息顯示：
- ✅ 應用程式可以找到 MongoDB 服務器（`ac-e6ij3sh-shard-00-00.yyykp09.mongodb.net`）
- ❌ SSL 握手失敗

這通常表示：
1. **MongoDB Atlas IP 白名單未設定**（最常見）
2. **密碼錯誤**
3. **用戶名錯誤**

---

## ✅ 解決方案

### 步驟 1：設定 MongoDB Atlas IP 白名單（最重要！）

1. **訪問 MongoDB Atlas**：https://cloud.mongodb.com
2. **登入您的帳號**
3. **點擊左側導航的 "Network Access"**
4. **點擊 "Add IP Address" 按鈕**
5. **選擇 "Allow Access from Anywhere"**（或輸入 `0.0.0.0/0`）
   - 這允許從任何 IP 連接（包括 Railway）
6. **點擊 "Confirm"**
7. **等待幾分鐘讓設定生效**

**重要**：如果 IP 白名單未設定，即使密碼正確，MongoDB 也會拒絕連接。

---

### 步驟 2：確認密碼正確

1. **在 MongoDB Atlas Dashboard**
2. **點擊 "Database Access"**（左側導航）
3. **找到用戶**：`aadam1983119_db_user`
4. **確認密碼是否正確**
5. **如果忘記密碼**：
   - 點擊用戶旁邊的 "Edit"
   - 點擊 "Edit Password"
   - 設定新密碼
   - **記下新密碼**

---

### 步驟 3：更新 Railway 環境變數

如果更改了密碼：

1. **回到 Railway Dashboard**
2. **點擊 "Variables" 標籤**
3. **找到 `MONGODB_URL`**
4. **更新連接字串**（使用新密碼）：
   ```
   mongodb+srv://aadam1983119_db_user:NEW_PASSWORD@adamau1983119.yyykp09.mongodb.net/?retryWrites=true&w=majority&appName=adamau1983119
   ```
5. **保存**

---

### 步驟 4：增加連接超時時間（可選）

如果連接仍然失敗，可以增加超時時間。修改 `backend/app/database.py`：

```python
client = AsyncIOMotorClient(
    settings.MONGODB_URL,
    serverSelectionTimeoutMS=30000,  # 增加到 30 秒
    connectTimeoutMS=30000,
    socketTimeoutMS=30000,
)
```

---

## 🔍 驗證步驟

### 1. 確認 IP 白名單已設定

在 MongoDB Atlas：
- Network Access → 應該看到 `0.0.0.0/0` 或 "Allow Access from Anywhere"

### 2. 測試連接字串

在本地測試（使用 Python）：

```python
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://aadam1983119_db_user:YOUR_PASSWORD@adamau1983119.yyykp09.mongodb.net/?retryWrites=true&w=majority&appName=adamau1983119"

client = MongoClient(uri, server_api=ServerApi('1'))
try:
    client.admin.command('ping')
    print("✅ 連接成功！")
except Exception as e:
    print(f"❌ 連接失敗: {e}")
```

如果本地測試成功，Railway 部署也應該成功。

---

## 📋 檢查清單

### MongoDB Atlas 設定
- [ ] IP 白名單已設定（允許所有 IP：`0.0.0.0/0`）
- [ ] 資料庫用戶已建立（`aadam1983119_db_user`）
- [ ] 密碼已知且正確

### Railway 設定
- [ ] `MONGODB_URL` 環境變數已正確設定
- [ ] 連接字串使用正確的用戶名和密碼
- [ ] 連接字串使用正確的集群名稱（`adamau1983119.yyykp09.mongodb.net`）

---

## 🆘 常見問題

### 問題 1：IP 白名單已設定但仍失敗

**解決**：
- 等待幾分鐘讓設定生效
- 確認設定為 `0.0.0.0/0`（允許所有 IP）
- 確認沒有其他 IP 限制規則

### 問題 2：密碼包含特殊字符

**解決**：
- 對密碼進行 URL 編碼
- 或更改密碼為不包含特殊字符的密碼

### 問題 3：用戶名錯誤

**解決**：
- 確認用戶名是 `aadam1983119_db_user`
- 確認用戶在 MongoDB Atlas 中已建立

---

## 🎯 快速修復步驟

1. **設定 MongoDB Atlas IP 白名單**（最重要！）
   - Network Access → Add IP Address → Allow Access from Anywhere
2. **確認密碼正確**
   - Database Access → 檢查用戶密碼
3. **更新 Railway 環境變數**（如果需要）
   - Variables → MONGODB_URL → 更新連接字串
4. **重新部署**
   - Railway 會自動重新部署
5. **檢查日誌**
   - 應該看到 "成功連接到 MongoDB"

---

**最後更新**：2025-12-29  
**狀態**：🔧 需要設定 MongoDB Atlas IP 白名單

