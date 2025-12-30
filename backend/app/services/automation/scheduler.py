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

logger = logging.getLogger(__name__)


class SchedulerService:
    """排程服務"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.topic_collector = TopicCollector()
        self.workflow = AutomationWorkflow()
        self.topic_repo = TopicRepository()
        self.is_running = False
    
    def start(self):
        """啟動排程服務"""
        if self.is_running:
            logger.warning("排程服務已經在運行")
            return
        
        # 設定每日任務（使用 UTC 時間，需根據時區調整）
        # 注意：CronTrigger 使用 UTC 時間
        # 如果服務器在 UTC+8（香港時間），需要減 8 小時
        
        # 計算 UTC 時間（假設目標是香港時間 07:00, 12:00, 18:00）
        # 香港時間 = UTC + 8，所以 UTC 時間 = 香港時間 - 8
        # 07:00 HKT = 23:00 UTC (前一天)
        # 12:00 HKT = 04:00 UTC
        # 18:00 HKT = 10:00 UTC
        
        # 07:00 香港時間 = 23:00 UTC（前一天）
        self.scheduler.add_job(
            self._generate_topics_for_timeslot,
            CronTrigger(hour=23, minute=0, timezone='UTC'),  # 香港時間 07:00
            id="fashion_topics_07:00",
            args=[Category.FASHION, "07:00"],
            replace_existing=True
        )
        
        # 12:00 香港時間 = 04:00 UTC
        self.scheduler.add_job(
            self._generate_topics_for_timeslot,
            CronTrigger(hour=4, minute=0, timezone='UTC'),  # 香港時間 12:00
            id="food_topics_12:00",
            args=[Category.FOOD, "12:00"],
            replace_existing=True
        )
        
        # 18:00 香港時間 = 10:00 UTC
        self.scheduler.add_job(
            self._generate_topics_for_timeslot,
            CronTrigger(hour=10, minute=0, timezone='UTC'),  # 香港時間 18:00
            id="trend_topics_18:00",
            args=[Category.TREND, "18:00"],
            replace_existing=True
        )
        
        logger.info("排程任務已設定：")
        logger.info("  - 07:00 HKT (23:00 UTC) - 時尚趨勢")
        logger.info("  - 12:00 HKT (04:00 UTC) - 美食推薦")
        logger.info("  - 18:00 HKT (10:00 UTC) - 社會趨勢")
        
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
    
    async def _generate_topics_for_timeslot(
        self,
        category: Category,
        time_slot: str
    ):
        """
        為指定時間段生成主題
        
        Args:
            category: 主題分類
            time_slot: 時間段（07:00, 12:00, 18:00）
        """
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
                        image_count=3
                    )
                    
                    logger.info(f"主題 {topic_id} 建立並處理完成")
                    
                except Exception as e:
                    logger.error(f"建立主題失敗: {e}")
                    continue
            
            logger.info(f"時間段 {time_slot} 完成，共建立 {len(created_topics)} 個主題")
            
        except Exception as e:
            logger.error(f"為時間段 {time_slot} 生成主題失敗: {e}")
    
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
                        image_count=3
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

