# 修復 bson null bytes 錯誤

## 🔴 錯誤訊息
```
SyntaxError: source code string cannot contain null bytes
```

## 📋 問題原因
`bson` 模組文件損壞，包含 null bytes。這通常發生在：
- 安裝過程中斷
- 虛擬環境文件損壞
- Python 3.13 與某些包的兼容性問題

## ✅ 解決方案

### 方案 1：重新安裝 pymongo 和 motor（推薦）

```powershell
# 進入後端目錄
cd backend

# 激活虛擬環境
.\venv\Scripts\Activate.ps1

# 卸載並重新安裝 pymongo 和 motor
pip uninstall -y pymongo motor
pip install --no-cache-dir pymongo>=4.10.0 motor>=3.6.0

# 驗證安裝
python -c "import pymongo; import motor; print('✅ 安裝成功')"
```

### 方案 2：完全重新安裝所有依賴

如果方案 1 無效，完全重新安裝：

```powershell
# 進入後端目錄
cd backend

# 激活虛擬環境
.\venv\Scripts\Activate.ps1

# 卸載所有依賴
pip freeze > temp_requirements.txt
pip uninstall -y -r temp_requirements.txt

# 清除 pip 緩存
pip cache purge

# 重新安裝所有依賴
pip install --no-cache-dir -r requirements.txt

# 清理臨時文件
Remove-Item temp_requirements.txt
```

### 方案 3：重新創建虛擬環境（最後手段）

如果以上方案都無效：

```powershell
# 進入後端目錄
cd backend

# 刪除舊的虛擬環境
Remove-Item -Recurse -Force venv

# 創建新的虛擬環境
python -m venv venv

# 激活虛擬環境
.\venv\Scripts\Activate.ps1

# 升級 pip
python -m pip install --upgrade pip

# 安裝依賴
pip install -r requirements.txt
```

## 🚀 快速修復腳本

我已經為您創建了自動修復腳本，請執行：

```powershell
.\修復_bson錯誤.ps1
```

## ✅ 驗證修復

修復後，驗證是否可以正常導入：

```powershell
python -c "from pymongo.errors import ConnectionFailure; print('✅ ConnectionFailure 可以正常導入')"
python -c "import motor; print('✅ motor 可以正常導入')"
```

然後重新啟動服務器：

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

