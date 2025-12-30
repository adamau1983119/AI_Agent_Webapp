# CORS 錯誤修復報告

## 🚨 發現的問題

從 Network 標籤可以看到：
1. **CORS 錯誤**: `Access-Control-Allow-Origin` header 缺失
2. **502 Bad Gateway**: Preflight 請求失敗
3. **請求被阻止**: `topics` 和 `schedules` API 請求都被 CORS 阻止

---

## 🔍 問題根源

### 問題 1: CustomCORSMiddleware 實現不完整

**位置**: `backend/app/main.py` 第 46 行

**問題**:
```python
# 設定 CORS header
if  # ❌ 缺少條件判斷
    response.headers["Access-Control-Allow-Origin"] = origin
```

**影響**: CORS header 沒有被正確設定，導致瀏覽器阻止請求

---

### 問題 2: CORS_ORIGINS 可能未正確解析

**可能原因**:
- Railway 環境變數格式不正確
- 解析邏輯有問題
- 允許的來源列表為空

---

### 問題 3: 502 Bad Gateway 錯誤

**可能原因**:
- 後端服務未運行
- Railway 代理層問題
- 中間件順序問題

---

## ✅ 已完成的修復

### 1. 修復 CustomCORSMiddleware

**修復內容**:
- ✅ 補全 `if` 條件判斷
- ✅ 添加完整的 CORS header 設定
- ✅ 添加日誌記錄（調試用）
- ✅ 處理所有邊界情況（無 origin、空列表等）

**新實現**:
```python
class CustomCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        allowed_origins = settings.CORS_ORIGINS
        
        # 正確解析 allowed_origins
        if isinstance(allowed_origins, str):
            allowed_origins = [o.strip() for o in allowed_origins.split(',') if o.strip()]
        
        # 處理 OPTIONS 預檢請求
        if request.method == "OPTIONS":
            response = Response(status_code=200)
            if origin and (origin in allowed_origins or "*" in allowed_origins):
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
                response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-API-Key, Accept"
                response.headers["Access-Control-Allow-Credentials"] = "true"
                response.headers["Access-Control-Max-Age"] = "3600"
            return response
        
        # 處理實際請求
        response = await call_next(request)
        
        # 設定 CORS header
        if origin and (origin in allowed_origins or "*" in allowed_origins):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Expose-Headers"] = "X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset"
        
        return response
```

---

### 2. 改進 CORS 中間件配置

**修復內容**:
- ✅ 確保 `CORS_ORIGINS` 正確解析為列表
- ✅ 添加詳細日誌記錄
- ✅ 改進錯誤處理

---

## 🔧 必須檢查的環境變數

### Railway 後端環境變數

**必須設定**:
```
CORS_ORIGINS=https://ai-agent-webapp-ten.vercel.app,http://localhost:5173,http://localhost:3000
```

**或使用 JSON 格式**:
```
CORS_ORIGINS=["https://ai-agent-webapp-ten.vercel.app","http://localhost:5173","http://localhost:3000"]
```

**檢查步驟**:
1. 訪問 Railway Dashboard
2. 選擇專案：`AI_Agent_Webapp`
3. 點擊服務：`backend`
4. 點擊 "Variables" 標籤
5. 檢查或添加 `CORS_ORIGINS`
6. 保存後，Railway 會自動重新部署

---

## 📋 驗證步驟

### 步驟 1: 檢查後端日誌

在 Railway Dashboard 查看日誌，應該看到：
```
設定 CORS，允許的來源: ['https://ai-agent-webapp-ten.vercel.app', ...]
CORS_ORIGINS 類型: <class 'list'>
解析後的 CORS_ORIGINS: ['https://ai-agent-webapp-ten.vercel.app', ...]
```

### 步驟 2: 測試 CORS

**使用 curl 測試**:
```bash
# 測試 OPTIONS 預檢請求
curl -X OPTIONS \
  -H "Origin: https://ai-agent-webapp-ten.vercel.app" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Content-Type" \
  https://your-backend-domain.railway.app/api/v1/topics \
  -v
```

**應該看到**:
```
< HTTP/1.1 200 OK
< Access-Control-Allow-Origin: https://ai-agent-webapp-ten.vercel.app
< Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
< Access-Control-Allow-Headers: Content-Type, Authorization, X-API-Key, Accept
< Access-Control-Allow-Credentials: true
```

### 步驟 3: 檢查瀏覽器 Network 標籤

**正常情況下應該看到**:
- ✅ `topics?page=1&limit=12` - 狀態 200（不是 CORS 錯誤）
- ✅ `schedules` - 狀態 200（不是 CORS 錯誤）
- ✅ 沒有 502 錯誤

---

## 🚨 如果問題仍然存在

### 檢查 1: Railway 環境變數格式

**錯誤格式**:
```
CORS_ORIGINS=https://ai-agent-webapp-ten.vercel.app  # 缺少逗號分隔
```

**正確格式**:
```
CORS_ORIGINS=https://ai-agent-webapp-ten.vercel.app,http://localhost:5173
```

### 檢查 2: Railway 代理層

如果 Railway 有自己的代理層，可能需要：
1. 檢查 Railway 網路設定
2. 確認沒有額外的 CORS 設定覆蓋應用設定

### 檢查 3: 後端服務狀態

**檢查健康檢查**:
```
https://your-backend-domain.railway.app/health
```

如果返回 502，表示後端服務未運行或 Railway 代理有問題。

---

## 📊 修復前後對比

### 修復前
- ❌ `Access-Control-Allow-Origin` header 缺失
- ❌ 502 Bad Gateway 錯誤
- ❌ 所有 API 請求被 CORS 阻止

### 修復後（預期）
- ✅ `Access-Control-Allow-Origin` header 正確設定
- ✅ 200 OK 響應
- ✅ API 請求成功

---

**報告生成時間**: 2025-12-30  
**狀態**: ✅ **CORS 中間件已修復，需要檢查環境變數**

