# 🚀 快速測試指南

## ✅ 當前狀態

根據檢查：
- ✅ 後端服務運行在 http://localhost:8000
- ✅ 前端服務運行在 http://localhost:3000
- ✅ 資料庫連接正常
- ✅ API 健康檢查通過

## 🧪 測試步驟

### 方法 1：通過前端界面測試（推薦）

1. **訪問前端 Dashboard**
   - 打開瀏覽器訪問：http://localhost:3000
   - 你應該看到 Dashboard 界面

2. **生成今日主題**
   - 點擊「今日主題」卡片上的「生成中...」按鈕（紫色按鈕）
   - 系統會開始從 72 個 RSS Feed 收集主題
   - 等待幾秒鐘，主題會自動顯示

3. **檢查生成的主題**
   - 查看「今日主題」區域
   - 每個主題應該包含：
     - ✅ 中文標題
     - ✅ 30 字摘要
     - ✅ 原文連結（點擊可查看）
     - ✅ 原文圖片（會自動顯示）

4. **生成內容**
   - 點擊一個主題卡片
   - 點擊「生成內容」按鈕
   - 檢查生成的內容是否：
     - ✅ 引用原文連結
     - ✅ 顯示原文圖片
     - ✅ 基於原文內容改寫

### 方法 2：通過 API 直接測試

**1. 生成今日主題：**
```bash
curl -X POST "http://localhost:8000/api/v1/schedules/generate-today" \
  -H "Content-Type: application/json" \
  -d "{\"force\": false}"
```

**2. 查看生成的主題：**
```bash
curl "http://localhost:8000/api/v1/topics?limit=10&page=1"
```

**3. 查看特定主題的詳細資訊：**
```bash
curl "http://localhost:8000/api/v1/topics/{topic_id}"
```

**4. 生成內容：**
```bash
curl -X POST "http://localhost:8000/api/v1/contents/generate" \
  -H "Content-Type: application/json" \
  -d "{\"topic_id\": \"YOUR_TOPIC_ID\", \"type\": \"both\"}"
```

## 📊 預期結果

### 主題應包含：
```json
{
  "title": "中文標題",
  "description": "30字摘要",
  "sources": [{
    "url": "https://www.vogue.com/article/...",
    "images": [
      "https://assets.vogue.com/photos/...",
      "https://assets.vogue.com/photos/..."
    ],
    "original_content": "原文內容...",
    "language": "en",
    "style": {
      "tone": "neutral",
      "structure": "short_paragraphs",
      "vocabulary": "professional_terms"
    }
  }]
}
```

### 內容應包含：
```json
{
  "article": "基於原文改寫的中文文章（引用原文連結）...",
  "source_urls": ["https://www.vogue.com/article/..."],
  "source_images": [
    "https://assets.vogue.com/photos/..."
  ],
  "images": [
    {
      "url": "https://assets.vogue.com/photos/...",
      "image_type": "source",
      "source": "Source Article"
    }
  ]
}
```

## 🔍 檢查清單

- [ ] 後端服務運行在 http://localhost:8000
- [ ] 前端服務運行在 http://localhost:3000
- [ ] 可以訪問 http://localhost:8000/docs 查看 API 文檔
- [ ] 點擊「生成中...」按鈕可以生成主題
- [ ] 生成的主題包含原文連結
- [ ] 生成的主題包含原文圖片
- [ ] 生成的內容引用原文連結
- [ ] 生成的內容顯示原文圖片

## 💡 提示

1. **如果「生成中...」按鈕沒有反應：**
   - 檢查瀏覽器控制台是否有錯誤
   - 檢查後端日誌是否有錯誤
   - 確認 MongoDB 連接正常

2. **如果主題生成失敗：**
   - 檢查網路連接
   - 檢查 RSS Feed 是否可訪問
   - 查看後端日誌錯誤訊息

3. **如果圖片不顯示：**
   - 檢查圖片 URL 是否有效
   - 檢查 CORS 設定
   - 檢查圖片代理端點是否正常

4. **如果內容生成失敗：**
   - 檢查 AI API Key 是否配置
   - 檢查 MongoDB 連接
   - 查看後端日誌錯誤訊息

## 🎯 下一步

1. 點擊「生成中...」按鈕生成今日主題
2. 等待主題生成完成（通常需要 1-2 分鐘）
3. 檢查生成的主題是否包含原文連結和圖片
4. 選擇一個主題生成內容
5. 檢查生成的內容是否正確引用原文

