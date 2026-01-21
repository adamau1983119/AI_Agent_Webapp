# IK Analyzer 快速啟動指南

## ✅ 已完成

- ✅ IK Analyzer 已安裝到 Elasticsearch 8.11.0
- ✅ 插件驗證：`analysis-ik` 已安裝

## 📋 下一步操作

### 步驟 1：啟動 Elasticsearch

打開新的 PowerShell 窗口，執行：

```powershell
cd "D:\Users\Ophelia Chan\Desktop\elasticsearch-8.11.0"
.\bin\elasticsearch.bat
```

**等待啟動完成**（約 30-60 秒），看到以下訊息表示啟動成功：
```
[INFO ][o.e.n.Node ] [KCS_PC02] started
```

### 步驟 2：測試 IK Analyzer

在另一個 PowerShell 窗口中，執行測試腳本：

```powershell
cd "F:\Adam 2025\Myproject\AI_Agent_Wbbapp_for_Social_Media_Content_Generation"
.\backend\scripts\start_elasticsearch_and_test.ps1
```

或手動測試：

```powershell
$password = "xP*87btATBNvn9FfsfrZ"
$credential = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("elastic:$password"))

curl -X POST "http://localhost:9200/_analyze?pretty" `
  -H "Authorization: Basic $credential" `
  -H "Content-Type: application/json" `
  -d '{"analyzer": "ik_max_word", "text": "中華人民共和國"}'
```

### 步驟 3：更新 .env 文件

在 `backend` 目錄下找到或創建 `.env` 文件，添加：

```env
ELASTICSEARCH_ENABLED=true
ELASTICSEARCH_HOSTS=http://localhost:9200
ELASTICSEARCH_INDEX=topics
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=xP*87btATBNvn9FfsfrZ
ELASTICSEARCH_TIMEOUT=30
ELASTICSEARCH_MAX_RETRIES=3
```

### 步驟 4：重啟應用程式

重啟 FastAPI 應用程式，系統會自動使用 Elasticsearch 進行中文全文搜尋。

## 🎯 驗證清單

- [ ] Elasticsearch 已啟動
- [ ] IK Analyzer 測試通過
- [ ] .env 文件已更新
- [ ] 應用程式已重啟
- [ ] 搜尋功能正常

## 📝 重要提示

1. **Elasticsearch 必須運行**才能使用 Elasticsearch 搜尋
2. **如果 Elasticsearch 不可用**，系統會自動回退到 MongoDB 搜尋
3. **密碼請妥善保管**，不要提交到版本控制系統

## 🔧 故障排除

### Elasticsearch 無法啟動
- 檢查端口 9200 是否被占用
- 查看 `logs/elasticsearch.log` 文件

### IK Analyzer 測試失敗
- 確認 Elasticsearch 已完全啟動
- 檢查認證信息是否正確
- 查看 Elasticsearch 日誌

### 應用程式無法連接 Elasticsearch
- 確認 Elasticsearch 正在運行
- 檢查 .env 配置是否正確
- 查看應用程式日誌

