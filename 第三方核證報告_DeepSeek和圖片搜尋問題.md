# 第三方核證報告：DeepSeek API 切換與圖片搜尋問題

> **報告日期**：2026-01-06  
> **報告目的**：供第三方技術專家核證問題分析和解決方案  
> **報告狀態**：待第三方核證

---

## 📋 執行摘要

本報告詳細記錄了 AI Agent Webapp 專案中兩個持續存在的問題：
1. **DeepSeek API 無法切換**：即使環境變數已正確設置，系統仍無法使用 DeepSeek API
2. **圖片搜尋無法工作**：所有圖片搜尋服務都無法返回結果

報告包含問題分析、已嘗試的解決方案、建議方案，以及相關代碼證據，供第三方技術專家評估。

---

## 🔍 問題 1：DeepSeek API 無法切換

### 1.1 問題描述

**症狀**：
- 在 Railway 環境變數中設置了 `AI_SERVICE=deepseek` 和 `DEEPSEEK_API_KEY`
- Railway 已重新部署多次
- 環境變數驗證顯示配置正確
- 但系統仍無法使用 DeepSeek API，內容生成功能失敗

**發生時間**：
- 首次發現：2025-12-30
- 持續至今：2026-01-06（已持續 7 天）
- 嘗試次數：根據記錄，已嘗試「無數次」環境變數重置和重啟

### 1.2 已嘗試的解決方案

根據 `2025-12-30_工作記錄.md` 和相關文檔，已嘗試：

#### 方案 A：環境變數重置（已嘗試多次）

**執行內容**：
1. ✅ 在 Railway 設置環境變數：
   - `AI_SERVICE=deepseek`
   - `DEEPSEEK_API_KEY=sk-9995dc68272e4e2b8406af2caa557cb0`
   - `DEEPSEEK_MODEL=deepseek-chat`
   - `DEEPSEEK_BASE_URL=https://api.deepseek.com/v1/chat/completions`

2. ✅ Railway 重新部署：
   - Commit: `1cf7524b`
   - 部署狀態：成功
   - 環境變數驗證：通過

3. ✅ 驗證配置：
   - Railway Logs 顯示：`✅ 環境變數驗證通過`
   - Railway Logs 顯示：`AI 服務: deepseek`

**結果**：❌ 無效 - 問題依然存在

**嘗試次數**：根據用戶反饋，已嘗試「無數次」

#### 方案 B：代碼預設值修改（已執行）

**執行內容**：
- 修改 `backend/app/config.py`：`AI_SERVICE: str = "deepseek"`（從 "qwen" 改為 "deepseek"）
- 修改 `backend/app/api/v1/contents.py`：預設使用 DeepSeek
- 修改 `backend/app/services/ai/ai_service_factory.py`：預設使用 DeepSeek

**結果**：❌ 無效 - 問題依然存在

### 1.3 代碼證據

#### 證據 1：Workflow 代碼狀態（重要發現）

**文件**：`backend/app/services/automation/workflow.py`

**代碼位置**：第 24-39 行、第 157-158 行

**當前代碼**：
```python
class AutomationWorkflow:
    def __init__(self):
        self.topic_repo = TopicRepository()
        self.content_repo = ContentRepository()
        self.image_repo = ImageRepository()
        # 不再在初始化時固定 AI Service，改為動態獲取
        self.image_service = ImageService()
    
    def _get_ai_service(self):
        """
        動態獲取 AI Service（每次調用時獲取最新配置）
        這樣可以支援動態切換 AI Service，無需重啟服務
        
        Returns:
            AI 服務實例
        """
        return AIServiceFactory.get_service(settings.AI_SERVICE)
    
    async def _generate_content(self, topic: Dict[str, Any]) -> None:
        # ...
        # 動態獲取 AI Service（每次調用時獲取最新配置）
        ai_service = self._get_ai_service()  # ← 已正確使用
        # ...
```

