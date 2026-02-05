# Elasticsearch 快速啟動腳本 (Windows PowerShell)
# 檢查並提供 Elasticsearch 安裝/啟動指南

Write-Host "=== Elasticsearch 快速啟動指南 ===" -ForegroundColor Green
Write-Host ""

# 檢查 Elasticsearch 是否運行
Write-Host "檢查 Elasticsearch 連接..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9200" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✅ Elasticsearch 正在運行！" -ForegroundColor Green
    $content = $response.Content | ConvertFrom-Json
    Write-Host "版本: $($content.version.number)" -ForegroundColor Cyan
    Write-Host "集群名稱: $($content.cluster_name)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Elasticsearch 已準備就緒，可以繼續安裝 IK Analyzer。" -ForegroundColor Green
    exit 0
} catch {
    Write-Host "❌ Elasticsearch 未運行或未安裝" -ForegroundColor Red
    Write-Host ""
}

# 檢查 Docker 是否可用
Write-Host "檢查 Docker..." -ForegroundColor Yellow
$dockerAvailable = $false
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker 已安裝: $dockerVersion" -ForegroundColor Green
        $dockerAvailable = $true
    }
} catch {
    Write-Host "❌ Docker 未安裝" -ForegroundColor Yellow
}

# 檢查 Java
Write-Host "檢查 Java..." -ForegroundColor Yellow
$javaAvailable = $false
try {
    $javaVersion = java -version 2>&1 | Select-Object -First 1
    if ($javaVersion -match "version") {
        Write-Host "✅ Java 已安裝: $javaVersion" -ForegroundColor Green
        $javaAvailable = $true
    }
} catch {
    Write-Host "❌ Java 未安裝（Elasticsearch 需要 Java）" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== 安裝選項 ===" -ForegroundColor Green
Write-Host ""

# 選項 1：Docker（推薦）
if ($dockerAvailable) {
    Write-Host "選項 1：使用 Docker 啟動 Elasticsearch（推薦）" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "執行以下命令：" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "docker run -d \`" -ForegroundColor Green
    Write-Host "  --name elasticsearch \`" -ForegroundColor Green
    Write-Host "  -p 9200:9200 \`" -ForegroundColor Green
    Write-Host "  -p 9300:9300 \`" -ForegroundColor Green
    Write-Host "  -e `"discovery.type=single-node`" \`" -ForegroundColor Green
    Write-Host "  -e `"ES_JAVA_OPTS=-Xms512m -Xmx512m`" \`" -ForegroundColor Green
    Write-Host "  docker.elastic.co/elasticsearch/elasticsearch:8.11.0" -ForegroundColor Green
    Write-Host ""
    Write-Host "等待 30-60 秒後，執行：" -ForegroundColor Yellow
    Write-Host "curl http://localhost:9200" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "選項 1：安裝 Docker Desktop（推薦）" -ForegroundColor Cyan
    Write-Host "1. 下載：https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    Write-Host "2. 安裝後重新運行此腳本" -ForegroundColor Yellow
    Write-Host ""
}

# 選項 2：手動安裝
Write-Host "選項 2：手動安裝 Elasticsearch" -ForegroundColor Cyan
Write-Host "1. 下載：https://www.elastic.co/downloads/elasticsearch" -ForegroundColor Yellow
Write-Host "2. 解壓縮到 C:\elasticsearch-8.11.0" -ForegroundColor Yellow
Write-Host "3. 執行：.\bin\elasticsearch.bat" -ForegroundColor Yellow
Write-Host ""

# 選項 3：使用 MongoDB（不需要 Elasticsearch）
Write-Host "選項 3：使用 MongoDB 搜尋（不需要 Elasticsearch）" -ForegroundColor Cyan
Write-Host "系統已實作 MongoDB 搜尋功能，可以跳過 Elasticsearch 安裝。" -ForegroundColor Yellow
Write-Host "只需確保：" -ForegroundColor Yellow
Write-Host "  - ELASTICSEARCH_ENABLED=false（在 .env 文件中）" -ForegroundColor Yellow
Write-Host "  - MongoDB 已連接" -ForegroundColor Yellow
Write-Host ""

Write-Host "=== 詳細安裝指南 ===" -ForegroundColor Green
Write-Host "請參考：backend\scripts\install_elasticsearch_windows.md" -ForegroundColor Yellow
Write-Host ""

# 詢問用戶選擇
Write-Host "您想使用哪個選項？" -ForegroundColor Cyan
Write-Host "1. Docker（如果已安裝）" -ForegroundColor White
Write-Host "2. 手動安裝" -ForegroundColor White
Write-Host "3. 使用 MongoDB（跳過 Elasticsearch）" -ForegroundColor White
Write-Host ""
$choice = Read-Host "請輸入選項 (1/2/3)"

switch ($choice) {
    "1" {
        if ($dockerAvailable) {
            Write-Host ""
            Write-Host "正在啟動 Elasticsearch Docker 容器..." -ForegroundColor Yellow
            docker run -d --name elasticsearch -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" docker.elastic.co/elasticsearch/elasticsearch:8.11.0
            Write-Host ""
            Write-Host "等待 30-60 秒讓 Elasticsearch 啟動..." -ForegroundColor Yellow
            Start-Sleep -Seconds 5
            Write-Host "檢查狀態..." -ForegroundColor Yellow
            docker ps | Select-String "elasticsearch"
            Write-Host ""
            Write-Host "執行以下命令驗證：" -ForegroundColor Yellow
            Write-Host "curl http://localhost:9200" -ForegroundColor Green
        } else {
            Write-Host "Docker 未安裝，請先安裝 Docker Desktop。" -ForegroundColor Red
        }
    }
    "2" {
        Write-Host ""
        Write-Host "請按照以下步驟操作：" -ForegroundColor Yellow
        Write-Host "1. 訪問：https://www.elastic.co/downloads/elasticsearch" -ForegroundColor White
        Write-Host "2. 下載 Windows ZIP 版本" -ForegroundColor White
        Write-Host "3. 解壓縮到 C:\elasticsearch-8.11.0" -ForegroundColor White
        Write-Host "4. 執行：cd C:\elasticsearch-8.11.0" -ForegroundColor White
        Write-Host "5. 執行：.\bin\elasticsearch.bat" -ForegroundColor White
    }
    "3" {
        Write-Host ""
        Write-Host "✅ 選擇使用 MongoDB 搜尋" -ForegroundColor Green
        Write-Host ""
        Write-Host "請確保 .env 文件中設定：" -ForegroundColor Yellow
        Write-Host "ELASTICSEARCH_ENABLED=false" -ForegroundColor Green
        Write-Host ""
        Write-Host "系統將自動使用 MongoDB 進行中文搜尋。" -ForegroundColor Green
    }
    default {
        Write-Host "無效選項，請重新運行腳本。" -ForegroundColor Red
    }
}

