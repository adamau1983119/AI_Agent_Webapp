@echo off
chcp 65001 >nul
echo ========================================
echo 啟動前端服務器 (端口 3000)
echo ========================================
echo.

cd /d "%~dp0frontend"
if not exist "node_modules" (
    echo 正在安裝依賴...
    call npm install
)

echo 啟動前端開發服務器...
call npm run dev

pause

