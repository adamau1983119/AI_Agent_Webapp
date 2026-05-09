# 用本機 HTTPS 啟動後端（僅供測試 Meta 連接／發文）
# 執行前請先關閉佔用 8000 的程式；backend\.env 的 BACKEND_URL=https://localhost:8000
# 測完請改回 http://localhost:8000 並用一般指令啟動

$backendRoot = Split-Path -Parent $PSScriptRoot
$keyPath = Join-Path $backendRoot "certs\key.pem"
$certPath = Join-Path $backendRoot "certs\cert.pem"

if (-not (Test-Path $keyPath) -or -not (Test-Path $certPath)) {
    Write-Host "找不到憑證。請先執行: .\scripts\gen_ssl_cert.ps1 或 python scripts/gen_ssl_cert.py" -ForegroundColor Yellow
    exit 1
}

Set-Location $backendRoot
Write-Host "啟動後端 (HTTPS, port 8000) ... 測完 Meta 後請用一般指令啟動並還原 .env" -ForegroundColor Cyan
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --ssl-keyfile=certs/key.pem --ssl-certfile=certs/cert.pem
