# IK Analyzer 快速安裝腳本
# 自動化安裝流程

$ErrorActionPreference = "Stop"

$elasticsearchPath = "D:\Users\Ophelia Chan\Desktop\elasticsearch-8.11.0"
$ikZipPath = "D:\Users\Ophelia Chan\Downloads\analysis-ik-Latest.zip"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  IK Analyzer 自動安裝腳本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 檢查文件是否存在
if (-not (Test-Path $ikZipPath)) {
    Write-Host "❌ 錯誤：找不到 IK Analyzer ZIP 文件" -ForegroundColor Red
    Write-Host "   路徑：$ikZipPath" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $elasticsearchPath)) {
    Write-Host "❌ 錯誤：找不到 Elasticsearch 目錄" -ForegroundColor Red
    Write-Host "   路徑：$elasticsearchPath" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ 找到 IK Analyzer ZIP 文件" -ForegroundColor Green
Write-Host "✅ 找到 Elasticsearch 目錄" -ForegroundColor Green
Write-Host ""

# 檢查 Elasticsearch 是否正在運行
Write-Host "檢查 Elasticsearch 狀態..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9200" -TimeoutSec 2 -ErrorAction SilentlyContinue
    Write-Host "⚠️  Elasticsearch 正在運行中！" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "請先停止 Elasticsearch：" -ForegroundColor Yellow
    Write-Host "  1. 在運行 Elasticsearch 的 PowerShell 窗口中按 Ctrl+C" -ForegroundColor White
    Write-Host "  2. 等待完全停止" -ForegroundColor White
    Write-Host "  3. 然後重新執行此腳本" -ForegroundColor White
    Write-Host ""
    $continue = Read-Host "是否已停止 Elasticsearch？(Y/N)"
    if ($continue -ne "Y" -and $continue -ne "y") {
        Write-Host "安裝已取消。" -ForegroundColor Yellow
        exit 0
    }
} catch {
    Write-Host "✅ Elasticsearch 已停止" -ForegroundColor Green
    Write-Host ""
}

# 轉換路徑格式
$fileUrl = "file:///" + ($ikZipPath -replace "\\", "/" -replace ":", ":")

Write-Host "開始安裝 IK Analyzer..." -ForegroundColor Cyan
Write-Host "  來源：$ikZipPath" -ForegroundColor Gray
Write-Host "  目標：$elasticsearchPath" -ForegroundColor Gray
Write-Host ""

# 進入 Elasticsearch 目錄
Push-Location $elasticsearchPath

try {
    # 執行安裝
    Write-Host "執行安裝命令..." -ForegroundColor Cyan
    & ".\bin\elasticsearch-plugin.bat" install $fileUrl
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  ✅ IK Analyzer 安裝成功！" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "下一步操作：" -ForegroundColor Cyan
        Write-Host "  1. 重新啟動 Elasticsearch：" -ForegroundColor Yellow
        Write-Host "     cd `"$elasticsearchPath`"" -ForegroundColor DarkGray
        Write-Host "     .\bin\elasticsearch.bat" -ForegroundColor DarkGray
        Write-Host ""
        Write-Host "  2. 驗證安裝：" -ForegroundColor Yellow
        Write-Host "     .\bin\elasticsearch-plugin list" -ForegroundColor DarkGray
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "❌ 安裝失敗，錯誤代碼：$LASTEXITCODE" -ForegroundColor Red
        Write-Host ""
        Write-Host "可能的原因：" -ForegroundColor Yellow
        Write-Host "  - Elasticsearch 仍在運行（必須先停止）" -ForegroundColor White
        Write-Host "  - ZIP 文件損壞或格式不正確" -ForegroundColor White
        Write-Host "  - 版本不兼容" -ForegroundColor White
        Write-Host ""
    }
} catch {
    Write-Host ""
    Write-Host "❌ 安裝過程中發生錯誤：" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
} finally {
    Pop-Location
}

Write-Host "腳本執行完成。" -ForegroundColor Cyan
Write-Host ""
