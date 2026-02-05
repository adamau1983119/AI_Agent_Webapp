# 前端顯示問題診斷腳本
# 用於快速診斷 CORS 和速率限制問題

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "前端顯示問題診斷腳本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 檢查後端服務狀態
Write-Host "1. 檢查後端服務狀態..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "   ✅ 後端服務運行正常 (Status: $($healthResponse.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "   ❌ 後端服務無法訪問: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 2. 檢查 CORS Header (OPTIONS 預檢請求)
Write-Host "2. 檢查 CORS Header (OPTIONS 預檢請求)..." -ForegroundColor Yellow
try {
    $corsResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/topics" `
        -Method OPTIONS `
        -Headers @{
            "Origin" = "http://localhost:3000"
            "Access-Control-Request-Method" = "GET"
            "Access-Control-Request-Headers" = "Content-Type"
        } `
        -UseBasicParsing `
        -ErrorAction Stop
    
    $allowOrigin = $corsResponse.Headers["Access-Control-Allow-Origin"]
    $allowMethods = $corsResponse.Headers["Access-Control-Allow-Methods"]
    
    if ($allowOrigin) {
        Write-Host "   ✅ Access-Control-Allow-Origin: $allowOrigin" -ForegroundColor Green
    } else {
        Write-Host "   ❌ 缺少 Access-Control-Allow-Origin header" -ForegroundColor Red
    }
    
    if ($allowMethods) {
        Write-Host "   ✅ Access-Control-Allow-Methods: $allowMethods" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  缺少 Access-Control-Allow-Methods header" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ CORS 預檢請求失敗: $_" -ForegroundColor Red
}
Write-Host ""

# 3. 檢查實際 API 請求的 CORS Header
Write-Host "3. 檢查實際 API 請求的 CORS Header..." -ForegroundColor Yellow
try {
    $apiResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/topics?page=1&limit=12" `
        -Headers @{
            "Origin" = "http://localhost:3000"
        } `
        -UseBasicParsing `
        -ErrorAction Stop
    
    $allowOrigin = $apiResponse.Headers["Access-Control-Allow-Origin"]
    Write-Host "   ✅ API 請求成功 (Status: $($apiResponse.StatusCode))" -ForegroundColor Green
    if ($allowOrigin) {
        Write-Host "   ✅ Access-Control-Allow-Origin: $allowOrigin" -ForegroundColor Green
    } else {
        Write-Host "   ❌ 缺少 Access-Control-Allow-Origin header" -ForegroundColor Red
    }
    
    # 檢查速率限制 header
    $rateLimit = $apiResponse.Headers["X-RateLimit-Limit"]
    $rateRemaining = $apiResponse.Headers["X-RateLimit-Remaining"]
    if ($rateLimit) {
        Write-Host "   ℹ️  速率限制: $rateLimit/分鐘，剩餘: $rateRemaining" -ForegroundColor Cyan
    }
} catch {
    if ($_.Exception.Response.StatusCode -eq 429) {
        Write-Host "   ⚠️  觸發速率限制 (429)" -ForegroundColor Yellow
        $errorResponse = $_.Exception.Response
        $allowOrigin = $errorResponse.Headers["Access-Control-Allow-Origin"]
        if ($allowOrigin) {
            Write-Host "   ✅ 429 響應包含 CORS header: $allowOrigin" -ForegroundColor Green
        } else {
            Write-Host "   ❌ 429 響應缺少 CORS header" -ForegroundColor Red
        }
    } else {
        Write-Host "   ❌ API 請求失敗: $_" -ForegroundColor Red
    }
}
Write-Host ""

# 4. 測試速率限制
Write-Host "4. 測試速率限制（發送 5 個請求）..." -ForegroundColor Yellow
$rateLimitResults = @()
1..5 | ForEach-Object {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/topics?page=1&limit=12" `
            -UseBasicParsing `
            -ErrorAction Stop
        $rateLimitResults += [PSCustomObject]@{
            Request = $_
            Status = $response.StatusCode
            RateLimit = $response.Headers["X-RateLimit-Limit"]
            Remaining = $response.Headers["X-RateLimit-Remaining"]
        }
        Write-Host "   請求 $_: Status $($response.StatusCode), 剩餘: $($response.Headers['X-RateLimit-Remaining'])" -ForegroundColor Green
    } catch {
        if ($_.Exception.Response.StatusCode -eq 429) {
            Write-Host "   請求 $_: ❌ 429 (速率限制)" -ForegroundColor Red
        } else {
            Write-Host "   請求 $_: ❌ 錯誤 - $_" -ForegroundColor Red
        }
    }
    Start-Sleep -Milliseconds 500
}
Write-Host ""

# 5. 檢查前端服務
Write-Host "5. 檢查前端服務..." -ForegroundColor Yellow
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    Write-Host "   ✅ 前端服務運行正常 (Status: $($frontendResponse.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  前端服務可能未運行或無法訪問" -ForegroundColor Yellow
    Write-Host "      提示: 請確保前端服務在 localhost:3000 運行" -ForegroundColor Yellow
}
Write-Host ""

# 6. 總結
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "診斷完成" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "建議檢查項目：" -ForegroundColor Yellow
Write-Host "1. 確認後端 CORS 設定包含 'http://localhost:3000'" -ForegroundColor White
Write-Host "2. 確認速率限制設定合理（建議開發環境 120 次/分鐘）" -ForegroundColor White
Write-Host "3. 確認 OPTIONS 預檢請求不被計入速率限制" -ForegroundColor White
Write-Host "4. 檢查瀏覽器控制台的 Network 標籤，查看實際的請求/響應 header" -ForegroundColor White
Write-Host ""

