# Elasticsearch 9.2.4 IK Analyzer 安裝指南

## 📋 快速安裝步驟

### 步驟 1：啟動 Elasticsearch

在 PowerShell 中執行：

```powershell
# 進入 Elasticsearch 目錄（請替換為您的實際路徑）
cd "D:\Users\Ophelia Chan\elasticsearch-9.2.4"

# 啟動 Elasticsearch
.\bin\elasticsearch.bat
```

**注意**：保持這個 PowerShell 窗口打開，Elasticsearch 會持續運行。

### 步驟 2：驗證 Elasticsearch 運行

打開**另一個** PowerShell 窗口，執行：

```powershell
curl http://localhost:9200
```

如果看到 JSON 回應，表示 Elasticsearch 已成功啟動。

### 步驟 3：安裝 IK Analyzer

**重要**：Elasticsearch 9.2.4 是較新版本，IK Analyzer 可能還沒有官方 9.2.4 版本。

#### 選項 A：使用最新可用版本（推薦）

IK Analyzer 通常支援多個 Elasticsearch 版本。可以嘗試使用 8.x 版本：

```powershell
# 在 Elasticsearch 目錄中執行
.\bin\elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v8.11.0/elasticsearch-analysis-ik-8.11.0.zip
```

#### 選項 B：檢查是否有 9.2.4 版本

訪問 [IK Analyzer Releases](https://github.com/medcl/elasticsearch-analysis-ik/releases) 查看是否有 9.2.4 版本。

如果有，使用：

```powershell
.\bin\elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v9.2.4/elasticsearch-analysis-ik-9.2.4.zip
```

### 步驟 4：重啟 Elasticsearch

1. 在運行 Elasticsearch 的 PowerShell 窗口中按 `Ctrl+C` 停止
2. 重新啟動：

```powershell
.\bin\elasticsearch.bat
```

### 步驟 5：驗證 IK Analyzer 安裝

```powershell
# 檢查已安裝的插件
.\bin\elasticsearch-plugin list

# 應該看到：analysis-ik
```

### 步驟 6：測試中文分詞

```powershell
curl -X POST "http://localhost:9200/_analyze" -H 'Content-Type: application/json' -d'{\"analyzer\": \"ik_max_word\", \"text\": \"中華人民共和國\"}'
```

## 🔧 如果版本不匹配

如果 IK Analyzer 8.11.0 與 Elasticsearch 9.2.4 不兼容，可以：

1. **降級 Elasticsearch** 到 8.11.0（推薦）
2. **等待 IK Analyzer 9.2.4 版本發布**
3. **使用 MongoDB 搜尋**（系統已支援，無需 Elasticsearch）

## 📝 完整命令序列

```powershell
# 1. 進入 Elasticsearch 目錄
cd "D:\Users\Ophelia Chan\elasticsearch-9.2.4"

# 2. 啟動 Elasticsearch（第一個窗口）
.\bin\elasticsearch.bat

# 3. 打開另一個 PowerShell，安裝 IK Analyzer
cd "D:\Users\Ophelia Chan\elasticsearch-9.2.4"
.\bin\elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v8.11.0/elasticsearch-analysis-ik-8.11.0.zip

# 4. 停止並重啟 Elasticsearch（在第一個窗口中按 Ctrl+C，然後重新運行）
.\bin\elasticsearch.bat

# 5. 驗證安裝
.\bin\elasticsearch-plugin list
```

## ✅ 安裝完成後

1. 在 `.env` 文件中啟用 Elasticsearch：
   ```env
   ELASTICSEARCH_ENABLED=true
   ELASTICSEARCH_HOSTS=http://localhost:9200
   ELASTICSEARCH_INDEX=topics
   ```

2. 重啟應用程式

3. 測試搜尋功能

