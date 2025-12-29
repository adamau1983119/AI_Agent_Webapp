# Railway 部署故障排除指南

> **問題**：部署失敗（Build failed）  
> **專案**：AI_Agent_Webapp - Backend

---

## 🔍 步驟 1：查看部署日誌

### 在 Railway Dashboard 查看日誌

1. **點擊 "Logs" 標籤**
2. **查看最新的部署日誌**
3. **尋找錯誤訊息**（通常是紅色文字）

### 常見錯誤訊息

#### 錯誤 1：找不到 `requirements.txt`
```
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'
```
**原因**：Root Directory 設定錯誤  
**解決**：設定 Root Directory 為 `backend`

#### 錯誤 2：找不到模組
```
ModuleNotFoundError: No module named 'xxx'
```
**原因**：`requirements.txt` 缺少依賴  
**解決**：檢查並更新 `requirements.txt`

#### 錯誤 3：找不到 `app/main.py`
```
ModuleNotFoundError: No module named 'app'
```
**原因**：Root Directory 設定錯誤或 Python 路徑問題  
**解決**：確認 Root Directory 為 `backend`

#### 錯誤 4：Python 版本不兼容
```
ERROR: Package 'xxx' requires a different Python
```
**原因**：Python 版本太舊或太新  
**解決**：在 `railway.json` 指定 Python 版本

---

## 🔧 步驟 2：檢查 Root Directory

### 確認設定

1. **點擊 "Settings" 標籤**
2. **找到 "Root Directory"**
3. **確認設定為**：`backend`

### 如果設定錯誤

1. **點擊編輯**
2. **輸入**：`backend`
3. **保存**
4. **重新部署**（Railway 會自動觸發）

---

## 🔧 步驟 3：檢查建置配置

### 確認 railway.json 存在

在 `backend/railway.json` 應該有：

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 如果 railway.json 不存在或錯誤

1. **確認文件在 `backend/` 目錄中**
2. **確認格式正確（JSON）**
3. **提交到 GitHub**：
   ```bash
   git add backend/railway.json
   git commit -m "fix: Add railway.json configuration"
   git push
   ```

---

## 🔧 步驟 4：檢查 requirements.txt

### 確認文件存在

`backend/requirements.txt` 應該包含所有必要的依賴。

### 常見問題

#### 問題 1：依賴版本衝突
**解決**：檢查是否有版本衝突，更新到兼容版本

#### 問題 2：缺少依賴
**解決**：確認所有使用的套件都在 `requirements.txt` 中

### 驗證 requirements.txt

在本地測試安裝：
```bash
cd backend
pip install -r requirements.txt
```

如果本地安裝失敗，Railway 也會失敗。

---

## 🔧 步驟 5：檢查 Procfile

### 確認文件存在

`backend/Procfile` 應該包含：

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 如果 Procfile 不存在

1. **建立文件**：`backend/Procfile`
2. **添加內容**：`web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. **提交到 GitHub**

---

## 🔧 步驟 6：手動設定建置命令

如果自動偵測失敗，可以手動設定：

### 在 Railway Dashboard

1. **點擊服務卡片**
2. **點擊 "Settings"**
3. **找到 "Build Command"**
4. **設定為**：`pip install -r requirements.txt`
5. **找到 "Start Command"**
6. **設定為**：`uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## 🔧 步驟 7：檢查 Python 版本

### 指定 Python 版本

在 `backend/railway.json` 添加：

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt",
    "nixpacksConfig": {
      "phases": {
        "setup": {
          "nixPkgs": ["python311"]
        }
      }
    }
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

或使用 `runtime.txt`：

1. **建立文件**：`backend/runtime.txt`
2. **添加內容**：`python-3.11` 或 `python-3.12`
3. **提交到 GitHub**

---

## 🔧 步驟 8：檢查環境變數

### 必須的環境變數

確保以下環境變數已設定：

```
MONGODB_URL=mongodb+srv://...
MONGODB_DB_NAME=ai_agent_webapp
PORT=8000
AI_SERVICE=ollama
ENVIRONMENT=production
DEBUG=false
```

### 檢查方式

1. **點擊 "Variables" 標籤**
2. **確認所有必須的環境變數都存在**
3. **檢查值是否正確**

---

## 🔄 步驟 9：重新部署

### 方法 1：自動重新部署

1. **修復問題後**（例如更新 Root Directory）
2. **Railway 會自動觸發重新部署**

### 方法 2：手動重新部署

1. **點擊服務卡片**
2. **點擊 "Deploy" 或 "Redeploy"**
3. **等待部署完成**

### 方法 3：通過 Git 觸發

1. **修復問題後提交到 GitHub**
2. **Railway 會自動偵測並重新部署**

---

## 📋 快速檢查清單

### 部署前檢查
- [ ] Root Directory 設定為 `backend`
- [ ] `backend/railway.json` 存在且格式正確
- [ ] `backend/Procfile` 存在
- [ ] `backend/requirements.txt` 存在且包含所有依賴
- [ ] 所有必須的環境變數已設定
- [ ] 代碼已提交到 GitHub

### 部署後檢查
- [ ] 查看部署日誌，確認沒有錯誤
- [ ] 健康檢查端點正常（`/health`）
- [ ] API 文檔可訪問（`/docs`）

---

## 🆘 常見錯誤解決方案

### 錯誤：找不到 requirements.txt

**解決步驟**：
1. 確認 Root Directory 為 `backend`
2. 確認 `backend/requirements.txt` 存在
3. 確認文件已提交到 GitHub

### 錯誤：找不到 app 模組

**解決步驟**：
1. 確認 Root Directory 為 `backend`
2. 確認 `backend/app/main.py` 存在
3. 確認 `backend/app/__init__.py` 存在

### 錯誤：依賴安裝失敗

**解決步驟**：
1. 檢查 `requirements.txt` 格式
2. 確認所有依賴名稱正確
3. 檢查版本號是否兼容
4. 在本地測試安裝：`pip install -r requirements.txt`

### 錯誤：啟動命令失敗

**解決步驟**：
1. 確認 Start Command 正確：
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
2. 確認 `app.main:app` 路徑正確
3. 確認 FastAPI 應用在 `app/main.py` 中

---

## 🔍 診斷命令

### 在本地測試建置

```bash
# 1. 進入後端目錄
cd backend

# 2. 測試安裝依賴
pip install -r requirements.txt

# 3. 測試啟動（需要設定環境變數）
export MONGODB_URL="your-mongodb-url"
export MONGODB_DB_NAME="ai_agent_webapp"
export PORT=8000
export AI_SERVICE=ollama
export ENVIRONMENT=production
export DEBUG=false

# 4. 測試啟動
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

如果本地測試成功，Railway 部署應該也會成功。

---

## 📝 下一步

1. **查看部署日誌**，找出具體錯誤
2. **根據錯誤訊息**，參考上面的解決方案
3. **修復問題後**，重新部署
4. **如果仍有問題**，請提供具體的錯誤訊息

---

## 💡 提示

1. **Railway 會自動偵測 Python 專案**，但 Root Directory 必須正確
2. **建置日誌會顯示詳細錯誤**，仔細閱讀可以快速定位問題
3. **本地測試可以避免很多問題**，建議先在本地驗證

---

**最後更新**：2025-12-29  
**狀態**：🔧 故障排除中

