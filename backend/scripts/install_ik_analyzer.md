# Elasticsearch IK Analyzer 安裝指南

## ⚠️ 重要提示

**如果自動安裝失敗**（下載 URL 不存在），請參考：
- `ik_analyzer_solution.md` - 完整的解決方案
- `ik_analyzer_manual_install.md` - 手動安裝方法

**推薦做法**：目前系統已完全支援 MongoDB 搜尋，無需 IK Analyzer 即可正常運作。

## 📋 概述

IK Analyzer 是 Elasticsearch 的中文分詞插件，用於支援中文全文搜尋。本指南提供多種安裝方法。

## 🔍 檢查 Elasticsearch 版本

首先需要確認您的 Elasticsearch 版本：

```bash
curl http://localhost:9200
```

查看返回的 `version.number` 欄位，例如：`"version" : { "number" : "8.11.0" }`

## 📦 方法 1：使用 Elasticsearch Plugin 命令安裝（推薦）

### ⚠️ 重要變更

**Breaking Change**: IK Analyzer 最新版本的插件包不再在 GitHub Releases 頁面發布，請使用新的下載源。

### 步驟 1：使用新的下載源安裝 IK Analyzer

```bash
# 進入 Elasticsearch 安裝目錄
cd /path/to/elasticsearch

# 安裝 IK Analyzer（使用新的下載源）
# 格式：https://get.infini.cloud/elasticsearch/analysis-ik/{版本號}
# 使用 --batch 參數自動確認權限提示
bin/elasticsearch-plugin install --batch https://get.infini.cloud/elasticsearch/analysis-ik/8.11.0
```

**注意**：
- 請將 `8.11.0` 替換為您的 Elasticsearch 版本號
- 新的下載源：`https://get.infini.cloud/elasticsearch/analysis-ik/{版本號}`
- **必須使用 `--batch` 參數**以避免交互式確認提示
- 如果 8.11.0 不可用，可以嘗試較接近的版本（如 8.10.0、8.9.0）

**Windows PowerShell 範例**：
```powershell
cd "D:\Users\Ophelia Chan\Desktop\elasticsearch-8.11.0"
.\bin\elasticsearch-plugin.bat install --batch https://get.infini.cloud/elasticsearch/analysis-ik/8.11.0
```

### 步驟 2：重啟 Elasticsearch

```bash
# 停止 Elasticsearch
# 然後重新啟動
bin/elasticsearch
```

### 步驟 3：驗證安裝

```bash
# 檢查已安裝的插件
bin/elasticsearch-plugin list

# 應該看到：analysis-ik
```

## 📦 方法 2：手動安裝（適用於無法訪問 GitHub 的情況）

### 步驟 1：下載 IK Analyzer

