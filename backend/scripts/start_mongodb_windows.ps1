# 啟動 Windows 上由 MongoDB Server 安裝程式註冊的服務（需系統管理員權限時才會成功啟動部分環境下的服務）
# 使用方式：在 PowerShell 執行
#   Set-Location "本專案\backend\scripts"
#   .\start_mongodb_windows.ps1

$ErrorActionPreference = "Stop"
$names = @("MongoDB", "MongoDB Server")
$svc = $null
foreach ($n in $names) {
  $svc = Get-Service -Name $n -ErrorAction SilentlyContinue
  if ($svc) { break }
}
if (-not $svc) {
  $svc = Get-Service | Where-Object { $_.Name -like "MongoDB*" } | Select-Object -First 1
}
if (-not $svc) {
  Write-Host "找不到 MongoDB 服務。請先安裝："
  Write-Host "  winget install MongoDB.Server --accept-package-agreements"
  Write-Host "或使用專案根目錄 docker compose（需 Docker Desktop）。"
  exit 1
}
if ($svc.Status -ne "Running") {
  try {
    Start-Service -Name $svc.Name
  } catch {
    Write-Host "啟動服務失敗（可改以系統管理員執行本腳本，或到 services.msc 手動啟動「$($svc.Name)」）。"
    Write-Host $_.Exception.Message
    exit 1
  }
}
Get-Service -Name $svc.Name | Format-Table Name, Status, StartType
Write-Host "MongoDB 服務已在執行。請確認 backend/.env 為 MONGODB_URL=mongodb://localhost:27017 後重啟後端。"
