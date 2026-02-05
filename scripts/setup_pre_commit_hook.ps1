# 設置 Pre-commit Hook 腳本 (Windows PowerShell)

$HookFile = ".git/hooks/pre-commit"

# 檢查是否在 Git 倉庫中
if (-not (Test-Path ".git")) {
    Write-Host "[ERROR] Current directory is not a Git repository" -ForegroundColor Red
    exit 1
}

# 創建 hooks 目錄（如果不存在）
$HooksDir = ".git/hooks"
if (-not (Test-Path $HooksDir)) {
    New-Item -ItemType Directory -Path $HooksDir -Force | Out-Null
}

# 創建 pre-commit hook 內容
$HookContent = @"
#!/bin/sh
# Pre-commit hook: 驗證專案結構

echo "🔍 驗證專案結構..."

# 執行結構驗證腳本
python scripts/validate_structure.py

if [ `$? -ne 0 ]; then
    echo "❌ 結構驗證失敗，提交已取消。"
    exit 1
fi

echo "✅ 結構驗證通過"
exit 0
"@

# 對於 Windows，創建 PowerShell 版本的 hook
$PowerShellHookContent = @"
# Pre-commit hook: 驗證專案結構 (PowerShell)

Write-Host "🔍 驗證專案結構..." -ForegroundColor Cyan

# 執行結構驗證腳本
python scripts/validate_structure.py

if (`$LASTEXITCODE -ne 0) {
    Write-Host "❌ 結構驗證失敗，提交已取消。" -ForegroundColor Red
    exit 1
}

Write-Host "✅ 結構驗證通過" -ForegroundColor Green
exit 0
"@

# 寫入 hook 文件
try {
    # 設置控制台編碼為 UTF-8
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    
    # 嘗試使用 bash 版本（適用於 Git Bash）
    $HookContent | Out-File -FilePath $HookFile -Encoding ASCII -NoNewline
    Write-Host "[OK] Pre-commit hook created: $HookFile" -ForegroundColor Green
    
    # 也創建 PowerShell 版本（備用）
    $PowerShellHookFile = ".git/hooks/pre-commit.ps1"
    $PowerShellHookContent | Out-File -FilePath $PowerShellHookFile -Encoding UTF8
    Write-Host "[OK] PowerShell hook created: $PowerShellHookFile" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "Note: If using Git Bash, ensure Python is in PATH" -ForegroundColor Yellow
    Write-Host "      If using PowerShell, configure Git to use PowerShell hook" -ForegroundColor Yellow
    
} catch {
    Write-Host "[ERROR] Failed to create hook: $_" -ForegroundColor Red
    exit 1
}