訪問 [IK Analyzer Releases](https://github.com/medcl/elasticsearch-analysis-ik/releases)

下載對應版本的 ZIP 文件，例如：
- Elasticsearch 8.11.0 → `elasticsearch-analysis-ik-8.11.0.zip`
- Elasticsearch 7.17.0 → `elasticsearch-analysis-ik-7.17.0.zip`

### 步驟 2：安裝插件

```bash
# 進入 Elasticsearch 安裝目錄
cd /path/to/elasticsearch

# 使用本地文件安裝
bin/elasticsearch-plugin install file:///path/to/elasticsearch-analysis-ik-8.11.0.zip
```

### 步驟 3：重啟 Elasticsearch

```bash
bin/elasticsearch
```

## 📦 方法 3：Docker 環境安裝

如果您使用 Docker 運行 Elasticsearch：

### 方法 A：構建自定義鏡像

創建 `Dockerfile`：

```dockerfile
FROM docker.elastic.co/elasticsearch/elasticsearch:8.11.0

RUN bin/elasticsearch-plugin install --batch https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v8.11.0/elasticsearch-analysis-ik-8.11.0.zip
```

構建並運行：

```bash
docker build -t elasticsearch-ik:8.11.0 .
docker run -p 9200:9200 -p 9300:9300 elasticsearch-ik:8.11.0
```

### 方法 B：使用 Docker Compose

創建 `docker-compose.yml`：

```yaml
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    container_name: elasticsearch
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
      - "9300:9300"
    volumes:
      - es_data:/usr/share/elasticsearch/data
    command: >
      bash -c "
        bin/elasticsearch-plugin install --batch https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v8.11.0/elasticsearch-analysis-ik-8.11.0.zip &&
        /usr/local/bin/docker-entrypoint.sh
      "

volumes:
  es_data:
```

運行：

```bash
docker-compose up -d
```

## 🧪 驗證 IK Analyzer 是否正常工作

### 測試 1：檢查插件列表

```bash
curl http://localhost:9200/_cat/plugins
```

應該看到 `analysis-ik` 插件。

### 測試 2：測試中文分詞

```bash
curl -X POST "http://localhost:9200/_analyze" -H 'Content-Type: application/json' -d'
{
  "analyzer": "ik_max_word",
  "text": "中華人民共和國"
}'
```

預期結果應該將「中華人民共和國」分解為多個詞彙。

### 測試 3：測試搜尋功能

```bash
curl -X POST "http://localhost:9200/test_index/_analyze" -H 'Content-Type: application/json' -d'
{
  "analyzer": "ik_smart",
  "text": "我愛北京天安門"
}'
```

## 🔧 IK Analyzer 配置選項

IK Analyzer 提供兩種分析器：

1. **ik_max_word**：細粒度分詞（會將文本做最細粒度的拆分）
   - 適合：索引時使用
   - 範例：「中華人民共和國」→「中華」、「人民」、「共和國」、「中華人民」、「人民共和國」等

2. **ik_smart**：智能分詞（會做最粗粒度的拆分）
   - 適合：搜尋時使用
   - 範例：「中華人民共和國」→「中華人民共和國」

## 📝 自定義詞典（可選）

如果需要添加自定義詞彙，可以編輯：

```
elasticsearch/config/analysis-ik/IKAnalyzer.cfg.xml
```

添加自定義詞典：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE properties SYSTEM "http://java.sun.com/dtd/properties.dtd">
<properties>
    <comment>IK Analyzer 擴展配置</comment>
    <!-- 自定義詞典 -->
    <entry key="ext_dict">custom_dict.dic</entry>
    <!-- 自定義停用詞 -->
    <entry key="ext_stopwords">custom_stopwords.dic</entry>
</properties>
```

然後在 `elasticsearch/config/analysis-ik/` 目錄下創建對應的 `.dic` 文件。

## 🐛 常見問題

### 問題 1：插件安裝失敗

**錯誤**：`Plugin [analysis-ik] is incompatible with Elasticsearch [8.11.0]`

**解決**：確保下載的 IK Analyzer 版本與 Elasticsearch 版本完全匹配。

### 問題 2：無法訪問 GitHub

**解決**：使用手動安裝方法（方法 2），或使用代理。

### 問題 3：Docker 容器重啟後插件消失

**解決**：使用 Docker Volume 持久化插件目錄，或構建自定義鏡像。

### 問題 4：分詞結果不理想

**解決**：
1. 嘗試切換 `ik_max_word` 和 `ik_smart`
2. 添加自定義詞典
3. 調整 IK Analyzer 配置

## 📚 參考資料

- [IK Analyzer GitHub](https://github.com/medcl/elasticsearch-analysis-ik)
- [IK Analyzer Releases](https://github.com/medcl/elasticsearch-analysis-ik/releases)
- [Elasticsearch Plugin 文檔](https://www.elastic.co/guide/en/elasticsearch/plugins/current/index.html)

## ✅ 安裝完成後

安裝完成後，您的應用程式會自動使用 IK Analyzer 進行中文分詞。確保：

1. ✅ Elasticsearch 已重啟
2. ✅ IK Analyzer 插件已安裝並驗證
3. ✅ 應用程式配置中 `ELASTICSEARCH_ENABLED=true`
4. ✅ 應用程式已重新啟動

然後測試搜尋功能，應該可以看到更好的中文搜尋效果！

