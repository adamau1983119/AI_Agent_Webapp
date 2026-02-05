# Elasticsearch 啟動與 IK Analyzer 測試腳本

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Elasticsearch 啟動與測試" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$elasticsearchPath = "D:\Users\Ophelia Chan\Desktop\elasticsearch-8.11.0"
$password = "xP*87btATBNvn9FfsfrZ"

# 檢查 Elasticsearch 是否已安裝
if (-not (Test-Path $elasticsearchPath)) {
    Write-Host "錯誤：找不到 Elasticsearch 目錄" -ForegroundColor Red
    Write-Host "路徑：$elasticsearchPath" -ForegroundColor Yellow
    exit 1
}

# 檢查 IK Analyzer 是否已安裝
Write-Host "檢查 IK Analyzer 插件..." -ForegroundColor Cyan
Push-Location $elasticsearchPath
$plugins = .\bin\elasticsearch-plugin.bat list 2>&1
Pop-Location

if ($plugins -match "analysis-ik") {
    Write-Host "✅ IK Analyzer 已安裝" -ForegroundColor Green
} else {
    Write-Host "❌ IK Analyzer 未安裝" -ForegroundColor Red
    Write-Host "請先安裝 IK Analyzer：" -ForegroundColor Yellow
    Write-Host "  cd `"$elasticsearchPath`"" -ForegroundColor Gray
    Write-Host "  .\bin\elasticsearch-plugin install --batch https://get.infini.cloud/elasticsearch/analysis-ik/8.11.0" -ForegroundColor Gray
    exit 1
}

Write-Host ""

# 檢查 Elasticsearch 是否正在運行
Write-Host "檢查 Elasticsearch 狀態..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9200" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✅ Elasticsearch 正在運行" -ForegroundColor Green
    $json = $response.Content | ConvertFrom-Json
    Write-Host "版本: $($json.version.number)" -ForegroundColor Gray
    Write-Host "集群名稱: $($json.cluster_name)" -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "❌ Elasticsearch 未運行" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "請在另一個 PowerShell 窗口中啟動 Elasticsearch：" -ForegroundColor Yellow
    Write-Host "  cd `"$elasticsearchPath`"" -ForegroundColor Gray
    Write-Host "  .\bin\elasticsearch.bat" -ForegroundColor Gray
    Write-Host ""
    Write-Host "等待 Elasticsearch 啟動完成（約 30-60 秒），然後按任意鍵繼續測試..." -ForegroundColor Cyan
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    Write-Host ""
}

# 測試 IK Analyzer
Write-Host "測試 IK Analyzer 中文分詞..." -ForegroundColor Cyan
Write-Host ""

$credential = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("elastic:$password"))

$testTexts = @(
    "中華人民共和國",
    "你好世界",
    "人工智慧"
)

foreach ($text in $testTexts) {
    Write-Host "測試文字: $text" -ForegroundColor Gray
    try {
        $body = @{
            analyzer = "ik_max_word"
            text = $text
        } | ConvertTo-Json
        
        $headers = @{
            "Authorization" = "Basic $credential"
            "Content-Type" = "application/json"
        }
        
        $response = Invoke-RestMethod -Uri "http://localhost:9200/_analyze?pretty" `
            -Method Post `
            -Headers $headers `
            -Body $body `
            -ErrorAction Stop
        
        Write-Host "分詞結果: " -ForegroundColor Green -NoNewline
        $tokens = $response.tokens | ForEach-Object { $_.token }
        Write-Host ($tokens -join ", ") -ForegroundColor White
        Write-Host ""
    } catch {
        Write-Host "❌ 測試失敗: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host ""
    }
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  測試完成" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

