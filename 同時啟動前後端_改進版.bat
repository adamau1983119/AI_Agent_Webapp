@echo off
chcp 65001 >nul
echo ========================================
echo 同時啟動前端和後端服務器
echo ========================================
echo.

REM 檢查前端目錄
if not exist "%~dp0frontend\package.json" (
    echo [錯誤] 找不到前端目錄或 package.json
    echo 請確認您在專案根目錄執行此腳本
    pause
    exit /b 1
)

REM 檢查後端目錄和虛擬環境
if not exist "%~dp0backend\venv\Scripts\python.exe" (
    echo [錯誤] 找不到後端虛擬環境
    echo 請確認：
    echo   1. backend\venv\Scripts\python.exe 存在
    echo   2. 虛擬環境已正確建立
    echo.
    echo 如果虛擬環境不存在，請執行：
    echo   cd backend
    echo   python -m venv venv
    echo   .\venv\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

echo [檢查] 前端目錄：✅
echo [檢查] 後端虛擬環境：✅
echo.

REM 檢查端口是否被佔用（可選）
echo [提示] 正在啟動服務器...
echo.

REM 啟動前端服務器
echo [啟動] 前端服務器 (端口 3000)...
start "前端服務器 (3000)" cmd /k "cd /d %~dp0frontend && npm run dev"
timeout /t 2 /nobreak >nul

REM 啟動後端服務器
echo [啟動] 後端服務器 (端口 8000)...
start "後端服務器 (8000)" cmd /k "cd /d %~dp0backend && .\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo ========================================
echo 兩個服務器已在新窗口中啟動
echo ========================================
echo.
echo 前端: http://localhost:3000
echo 後端: http://localhost:8000
echo API 文檔: http://localhost:8000/docs
echo.
echo [提示] 如果服務器啟動失敗，請檢查：
echo   1. 前端：確認 npm 已安裝並執行 'npm install'
echo   2. 後端：確認虛擬環境已啟動並安裝依賴
echo   3. 端口：確認 3000 和 8000 端口未被佔用
echo.
echo 按任意鍵關閉此窗口（服務器將繼續運行）
pause >nul

