# 自動備份腳本 (Windows PowerShell)
# 在修改關鍵文件前自動創建備份

$ErrorActionPreference = "Stop"

# 獲取當前時間戳
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupDir = "backups/daily/$Timestamp"

# 創建備份目錄
New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null

Write-Host "📦 開始備份..." -ForegroundColor Cyan

# 關鍵文件列表
$CriticalFiles = @(
    "backend/app/main.py",
    "backend/app/config.py",
    "backend/app/database.py"
)

# 備份關鍵文件
$BackedUpFiles = 0
foreach ($file in $CriticalFiles) {
    if (Test-Path $file) {
        $DestPath = Join-Path $BackupDir $file
        $DestDir = Split-Path $DestPath -Parent
        New-Item -ItemType Directory -Path $DestDir -Force | Out-Null
        Copy-Item -Path $file -Destination $DestPath -Force
        $BackedUpFiles++
        Write-Host "  ✅ 已備份: $file" -ForegroundColor Green
    }
}

# 創建 Git 標籤（如果可用）
try {
    $TagName = "backup-$Timestamp"
    git tag -a $TagName -m "自動備份標籤 - $Timestamp" 2>&1 | Out-Null
    Write-Host "  ✅ 已創建 Git 標籤: $TagName" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️ 無法創建 Git 標籤（可能不在 Git 倉庫中）" -ForegroundColor Yellow
}

# 記錄備份日誌
$LogFile = "backups/backup_log.txt"
$LogEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - 備份完成: $BackupDir (備份了 $BackedUpFiles 個文件)"
Add-Content -Path $LogFile -Value $LogEntry

Write-Host "`n✅ 備份完成: $BackupDir" -ForegroundColor Green
Write-Host "   備份了 $BackedUpFiles 個關鍵文件" -ForegroundColor Green

