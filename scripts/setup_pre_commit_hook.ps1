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
# Pre-commit hook: project structure & multilingual safeguard

echo "[1/3] Validating project structure..."
python scripts/validate_structure.py
if [ `$? -ne 0 ]; then
    echo "ERROR: Structure validation failed. Commit aborted."
    exit 1
fi

echo "[2/3] Executing strict multilingual audit (Rule 17)..."
python scripts/audit_project_i18n.py --strict
if [ `$? -ne 0 ]; then
    echo "ERROR: Multilingual safeguard audit failed! Commit aborted."
    echo "To undo changes, run: .\scripts\undo_all.ps1"
    exit 1
fi

echo "[3/3] Running language conversion unit tests..."
python -m unittest backend/tests/test_i18n_language_conversion.py
if [ `$? -ne 0 ]; then
    echo "ERROR: Unit tests failed! Commit aborted."
    exit 1
fi

echo "SUCCESS: All pre-commit gatekeeper checks passed!"
exit 0
"@

# 對於 Windows，創建 PowerShell 版本的 hook
$PowerShellHookContent = @"
# Pre-commit hook: 專案架構與全端多語言物理門禁 (PowerShell)

Write-Host "🔍 [1/3] 驗證專案架構與基本規範..." -ForegroundColor Cyan
python scripts/validate_structure.py
if (`$LASTEXITCODE -ne 0) {
    Write-Host "❌ 結構驗證失敗，提交已取消。" -ForegroundColor Red
    exit 1
}

Write-Host "🔍 [2/3] 執行全端多語言自動化嚴格審計 (Rule 17)..." -ForegroundColor Cyan
python scripts/audit_project_i18n.py --strict
if (`$LASTEXITCODE -ne 0) {
    Write-Host "❌ 多語言防護審計失敗，提交已強制拒絕！" -ForegroundColor Red
    Write-Host "💡 控制人員若要一鍵還原誤修改，請執行: .\scripts\undo_all.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "🔍 [3/3] 執行語言腳本判定與成套翻譯單元測試..." -ForegroundColor Cyan
python -m unittest backend/tests/test_i18n_language_conversion.py
if (`$LASTEXITCODE -ne 0) {
    Write-Host "❌ 語言轉換單元測試未通過，提交已強制拒絕！" -ForegroundColor Red
    exit 1
}

Write-Host "✅ 所有物理門禁檢驗 100% 通過，允許 Commit！" -ForegroundColor Green
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

