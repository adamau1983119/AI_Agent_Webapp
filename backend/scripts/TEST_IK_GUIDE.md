# IK Analyzer 測試指南

## 📋 測試步驟

### 步驟 1：確認 Elasticsearch 正在運行

Elasticsearch 應該已經在新窗口中啟動。請檢查：

1. **查看 Elasticsearch 窗口**，尋找以下訊息：
   ```
   [INFO ][o.e.n.Node ] [KCS_PC02] started
   ```

2. **或執行檢查命令**：
   ```powershell
   curl http://localhost:9200
   ```
   應該返回 JSON 格式的 Elasticsearch 信息。

### 步驟 2：執行測試腳本

在 PowerShell 中執行：

```powershell
cd "F:\Adam 2025\Myproject\AI_Agent_Wbbapp_for_Social_Media_Content_Generation"
.\backend\scripts\start_and_test_ik.ps1
```

### 步驟 3：手動測試（可選）

如果腳本無法運行，可以手動測試：

```powershell
$password = "xP*87btATBNvn9FfsfrZ"
$credential = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("elastic:$password"))

# 測試 ik_max_word
$body = @{
    analyzer = "ik_max_word"
    text = "test text"
} | ConvertTo-Json

$headers = @{
    "Authorization" = "Basic $credential"
    "Content-Type" = "application/json"
}

curl -X POST "http://localhost:9200/_analyze" `
  -H "Authorization: Basic $credential" `
  -H "Content-Type: application/json" `
  -d $body
```

## ✅ 預期結果

如果 IK Analyzer 正常工作，應該看到：

```json
{
  "tokens": [
    {
      "token": "test",
      "start_offset": 0,
      "end_offset": 4,
      "type": "ENGLISH",
      "position": 0
    },
    {
      "token": "text",
      "start_offset": 5,
      "end_offset": 9,
      "type": "ENGLISH",
      "position": 1
    }
  ]
}
```

## 🔧 故障排除

### 問題 1：Elasticsearch 無法啟動
- 檢查端口 9200 是否被占用
- 查看 Elasticsearch 窗口中的錯誤訊息
- 檢查 Java 版本是否兼容

### 問題 2：IK Analyzer 測試失敗
- 確認 IK Analyzer 插件已安裝：`.\bin\elasticsearch-plugin list`
- 確認 Elasticsearch 已重啟（安裝插件後必須重啟）
- 檢查認證信息是否正確

### 問題 3：認證失敗
- 確認密碼正確：`xP*87btATBNvn9FfsfrZ`
- 確認用戶名正確：`elastic`
- 檢查 Elasticsearch 安全設置

## 📝 下一步

測試成功後：

1. **更新 .env 文件**以啟用 Elasticsearch
2. **重啟應用程式**
3. **測試搜尋功能**

參考：`backend/scripts/QUICK_START.md`

