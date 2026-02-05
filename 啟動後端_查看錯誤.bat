@echo off
chcp 65001 >nul
echo ========================================
echo   啟動後端服務器（查看完整錯誤）
echo ========================================
echo.

cd /d "%~dp0backend"

if not exist "venv\Scripts\python.exe" (
    echo [錯誤] 虛擬環境不存在！
    pause
    exit /b 1
)

echo 正在啟動服務器...
echo 服務器將運行在: http://localhost:8000
echo.
echo 如果看到錯誤，請複製完整的錯誤訊息
echo 按 Ctrl+C 停止服務器
echo.
echo ========================================
echo.

set PYTHONIOENCODING=utf-8
venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause

