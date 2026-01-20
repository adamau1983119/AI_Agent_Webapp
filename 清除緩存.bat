@echo off
chcp 65001 >nul
echo ========================================
echo 清除 Python 緩存
echo ========================================
echo.

echo 正在清除 __pycache__ 目錄...
for /d /r backend %%d in (__pycache__) do @if exist "%%d" (
    echo 刪除: %%d
    rd /s /q "%%d"
)

echo.
echo 正在清除 .pyc 文件...
for /r backend %%f in (*.pyc) do @if exist "%%f" (
    echo 刪除: %%f
    del /q "%%f"
)

echo.
echo ========================================
echo 緩存清除完成！
echo ========================================
echo.
echo 請重新啟動後端服務器以使用最新代碼。
pause