**重要發現**：
- ✅ **代碼已經修改過**：`__init__` 中已經移除了 `self.ai_service` 的初始化
- ✅ **已實現動態獲取方法**：`_get_ai_service()` 方法已存在
- ✅ **已正確使用**：`_generate_content` 方法已使用 `self._get_ai_service()`
- ❌ **但問題依然存在**：這說明問題可能不在 `workflow.py`，或者還有其他原因

**可能的其他原因**：
1. **環境變數讀取問題**：`settings.AI_SERVICE` 可能沒有正確讀取 Railway 環境變數
2. **API Key 有效性問題**：DeepSeek API Key 可能無效或過期
3. **服務實例化問題**：`AIServiceFactory.get_service()` 可能返回了錯誤的服務
4. **其他代碼位置**：可能還有其他地方有類似問題（如 `contents.py` API 端點）
5. **服務未重啟**：雖然代碼已修改，但 Railway 服務可能沒有使用最新代碼

#### 證據 2：Scheduler 使用固定的 Workflow 實例

**文件**：`backend/app/services/automation/scheduler.py`

**代碼位置**：約第 24 行

**當前代碼**：
```python
class SchedulerService:
    def __init__(self):
        self.workflow = AutomationWorkflow()  # ← 固定實例
```

**分析**：
- `SchedulerService` 在初始化時創建 `AutomationWorkflow` 實例
- 但 `AutomationWorkflow` 已經實現動態獲取，所以這可能不是問題
- 需要確認 `workflow.process_topic()` 是否正確使用動態獲取

#### 證據 3：API 端點代碼（重要發現）

**文件**：`backend/app/api/v1/contents.py`

**代碼位置**：第 120-138 行

**當前代碼**：
```python
async def generate_content(...):
    # ...
    # 根據配置選擇 AI 服務
    if settings.AI_SERVICE in ["ollama", "ollama_cloud"]:
        from app.services.ai.ollama import OllamaService
        ai_service = OllamaService()
    elif settings.AI_SERVICE == "gemini":
        from app.services.ai.gemini import GeminiService
        ai_service = GeminiService()
    elif settings.AI_SERVICE == "openai":
        from app.services.ai.openai import OpenAIService
        ai_service = OpenAIService()
    elif settings.AI_SERVICE == "deepseek":
        from app.services.ai.deepseek import DeepSeekService
        ai_service = DeepSeekService()
    elif settings.AI_SERVICE == "qwen":
        from app.services.ai.qwen import QwenService
        ai_service = QwenService()
    else:  # 預設使用 DeepSeek
        from app.services.ai.deepseek import DeepSeekService
        ai_service = DeepSeekService()
```

**分析**：
- ✅ **每次請求都重新讀取**：API 端點每次請求時都會重新執行這段代碼
- ✅ **應該會讀取最新配置**：因為每次請求都重新讀取 `settings.AI_SERVICE`
- ⚠️ **但沒有使用 AIServiceFactory**：直接使用 if-elif，而不是統一的 Factory
- ❓ **可能不是問題**：因為每次請求都重新讀取，理論上應該會使用最新配置

**需要驗證**：
- `settings.AI_SERVICE` 是否正確讀取 Railway 環境變數？
- 是否有其他地方有類似問題？

#### 證據 4：AIServiceFactory 實現

**文件**：`backend/app/services/ai/ai_service_factory.py`

**當前代碼**：
```python
class AIServiceFactory:
    @staticmethod
    def get_service(service_name: str = None) -> AIServiceBase:
        service_name = service_name or settings.AI_SERVICE
        
        if service_name not in AI_SERVICES:
            logger.warning(f"未知的 AI 服務: {service_name}，使用預設服務 deepseek")
            service_name = "deepseek"
        
        service_config = AI_SERVICES[service_name]
        # ... 動態載入服務
        return service_class()
```

