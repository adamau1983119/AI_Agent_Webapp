"""
自動化工作流服務
處理主題生成後的完整流程：內容生成 → 圖片搜尋 → 準備發布
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from app.services.repositories.topic_repository import TopicRepository
from app.services.repositories.content_repository import ContentRepository
from app.services.repositories.image_repository import ImageRepository
from app.services.ai.ai_service_factory import AIServiceFactory
from app.services.images.image_service import ImageService
from app.config import settings
from app.models.topic import Status

logger = logging.getLogger(__name__)


class AutomationWorkflow:
    """自動化工作流"""
    
    def __init__(self):
        self.topic_repo = TopicRepository()
        self.content_repo = ContentRepository()
        self.image_repo = ImageRepository()
        self.ai_service = AIServiceFactory.get_service(settings.AI_SERVICE)
        self.image_service = ImageService()
    
    async def process_topic(
        self,
        topic_id: str,
        auto_generate_content: bool = True,
        auto_search_images: bool = True,
        image_count: int = 3
    ) -> Dict[str, Any]:
        """
        處理主題的完整工作流
        
        Args:
            topic_id: 主題 ID
            auto_generate_content: 是否自動生成內容
            auto_search_images: 是否自動搜尋圖片
            image_count: 需要搜尋的圖片數量
            
        Returns:
            處理結果
        """
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
            
            logger.info(f"主題 {topic_id} 處理完成: {result}")
            return result
            
        except Exception as e:
            error_msg = f"處理主題失敗: {e}"
            logger.error(error_msg)
            result["errors"].append(error_msg)
            return result
    
    async def _generate_content(self, topic: Dict[str, Any]) -> None:
        """生成內容"""
        topic_id = topic["id"]
        topic_title = topic["title"]
        topic_category = topic["category"]
        
        # 提取關鍵字
        keywords = []
        for source in topic.get("sources", []):
            if "keywords" in source:
                keywords.extend(source["keywords"])
        
        # 生成內容（短文和腳本）
        result = await self.ai_service.generate_both(
            topic_title=topic_title,
            topic_category=topic_category,
            keywords=keywords,
            article_length=500,
            script_duration=30
        )
        
        # 計算字數和時長
        word_count = len(result["article"] or "") + len(result["script"] or "")
        estimated_duration = word_count // 17  # 假設每 17 字 = 1 秒
        
        # 檢查是否已存在內容
        existing_content = await self.content_repo.get_content_by_topic_id(topic_id)
        
        now = datetime.utcnow()
        
        if existing_content:
            # 更新現有內容
            content_id = existing_content["id"]
            update_data = {
                "article": result["article"],
                "script": result["script"],
                "word_count": word_count,
                "estimated_duration": estimated_duration,
                "model_used": getattr(self.ai_service, 'model_name', 'unknown'),
                "prompt_version": "v1.0",
                "version": existing_content.get("version", 0) + 1,
                "updated_at": now,
            }
            await self.content_repo.update_content(content_id, update_data)
        else:
            # 建立新內容
            content_data = {
                "id": topic_id,
                "topic_id": topic_id,
                "article": result["article"],
                "script": result["script"],
                "word_count": word_count,
                "estimated_duration": estimated_duration,
                "model_used": getattr(self.ai_service, 'model_name', 'unknown'),
                "prompt_version": "v1.0",
                "version": 1,
                "generated_at": now,
                "updated_at": now,
            }
            await self.content_repo.create_content(content_data)
        
        logger.info(f"主題 {topic_id} 內容生成完成")
    
    async def _search_and_add_images(
        self,
        topic: Dict[str, Any],
        count: int
    ) -> int:
        """搜尋並添加圖片"""
        topic_id = topic["id"]
        topic_title = topic["title"]
        
        # 提取關鍵字用於圖片搜尋
        keywords_list = []
        for source in topic.get("sources", []):
            if "keywords" in source:
                keywords_list.extend(source["keywords"])
        
        # 如果沒有關鍵字，使用標題
        if not keywords_list:
            keywords_list = [topic_title]
        
        # 使用第一個關鍵字搜尋圖片
        search_keyword = keywords_list[0] if keywords_list else topic_title
        
        try:
            # 搜尋圖片
            images = await self.image_service.search_images(
                keywords=search_keyword,
                source=None,  # 自動選擇
                page=1,
                limit=count,
                use_fallback=True
            )
            
            # 添加圖片到主題
            added_count = 0
            existing_images = await self.image_repo.get_images_by_topic_id(topic_id)
            max_order = max([img.get("order", 0) for img in existing_images]) if existing_images else -1
            
            for idx, image in enumerate(images[:count]):
                try:
                    # 處理圖片來源
                    image_source = image.get("source", "unknown")
                    if hasattr(image_source, 'value'):
                        image_source = image_source.value
                    elif isinstance(image_source, str):
                        image_source = image_source
                    else:
                        image_source = str(image_source) if image_source else "unknown"
                    
                    image_data = {
                        "id": image.get("id", f"img_{topic_id}_{idx}"),
                        "topic_id": topic_id,
                        "url": image.get("url", ""),
                        "source": image_source,
                        "photographer": image.get("photographer"),
                        "photographer_url": image.get("photographer_url"),
                        "license": image.get("license", "Unknown"),
                        "keywords": keywords_list,
                        "order": max_order + idx + 1,
                        "width": image.get("width"),
                        "height": image.get("height"),
                        "fetched_at": datetime.utcnow(),
                    }
                    
                    await self.image_repo.create_image(image_data)
                    added_count += 1
                    
                except Exception as e:
                    logger.warning(f"添加圖片失敗: {e}")
                    continue
            
            logger.info(f"主題 {topic_id} 添加了 {added_count} 張圖片")
            return added_count
            
        except Exception as e:
            logger.error(f"搜尋圖片失敗: {e}")
            return 0

