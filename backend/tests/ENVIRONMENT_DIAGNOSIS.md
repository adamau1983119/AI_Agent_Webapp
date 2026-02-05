# Python 環境配置問題診斷

## 🔍 發現的問題

### 1. **路徑解析問題**
- PowerShell 在解析相對路徑時出現問題
- 嘗試訪問 `backend\venv` 時，路徑被重複解析為 `backend\backend\venv`
- **原因**：可能是工作目錄設置問題

### 2. **Python 版本不匹配**
- 系統 PATH 中有：`Python 3.9`
- 錯誤訊息顯示系統在尋找：`Python 3.11`
- **原因**：可能有配置指向了不存在的 Python 3.11 路徑

### 3. **虛擬環境路徑問題**
- `backend\venv` 路徑無法訪問
- **可能原因**：
  - 虛擬環境不存在
  - 路徑權限問題
  - 工作目錄不正確

## ✅ 解決方案

### 方案 1：使用絕對路徑

```powershell
# 確認項目根目錄
$projectRoot = "F:\Adam 2025\Myproject\AI_Agent_Wbbapp_for_Social_Media_Content_Generation"

# 使用絕對路徑執行
& "$projectRoot\backend\venv\Scripts\python.exe" --version
```

### 方案 2：切換到正確目錄

```powershell
# 切換到 backend 目錄
cd "F:\Adam 2025\Myproject\AI_Agent_Wbbapp_for_Social_Media_Content_Generation\backend"

# 激活虛擬環境
.\venv\Scripts\Activate.ps1

# 執行測試
pytest tests/ -v
```

### 方案 3：使用系統 Python（如果虛擬環境不可用）

```powershell
# 使用系統 Python 3.9
python -m pip install -r backend/tests/requirements-test.txt
python -m pytest backend/tests/ -v
```

### 方案 4：重新創建虛擬環境

```powershell
# 進入 backend 目錄
cd backend

# 刪除舊的虛擬環境（如果存在）
Remove-Item -Recurse -Force venv -ErrorAction SilentlyContinue

# 創建新的虛擬環境（使用 Python 3.9）
python -m venv venv

# 激活虛擬環境
.\venv\Scripts\Activate.ps1

# 安裝依賴
pip install -r requirements.txt
pip install -r tests/requirements-test.txt

# 執行測試
pytest tests/ -v
```

## 🔧 快速診斷命令

```powershell
# 1. 檢查當前目錄
Get-Location

# 2. 檢查 Python 版本
python --version

# 3. 檢查虛擬環境是否存在
Test-Path "F:\Adam 2025\Myproject\AI_Agent_Wbbapp_for_Social_Media_Content_Generation\backend\venv"

# 4. 檢查虛擬環境中的 Python
Test-Path "F:\Adam 2025\Myproject\AI_Agent_Wbbapp_for_Social_Media_Content_Generation\backend\venv\Scripts\python.exe"

# 5. 列出所有 Python 版本
Get-Command python* | Select-Object Name, Source
```

## 📝 建議的執行步驟

1. **確認工作目錄**：
   ```powershell
   cd "F:\Adam 2025\Myproject\AI_Agent_Wbbapp_for_Social_Media_Content_Generation"
   ```

2. **檢查虛擬環境**：
   ```powershell
   Test-Path "backend\venv\Scripts\python.exe"
   ```

3. **如果虛擬環境存在，直接執行**：
   ```powershell
   & "backend\venv\Scripts\python.exe" -m pytest backend/tests/ -v
   ```

4. **如果虛擬環境不存在，使用系統 Python**：
   ```powershell
   python -m pip install pytest pytest-asyncio
   python -m pytest backend/tests/ -v
   ```

## ⚠️ 注意事項

- 確保在項目根目錄執行命令
- 如果使用虛擬環境，確保已激活
- 如果遇到權限問題，以管理員身份運行 PowerShell

