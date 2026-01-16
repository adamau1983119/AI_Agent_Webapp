"""
排程服務
使用 APScheduler 執行定時任務
"""
import logging
from datetime import datetime, time
from typing import Dict, Any, List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.automation.topic_collector import TopicCollector
from app.services.automation.workflow import AutomationWorkflow
from app.services.repositories.topic_repository import TopicRepository
from app.models.topic import Category, Status
from app.config.topic_config import get_topic_config

logger = logging.getLogger(__name__)


class SchedulerService:
    """排程服務"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.topic_collector = TopicCollector()
        self.workflow = AutomationWorkflow()
        self.topic_repo = TopicRepository()
        self.is_running = False
        self.config = get_topic_config()  # 載入配置檔
    
    def start(self):
        """啟動排程服務"""
        if self.is_running:
            logger.warning("排程服務已經在運行")
            return
        
        # 從配置檔讀取生成時間和時區
        hkt_time_str = self.config.get_daily_generation_time()
        utc_time = self.config.get_utc_time_for_schedule()
        
        logger.info(f"從配置檔讀取生成時間: {hkt_time_str} ({self.config.get_daily_generation_timezone()})")
        logger.info(f"轉換為 UTC 時間: {utc_time.hour:02d}:{utc_time.minute:02d}")
        
        # 階段 1：所有分類都在 07:00 生成（從配置檔讀取）
        # 為每個分類設定排程任務
        categories = [Category.FASHION, Category.FOOD, Category.TREND]
        
        for category in categories:
            category_name = category.value
            job_id = f"{category_name}_topics_{hkt_time_str.replace(':', '')}"
            
            self.scheduler.add_job(
                self._generate_topics_for_category,
                CronTrigger(hour=utc_time.hour, minute=utc_time.minute, timezone='UTC'),
                id=job_id,
                args=[category, hkt_time_str],
                replace_existing=True
            )
            
            logger.info(f"排程任務已設定: {job_id} - {category_name} 分類，{hkt_time_str} HKT ({utc_time.hour:02d}:{utc_time.minute:02d} UTC)")
        
        self.scheduler.start()
        self.is_running = True
        logger.info("排程服務已啟動")
    
    def stop(self):
        """停止排程服務"""
        if not self.is_running:
            return
        
        self.scheduler.shutdown()
        self.is_running = False
        logger.info("排程服務已停止")
    
    async def _generate_topics_for_category(
        self,
        category: Category,
        time_slot: str
    ):
        """
        為指定分類生成主題（階段 1：從配置檔讀取參數）
        
        Args:
            category: 主題分類
            time_slot: 時間段（用於日誌記錄）
        """
        category_name = category.value
        logger.info(f"開始為 {category_name} 分類生成主題（時間段: {time_slot}）")
        
        try:
            # 檢查每日限制（如果啟用）
            if self.config.is_daily_limit_enabled():
                if await self._check_daily_limit(category):
                    logger.info(f"{category_name} 分類今天已經生成過，跳過")
                    return
            
            # 從配置檔讀取生成數量
            count = self.config.get_category_count(category_name)
            preview_images_count = self.config.get_preview_images_count(category_name)
            should_generate_content = self.config.should_generate_content(category_name)
            
            logger.info(f"{category_name} 分類配置: count={count}, preview_images={preview_images_count}, generate_content={should_generate_content}")
            
            # 收集主題
            topics_data = await self.topic_collector.collect_topics(
                category=category,
                count=count,  # 從配置檔讀取
                use_fallback=True
            )
            
            created_topics = []
            
            # 為每個主題建立資料庫記錄並處理
            for topic_data in topics_data:
                try:
                    # 生成唯一 ID
                    topic_id = f"topic_{category.value}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{len(created_topics)}"
                    topic_data["id"] = topic_id
                    topic_data["status"] = Status.PENDING.value
                    topic_data["generated_at"] = datetime.utcnow()
                    topic_data["updated_at"] = datetime.utcnow()
                    topic_data["created_at"] = datetime.utcnow()
                    
                    # 階段 1：初始化新欄位
                    topic_data["preview_images"] = []
                    topic_data["is_expanded"] = False
                    topic_data["generation_config"] = {
                        "category": category_name,
                        "count": count,
                        "preview_images_count": preview_images_count,
                        "generate_content": should_generate_content,
                        "generated_at": time_slot
                    }
                    
                    # 建立主題
                    created_topic = await self.topic_repo.create_topic(topic_data)
                    created_topics.append(created_topic)
                    
                    # 階段 1：只生成預覽圖片，不生成內容
                    if preview_images_count > 0:
                        # 搜尋預覽圖片（階段 1：只搜尋 1 張）
                        await self.workflow.process_topic(
                            topic_id=topic_id,
                            auto_generate_content=should_generate_content,  # 從配置檔讀取（階段 1：False）
                            auto_search_images=True,
                            image_count=preview_images_count  # 從配置檔讀取（階段 1：1 張）
                        )
                    
                    logger.info(f"主題 {topic_id} 建立並處理完成（預覽圖片: {preview_images_count} 張）")
                    
                except Exception as e:
                    logger.error(f"建立主題失敗: {e}")
                    continue
            
            logger.info(f"{category_name} 分類完成，共建立 {len(created_topics)} 個主題")
            
        except Exception as e:
            logger.error(f"為 {category_name} 分類生成主題失敗: {e}")
    
    async def _check_daily_limit(self, category: Category) -> bool:
        """
        檢查每日限制（是否今天已經生成過）
        
        Args:
            category: 主題分類
            
        Returns:
            True 如果今天已經生成過，False 如果還沒生成
        """
        try:
            from datetime import date
            today = date.today()
            today_str = today.strftime("%Y-%m-%d")
            
            # 查詢今天是否已經有該分類的主題
            unique_key = self.config.get_daily_limit_unique_key()
            
            if unique_key == "date_category":
                # 使用 list_topics 方法檢查今天是否有該分類的主題
                topics, total = await self.topic_repo.list_topics(
                    category=category,
                    date=today_str,
                    page=1,
                    limit=1  # 只需要檢查是否有，不需要全部
                )
                return total > 0
            else:
                # 其他 unique_key 類型的處理
                logger.warning(f"不支援的 unique_key 類型: {unique_key}")
                return False
                
        except Exception as e:
            logger.error(f"檢查每日限制失敗: {e}")
            return False  # 如果檢查失敗，允許生成
    
    async def trigger_manual_generation(
        self,
        category: Category,
        count: int = 3
    ) -> List[Dict[str, Any]]:
        """
        手動觸發主題生成（用於測試或立即執行）
        
        Args:
            category: 主題分類
            count: 生成數量
            
        Returns:
            建立的主題列表
        """
        logger.info(f"手動觸發生成 {count} 個 {category.value} 主題")
        
        try:
            # 收集主題
            topics_data = await self.topic_collector.collect_topics(
                category=category,
                count=count,
                use_fallback=True
            )
            
            created_topics = []
            
            # 為每個主題建立資料庫記錄並處理
            for topic_data in topics_data:
                try:
                    # 生成唯一 ID
                    topic_id = f"topic_{category.value}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{len(created_topics)}"
                    topic_data["id"] = topic_id
                    topic_data["status"] = Status.PENDING.value
                    topic_data["generated_at"] = datetime.utcnow()
                    topic_data["updated_at"] = datetime.utcnow()
                    topic_data["created_at"] = datetime.utcnow()
                    
                    # 建立主題
                    created_topic = await self.topic_repo.create_topic(topic_data)
                    created_topics.append(created_topic)
                    
                    # 處理主題（生成內容和圖片）
                    await self.workflow.process_topic(
                        topic_id=topic_id,
                        auto_generate_content=True,
                        auto_search_images=True,
                        image_count=8  # 改為 8 張照片（符合需求）
                    )
                    
                    logger.info(f"主題 {topic_id} 建立並處理完成")
                    
                except Exception as e:
                    logger.error(f"建立主題失敗: {e}")
                    continue
            
            logger.info(f"手動生成完成，共建立 {len(created_topics)} 個主題")
            return created_topics
            
        except Exception as e:
            logger.error(f"手動生成主題失敗: {e}")
            raise

