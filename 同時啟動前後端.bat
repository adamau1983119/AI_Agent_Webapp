@echo off
chcp 65001 >nul
echo ========================================
echo 同時啟動前端和後端服務器
echo ========================================
echo.

start "前端服務器 (3000)" cmd /k "cd /d %~dp0frontend && npm run dev"
timeout /t 2 /nobreak >nul

start "後端服務器 (8000)" cmd /k "cd /d %~dp0backend && .\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo ========================================
echo 兩個服務器已在新窗口中啟動
echo ========================================
echo 前端: http://localhost:3000
echo 後端: http://localhost:8000
echo.
echo 按任意鍵關閉此窗口（服務器將繼續運行）
pause >nul

