# Webapp 內容生成問題診斷報告

## 📋 執行摘要

**問題描述**：Webapp 完全未能按照主題生成文字及給予相關的圖片。

**報告日期**：2025-01-XX

**報告目的**：提供第三方技術團隊完整的系統架構、關鍵程式碼和診斷建議，以便快速定位和解決問題。

---

## 🏗️ 系統架構概述

### 1. 整體工作流程

```
主題收集 (TopicCollector)
    ↓
排程服務 (SchedulerService) - 每日 07:00, 12:00, 18:00
    ↓
自動化工作流 (AutomationWorkflow)
    ├── 生成內容 (AI Service)
    └── 搜尋圖片 (Image Service)
    ↓
資料庫 (MongoDB)
```

### 2. 關鍵組件

| 組件 | 檔案位置 | 功能 |
|------|---------|------|
| **排程服務** | `backend/app/services/automation/scheduler.py` | 定時觸發主題生成 |
| **自動化工作流** | `backend/app/services/automation/workflow.py` | 處理內容和圖片生成 |
| **AI 服務** | `backend/app/services/ai/` | 生成文字內容 |
| **圖片服務** | `backend/app/services/images/image_service.py` | 搜尋相關圖片 |
| **主題收集器** | `backend/app/services/automation/topic_collector.py` | 從 RSS 或關鍵字收集主題 |
| **排程監控** | `backend/app/services/automation/scheduler_monitor.py` | 監控排程健康狀態 |

---

## 🔍 關鍵程式碼分析

### 1. 排程服務啟動邏輯

**檔案**：`backend/app/main.py` (第 86-117 行)

```python
# 檢查是否應該啟動排程服務
should_start_scheduler = (
    settings.ENVIRONMENT == "production" or 
    getattr(settings, 'AUTO_START_SCHEDULER', 'false').lower() == 'true'
)

if should_start_scheduler:
    scheduler_service = SchedulerService()
    scheduler_service.start()
    logger.info("✅ 排程服務已啟動（生產環境）")
```

**關鍵問題點**：
- ⚠️ 排程服務只在 `ENVIRONMENT=production` 或 `AUTO_START_SCHEDULER=true` 時啟動
- ⚠️ 預設環境為 `development`，排程服務不會自動啟動
- ⚠️ 如果環境變數未正確設定，排程服務將不會運行

### 2. 自動化工作流處理邏輯

**檔案**：`backend/app/services/automation/workflow.py` (第 29-91 行)

```python
async def process_topic(
    self,
    topic_id: str,
    auto_generate_content: bool = True,
    auto_search_images: bool = True,
    image_count: int = 3
) -> Dict[str, Any]:
    result = {
        "topic_id": topic_id,
        "content_generated": False,
        "images_added": 0,
        "errors": [],
    }
    
    try:
        # 1. 取得主題
        topic = await self.topic_repo.get_topic_by_id(topic_id)
        if not topic:
            raise ValueError(f"主題不存在: {topic_id}")
        
        # 2. 生成內容
        if auto_generate_content:
            try:
                await self._generate_content(topic)
                result["content_generated"] = True
            except Exception as e:
                error_msg = f"生成內容失敗: {e}"
                logger.error(error_msg)
                result["errors"].append(error_msg)
        
        # 3. 搜尋並添加圖片
        if auto_search_images:
            try:
                images_added = await self._search_and_add_images(
                    topic,
                    image_count
                )
                result["images_added"] = images_added
            except Exception as e:
                error_msg = f"搜尋圖片失敗: {e}"
                logger.error(error_msg)
                result["errors"].append(error_msg)
        
        return result
    except Exception as e:
        error_msg = f"處理主題失敗: {e}"
        logger.error(error_msg)
        result["errors"].append(error_msg)
        return result
```

