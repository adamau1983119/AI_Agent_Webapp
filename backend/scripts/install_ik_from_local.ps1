# IK Analyzer 本地安裝腳本
# 使用本地 ZIP 文件安裝 IK Analyzer

$elasticsearchPath = "D:\Users\Ophelia Chan\Desktop\elasticsearch-8.11.0"
$ikZipPath = "D:\Users\Ophelia Chan\Downloads\analysis-ik-Latest.zip"

Write-Host "=== IK Analyzer 本地安裝腳本 ===" -ForegroundColor Cyan
Write-Host ""

# 檢查文件是否存在
if (-not (Test-Path $ikZipPath)) {
    Write-Host "❌ 錯誤：找不到 IK Analyzer ZIP 文件：" -ForegroundColor Red
    Write-Host "   $ikZipPath" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "請確認文件路徑是否正確。" -ForegroundColor Yellow
    exit 1
}

# 檢查 Elasticsearch 目錄是否存在
if (-not (Test-Path $elasticsearchPath)) {
    Write-Host "❌ 錯誤：找不到 Elasticsearch 目錄：" -ForegroundColor Red
    Write-Host "   $elasticsearchPath" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "請確認 Elasticsearch 安裝路徑是否正確。" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ 找到 IK Analyzer ZIP 文件：" -ForegroundColor Green
Write-Host "   $ikZipPath" -ForegroundColor Gray
Write-Host ""
Write-Host "✅ 找到 Elasticsearch 目錄：" -ForegroundColor Green
Write-Host "   $elasticsearchPath" -ForegroundColor Gray
Write-Host ""

# 檢查 Elasticsearch 是否正在運行
Write-Host "⚠️  重要提示：" -ForegroundColor Yellow
Write-Host "   安裝插件前必須停止 Elasticsearch！" -ForegroundColor Yellow
Write-Host ""
$continue = Read-Host "Elasticsearch 是否已停止？(Y/N)"

if ($continue -ne "Y" -and $continue -ne "y") {
    Write-Host ""
    Write-Host "請先停止 Elasticsearch，然後重新執行此腳本。" -ForegroundColor Yellow
    Write-Host "停止方法：在運行 Elasticsearch 的 PowerShell 窗口中按 Ctrl+C" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "開始安裝 IK Analyzer..." -ForegroundColor Cyan
Write-Host ""

# 轉換 Windows 路徑為 file:// URL 格式
$fileUrl = "file:///" + ($ikZipPath -replace "\\", "/" -replace ":", ":")

Write-Host "安裝命令：" -ForegroundColor Gray
Write-Host "  cd `"$elasticsearchPath`"" -ForegroundColor DarkGray
Write-Host "  .\bin\elasticsearch-plugin install `"$fileUrl`"" -ForegroundColor DarkGray
Write-Host ""

# 進入 Elasticsearch 目錄
Set-Location $elasticsearchPath

# 執行安裝
try {
    Write-Host "正在安裝..." -ForegroundColor Cyan
    & ".\bin\elasticsearch-plugin.bat" install $fileUrl
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ IK Analyzer 安裝成功！" -ForegroundColor Green
        Write-Host ""
        Write-Host "下一步：" -ForegroundColor Cyan
        Write-Host "  1. 重新啟動 Elasticsearch：" -ForegroundColor Yellow
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
        Write-Host "  1. Elasticsearch 仍在運行（必須先停止）" -ForegroundColor Yellow
        Write-Host "  2. ZIP 文件損壞或格式不正確" -ForegroundColor Yellow
        Write-Host "  3. 版本不兼容" -ForegroundColor Yellow
        Write-Host ""
    }
} catch {
    Write-Host ""
    Write-Host "❌ 安裝過程中發生錯誤：" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
}

