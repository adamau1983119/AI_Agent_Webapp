# 查找 Elasticsearch 安裝目錄的腳本

Write-Host "=== 查找 Elasticsearch 目錄 ===" -ForegroundColor Green
Write-Host ""

# 常見位置列表
$searchPaths = @(
    "$env:USERPROFILE",
    "$env:USERPROFILE\Downloads",
    "$env:USERPROFILE\Desktop",
    "$env:USERPROFILE\Documents",
    "C:\",
    "D:\",
    "E:\"
)

$found = $false

foreach ($path in $searchPaths) {
    if (Test-Path $path) {
        Write-Host "搜尋: $path" -ForegroundColor Yellow
        $results = Get-ChildItem -Path $path -Filter "elasticsearch*" -Directory -ErrorAction SilentlyContinue
        
        if ($results) {
            foreach ($result in $results) {
                Write-Host "✅ 找到: $($result.FullName)" -ForegroundColor Green
                $found = $true
                
                # 檢查是否是有效的 Elasticsearch 目錄
                if (Test-Path "$($result.FullName)\bin\elasticsearch.bat") {
                    Write-Host "   ✓ 這是有效的 Elasticsearch 安裝目錄" -ForegroundColor Cyan
                    Write-Host ""
                    Write-Host "使用以下命令進入目錄：" -ForegroundColor Yellow
                    Write-Host "cd `"$($result.FullName)`"" -ForegroundColor White
                }
            }
        }
    }
}
    }
}

if (-not $found) {
    Write-Host "❌ 未找到 Elasticsearch 目錄" -ForegroundColor Red
    Write-Host ""
    Write-Host "請確認：" -ForegroundColor Yellow
    Write-Host "1. Elasticsearch 是否已解壓縮？" -ForegroundColor White
    Write-Host "2. 解壓縮到哪個目錄？" -ForegroundColor White
    Write-Host ""
    Write-Host "或者手動指定路徑：" -ForegroundColor Yellow
    Write-Host "cd `"<您的 Elasticsearch 路徑>`"" -ForegroundColor White
}

Write-Host ""
Write-Host "=== 搜尋完成 ===" -ForegroundColor Green

