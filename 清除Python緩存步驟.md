# 清除 Python 緩存步驟

## 📋 步驟說明

### 方法 1：使用 PowerShell 命令（推薦）

#### 步驟 1：打開 PowerShell
- 在項目根目錄打開 PowerShell 終端

#### 步驟 2：清除 `__pycache__` 目錄
```powershell
Get-ChildItem -Path backend -Filter __pycache__ -Recurse -Directory | Remove-Item -Recurse -Force
```

#### 步驟 3：清除 `.pyc` 文件
```powershell
Get-ChildItem -Path backend -Filter *.pyc -Recurse -File | Remove-Item -Force
```

#### 步驟 4：驗證清除結果
```powershell
Get-ChildItem -Path backend -Filter __pycache__ -Recurse -Directory
```
如果沒有輸出，表示緩存已清除。

---

### 方法 2：手動刪除

#### 步驟 1：在文件資源管理器中打開項目
- 導航到 `backend` 目錄

#### 步驟 2：搜尋 `__pycache__` 目錄
- 在搜尋框中輸入：`__pycache__`
- 選擇所有找到的 `__pycache__` 目錄

#### 步驟 3：刪除所有 `__pycache__` 目錄
- 右鍵點擊 → 刪除
- 或按 `Delete` 鍵

#### 步驟 4：搜尋 `.pyc` 文件
- 在搜尋框中輸入：`*.pyc`
- 選擇所有找到的 `.pyc` 文件

#### 步驟 5：刪除所有 `.pyc` 文件
- 右鍵點擊 → 刪除
- 或按 `Delete` 鍵

---

### 方法 3：使用批處理文件（一鍵清除）

創建一個批處理文件 `清除緩存.bat`：

```batch
@echo off
echo 正在清除 Python 緩存...
for /d /r backend %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
for /r backend %%f in (*.pyc) do @if exist "%%f" del /q "%%f"
echo 緩存清除完成！
pause
```

然後雙擊執行即可。

---

## ✅ 清除完成後的步驟

### 1. 重新啟動後端服務器
```powershell
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 測試 API
```powershell
python diagnose_generate_today.py
```

---

## 📝 注意事項

1. **清除緩存不會影響源代碼**：只會刪除編譯後的 `.pyc` 文件和 `__pycache__` 目錄
2. **下次運行時會自動重新生成**：Python 會自動重新編譯並創建新的緩存
3. **建議在修改代碼後清除緩存**：確保使用最新的代碼

---

## 🔍 驗證緩存是否已清除

執行以下命令檢查：
```powershell
Get-ChildItem -Path backend -Filter __pycache__ -Recurse -Directory | Measure-Object
```

如果 `Count` 為 `0`，表示緩存已清除。

