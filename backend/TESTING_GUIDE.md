# 🧪 測試指南 - 內容生成與圖片提取

## ✅ 測試結果確認

根據剛才的測試，以下功能已正常工作：

### 1. RSS Feed 收集功能 ✅
- ✅ 成功從 FASHION 類別收集主題
- ✅ 成功提取原文圖片（4 張）
- ✅ 成功提取原文內容（2542 字）
- ✅ 成功檢測語言和風格

### 2. 文章提取器 ✅
- ✅ 成功提取文章圖片（5 張）
- ✅ 成功提取文章內容（2278 字）
- ✅ 成功檢測語言和風格

## 🚀 啟動服務進行完整測試

### 步驟 1：啟動後端服務（端口 8000）

**方法 1：使用啟動腳本**
```powershell
.\啟動後端服務器.ps1
```

**方法 2：手動啟動**
```powershell
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**成功標誌：**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

### 步驟 2：啟動前端服務（端口 3000 或 5173）

**檢查前端配置：**
```powershell
cd frontend
npm run dev
```

**注意：** 前端可能運行在端口 3000 或 5173，請檢查終端輸出。

### 步驟 3：測試 API 端點

#### 3.1 健康檢查
```bash
curl http://localhost:8000/health
```

#### 3.2 收集主題（FASHION）
```bash
curl -X POST "http://localhost:8000/api/v1/topics/collect" \
  -H "Content-Type: application/json" \
  -d '{"category": "fashion", "count": 1}'
```

#### 3.3 生成今日主題
```bash
curl -X POST "http://localhost:8000/api/v1/schedules/generate-today" \
  -H "Content-Type: application/json"
```

#### 3.4 生成內容（需要先有主題）
```bash
curl -X POST "http://localhost:8000/api/v1/contents/generate" \
  -H "Content-Type: application/json" \
  -d '{"topic_id": "YOUR_TOPIC_ID"}'
```

### 步驟 4：在前端測試

1. **訪問前端頁面**
   - http://localhost:3000 或 http://localhost:5173

2. **測試功能**
   - 點擊「生成今日主題」按鈕
   - 查看生成的主題是否包含：
     - ✅ 原文連結
     - ✅ 原文圖片
     - ✅ 中文標題和摘要

3. **生成內容**
   - 選擇一個主題
   - 點擊「生成內容」
   - 檢查生成的內容是否：
     - ✅ 引用原文連結
     - ✅ 顯示原文圖片
     - ✅ 基於原文內容改寫（非無中生有）

## 📊 預期結果

### 主題收集結果應包含：
```json
{
  "title": "中文標題",
  "description": "30字摘要",
  "sources": [{
    "url": "原文連結",
    "images": ["圖片URL1", "圖片URL2", ...],
    "original_content": "原文內容",
    "language": "en",
    "style": {
      "tone": "neutral",
      "structure": "short_paragraphs",
      "vocabulary": "professional_terms"
    }
  }]
}
```

### 內容生成結果應包含：
```json
{
  "article": "基於原文改寫的中文文章（引用原文連結）",
  "source_urls": ["原文連結"],
  "source_images": ["原文圖片URL1", "原文圖片URL2", ...],
  "images": [
    {
      "url": "圖片URL",
      "image_type": "source",  // 原文圖片
      "source": "Source Article"
    },
    {
      "url": "圖片URL",
      "image_type": "matched",  // 匹配的圖片
      "source": "Unsplash"
    }
  ]
}
```

## 🔍 檢查清單

- [ ] 後端服務運行在 http://localhost:8000
- [ ] 前端服務運行在 http://localhost:3000（或 5173）
- [ ] 可以訪問 http://localhost:8000/docs 查看 API 文檔
- [ ] 可以訪問 http://localhost:8000/health 檢查健康狀態
- [ ] 主題收集功能正常
- [ ] 內容生成功能正常
- [ ] 圖片提取功能正常
- [ ] 生成的內容包含原文連結
- [ ] 生成的內容包含原文圖片
- [ ] 圖片類型正確區分（source/matched）

## 🐛 常見問題

### 問題 1：後端無法啟動
**解決方案：**
- 檢查 MongoDB 是否運行
- 檢查端口 8000 是否被占用
- 檢查 `.env` 文件配置

### 問題 2：無法收集主題
**解決方案：**
- 檢查網路連接
- 檢查 RSS Feed 是否可訪問
- 查看後端日誌錯誤訊息

### 問題 3：無法提取圖片
**解決方案：**
- 檢查目標網站是否允許爬蟲
- 某些網站可能需要特殊處理（如 NYT、WSJ 需要訂閱）

### 問題 4：內容生成失敗
**解決方案：**
- 檢查 AI API Key 是否配置
- 檢查 MongoDB 連接
- 查看後端日誌錯誤訊息

## 📝 測試腳本

已創建測試腳本 `backend/test_content_generation.py`，可以隨時運行：

```powershell
cd backend
.\venv\Scripts\python.exe test_content_generation.py
```

這個腳本會測試：
1. RSS Feed 收集功能
2. 文章提取器功能
3. 後端 API 連接（如果服務運行中）

