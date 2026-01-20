# 修復 bson null bytes 錯誤的 PowerShell 腳本

Write-Host "🔧 開始修復 bson null bytes 錯誤..." -ForegroundColor Yellow

# 檢查是否在正確的目錄
if (-not (Test-Path "requirements.txt")) {
    Write-Host "❌ 錯誤：請在 backend 目錄下執行此腳本" -ForegroundColor Red
    exit 1
}

# 檢查虛擬環境是否存在
if (-not (Test-Path "venv")) {
    Write-Host "❌ 錯誤：虛擬環境不存在，請先創建虛擬環境" -ForegroundColor Red
    exit 1
}

# 激活虛擬環境
Write-Host "📦 激活虛擬環境..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"

# 升級 pip
Write-Host "⬆️  升級 pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

# 卸載 pymongo 和 motor
Write-Host "🗑️  卸載 pymongo 和 motor..." -ForegroundColor Cyan
pip uninstall -y pymongo motor bson 2>$null

# 清除 pip 緩存
Write-Host "🧹 清除 pip 緩存..." -ForegroundColor Cyan
pip cache purge

# 重新安裝 pymongo 和 motor
Write-Host "📥 重新安裝 pymongo 和 motor..." -ForegroundColor Cyan
pip install --no-cache-dir pymongo>=4.10.0 motor>=3.6.0

# 驗證安裝
Write-Host "✅ 驗證安裝..." -ForegroundColor Cyan
try {
    python -c "import pymongo; import motor; from pymongo.errors import ConnectionFailure; print('✅ 所有模組可以正常導入')"
    Write-Host "`n✅ 修復完成！現在可以重新啟動服務器了" -ForegroundColor Green
    Write-Host "`n執行以下命令啟動服務器：" -ForegroundColor Yellow
    Write-Host "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
} catch {
    Write-Host "`n❌ 驗證失敗，請嘗試方案 2 或方案 3" -ForegroundColor Red
    exit 1
}