**關鍵問題點**：
- ⚠️ 錯誤被捕捉但不會中斷流程，可能導致靜默失敗
- ⚠️ 錯誤訊息只記錄在日誌中，前端無法得知具體失敗原因
- ⚠️ 如果 AI 服務或圖片服務配置錯誤，會導致生成失敗但不會拋出異常

### 3. AI 服務配置

**檔案**：`backend/app/services/automation/workflow.py` (第 22-27 行)

```python
def __init__(self):
    self.topic_repo = TopicRepository()
    self.content_repo = ContentRepository()
    self.image_repo = ImageRepository()
    self.ai_service = AIServiceFactory.get_service(settings.AI_SERVICE)
    self.image_service = ImageService()
```

**檔案**：`backend/app/config.py` (第 54 行)

```python
AI_SERVICE: str = "qwen"  # 預設使用通義千問
```

**檔案**：`backend/app/services/ai/qwen.py` (第 53-54 行)

```python
if not self.api_key:
    raise ValueError("通義千問 API Key 未設定")
```

**關鍵問題點**：
- ⚠️ 如果 `QWEN_API_KEY` 未設定，AI 服務會拋出異常
- ⚠️ 預設使用 `qwen`，但可能未配置 API Key
- ⚠️ 沒有備援 AI 服務機制（雖然支援多種服務，但需要手動切換）

### 4. 圖片服務配置

**檔案**：`backend/app/services/images/image_service.py` (第 30-90 行)

```python
async def search_images(
    self,
    keywords: str,
    source: Optional[ImageSource] = None,
    page: int = 1,
    limit: int = 20,
    use_fallback: bool = True
) -> List[Dict[str, Any]]:
    # 按優先順序嘗試各個服務
    last_error = None
    for service, service_source in self.services:
        try:
            images = await service.search_images(keywords, page, limit)
            logger.info(f"使用 {service_source.value} 成功搜尋圖片")
            return images
        except ValueError as e:
            # API Key 未設定，跳過此服務
            logger.warning(f"{service_source.value} API Key 未設定，跳過")
            continue
        except Exception as e:
            logger.warning(f"{service_source.value} 搜尋失敗: {e}")
            last_error = e
            continue
    
    # 所有服務都失敗
    if last_error:
        raise last_error
    raise ValueError("沒有可用的圖片服務（所有 API Key 都未設定）")
```

**關鍵問題點**：
- ⚠️ 如果所有圖片服務的 API Key 都未設定，會拋出異常
- ⚠️ 雖然有備援機制，但如果所有服務都失敗，圖片生成會失敗
- ⚠️ 錯誤訊息可能不夠明確，無法判斷是哪個服務失敗

### 5. 排程觸發邏輯

**檔案**：`backend/app/services/automation/scheduler.py` (第 89-145 行)

```python
async def _generate_topics_for_timeslot(
    self,
    category: Category,
    time_slot: str
):
    logger.info(f"開始為時間段 {time_slot} 生成 {category.value} 主題")
    
    try:
        # 收集主題
        topics_data = await self.topic_collector.collect_topics(
            category=category,
            count=3,
            use_fallback=True
        )
        
        created_topics = []
        
        # 為每個主題建立資料庫記錄並處理
        for topic_data in topics_data:
            try:
                # 生成唯一 ID
                topic_id = f"topic_{category.value}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{len(created_topics)}"
                # ... 建立主題 ...
                
                # 處理主題（生成內容和圖片）
                await self.workflow.process_topic(
                    topic_id=topic_id,
                    auto_generate_content=True,
                    auto_search_images=True,
                    image_count=8
                )
                
                logger.info(f"主題 {topic_id} 建立並處理完成")
                
            except Exception as e:
                logger.error(f"建立主題失敗: {e}")
                continue  # 繼續處理下一個主題
```

**關鍵問題點**：
- ⚠️ 如果某個主題處理失敗，會繼續處理下一個，但錯誤可能被忽略
- ⚠️ 沒有重試機制，如果 AI 服務暫時不可用，會直接失敗
- ⚠️ 沒有通知機制，無法得知排程任務是否成功執行

