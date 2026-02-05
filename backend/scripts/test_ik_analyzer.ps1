# Simple IK Analyzer Test Script

$elasticsearchPath = "D:\Users\Ophelia Chan\Desktop\elasticsearch-8.11.0"
$password = "xP*87btATBNvn9FfsfrZ"

Write-Host "Testing IK Analyzer..." -ForegroundColor Cyan
Write-Host ""

# Check if Elasticsearch is running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9200" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "Elasticsearch is running" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "Elasticsearch is not running" -ForegroundColor Red
    Write-Host "Please start Elasticsearch first:" -ForegroundColor Yellow
    Write-Host "  cd `"$elasticsearchPath`"" -ForegroundColor Gray
    Write-Host "  .\bin\elasticsearch.bat" -ForegroundColor Gray
    exit 1
}

# Test IK Analyzer
$credential = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("elastic:$password"))

$testText = "Chinese text test"
$body = @{
    analyzer = "ik_max_word"
    text = $testText
} | ConvertTo-Json

$headers = @{
    "Authorization" = "Basic $credential"
    "Content-Type" = "application/json"
}

try {
    Write-Host "Testing analyzer: ik_max_word" -ForegroundColor Cyan
    Write-Host "Test text: $testText" -ForegroundColor Gray
    Write-Host ""
    
    $response = Invoke-RestMethod -Uri "http://localhost:9200/_analyze?pretty" `
        -Method Post `
        -Headers $headers `
        -Body $body `
        -ErrorAction Stop
    
    Write-Host "Success! Tokens:" -ForegroundColor Green
    $response.tokens | ForEach-Object {
        Write-Host "  - $($_.token)" -ForegroundColor White
    }
    Write-Host ""
    Write-Host "IK Analyzer is working correctly!" -ForegroundColor Green
} catch {
    Write-Host "Test failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check:" -ForegroundColor Yellow
    Write-Host "  1. Elasticsearch is running" -ForegroundColor White
    Write-Host "  2. IK Analyzer plugin is installed" -ForegroundColor White
    Write-Host "  3. Credentials are correct" -ForegroundColor White
}

