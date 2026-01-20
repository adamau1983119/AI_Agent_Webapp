# 啟動後端服務器
Write-Host "正在啟動後端服務器..." -ForegroundColor Green

# 設置執行策略（如果需要）
$currentPolicy = Get-ExecutionPolicy -Scope CurrentUser
if ($currentPolicy -eq "Restricted") {
    Write-Host "設置執行策略為 RemoteSigned..." -ForegroundColor Yellow
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
}

# 進入後端目錄
Set-Location "$PSScriptRoot\backend"

# 檢查虛擬環境是否存在
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "錯誤：虛擬環境不存在！" -ForegroundColor Red
    Write-Host "請先執行: python -m venv venv" -ForegroundColor Yellow
    pause
    exit 1
}

# 直接使用虛擬環境的 Python（不需要激活）
Write-Host "使用虛擬環境的 Python 啟動服務器..." -ForegroundColor Green
& ".\venv\Scripts\python.exe" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

