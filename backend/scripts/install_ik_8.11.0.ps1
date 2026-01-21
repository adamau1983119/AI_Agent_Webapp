# Elasticsearch 8.11.0 IK Analyzer 安裝腳本
# 路徑: D:\Users\Ophelia Chan\Desktop\elasticsearch-8.11.0

$ES_PATH = "D:\Users\Ophelia Chan\Desktop\elasticsearch-8.11.0"
$IK_VERSION = "8.11.0"
$IK_URL = "https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v8.11.0/elasticsearch-analysis-ik-8.11.0.zip"

Write-Host "=== Elasticsearch 8.11.0 IK Analyzer 安裝腳本 ===" -ForegroundColor Green
Write-Host "Elasticsearch 路徑: $ES_PATH" -ForegroundColor Yellow
Write-Host "IK Analyzer 版本: $IK_VERSION" -ForegroundColor Yellow
Write-Host ""

# 檢查路徑是否存在
if (-not (Test-Path $ES_PATH)) {
    Write-Host "❌ Elasticsearch 目錄不存在: $ES_PATH" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Elasticsearch 目錄存在" -ForegroundColor Green

# 檢查 elasticsearch-plugin.bat
if (-not (Test-Path "$ES_PATH\bin\elasticsearch-plugin.bat")) {
    Write-Host "❌ 找不到 elasticsearch-plugin.bat" -ForegroundColor Red
    exit 1
}

Write-Host "✅ 找到 elasticsearch-plugin.bat" -ForegroundColor Green

# 檢查 Elasticsearch 是否運行
Write-Host "`n檢查 Elasticsearch 是否運行..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9200" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    $esInfo = $response.Content | ConvertFrom-Json
    $version = $esInfo.version.number
    Write-Host "⚠️ Elasticsearch 正在運行，版本: $version" -ForegroundColor Yellow
    Write-Host "   請先停止 Elasticsearch（按 Ctrl+C），然後重新運行此腳本" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "安裝命令：" -ForegroundColor Cyan
    Write-Host "cd `"$ES_PATH`"" -ForegroundColor White
    Write-Host ".\bin\elasticsearch-plugin install $IK_URL" -ForegroundColor White
    exit 0
} catch {
    Write-Host "✅ Elasticsearch 未運行（可以安裝插件）" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== 安裝步驟 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "步驟 1: 進入 Elasticsearch 目錄" -ForegroundColor Yellow
Write-Host "cd `"$ES_PATH`"" -ForegroundColor White
Write-Host ""

Write-Host "步驟 2: 安裝 IK Analyzer" -ForegroundColor Yellow
Write-Host ".\bin\elasticsearch-plugin install $IK_URL" -ForegroundColor White
Write-Host ""

Write-Host "步驟 3: 啟動 Elasticsearch" -ForegroundColor Yellow
Write-Host ".\bin\elasticsearch.bat" -ForegroundColor White
Write-Host ""

Write-Host "步驟 4: 驗證安裝（在另一個 PowerShell 窗口）" -ForegroundColor Yellow
Write-Host "cd `"$ES_PATH`"" -ForegroundColor White
Write-Host ".\bin\elasticsearch-plugin list" -ForegroundColor White
Write-Host ""

Write-Host "步驟 5: 測試中文分詞" -ForegroundColor Yellow
Write-Host 'curl -X POST "http://localhost:9200/_analyze" -H "Content-Type: application/json" -d ''{"analyzer": "ik_max_word", "text": "中華人民共和國"}''' -ForegroundColor White
Write-Host ""

Write-Host "=== 快速命令序列 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "# 1. 進入目錄並安裝" -ForegroundColor Gray
Write-Host "cd `"$ES_PATH`"" -ForegroundColor White
Write-Host ".\bin\elasticsearch-plugin install $IK_URL" -ForegroundColor White
Write-Host ""
Write-Host "# 2. 啟動 Elasticsearch" -ForegroundColor Gray
Write-Host ".\bin\elasticsearch.bat" -ForegroundColor White
Write-Host ""

