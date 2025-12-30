@echo off
chcp 65001 >nul
echo ========================================
echo    AI Agent Webapp 快速啟動測試
echo ========================================
echo.

echo [1/3] 檢查環境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 未安裝或不在 PATH 中
    pause
    exit /b 1
)
echo ✅ Python 已安裝

node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js 未安裝或不在 PATH 中
    pause
    exit /b 1
)
echo ✅ Node.js 已安裝
echo.

echo [2/3] 啟動後端服務...
start "Backend Server" cmd /k "cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul
echo ✅ 後端服務已啟動 (http://localhost:8000)
echo.

echo [3/3] 啟動前端服務...
start "Frontend Server" cmd /k "cd frontend && npm run dev"
timeout /t 3 /nobreak >nul
echo ✅ 前端服務已啟動 (http://localhost:5173)
echo.

echo ========================================
echo    服務啟動完成！
echo ========================================
echo.
echo 後端 API 文檔: http://localhost:8000/docs
echo 前端應用: http://localhost:5173
echo.
echo 按任意鍵打開瀏覽器...
pause >nul

start http://localhost:5173
start http://localhost:8000/docs

echo.
echo 提示: 關閉此窗口不會停止服務
echo 要停止服務，請關閉對應的命令窗口
echo.
pause

