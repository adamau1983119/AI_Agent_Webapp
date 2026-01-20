@echo off
echo 正在啟動後端服務器...
cd /d "%~dp0backend"

REM 檢查虛擬環境是否存在
if not exist "venv\Scripts\python.exe" (
    echo 錯誤：虛擬環境不存在！
    echo 請先執行: python -m venv venv
    pause
    exit /b 1
)

REM 直接使用虛擬環境的 Python（不需要激活）
echo 使用虛擬環境的 Python 啟動服務器...
venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause

