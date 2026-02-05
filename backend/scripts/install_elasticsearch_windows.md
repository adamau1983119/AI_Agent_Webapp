# Elasticsearch Windows 安裝指南

## 📋 概述

本指南提供在 Windows 上安裝和配置 Elasticsearch 的詳細步驟。

## 🔍 檢查 Elasticsearch 是否已安裝

### 方法 1：檢查服務

```powershell
# 檢查 Elasticsearch 服務是否運行
Get-Service | Where-Object {$_.Name -like "*elastic*"}
```

### 方法 2：檢查進程

```powershell
# 檢查是否有 Elasticsearch 進程
Get-Process | Where-Object {$_.ProcessName -like "*elastic*"}
```

### 方法 3：檢查安裝目錄

常見的安裝位置：
- `C:\Program Files\Elastic\Elasticsearch`
- `C:\elasticsearch`
- `D:\elasticsearch`

## 📦 安裝 Elasticsearch

### 方法 1：使用 ZIP 文件安裝（推薦）

#### 步驟 1：下載 Elasticsearch

1. 訪問 [Elasticsearch 下載頁面](https://www.elastic.co/downloads/elasticsearch)
2. 選擇 Windows 版本（ZIP）
3. 下載最新版本（建議 8.11.0 或更高）

#### 步驟 2：解壓縮

```powershell
# 解壓縮到目標目錄（例如：C:\elasticsearch）
Expand-Archive -Path "elasticsearch-8.11.0-windows-x86_64.zip" -DestinationPath "C:\"
```

#### 步驟 3：配置環境變數（可選）

```powershell
# 設置 JAVA_HOME（如果尚未設置）
# Elasticsearch 8.x 需要 Java 17 或更高版本
$env:JAVA_HOME = "C:\Program Files\Java\jdk-17"

# 添加到 PATH（可選）
$env:PATH += ";C:\elasticsearch\elasticsearch-8.11.0\bin"
```

#### 步驟 4：啟動 Elasticsearch

```powershell
# 進入 Elasticsearch 目錄
cd C:\elasticsearch\elasticsearch-8.11.0

# 啟動 Elasticsearch（前台運行）
.\bin\elasticsearch.bat
```

或者作為服務安裝：

```powershell
# 以管理員身份運行 PowerShell，然後執行：
.\bin\elasticsearch-service.bat install

# 啟動服務
.\bin\elasticsearch-service.bat start
```

### 方法 2：使用 Chocolatey 安裝

```powershell
# 以管理員身份運行
choco install elasticsearch

# 啟動服務
Start-Service elasticsearch
```

### 方法 3：使用 Docker（推薦用於開發）

```powershell
# 拉取 Elasticsearch 鏡像
docker pull docker.elastic.co/elasticsearch/elasticsearch:8.11.0

# 運行容器
docker run -d `
  --name elasticsearch `
  -p 9200:9200 `
  -p 9300:9300 `
  -e "discovery.type=single-node" `
  -e "xpack.security.enabled=false" `
  docker.elastic.co/elasticsearch/elasticsearch:8.11.0
```

## ✅ 驗證安裝

### 檢查 Elasticsearch 是否運行

```powershell
# 測試連接
curl http://localhost:9200

# 應該看到類似以下的 JSON 回應：
# {
#   "name" : "...",
#   "cluster_name" : "elasticsearch",
#   "cluster_uuid" : "...",
#   "version" : {
#     "number" : "8.11.0",
#     ...
#   }
# }
```

### 檢查版本

```powershell
# 獲取版本資訊
$response = Invoke-WebRequest -Uri "http://localhost:9200" -UseBasicParsing
$response.Content | ConvertFrom-Json | Select-Object -ExpandProperty version
```

## 🔧 常見問題

### 問題 1：端口 9200 已被佔用

**解決方法：**

```powershell
# 檢查端口佔用
netstat -ano | findstr :9200

# 終止佔用進程（替換 PID）
taskkill /PID <PID> /F

# 或修改 Elasticsearch 配置
# 編輯 config/elasticsearch.yml，修改：
# http.port: 9201
```

### 問題 2：Java 版本不正確

**檢查 Java 版本：**

```powershell
java -version
```

**要求：**
- Elasticsearch 8.x 需要 Java 17 或更高版本
- Elasticsearch 7.x 需要 Java 11 或更高版本

**安裝 Java：**

```powershell
# 使用 Chocolatey
choco install openjdk17

# 或下載安裝
# https://adoptium.net/
```

### 問題 3：記憶體不足

**解決方法：**

編輯 `config/jvm.options`：

```properties
# 設置堆記憶體（根據系統記憶體調整）
-Xms512m
-Xmx512m
```

### 問題 4：權限問題

**解決方法：**

```powershell
# 以管理員身份運行 PowerShell
# 設置目錄權限
icacls "C:\elasticsearch" /grant Everyone:F /T
```

## 🚀 快速啟動腳本

創建 `start_elasticsearch.ps1`：

```powershell
# start_elasticsearch.ps1
$ES_HOME = "C:\elasticsearch\elasticsearch-8.11.0"

if (Test-Path "$ES_HOME\bin\elasticsearch.bat") {
    Write-Host "啟動 Elasticsearch..." -ForegroundColor Green
    Set-Location $ES_HOME
    Start-Process -FilePath "$ES_HOME\bin\elasticsearch.bat" -WindowStyle Normal
    Write-Host "等待 Elasticsearch 啟動..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    # 測試連接
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:9200" -UseBasicParsing
        Write-Host "✅ Elasticsearch 已成功啟動！" -ForegroundColor Green
        $response.Content | ConvertFrom-Json | Format-List
    } catch {
        Write-Host "⚠️ Elasticsearch 可能還在啟動中，請稍後再試" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ 找不到 Elasticsearch，請檢查安裝路徑" -ForegroundColor Red
}
```

## 📝 下一步

安裝並啟動 Elasticsearch 後：

1. ✅ 驗證 Elasticsearch 運行正常
2. ✅ 安裝 IK Analyzer 插件（參考 `install_ik_analyzer.md`）
3. ✅ 配置應用程式連接 Elasticsearch

## 🔗 相關資源

- [Elasticsearch 官方文檔](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Elasticsearch Windows 安裝指南](https://www.elastic.co/guide/en/elasticsearch/reference/current/zip-windows.html)
- [IK Analyzer 安裝指南](./install_ik_analyzer.md)