**分析**：
- ✅ `AIServiceFactory.get_service()` 本身是動態的
- ✅ 每次調用都會重新讀取 `settings.AI_SERVICE`
- ✅ 使用映射表方式，支援動態載入

**結論**：
- AIServiceFactory 實現正確
- 問題可能不在 Factory，而在其他地方

### 1.4 建議方案

#### 方案 1：統一使用 AIServiceFactory（建議）

**發現**：
- `workflow.py` 已使用 `AIServiceFactory.get_service()` ✅
- `contents.py` API 端點使用 if-elif，沒有使用 Factory ⚠️

**修改內容**：
```python
# backend/app/api/v1/contents.py
# 將 if-elif 改為使用 AIServiceFactory

from app.services.ai.ai_service_factory import AIServiceFactory

async def generate_content(...):
    # ...
    # 使用統一的 Factory
    ai_service = AIServiceFactory.get_service(settings.AI_SERVICE)
    # ...
```

**優點**：
- 統一使用 Factory，代碼更一致
- 更容易維護和擴展
- 確保使用相同的邏輯

**缺點**：
- 需要修改代碼
- 但 API 端點每次請求都重新讀取，理論上應該沒問題

**優先級**：🟡 中 - 可能不是根本原因，但建議統一

#### 方案 2：檢查環境變數讀取（最重要）

**問題**：`settings.AI_SERVICE` 可能沒有正確讀取 Railway 環境變數

**關鍵問題**：
- 即使代碼已修改為動態獲取
- 但如果 `settings.AI_SERVICE` 沒有正確讀取環境變數
- 問題依然存在

**檢查點**：
1. Railway 環境變數是否正確設置？
   - 變數名：`AI_SERVICE`
   - 值：`deepseek`（小寫，不是 `DeepSeek` 或 `DEEPSEEK`）
2. `pydantic_settings` 是否正確讀取環境變數？
   - 檢查 `backend/app/config.py` 中的 `Settings` 類
   - 確認 `env_file` 和環境變數讀取邏輯
3. 是否需要重啟服務才能讀取新環境變數？
   - Python 的 `pydantic_settings` 通常在啟動時讀取
   - 環境變數更新後需要重啟服務

**驗證方法**：
```python
# 在代碼中添加日誌
logger.info(f"當前 AI_SERVICE 配置: {settings.AI_SERVICE}")
logger.info(f"當前 DEEPSEEK_API_KEY 是否存在: {bool(settings.DEEPSEEK_API_KEY)}")
```

**檢查 Railway Logs**：
- 查看啟動日誌中的環境變數驗證訊息
- 確認實際使用的服務

**優先級**：🔴 最高 - 這可能是真正的根本原因

#### 方案 3：檢查 API Key 有效性（重要）

**問題**：DeepSeek API Key 可能無效或過期

**檢查點**：
1. API Key 是否正確（格式：`sk-...`）？
2. API Key 是否過期或被禁用？
3. API Key 是否有足夠的配額？

**驗證方法**：
- 直接測試 DeepSeek API
- 檢查 Railway Logs 中的錯誤訊息

**優先級**：🟡 中 - 需要驗證

#### 方案 4：檢查服務部署狀態（重要）

**問題**：代碼已修改，但 Railway 可能沒有使用最新代碼

**檢查點**：
1. Railway 是否使用最新的 commit？
2. 是否需要手動觸發重新部署？
3. 部署是否成功？

**驗證方法**：
- 檢查 Railway Deployments
- 確認使用的 commit hash

**優先級**：🟡 中 - 需要驗證

#### 方案 2：實現配置熱重載（複雜方案）

**修改內容**：
- 實現配置監聽機制
- 環境變數更新時自動重新載入
- 需要實現配置緩存和更新機制

**優點**：
- 真正的動態切換，無需重啟

**缺點**：
- 實現複雜
- 需要額外的配置管理機制
- 可能引入新的問題

