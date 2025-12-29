# MongoDB 連接問題解決指南

> **錯誤**：`pymongo.errors.ConfigurationError: The DNS query name does not exist: _mongodb._tcp.cluster.mongodb.net.`  
> **狀態**：部署成功，但應用程式啟動時崩潰

---

## 🔍 問題診斷

錯誤訊息顯示 MongoDB 連接字串有問題：
- Railway 無法解析 MongoDB Atlas 的 DNS
- 可能是 `MONGODB_URL` 環境變數未正確設定
- 或 MongoDB URL 格式錯誤

---

## ✅ 解決方案

### 步驟 1：檢查 MongoDB URL 格式

正確的 MongoDB Atlas 連接字串格式應該是：

```
mongodb+srv://username:password@cluster-name.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

或：

```
mongodb+srv://username:password@cluster-name.xxxxx.mongodb.net/database-name?retryWrites=true&w=majority
```

**重要**：
- `username`：您的 MongoDB Atlas 用戶名
- `password`：您的 MongoDB Atlas 密碼（需要 URL 編碼，例如 `@` 要變成 `%40`）
- `cluster-name`：您的 MongoDB Atlas 集群名稱
- `xxxxx`：MongoDB Atlas 提供的唯一標識符

---

### 步驟 2：在 Railway 設定環境變數

1. **訪問 Railway Dashboard**
2. **點擊服務**：`gentle-enchantment`
3. **點擊 "Variables" 標籤**
4. **找到 `MONGODB_URL` 環境變數**
5. **檢查值是否正確**

#### 檢查要點：

1. **URL 格式正確**：
   - 應該以 `mongodb+srv://` 開頭
   - 包含用戶名和密碼
   - 包含正確的集群名稱

2. **密碼需要 URL 編碼**：
   - 如果密碼包含特殊字符（如 `@`、`#`、`%`），需要編碼
   - `@` → `%40`
   - `#` → `%23`
   - `%` → `%25`
   - `&` → `%26`

3. **集群名稱正確**：
   - 從 MongoDB Atlas Dashboard 複製完整的連接字串
   - 不要手動修改集群名稱

---

### 步驟 3：從 MongoDB Atlas 獲取正確的連接字串

1. **訪問 MongoDB Atlas**：https://cloud.mongodb.com
2. **登入您的帳號**
3. **選擇您的集群**
4. **點擊 "Connect" 按鈕**
5. **選擇 "Connect your application"**
6. **複製連接字串**

連接字串格式：
```
mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

7. **替換 `<username>` 和 `<password>`**：
   - 將 `<username>` 替換為您的實際用戶名
   - 將 `<password>` 替換為您的實際密碼（如果需要，進行 URL 編碼）

---

### 步驟 4：更新 Railway 環境變數

1. **回到 Railway Dashboard**
2. **點擊 "Variables" 標籤**
3. **找到 `MONGODB_URL`**
4. **點擊編輯**
5. **貼上正確的 MongoDB 連接字串**
6. **保存**

---

### 步驟 5：檢查其他環境變數

確認以下環境變數也已正確設定：

```
MONGODB_DB_NAME=ai_agent_webapp
PORT=8000
AI_SERVICE=ollama
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=["https://ai-agent-webapp-ten.vercel.app"]
```

---

### 步驟 6：重新部署

更新環境變數後：

1. **Railway 會自動重新部署**
2. **或手動點擊 "Redeploy"**
3. **等待部署完成**
4. **查看 "Logs" 標籤確認沒有錯誤**

---

## 🔍 常見問題

### 問題 1：密碼包含特殊字符

**解決**：
- 對密碼進行 URL 編碼
- 或更改 MongoDB 密碼為不包含特殊字符的密碼

### 問題 2：集群名稱錯誤

**解決**：
- 從 MongoDB Atlas Dashboard 直接複製連接字串
- 不要手動輸入集群名稱

### 問題 3：IP 白名單未設定

**解決**：
1. 在 MongoDB Atlas Dashboard
2. Network Access → Add IP Address
3. 添加 `0.0.0.0/0`（允許所有 IP）
4. 或添加 Railway 的 IP 範圍

---

## 📝 MongoDB Atlas 設定檢查清單

### 必須完成
- [ ] MongoDB Atlas 集群已建立
- [ ] 資料庫用戶已建立
- [ ] IP 白名單已設定（允許所有 IP：`0.0.0.0/0`）
- [ ] 連接字串已複製
- [ ] Railway 環境變數 `MONGODB_URL` 已正確設定

---

## 🎯 快速修復步驟

1. **從 MongoDB Atlas 複製正確的連接字串**
2. **在 Railway 更新 `MONGODB_URL` 環境變數**
3. **確認密碼已正確編碼（如果需要）**
4. **保存並等待重新部署**
5. **檢查 Logs 確認連接成功**

---

**最後更新**：2025-12-29  
**狀態**：🔧 需要更新 MongoDB 連接字串

