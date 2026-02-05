# Start Application with Elasticsearch Support

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting Application" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$backendPath = "F:\Adam 2025\Myproject\AI_Agent_Wbbapp_for_Social_Media_Content_Generation\backend"

# Check if we're in the right directory
if (-not (Test-Path "$backendPath\app\main.py")) {
    Write-Host "Error: Cannot find app/main.py" -ForegroundColor Red
    Write-Host "Please run this script from the project root" -ForegroundColor Yellow
    exit 1
}

# Check Elasticsearch status
Write-Host "Checking Elasticsearch status..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "https://localhost:9200" -SkipCertificateCheck -TimeoutSec 2 -ErrorAction Stop 2>&1 | Out-Null
    Write-Host "✅ Elasticsearch is running" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Elasticsearch may not be running" -ForegroundColor Yellow
    Write-Host "   Please start Elasticsearch first:" -ForegroundColor White
    Write-Host "   cd `"D:\Users\Ophelia Chan\Desktop\elasticsearch-8.11.0`"" -ForegroundColor Gray
    Write-Host "   .\bin\elasticsearch.bat" -ForegroundColor Gray
    Write-Host ""
}

Write-Host ""
Write-Host "Starting FastAPI application..." -ForegroundColor Cyan
Write-Host ""
Write-Host "The application will:" -ForegroundColor Yellow
Write-Host "  1. Connect to Elasticsearch (HTTPS)" -ForegroundColor White
Write-Host "  2. Verify IK Analyzer plugin" -ForegroundColor White
Write-Host "  3. Create topics index if needed" -ForegroundColor White
Write-Host "  4. Start API server on http://localhost:8000" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Change to backend directory and start
Set-Location $backendPath
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