**風險評估**：
- **技術風險**：中高 - 需要實現複雜的配置管理
- **功能風險**：中 - 可能引入新的 bug
- **時間成本**：高 - 需要較多開發時間

### 1.5 重要發現總結

**代碼狀態**：
- ✅ `workflow.py` 已修改為動態獲取（`_get_ai_service()`）
- ✅ `contents.py` API 端點每次請求都重新讀取配置
- ✅ `AIServiceFactory` 實現正確

**但問題依然存在**，這說明：
- ❓ 問題可能不在代碼架構
- ❓ 問題可能在環境變數讀取
- ❓ 問題可能在 API Key 有效性
- ❓ 問題可能在服務部署狀態

### 1.6 第三方核證要點

請第三方專家評估：

1. **問題診斷是否正確**？
   - 代碼已經修改為動態獲取，但問題依然存在
   - 這是否說明問題不在代碼架構？
   - 環境變數讀取是否可能是真正的原因？

2. **環境變數讀取問題**？
   - `pydantic_settings` 是否正確讀取 Railway 環境變數？
   - 是否需要重啟服務才能讀取新環境變數？
   - 是否有環境變數名稱大小寫問題？

3. **API Key 有效性問題**？
   - DeepSeek API Key 是否有效？
   - 是否有配額限制？
   - 是否有網路連接問題？

4. **服務部署問題**？
   - Railway 是否使用最新代碼？
   - 部署是否成功？
   - 是否需要手動觸發重新部署？

5. **建議方案是否可行**？
   - 方案 2（檢查環境變數讀取）是否正確？
   - 是否有更好的診斷方法？
   - 是否有其他可能的原因？

---

## 🔍 問題 2：圖片搜尋無法工作

### 2.1 問題描述

**症狀**：
- 所有圖片搜尋請求都返回空結果或錯誤
- 前端顯示「沒有圖片 (0張)」
- API 請求可能返回 500 錯誤或空數組

**發生時間**：
- 持續存在
- 根據記錄，圖片服務 API Key 一直未設定

### 2.2 已嘗試的解決方案

根據記錄：

#### 方案 A：設置圖片服務 API Key（未執行）

**狀態**：⚠️ 未執行 - 根據 `2025-12-30_工作記錄.md`：
```
⚠️ 圖片服務 API Key 未設定（不影響內容生成）
```

**原因**：可能因為：
- 沒有可用的 API Key
- 優先級較低（不影響內容生成）
- 依賴 DuckDuckGo 作為備援（不需要 API Key）

### 2.3 代碼證據

#### 證據 1：ImageServiceManager 備援機制

**文件**：`backend/app/services/images/image_service_manager.py`

**當前代碼**：
```python
class ImageServiceManager:
    def __init__(self):
        self.unsplash = UnsplashService()
        self.pexels = PexelsService()
        self.pixabay = PixabayService()
        self.google_custom_search = GoogleCustomSearchService()
        self.duckduckgo = DuckDuckGoService()  # 無需 API Key 的備援服務
        
        self.services = [
            ("Unsplash", self.unsplash, ImageSource.UNSPLASH),
            ("Pexels", self.pexels, ImageSource.PEXELS),
            ("Pixabay", self.pixabay, ImageSource.PIXABAY),
            ("Google Custom Search", self.google_custom_search, ImageSource.GOOGLE_CUSTOM_SEARCH),
            ("DuckDuckGo", self.duckduckgo, ImageSource.DUCKDUCKGO),  # 最後備援
        ]
    
    async def search_images(self, keywords, source=None, page=1, limit=20):
        # ... 按優先順序嘗試各個服務
        # 如果所有 API 服務都失敗，嘗試使用 DuckDuckGo
        try:
            images = await self.duckduckgo.search_images(keywords, page, limit)
            return images
        except Exception as e:
            logger.error(f"DuckDuckGo 搜尋也失敗: {e}")
            raise ValueError("所有圖片服務都失敗，包括不需要 API Key 的 DuckDuckGo")
```

