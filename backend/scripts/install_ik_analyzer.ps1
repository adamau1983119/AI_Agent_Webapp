# Elasticsearch IK Analyzer 安裝腳本 (PowerShell)
# 使用方法: .\install_ik_analyzer.ps1 [elasticsearch_version]

param(
    [string]$ESVersion = "8.11.0",
    [string]$ESHost = "http://localhost:9200"
)

Write-Host "=== Elasticsearch IK Analyzer 安裝腳本 ===" -ForegroundColor Green
Write-Host "Elasticsearch 版本: $ESVersion" -ForegroundColor Yellow
Write-Host "Elasticsearch 主機: $ESHost" -ForegroundColor Yellow
Write-Host ""

# 檢查 Elasticsearch 是否運行
Write-Host "檢查 Elasticsearch 連接..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri $ESHost -UseBasicParsing -ErrorAction Stop
    Write-Host "✅ Elasticsearch 連接成功" -ForegroundColor Green
    
    # 嘗試獲取實際版本
    $content = $response.Content | ConvertFrom-Json
    if ($content.version.number) {
        $actualVersion = $content.version.number
        Write-Host "檢測到 Elasticsearch 版本: $actualVersion" -ForegroundColor Yellow
        $ESVersion = $actualVersion
    }
} catch {
    Write-Host "❌ 無法連接到 Elasticsearch" -ForegroundColor Red
    Write-Host "請確保 Elasticsearch 正在運行，或設置 ESHost 參數" -ForegroundColor Yellow
    exit 1
}

# 檢查 IK Analyzer 是否已安裝
Write-Host "`n檢查 IK Analyzer 是否已安裝..." -ForegroundColor Yellow
try {
    $plugins = Invoke-WebRequest -Uri "$ESHost/_cat/plugins" -UseBasicParsing -ErrorAction Stop
    if ($plugins.Content -match "analysis-ik") {
        Write-Host "✅ IK Analyzer 已安裝" -ForegroundColor Green
        Write-Host "如需重新安裝，請先卸載: bin/elasticsearch-plugin remove analysis-ik" -ForegroundColor Yellow
        exit 0
    }
} catch {
    Write-Host "無法檢查插件列表（可能未安裝）" -ForegroundColor Yellow
}

Write-Host "IK Analyzer 未安裝，開始安裝..." -ForegroundColor Yellow

# 構建下載 URL
$IKUrl = "https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v$ESVersion/elasticsearch-analysis-ik-$ESVersion.zip"

Write-Host "`n下載 URL: $IKUrl" -ForegroundColor Yellow

# 提示用戶手動安裝
Write-Host "`n=== 安裝步驟 ===" -ForegroundColor Yellow
Write-Host "1. 進入 Elasticsearch 安裝目錄"
Write-Host "2. 執行以下命令："
Write-Host ""
Write-Host "bin/elasticsearch-plugin install $IKUrl" -ForegroundColor Green
Write-Host ""
Write-Host "3. 重啟 Elasticsearch"
Write-Host ""
Write-Host "4. 驗證安裝："
Write-Host "bin/elasticsearch-plugin list" -ForegroundColor Green
Write-Host ""
Write-Host "5. 測試分詞："
$testCommand = "curl -X POST `"$ESHost/_analyze`" -H 'Content-Type: application/json' -d'{\"analyzer\": \"ik_max_word\", \"text\": \"中華人民共和國\"}'"
Write-Host $testCommand -ForegroundColor Green

# 如果是 Docker 環境
if ($env:DOCKER_CONTAINER) {
    Write-Host "`n=== Docker 安裝方法 ===" -ForegroundColor Yellow
    Write-Host "在 Docker 容器中執行："
    Write-Host "docker exec -it $env:DOCKER_CONTAINER bin/elasticsearch-plugin install $IKUrl" -ForegroundColor Green
    Write-Host "然後重啟容器："
    Write-Host "docker restart $env:DOCKER_CONTAINER" -ForegroundColor Green
}

Write-Host "`n=== 安裝指南完成 ===" -ForegroundColor Green

