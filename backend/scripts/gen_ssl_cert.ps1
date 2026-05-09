# 產生本機 HTTPS 自簽憑證（僅供開發／測試 Meta 連接用）
# 執行一次即可，產生的檔案請勿提交到 Git

$ErrorActionPreference = "Stop"
$backendRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$certsDir = Join-Path $backendRoot "certs"
$keyPath = Join-Path $certsDir "key.pem"
$certPath = Join-Path $certsDir "cert.pem"

if (-not (Test-Path $certsDir)) {
    New-Item -ItemType Directory -Path $certsDir | Out-Null
    Write-Host "已建立目錄: $certsDir"
}

# 檢查 OpenSSL（常見於 Git for Windows 或獨立安裝）
$openssl = $null
if (Get-Command openssl -ErrorAction SilentlyContinue) {
    $openssl = "openssl"
} else {
    $gitOpenSSL = Join-Path $env:ProgramFiles "Git\usr\bin\openssl.exe"
    if (Test-Path $gitOpenSSL) {
        $openssl = $gitOpenSSL
    }
}

if (-not $openssl) {
    Write-Host "找不到 OpenSSL。" -ForegroundColor Yellow
    Write-Host "請安裝其一："
    Write-Host "  1. Git for Windows (內含 OpenSSL): https://git-scm.com/download/win"
    Write-Host "  2. 或執行: choco install openssl"
    Write-Host ""
    Write-Host "若已安裝 Python，可改用: python scripts/gen_ssl_cert.py"
    exit 1
}

Write-Host "使用 OpenSSL 產生自簽憑證 (CN=localhost) ..."
& $openssl req -x509 -newkey rsa:2048 -keyout $keyPath -out $certPath -days 365 -nodes -subj "/CN=localhost" 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "產生憑證失敗。" -ForegroundColor Red
    exit 1
}

Write-Host "完成。憑證位置："
Write-Host "  私鑰: $keyPath"
Write-Host "  憑證: $certPath"
Write-Host ""
Write-Host "啟動後端 HTTPS 範例（在 backend 目錄執行，請先關閉佔用 8000 的程式）："
Write-Host "  .\scripts\start_backend_https.ps1"
Write-Host ""
Write-Host "瀏覽器首次開啟 https://localhost:8000 時會顯示「不安全」，點「進階」->「繼續前往」即可。"
