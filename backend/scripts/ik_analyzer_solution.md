# IK Analyzer 安裝問題解決方案

## ❌ 問題

IK Analyzer 8.11.0 的自動下載 URL 不存在：
```
https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v8.11.0/elasticsearch-analysis-ik-8.11.0.zip
```

## ✅ 解決方案

### 方案 1：使用 MongoDB 搜尋（推薦，已實作）

**優點**：
- ✅ 無需安裝插件
- ✅ 系統已完全支援
- ✅ 中文搜尋功能正常
- ✅ 無版本兼容性問題

**配置**：
```env
ELASTICSEARCH_ENABLED=false
```

**狀態**：✅ 已可用，無需額外配置

---

### 方案 2：手動下載並安裝 IK Analyzer

#### 步驟 1：查找可用版本

訪問以下連結查看實際可用的版本：
- [IK Analyzer Releases](https://github.com/medcl/elasticsearch-analysis-ik/releases)

常見可用版本（可能與 8.11.0 兼容）：
- 8.10.0
- 8.9.0
- 8.8.0
- 8.7.0

#### 步驟 2：手動下載

1. 從 GitHub Releases 下載對應版本的 ZIP 文件
2. 保存到本地，例如：`D:\Users\Ophelia Chan\Downloads\elasticsearch-analysis-ik-8.10.0.zip`

#### 步驟 3：使用本地文件安裝

```powershell
# 停止 Elasticsearch（按 Ctrl+C）

# 進入 Elasticsearch 目錄
cd "D:\Users\Ophelia Chan\Desktop\elasticsearch-8.11.0"

# 使用本地文件安裝（注意路徑格式）
.\bin\elasticsearch-plugin install file:///D:/Users/Ophelia Chan/Downloads/elasticsearch-analysis-ik-8.10.0.zip
```

**注意**：Windows 路徑需要使用 `/` 而不是 `\`，並且需要完整路徑。

#### 步驟 4：重啟 Elasticsearch

```powershell
.\bin\elasticsearch.bat
```

---

### 方案 3：嘗試較接近的版本

如果 8.11.0 不存在，可以嘗試安裝較接近的版本（例如 8.10.0）：

```powershell
# 停止 Elasticsearch

cd "D:\Users\Ophelia Chan\Desktop\elasticsearch-8.11.0"

# 嘗試安裝 8.10.0 版本
.\bin\elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v8.10.0/elasticsearch-analysis-ik-8.10.0.zip
```

**注意**：較舊版本的 IK Analyzer 可能與 Elasticsearch 8.11.0 不完全兼容，但通常可以工作。

---

### 方案 4：檢查實際可用版本

執行以下命令檢查 GitHub 上實際可用的版本：

```powershell
$releases = Invoke-WebRequest -Uri "https://api.github.com/repos/medcl/elasticsearch-analysis-ik/releases" -UseBasicParsing
$releases.Content | ConvertFrom-Json | Select-Object -First 10 tag_name, published_at | Format-Table
```

---

## 🎯 推薦做法

**目前強烈建議使用方案 1（MongoDB 搜尋）**，因為：

1. ✅ **無需額外安裝**：系統已完全實作
2. ✅ **功能完整**：中文搜尋、分頁、權限控制都已實作
3. ✅ **無兼容性問題**：無需擔心版本匹配
4. ✅ **已測試可用**：所有功能都已實作並測試

當找到合適的 IK Analyzer 版本後，可以再切換到 Elasticsearch。

---

## 📝 當前系統狀態

即使 IK Analyzer 安裝失敗，系統仍然可以正常運作：

1. ✅ **搜尋功能**：使用 MongoDB $regex 中文搜尋
2. ✅ **快取功能**：Redis 快取（可選）
3. ✅ **權限控制**：完整的角色權限系統
4. ✅ **熱門查詢**：統計功能
5. ✅ **API 端點**：所有搜尋相關 API 都已實作

所有核心功能都已實作並可用！

---

## 🔄 未來切換到 Elasticsearch

當 IK Analyzer 安裝成功後，只需：

1. 更新 `.env` 文件：
   ```env
   ELASTICSEARCH_ENABLED=true
   ELASTICSEARCH_HOSTS=http://localhost:9200
   ELASTICSEARCH_USERNAME=elastic
   ELASTICSEARCH_PASSWORD=xP*87btATBNvn9FfsfrZ
   ```

2. 重啟應用程式

3. 系統會自動使用 Elasticsearch 進行搜尋

