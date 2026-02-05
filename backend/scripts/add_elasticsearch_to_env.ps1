# Add Elasticsearch HTTPS configuration to .env file

$envPath = "F:\Adam 2025\Myproject\AI_Agent_Wbbapp_for_Social_Media_Content_Generation\backend\.env"

Write-Host ""
Write-Host "=== Adding Elasticsearch HTTPS Configuration ===" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path $envPath)) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    New-Item -Path $envPath -ItemType File -Force | Out-Null
}

# Read current content
$content = Get-Content $envPath -Raw -ErrorAction SilentlyContinue
if (-not $content) {
    $content = ""
}

# Elasticsearch configuration to add/update
$elasticsearchConfig = @"
# Elasticsearch 配置（HTTPS）
ELASTICSEARCH_ENABLED=true
ELASTICSEARCH_HOSTS=https://localhost:9200
ELASTICSEARCH_INDEX=topics
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=xP*87btATBNvn9FfsfrZ
ELASTICSEARCH_TIMEOUT=30
ELASTICSEARCH_MAX_RETRIES=3
ELASTICSEARCH_USE_SSL=true
"@

# Check if Elasticsearch config already exists
if ($content -match "ELASTICSEARCH_ENABLED") {
    Write-Host "Elasticsearch configuration found, updating..." -ForegroundColor Yellow
    
    # Remove existing Elasticsearch config lines
    $lines = Get-Content $envPath
    $newLines = @()
    $skipNext = $false
    
    foreach ($line in $lines) {
        if ($line -match "^# Elasticsearch|^ELASTICSEARCH_") {
            $skipNext = $true
            continue
        }
        if ($skipNext -and ($line -match "^#|^$" -or $line -match "^[A-Z]")) {
            $skipNext = $false
        }
        if (-not $skipNext) {
            $newLines += $line
        }
    }
    
    # Add new config
    $newContent = ($newLines -join "`n") + "`n`n" + $elasticsearchConfig
    Set-Content -Path $envPath -Value $newContent -NoNewline
} else {
    Write-Host "Adding Elasticsearch configuration..." -ForegroundColor Green
    
    # Append to file
    if ($content -and -not $content.EndsWith("`n")) {
        $content += "`n"
    }
    $content += "`n" + $elasticsearchConfig
    Set-Content -Path $envPath -Value $content -NoNewline
}

Write-Host ""
Write-Host "✅ Configuration updated!" -ForegroundColor Green
Write-Host ""
Write-Host "Elasticsearch configuration:" -ForegroundColor Cyan
Get-Content $envPath | Select-String -Pattern "ELASTICSEARCH" | ForEach-Object {
    Write-Host "  $_" -ForegroundColor Gray
}
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Test connection: python backend/scripts/test_https_connection.py" -ForegroundColor White
Write-Host "  2. Restart your application" -ForegroundColor White
Write-Host ""

