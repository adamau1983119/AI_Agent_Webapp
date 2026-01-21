# Quick Elasticsearch Status Check

Write-Host "Checking Elasticsearch..." -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -Uri "http://localhost:9200" -TimeoutSec 3 -ErrorAction Stop
    $json = $response.Content | ConvertFrom-Json
    
    Write-Host ""
    Write-Host "✅ Elasticsearch is running!" -ForegroundColor Green
    Write-Host "Version: $($json.version.number)" -ForegroundColor Gray
    Write-Host "Cluster: $($json.cluster_name)" -ForegroundColor Gray
    Write-Host "Node: $($json.name)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Ready to use!" -ForegroundColor Green
    exit 0
} catch {
    Write-Host ""
    Write-Host "❌ Elasticsearch is not running" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please start Elasticsearch:" -ForegroundColor Yellow
    Write-Host '  cd "D:\Users\Ophelia Chan\Desktop\elasticsearch-8.11.0"' -ForegroundColor Gray
    Write-Host "  .\bin\elasticsearch.bat" -ForegroundColor Gray
    exit 1
}