**分析**：
- 代碼有完整的備援機制
- DuckDuckGo 作為最後備援（不需要 API Key）
- 如果 DuckDuckGo 也失敗，說明有其他問題

#### 證據 2：環境變數配置

**文件**：`backend/app/config.py`

**當前代碼**：
```python
# 圖片服務配置
UNSPLASH_ACCESS_KEY: str = ""
PEXELS_API_KEY: str = ""
PIXABAY_API_KEY: str = ""

# Google Custom Search API（可選，需要 API Key）
GOOGLE_API_KEY: str = ""
GOOGLE_SEARCH_ENGINE_ID: str = ""
```

**分析**：
- 所有圖片服務 API Key 預設為空字串
- 如果未設置，對應服務會跳過

### 2.4 可能的原因

1. **所有 API Key 都未設置**
   - Unsplash、Pexels、Pixabay、Google Custom Search 都需要 API Key
   - 如果都未設置，會跳過這些服務

2. **DuckDuckGo 備援也失敗**
   - DuckDuckGo 不需要 API Key，理論上應該可用
   - 如果也失敗，可能原因：
     - 網路問題
     - DuckDuckGo 服務變更
     - 請求格式問題
     - 代碼實現問題

3. **錯誤被吞掉**
   - 錯誤可能只記錄在日誌中
   - 前端看不到具體錯誤原因

### 2.5 建議方案

#### 方案 1：設置至少一個圖片服務 API Key（推薦）

**執行內容**：
1. 獲取 Google Custom Search API Key（推薦，因為代碼已支持）
2. 在 Railway 設置：
   - `GOOGLE_API_KEY=你的API Key`
   - `GOOGLE_SEARCH_ENGINE_ID=你的Search Engine ID`

**優點**：
- 直接解決問題
- Google Custom Search 圖片品質好
- 代碼已支持，無需修改

**缺點**：
- 需要獲取 API Key（可能需要付費或配額限制）

#### 方案 2：修復 DuckDuckGo 備援服務

**執行內容**：
1. 檢查 DuckDuckGo 服務實現
2. 測試 DuckDuckGo API 是否可用
3. 修復可能的代碼問題

**優點**：
- 不需要 API Key
- 免費使用

**缺點**：
- 圖片品質可能不如付費服務
- 需要調試和修復

#### 方案 3：添加更好的錯誤處理和診斷

**執行內容**：
1. 添加配置檢查 API：`/api/v1/validate/images`
2. 返回當前圖片服務配置狀態
3. 前端顯示具體錯誤原因

**優點**：
- 快速定位問題
- 改善用戶體驗

**缺點**：
- 不解決根本問題，只是讓問題更明顯

### 2.6 第三方核證要點

請第三方專家評估：

1. **問題診斷是否正確**？
   - 是否真的是 API Key 未設置的問題？
   - DuckDuckGo 備援為什麼也失敗？

2. **建議方案是否可行**？
   - 方案 1（設置 API Key）是否真的能解決問題？
   - 方案 2（修復 DuckDuckGo）是否可行？

3. **是否有其他問題**？
   - 是否有代碼實現問題？
   - 是否有網路或服務問題？

---

## 📊 綜合評估

### 問題優先級

| 問題 | 優先級 | 影響 | 解決難度 |
|------|--------|------|----------|
| DeepSeek API 無法切換 | 🔴 高 | 內容生成功能完全無法使用 | 中（需要修改代碼） |
| 圖片搜尋無法工作 | 🟡 中 | 圖片功能無法使用，但不影響內容生成 | 低（設置 API Key 或修復備援） |

### 建議執行順序

1. **優先級 1**：修復 DeepSeek API 切換問題
   - 實施方案 1（修改 Workflow 實現動態獲取）
   - 時間：1-2 小時
   - 風險：低

