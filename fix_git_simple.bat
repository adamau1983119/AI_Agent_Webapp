@echo off
chcp 65001 >nul
echo === Git 倉庫修復腳本 ===
echo.

REM 設置變數
set TIMESTAMP=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set BACKUP_DIR=..\project_backup_%TIMESTAMP%
set TEMP_DIR=temp_git_recovery_%TIMESTAMP%

echo Step 1: 建立備份目錄
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
echo 備份目錄: %BACKUP_DIR%
echo.

echo Step 2: 備份損壞的 .git 目錄
if exist ".git" (
    echo 正在備份 .git 目錄...
    xcopy /E /I /H /Y ".git" ".git_corrupted_backup_%TIMESTAMP%\" >nul
    echo 已備份損壞的 .git 目錄
) else (
    echo .git 目錄不存在
)
echo.

echo Step 3: 從遠程倉庫恢復
if exist "%TEMP_DIR%" rmdir /S /Q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"
pushd "%TEMP_DIR%"

echo 正在從 GitHub 克隆...
git clone https://github.com/adamau1983119/AI_Agent_Webapp.git temp_repo
if errorlevel 1 (
    echo 錯誤: 無法從遠程克隆倉庫
    popd
    rmdir /S /Q "%TEMP_DIR%"
    pause
    exit /b 1
)

popd
echo.

echo Step 4: 替換 .git 目錄
if exist ".git" (
    echo 正在移除損壞的 .git 目錄...
    rmdir /S /Q ".git"
    if errorlevel 1 (
        echo 警告: 無法移除 .git 目錄，可能被其他程序鎖定
        echo 請關閉 Cursor 或其他可能使用 .git 的程序，然後重新執行此腳本
        pause
        exit /b 1
    )
)

echo 正在複製新的 .git 目錄...
set SOURCE_GIT=%TEMP_DIR%\temp_repo\.git
set DEST_GIT=.git

if not exist "%SOURCE_GIT%" (
    echo 錯誤: 臨時目錄中找不到 .git 目錄
    echo 源路徑: %SOURCE_GIT%
    echo 當前目錄: %CD%
    pause
    exit /b 1
)

echo 源路徑: %SOURCE_GIT%
echo 目標路徑: %DEST_GIT%
xcopy /E /I /H /Y "%SOURCE_GIT%" "%DEST_GIT%" >nul
if errorlevel 1 (
    echo 錯誤: 無法複製 .git 目錄
    echo 請檢查源路徑是否存在: %SOURCE_GIT%
    echo 請檢查當前目錄: %CD%
    pause
    exit /b 1
)
echo 已成功複製 .git 目錄

echo.

echo Step 5: 清理臨時目錄
rmdir /S /Q "%TEMP_DIR%"
echo.

echo Step 6: 驗證修復結果
git status
if errorlevel 1 (
    echo 警告: git status 失敗
) else (
    echo Git 狀態正常
)
echo.

git fetch origin
if errorlevel 1 (
    echo 警告: git fetch 失敗
) else (
    echo Git fetch 成功
)
echo.

echo === 修復完成 ===
echo.
echo 備份位置: %BACKUP_DIR%
echo 損壞的 .git 備份: .git_corrupted_backup_%TIMESTAMP%
echo.
echo 請檢查以下項目:
echo 1. git status - 檢查工作區狀態
echo 2. git log --oneline -5 - 檢查提交歷史
echo 3. git fetch origin - 測試遠程連接
echo.
pause

