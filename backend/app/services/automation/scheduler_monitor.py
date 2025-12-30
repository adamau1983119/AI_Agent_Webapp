"""
排程服務監控
確保排程服務正常運行，並在失敗時自動重啟
"""
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from app.services.automation.scheduler import SchedulerService
from app.services.repositories.topic_repository import TopicRepository

logger = logging.getLogger(__name__)


class SchedulerMonitor:
    """排程服務監控器"""
    
    def __init__(self, scheduler_service: SchedulerService):
        self.scheduler_service = scheduler_service
        self.topic_repo = TopicRepository()
        self.monitoring = False
        self.last_check: Optional[datetime] = None
    
    async def start_monitoring(self, check_interval: int = 300):
        """
        開始監控排程服務
        
        Args:
            check_interval: 檢查間隔（秒），預設 5 分鐘
        """
        if self.monitoring:
            logger.warning("監控服務已經在運行")
            return
        
        self.monitoring = True
        logger.info(f"排程監控服務已啟動，檢查間隔：{check_interval} 秒")
        
        while self.monitoring:
            try:
                await self._check_scheduler_health()
                await asyncio.sleep(check_interval)
            except Exception as e:
                logger.error(f"監控檢查失敗: {e}")
                await asyncio.sleep(check_interval)
    
    def stop_monitoring(self):
        """停止監控"""
        self.monitoring = False
        logger.info("排程監控服務已停止")
    
    async def _check_scheduler_health(self):
        """檢查排程服務健康狀態"""
        try:
            # 檢查排程服務是否運行
            if not self.scheduler_service.is_running:
                logger.warning("排程服務未運行，嘗試重新啟動...")
                self.scheduler_service.start()
                logger.info("排程服務已重新啟動")
            
            # 檢查今日是否有生成主題
            today = datetime.now().strftime("%Y-%m-%d")
            topics, _ = await self.topic_repo.list_topics(date=today, limit=100)
            
            # 檢查每個時間段的主題數量
            time_slots = {
                "07:00": {"expected": 3, "count": 0},
                "12:00": {"expected": 3, "count": 0},
                "18:00": {"expected": 3, "count": 0},
            }
            
            current_hour = datetime.now().hour
            
            for topic in topics:
                generated_at = topic.get("generated_at")
                if isinstance(generated_at, str):
                    try:
                        generated_at = datetime.fromisoformat(generated_at.replace('Z', '+00:00'))
                    except:
                        continue
                
                if isinstance(generated_at, datetime):
                    hour = generated_at.hour
                    if 6 <= hour < 10:
                        time_slots["07:00"]["count"] += 1
                    elif 11 <= hour < 14:
                        time_slots["12:00"]["count"] += 1
                    elif 17 <= hour < 20:
                        time_slots["18:00"]["count"] += 1
            
            # 檢查是否需要補生成
            for time_slot, data in time_slots.items():
                expected = data["expected"]
                count = data["count"]
                
                # 判斷時間段是否已過
                slot_hour = int(time_slot.split(":")[0])
                if current_hour >= slot_hour + 1:  # 時間段已過 1 小時
                    if count < expected:
                        logger.warning(
                            f"時間段 {time_slot} 主題不足：{count}/{expected}，"
                            f"建議手動觸發生成或檢查排程服務"
                        )
            
            self.last_check = datetime.now()
            
        except Exception as e:
            logger.error(f"健康檢查失敗: {e}")
    
    async def ensure_today_topics(self):
        """
        確保今日主題已生成
        如果不足，自動觸發生成
        """
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            topics, _ = await self.topic_repo.list_topics(date=today, limit=100)
            
            if len(topics) < 9:  # 應該有 9 個主題（3 個分類 × 3 個）
                logger.info(f"今日主題不足（{len(topics)}/9），自動觸發生成...")
                
                # 觸發生成所有分類的主題
                from app.models.topic import Category
                for category in [Category.FASHION, Category.FOOD, Category.TREND]:
                    try:
                        await self.scheduler_service.trigger_manual_generation(
                            category=category,
                            count=3
                        )
                        logger.info(f"已觸發生成 {category.value} 主題")
                    except Exception as e:
                        logger.error(f"觸發生成 {category.value} 主題失敗: {e}")
        except Exception as e:
            logger.error(f"確保今日主題失敗: {e}")

