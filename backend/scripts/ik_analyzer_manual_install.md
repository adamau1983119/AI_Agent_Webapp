# IK Analyzer 手動安裝指南

## ❌ 自動安裝失敗

IK Analyzer 8.11.0 的自動下載 URL 不存在。以下是手動安裝方法。

## 📦 方法 1：手動下載並安裝

### 步驟 1：下載 IK Analyzer

1. 訪問 [IK Analyzer GitHub Releases](https://github.com/medcl/elasticsearch-analysis-ik/releases)
2. 查找與 Elasticsearch 8.11.0 兼容的版本（通常是 8.x 版本）
3. 下載對應的 ZIP 文件，例如：
   - `elasticsearch-analysis-ik-8.11.0.zip`（如果有）
   - 或 `elasticsearch-analysis-ik-8.10.0.zip`（較接近的版本）

### 步驟 2：手動安裝

```powershell
# 進入 Elasticsearch 目錄
cd "D:\Users\Ophelia Chan\Desktop\elasticsearch-8.11.0"

# 使用本地文件安裝（替換為您下載的文件路徑）
.\bin\elasticsearch-plugin install file:///D:/Users/Ophelia Chan/Downloads/elasticsearch-analysis-ik-8.11.0.zip
```

**注意**：Windows 路徑格式需要使用 `/` 而不是 `\`，並且需要完整路徑。

### 步驟 3：重啟 Elasticsearch

```powershell
.\bin\elasticsearch.bat
```

---

## 📦 方法 2：檢查可用版本

訪問以下連結查看實際可用的版本：

- [IK Analyzer Releases](https://github.com/medcl/elasticsearch-analysis-ik/releases)
- [IK Analyzer 官方倉庫](https://github.com/medcl/elasticsearch-analysis-ik)

常見可用版本：
- 8.10.0
- 8.9.0
- 8.8.0
- 8.7.0

可以嘗試安裝較接近的版本（例如 8.10.0）：

```powershell
.\bin\elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v8.10.0/elasticsearch-analysis-ik-8.10.0.zip
```

---

## 📦 方法 3：使用 MongoDB 搜尋（推薦）

如果 IK Analyzer 安裝困難，建議使用 MongoDB 搜尋：

**優點**：
- ✅ 無需安裝插件
- ✅ 系統已完全支援
- ✅ 中文搜尋功能正常
- ✅ 無版本兼容性問題

**配置**：
```env
ELASTICSEARCH_ENABLED=false
```

---

## 🔍 檢查當前可用版本

執行以下命令檢查 GitHub 上實際可用的版本：

```powershell
# 使用 curl 檢查 GitHub API
curl https://api.github.com/repos/medcl/elasticsearch-analysis-ik/releases | ConvertFrom-Json | Select-Object -First 10 tag_name, published_at
```

---

## ✅ 推薦方案

**目前建議使用 MongoDB 搜尋**，因為：
1. ✅ 無需額外安裝
2. ✅ 功能完整
3. ✅ 已測試可用
4. ✅ 無版本兼容性問題

當找到合適的 IK Analyzer 版本後，可以再切換到 Elasticsearch。

