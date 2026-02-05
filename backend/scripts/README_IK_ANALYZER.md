# IK Analyzer 快速安裝指南

## 🚀 快速開始

### Windows (PowerShell)

```powershell
# 1. 進入 scripts 目錄
cd backend/scripts

# 2. 運行安裝檢查腳本
.\install_ik_analyzer.ps1

# 3. 按照提示安裝 IK Analyzer
```

### Linux/macOS

```bash
# 1. 進入 scripts 目錄
cd backend/scripts

# 2. 運行安裝檢查腳本
chmod +x install_ik_analyzer.sh
./install_ik_analyzer.sh

# 3. 按照提示安裝 IK Analyzer
```

## 📋 安裝步驟

### 方法 1：使用 Elasticsearch Plugin 命令（推薦）

1. **確認 Elasticsearch 版本**
   ```bash
   curl http://localhost:9200
   ```

2. **安裝 IK Analyzer**
   ```bash
   # 進入 Elasticsearch 安裝目錄
   cd /path/to/elasticsearch
   
   # 安裝插件（替換版本號）
   bin/elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v8.11.0/elasticsearch-analysis-ik-8.11.0.zip
   ```

3. **重啟 Elasticsearch**
   ```bash
   # 停止 Elasticsearch，然後重新啟動
   bin/elasticsearch
   ```

4. **驗證安裝**
   ```bash
   # 檢查插件列表
   bin/elasticsearch-plugin list
   
   # 應該看到: analysis-ik
   ```

### 方法 2：Docker 環境

如果您使用 Docker 運行 Elasticsearch：

```bash
# 在容器中安裝
docker exec -it <container_name> bin/elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v8.11.0/elasticsearch-analysis-ik-8.11.0.zip

# 重啟容器
docker restart <container_name>
```

## 🧪 測試 IK Analyzer

### 使用測試腳本

```bash
# Python 測試腳本
python backend/scripts/test_ik_analyzer.py

# 或指定 Elasticsearch 主機
python backend/scripts/test_ik_analyzer.py http://localhost:9200
```

### 手動測試

```bash
# 測試 ik_max_word（細粒度分詞）
curl -X POST "http://localhost:9200/_analyze" -H 'Content-Type: application/json' -d'
{
  "analyzer": "ik_max_word",
  "text": "中華人民共和國"
}'

# 測試 ik_smart（智能分詞）
curl -X POST "http://localhost:9200/_analyze" -H 'Content-Type: application/json' -d'
{
  "analyzer": "ik_smart",
  "text": "我愛北京天安門"
}'
```

## ✅ 驗證安裝成功

安裝成功後，您應該看到：

1. ✅ 插件列表中包含 `analysis-ik`
2. ✅ 測試分詞返回多個詞彙
3. ✅ 應用程式日誌顯示 "IK Analyzer 正常工作"

## 📚 詳細文檔

更多詳細資訊請參考：
- `backend/scripts/install_ik_analyzer.md` - 完整安裝指南
- [IK Analyzer GitHub](https://github.com/medcl/elasticsearch-analysis-ik)

## 🔧 常見問題

### Q: 如何知道需要安裝哪個版本？

A: IK Analyzer 版本必須與 Elasticsearch 版本完全匹配。運行 `curl http://localhost:9200` 查看版本號。

### Q: 安裝後需要重啟 Elasticsearch 嗎？

A: 是的，安裝插件後必須重啟 Elasticsearch 才能生效。

### Q: Docker 容器重啟後插件消失？

A: 使用 Docker Volume 持久化插件目錄，或構建自定義鏡像。

### Q: 如何卸載 IK Analyzer？

A: `bin/elasticsearch-plugin remove analysis-ik`

## 🎯 下一步

安裝完成後：

1. ✅ 確保 `ELASTICSEARCH_ENABLED=true` 在 `.env` 文件中
2. ✅ 重啟應用程式
3. ✅ 測試搜尋功能，應該看到更好的中文搜尋效果

