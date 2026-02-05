# Fix Elasticsearch HTTP Connection
# This script modifies elasticsearch.yml to disable HTTPS for development

$configPath = "D:\Users\Ophelia Chan\Desktop\elasticsearch-8.11.0\config\elasticsearch.yml"

Write-Host ""
Write-Host "=== Elasticsearch HTTP Configuration Fix ===" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $configPath)) {
    Write-Host "Error: Config file not found" -ForegroundColor Red
    Write-Host "Path: $configPath" -ForegroundColor Yellow
    exit 1
}

# Backup original config
$backupPath = "$configPath.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Copy-Item $configPath $backupPath
Write-Host "Backup created: $backupPath" -ForegroundColor Green
Write-Host ""

# Read config
$content = Get-Content $configPath -Raw

# Check if SSL is enabled
if ($content -match "xpack\.security\.http\.ssl:\s*\n\s*enabled:\s*true") {
    Write-Host "HTTPS is currently enabled" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To disable HTTPS for development, change:" -ForegroundColor Cyan
    Write-Host "  enabled: true" -ForegroundColor Gray
    Write-Host "to:" -ForegroundColor Cyan
    Write-Host "  enabled: false" -ForegroundColor Green
    Write-Host ""
    Write-Host "Would you like to disable HTTPS? (Y/N)" -ForegroundColor Yellow
    $response = Read-Host
    
    if ($response -eq "Y" -or $response -eq "y") {
        # Replace enabled: true with enabled: false
        $newContent = $content -replace "(xpack\.security\.http\.ssl:\s*\n\s*enabled:\s*)true", "`$1false"
        
        Set-Content -Path $configPath -Value $newContent -NoNewline
        
        Write-Host ""
        Write-Host "Configuration updated!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Please restart Elasticsearch for changes to take effect:" -ForegroundColor Yellow
        Write-Host "  1. Stop Elasticsearch (Ctrl+C)" -ForegroundColor White
        Write-Host "  2. Start Elasticsearch again" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host "Configuration not changed." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Alternative: Update application to use HTTPS" -ForegroundColor Cyan
        Write-Host "See: backend/scripts/fix_elasticsearch_http.md" -ForegroundColor Gray
    }
} else {
    Write-Host "HTTPS configuration not found or already disabled" -ForegroundColor Green
}

Write-Host ""