---

## 🚨 可能的問題點

### 1. 環境配置問題

**問題**：排程服務未啟動
- **原因**：`ENVIRONMENT` 未設定為 `production` 或 `AUTO_START_SCHEDULER` 未設定為 `true`
- **影響**：排程任務不會執行，主題不會自動生成
- **檢查方法**：
  ```bash
  # 檢查環境變數
  echo $ENVIRONMENT
  echo $AUTO_START_SCHEDULER
  ```

### 2. AI 服務配置問題

**問題**：AI API Key 未設定或無效
- **原因**：`QWEN_API_KEY` 或其他 AI 服務的 API Key 未設定
- **影響**：內容生成會失敗
- **檢查方法**：
  ```python
  # 檢查配置
  from app.config import settings
  print(f"AI_SERVICE: {settings.AI_SERVICE}")
  print(f"QWEN_API_KEY: {'已設定' if settings.QWEN_API_KEY else '未設定'}")
  ```

### 3. 圖片服務配置問題

**問題**：所有圖片服務的 API Key 都未設定
- **原因**：`UNSPLASH_ACCESS_KEY`、`PEXELS_API_KEY`、`PIXABAY_API_KEY` 都未設定
- **影響**：圖片搜尋會失敗
- **檢查方法**：
  ```python
  from app.config import settings
  print(f"UNSPLASH_ACCESS_KEY: {'已設定' if settings.UNSPLASH_ACCESS_KEY else '未設定'}")
  print(f"PEXELS_API_KEY: {'已設定' if settings.PEXELS_API_KEY else '未設定'}")
  print(f"PIXABAY_API_KEY: {'已設定' if settings.PIXABAY_API_KEY else '未設定'}")
  ```

### 4. 資料庫連接問題

**問題**：MongoDB 連接失敗
- **原因**：`MONGODB_URL` 未設定或連接字串錯誤
- **影響**：無法讀取或寫入主題、內容、圖片資料
- **檢查方法**：
  ```python
  from app.database import check_connection
  is_connected = await check_connection()
  print(f"MongoDB 連接狀態: {'已連接' if is_connected else '未連接'}")
  ```

### 5. 排程時間設定問題

**問題**：排程時間設定錯誤（UTC vs 本地時間）
- **原因**：排程使用 UTC 時間，但可能與預期時間不符
- **影響**：主題不會在預期時間生成
- **檢查方法**：
  ```python
  # 檢查排程設定
  # 07:00 HKT = 23:00 UTC (前一天)
  # 12:00 HKT = 04:00 UTC
  # 18:00 HKT = 10:00 UTC
  ```

### 6. 錯誤處理問題

**問題**：錯誤被靜默處理，無法追蹤
- **原因**：`workflow.process_topic` 中的錯誤被捕捉但不會中斷流程
- **影響**：無法得知具體失敗原因
- **檢查方法**：
  ```python
  # 檢查日誌
  # 查看 logs/app.log 或應用程式日誌輸出
  ```

---

## 🔧 診斷步驟

### 步驟 1：檢查環境變數

```bash
# 檢查關鍵環境變數
env | grep -E "ENVIRONMENT|AUTO_START_SCHEDULER|AI_SERVICE|QWEN_API_KEY|MONGODB_URL"
```

### 步驟 2：檢查排程服務狀態

```python
# 在 Python 中檢查
from app.services.automation.scheduler import SchedulerService
scheduler = SchedulerService()
print(f"排程服務運行狀態: {scheduler.is_running}")
```

### 步驟 3：檢查 AI 服務配置

```python
from app.config import settings
from app.services.ai.ai_service_factory import AIServiceFactory

try:
    ai_service = AIServiceFactory.get_service(settings.AI_SERVICE)
    print(f"AI 服務: {settings.AI_SERVICE}")
    print(f"AI 服務實例: {type(ai_service).__name__}")
except Exception as e:
    print(f"AI 服務初始化失敗: {e}")
```

