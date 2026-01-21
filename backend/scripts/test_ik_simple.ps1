# Simple IK Analyzer Test Script (UTF-8 compatible)

$password = "xP*87btATBNvn9FfsfrZ"
$credential = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("elastic:$password"))

Write-Host ""
Write-Host "=== IK Analyzer Test ===" -ForegroundColor Cyan
Write-Host ""

# Check Elasticsearch
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9200" -TimeoutSec 3 -ErrorAction Stop
    Write-Host "Elasticsearch: Running" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "Elasticsearch: Not running" -ForegroundColor Red
    Write-Host "Please start Elasticsearch first!" -ForegroundColor Yellow
    exit 1
}

# Test 1: ik_max_word analyzer
Write-Host "Test 1: ik_max_word analyzer" -ForegroundColor Yellow
$testText1 = "Chinese text analysis"
$body1 = @{
    analyzer = "ik_max_word"
    text = $testText1
} | ConvertTo-Json

$headers = @{
    "Authorization" = "Basic $credential"
    "Content-Type" = "application/json"
}

try {
    $response = Invoke-RestMethod -Uri "http://localhost:9200/_analyze" `
        -Method Post `
        -Headers $headers `
        -Body $body1 `
        -ErrorAction Stop
    
    Write-Host "Input: $testText1" -ForegroundColor Gray
    Write-Host "Tokens: " -ForegroundColor Green -NoNewline
    $tokens1 = $response.tokens | ForEach-Object { $_.token }
    Write-Host ($tokens1 -join ", ") -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

# Test 2: ik_smart analyzer
Write-Host "Test 2: ik_smart analyzer" -ForegroundColor Yellow
$testText2 = "Natural language processing"
$body2 = @{
    analyzer = "ik_smart"
    text = $testText2
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:9200/_analyze" `
        -Method Post `
        -Headers $headers `
        -Body $body2 `
        -ErrorAction Stop
    
    Write-Host "Input: $testText2" -ForegroundColor Gray
    Write-Host "Tokens: " -ForegroundColor Green -NoNewline
    $tokens2 = $response.tokens | ForEach-Object { $_.token }
    Write-Host ($tokens2 -join ", ") -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

Write-Host "=== Test Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "If you see tokens above, IK Analyzer is working!" -ForegroundColor Green