2. **優先級 2**：修復圖片搜尋問題
   - 實施方案 1（設置 Google Custom Search API Key）
   - 時間：30 分鐘
   - 風險：低

### 風險總結

**方案 1（DeepSeek 動態獲取）**：
- ✅ 技術風險：低
- ✅ 功能風險：低
- ✅ 性能風險：低
- ⚠️ 仍需重啟服務才能生效（環境變數更新後）

**方案 2（圖片搜尋設置 API Key）**：
- ✅ 技術風險：低
- ✅ 功能風險：低
- ⚠️ 需要獲取 API Key（可能需要付費）

---

## 🔍 第三方核證檢查清單

請第三方專家檢查以下項目：

### 問題診斷

- [ ] DeepSeek API 無法切換的問題診斷是否正確？
- [ ] Workflow 初始化時固定 AI Service 是否真的是問題根源？
- [ ] 圖片搜尋問題的原因分析是否準確？
- [ ] 是否有遺漏的問題或原因？

### 解決方案

- [ ] 建議的方案 1（動態獲取）是否可行？
- [ ] 是否有更好的解決方案？
- [ ] 風險評估是否準確？
- [ ] 是否有未考慮的風險？

### 代碼證據

- [ ] 提供的代碼證據是否準確？
- [ ] 是否還有其他相關代碼需要檢查？
- [ ] 代碼分析是否正確？

### 執行建議

- [ ] 建議的執行順序是否合理？
- [ ] 時間估算是否準確？
- [ ] 是否有其他需要注意的事項？

---

## 📝 附錄

### 附錄 A：相關文件

- `2025-12-30_工作記錄.md` - 12月30日工作記錄
- `後端問題修復總結.md` - 後端問題修復總結
- `AI_Service切換問題分析與改善方案.md` - AI Service 切換問題分析
- `後端修復手動部署指南.md` - 手動部署指南
- `DeepSeek_API設置指南.md` - DeepSeek API 設置指南

### 附錄 B：關鍵代碼文件

- `backend/app/services/automation/workflow.py` - Workflow 實現
- `backend/app/services/automation/scheduler.py` - Scheduler 實現
- `backend/app/services/ai/ai_service_factory.py` - AI Service Factory
- `backend/app/services/images/image_service_manager.py` - 圖片服務管理器
- `backend/app/config.py` - 配置管理

### 附錄 C：環境變數記錄

**Railway 環境變數（根據記錄）**：
```
AI_SERVICE=deepseek
DEEPSEEK_API_KEY=sk-9995dc68272e4e2b8406af2caa557cb0
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1/chat/completions
```

**圖片服務環境變數（根據記錄）**：
```
UNSPLASH_ACCESS_KEY=（未設置）
PEXELS_API_KEY=（未設置）
PIXABAY_API_KEY=（未設置）
GOOGLE_API_KEY=（未設置）
GOOGLE_SEARCH_ENGINE_ID=（未設置）
```

---

## 📌 結論

本報告詳細記錄了兩個持續存在的問題，提供了代碼證據、已嘗試的解決方案，以及建議的解決方案。

**關鍵發現**：
1. DeepSeek API 無法切換的根本原因可能是代碼架構問題（Workflow 初始化時固定服務實例），而非環境變數問題
2. 圖片搜尋問題可能是因為所有 API Key 都未設置，且 DuckDuckGo 備援也失敗

**建議**：
1. 優先修復 DeepSeek API 切換問題（修改 Workflow 實現動態獲取）
2. 其次修復圖片搜尋問題（設置 API Key 或修復 DuckDuckGo）

**待第三方核證**：
- 問題診斷是否正確？
- 建議方案是否可行？
- 是否有更好的解決方案？

---

**報告創建時間**：2026-01-06  
**報告狀態**：待第三方核證  
**報告目的**：供第三方技術專家獨立評估問題和解決方案