### 步驟 4：檢查圖片服務配置

```python
from app.services.images.image_service import ImageService

image_service = ImageService()
# 檢查各個服務的 API Key
print(f"Unsplash: {'已配置' if image_service.unsplash.api_key else '未配置'}")
print(f"Pexels: {'已配置' if image_service.pexels.api_key else '未配置'}")
print(f"Pixabay: {'已配置' if image_service.pixabay.api_key else '未配置'}")
```

### 步驟 5：手動測試工作流

```python
from app.services.automation.workflow import AutomationWorkflow

workflow = AutomationWorkflow()
result = await workflow.process_topic(
    topic_id="test_topic_id",
    auto_generate_content=True,
    auto_search_images=True,
    image_count=8
)
print(f"處理結果: {result}")
```

### 步驟 6：檢查日誌

```bash
# 查看應用程式日誌
tail -f logs/app.log

# 或查看 Railway 日誌
railway logs
```

---

## 💡 改善建議

### 1. 立即改善

#### 1.1 添加環境變數檢查

**建議**：在應用啟動時檢查關鍵環境變數

```python
# 在 main.py 中添加
def validate_environment():
    """驗證環境變數配置"""
    errors = []
    
    if settings.AI_SERVICE == "qwen" and not settings.QWEN_API_KEY:
        errors.append("QWEN_API_KEY 未設定")
    
    if not settings.UNSPLASH_ACCESS_KEY and not settings.PEXELS_API_KEY and not settings.PIXABAY_API_KEY:
        errors.append("所有圖片服務的 API Key 都未設定")
    
    if not settings.MONGODB_URL:
        errors.append("MONGODB_URL 未設定")
    
    if errors:
        logger.error("環境變數配置錯誤：")
        for error in errors:
            logger.error(f"  - {error}")
        raise ValueError("環境變數配置不完整")
```

#### 1.2 改善錯誤處理和報告

**建議**：添加更詳細的錯誤報告機制

```python
# 在 workflow.py 中改善
async def process_topic(...):
    result = {
        "topic_id": topic_id,
        "content_generated": False,
        "images_added": 0,
        "errors": [],
        "warnings": [],
    }
    
    # 添加詳細的錯誤資訊
    if auto_generate_content:
        try:
            await self._generate_content(topic)
            result["content_generated"] = True
        except ValueError as e:
            if "API Key 未設定" in str(e):
                result["errors"].append({
                    "type": "configuration_error",
                    "message": f"AI 服務配置錯誤: {e}",
                    "service": settings.AI_SERVICE
                })
            else:
                result["errors"].append({
                    "type": "generation_error",
                    "message": f"生成內容失敗: {e}"
                })
```

#### 1.3 添加健康檢查端點

**建議**：添加詳細的健康檢查端點

```python
# 在 health.py 中添加
@router.get("/detailed")
async def detailed_health_check():
    """詳細健康檢查"""
    checks = {
        "database": False,
        "scheduler": False,
        "ai_service": False,
        "image_service": False,
    }
    
    # 檢查資料庫
    try:
        checks["database"] = await check_connection()
    except:
        pass
    
    # 檢查排程服務
    try:
        from app.services.automation.scheduler import SchedulerService
        scheduler = SchedulerService()
        checks["scheduler"] = scheduler.is_running
    except:
        pass
    
    # 檢查 AI 服務
    try:
        from app.services.ai.ai_service_factory import AIServiceFactory
        ai_service = AIServiceFactory.get_service(settings.AI_SERVICE)
        checks["ai_service"] = True
    except:
        pass
    
    # 檢查圖片服務
    try:
        from app.services.images.image_service import ImageService
        image_service = ImageService()
        checks["image_service"] = any([
            image_service.unsplash.api_key,
            image_service.pexels.api_key,
            image_service.pixabay.api_key
        ])
    except:
        pass
    
    return {
        "status": "healthy" if all(checks.values()) else "unhealthy",
        "checks": checks
    }
```

