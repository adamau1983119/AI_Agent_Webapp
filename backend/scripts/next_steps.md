# 下一步操作指南

## ✅ 已完成

1. ✅ IK Analyzer 已安裝
2. ✅ Elasticsearch 已啟動並運行
3. ✅ 應用程式已更新以支援 HTTPS
4. ✅ .env 文件已更新

## 📋 下一步操作

### 步驟 1：測試 Elasticsearch 連接

執行測試腳本：

```powershell
cd "F:\Adam 2025\Myproject\AI_Agent_Wbbapp_for_Social_Media_Content_Generation"
python backend/scripts/test_https_connection.py
```

**預期結果**：
- ✅ Connection successful
- ✅ IK Analyzer is working
- ✅ Health status: GREEN

### 步驟 2：重啟應用程式

如果測試成功，重啟您的 FastAPI 應用程式：

```powershell
# 如果使用 uvicorn
cd backend
uvicorn app.main:app --reload

# 或使用其他啟動方式
python -m app.main
```

### 步驟 3：驗證搜尋功能

應用程式啟動後，測試搜尋 API：

```bash
# 測試搜尋端點
curl -X GET "http://localhost:8000/api/v1/topics/search?q=測試&page=1&limit=10" \
  -H "X-User-Role: user"
```

### 步驟 4：檢查日誌

查看應用程式日誌，確認：
- ✅ Elasticsearch 連接成功
- ✅ IK Analyzer 正常工作
- ✅ 索引已創建

## 🔍 故障排除

### 問題 1：連接失敗

**症狀**：測試腳本顯示連接失敗

**解決方案**：
1. 確認 Elasticsearch 正在運行
2. 檢查 `.env` 文件配置是否正確
3. 確認用戶名和密碼正確
4. 查看 Elasticsearch 日誌

### 問題 2：IK Analyzer 未工作

**症狀**：連接成功但 IK Analyzer 測試失敗

**解決方案**：
1. 確認 IK Analyzer 插件已安裝：`.\bin\elasticsearch-plugin list`
2. 重啟 Elasticsearch
3. 檢查 Elasticsearch 日誌

### 問題 3：SSL 證書錯誤

**症狀**：SSL 證書驗證失敗

**解決方案**：
- 開發環境：應用程式已配置為不驗證證書（`verify_certs=False`）
- 如果仍有問題，檢查 Elasticsearch SSL 配置

## 📝 配置檢查清單

- [ ] Elasticsearch 正在運行
- [ ] .env 文件已更新
- [ ] ELASTICSEARCH_ENABLED=true
- [ ] ELASTICSEARCH_HOSTS=https://localhost:9200
- [ ] ELASTICSEARCH_USERNAME=elastic
- [ ] ELASTICSEARCH_PASSWORD 已設置
- [ ] 測試連接成功
- [ ] 應用程式已重啟

## 🎯 成功標誌

當一切正常時，您應該看到：

1. **應用程式啟動日誌**：
   ```
   ✅ Elasticsearch 連接成功: elasticsearch
   ✅ IK Analyzer 插件已安裝
   ✅ IK Analyzer 正常工作
   ✅ 創建 Elasticsearch 索引: topics
   ```

2. **搜尋功能正常**：
   - 可以搜尋中文內容
   - 搜尋結果包含相關度分數
   - 分頁功能正常

3. **自動回退機制**：
   - 如果 Elasticsearch 不可用，自動使用 MongoDB 搜尋
   - 不會影響應用程式運行

## 📚 參考文檔

- `backend/scripts/update_env_https.md` - HTTPS 配置詳情
- `backend/scripts/test_https_connection.py` - 連接測試腳本
- `backend/scripts/install_ik_analyzer.md` - IK Analyzer 安裝指南

