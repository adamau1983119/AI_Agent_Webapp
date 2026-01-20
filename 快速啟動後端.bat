@echo off
chcp 65001 >nul
echo ========================================
echo   啟動後端服務器
echo ========================================
echo.

cd /d "%~dp0backend"

if not exist "venv\Scripts\python.exe" (
    echo [錯誤] 虛擬環境不存在！
    echo 請先執行: python -m venv venv
    echo 然後執行: venv\Scripts\pip.exe install -r requirements.txt
    pause
    exit /b 1
)

echo 正在啟動服務器...
echo 服務器將運行在: http://localhost:8000
echo API 文檔: http://localhost:8000/docs
echo.
echo 按 Ctrl+C 停止服務器
echo.

venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause

