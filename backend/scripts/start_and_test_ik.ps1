# Start Elasticsearch and Test IK Analyzer

$elasticsearchPath = "D:\Users\Ophelia Chan\Desktop\elasticsearch-8.11.0"
$password = "xP*87btATBNvn9FfsfrZ"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  IK Analyzer Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if Elasticsearch is running
Write-Host "Step 1: Checking Elasticsearch status..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9200" -TimeoutSec 3 -ErrorAction Stop
    Write-Host "Elasticsearch is running" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "Elasticsearch is not running" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Starting Elasticsearch..." -ForegroundColor Cyan
    Write-Host "Please wait for startup (30-60 seconds)" -ForegroundColor Yellow
    Write-Host ""
    
    Start-Process -FilePath "$elasticsearchPath\bin\elasticsearch.bat" `
        -WorkingDirectory $elasticsearchPath `
        -WindowStyle Normal
    
    Write-Host "Elasticsearch is starting in a new window..." -ForegroundColor Green
    Write-Host "Waiting for startup..." -ForegroundColor Yellow
    
    # Wait for Elasticsearch to start
    $maxAttempts = 15
    $attempt = 0
    $started = $false
    
    while ($attempt -lt $maxAttempts -and -not $started) {
        $attempt++
        Start-Sleep -Seconds 5
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:9200" -TimeoutSec 2 -ErrorAction Stop
            Write-Host "Elasticsearch started! ($attempt attempts)" -ForegroundColor Green
            $started = $true
        } catch {
            Write-Host "Waiting... ($attempt/$maxAttempts)" -ForegroundColor Gray
        }
    }
    
    if (-not $started) {
        Write-Host ""
        Write-Host "Elasticsearch may still be starting." -ForegroundColor Yellow
        Write-Host "Please check the Elasticsearch window and wait for 'started' message." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Then run this script again to test IK Analyzer." -ForegroundColor Cyan
        exit 0
    }
    Write-Host ""
}

# Step 2: Test IK Analyzer
Write-Host "Step 2: Testing IK Analyzer..." -ForegroundColor Cyan
Write-Host ""

$credential = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("elastic:$password"))
$headers = @{
    "Authorization" = "Basic $credential"
    "Content-Type" = "application/json"
}

# Test ik_max_word
Write-Host "Test 1: ik_max_word analyzer" -ForegroundColor Yellow
$testText1 = "test text for analysis"
$body1 = @{
    analyzer = "ik_max_word"
    text = $testText1
} | ConvertTo-Json

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
    
    Write-Host "IK Analyzer is working!" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible issues:" -ForegroundColor Yellow
    Write-Host "  1. IK Analyzer plugin not installed" -ForegroundColor White
    Write-Host "  2. Elasticsearch needs restart after plugin installation" -ForegroundColor White
    Write-Host "  3. Authentication failed" -ForegroundColor White
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Test Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