### 2. 中期改善

#### 2.1 添加重試機制

**建議**：為 AI 服務和圖片服務添加重試機制

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def _generate_content_with_retry(self, topic):
    """帶重試的內容生成"""
    return await self._generate_content(topic)
```

#### 2.2 添加監控和告警

**建議**：添加監控和告警機制，當排程任務失敗時發送通知

```python
async def send_alert(self, message: str):
    """發送告警通知"""
    # 可以整合 Slack、Email、Telegram 等通知服務
    logger.error(f"告警: {message}")
```

#### 2.3 改善日誌記錄

**建議**：添加結構化日誌，方便追蹤問題

```python
import structlog

logger = structlog.get_logger()

logger.info(
    "主題處理開始",
    topic_id=topic_id,
    auto_generate_content=auto_generate_content,
    auto_search_images=auto_search_images
)
```

### 3. 長期改善

#### 3.1 使用任務佇列

**建議**：使用 Celery 或類似工具處理異步任務

```python
from celery import Celery

app = Celery('tasks')

@app.task
def process_topic_async(topic_id: str):
    """異步處理主題"""
    # 處理邏輯
    pass
```

#### 3.2 添加資料庫事務

**建議**：確保資料一致性

```python
async def process_topic_with_transaction(self, topic_id: str):
    """使用事務處理主題"""
    async with self.db.transaction():
        # 處理邏輯
        pass
```

---

## 📊 關鍵檔案清單

| 檔案路徑 | 說明 | 關鍵行數 |
|---------|------|---------|
| `backend/app/main.py` | 應用入口，排程服務啟動邏輯 | 86-117 |
| `backend/app/config.py` | 環境配置 | 全部 |
| `backend/app/services/automation/scheduler.py` | 排程服務 | 89-145 |
| `backend/app/services/automation/workflow.py` | 自動化工作流 | 29-232 |
| `backend/app/services/ai/qwen.py` | AI 服務（通義千問） | 43-100 |
| `backend/app/services/images/image_service.py` | 圖片服務管理器 | 30-90 |
| `backend/app/services/automation/topic_collector.py` | 主題收集器 | 62-100 |
| `backend/app/services/automation/scheduler_monitor.py` | 排程監控 | 109-133 |

---

## 🎯 優先處理事項

1. **立即檢查環境變數配置**
   - 確認 `ENVIRONMENT` 或 `AUTO_START_SCHEDULER` 設定
   - 確認 `AI_SERVICE` 和對應的 API Key
   - 確認至少一個圖片服務的 API Key

2. **檢查排程服務狀態**
   - 確認排程服務是否正在運行
   - 檢查排程任務是否按時執行

3. **檢查日誌**
   - 查看應用程式日誌，尋找錯誤訊息
   - 特別關注 AI 服務和圖片服務的錯誤

4. **手動測試**
   - 使用 API 端點手動觸發主題生成
   - 檢查返回的錯誤訊息

5. **添加監控**
   - 實施健康檢查端點
   - 添加錯誤報告機制

---

## 📝 附錄：API 端點

### 手動觸發主題生成

```bash
POST /api/v1/schedules/generate-today
Content-Type: application/json

{
  "force": false
}
```

### 檢查排程狀態

```bash
GET /api/v1/schedules?date=2025-01-XX
```

### 手動生成內容

```bash
POST /api/v1/contents/{topic_id}/generate
Content-Type: application/json

{
  "type": "both",
  "article_length": 500,
  "script_duration": 30
}
```

### 手動搜尋圖片

```bash
POST /api/v1/images/{topic_id}/match?min_count=8
```

---

## 📞 聯繫資訊

如有任何問題，請參考：
- 專案文檔：`AI_Agents_API架構表與生產內容設定.md`
- 環境變數檢查清單：`環境變數檢查清單.md`
- 生產環境排程設定指南：`生產環境排程設定指南.md`

---

**報告結束**

