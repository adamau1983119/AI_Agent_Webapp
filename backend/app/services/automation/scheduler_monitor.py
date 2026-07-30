"""
排程服務監控
確保排程服務正常運行，並在失敗時自動重啟
daily 模式：以 HKT「今日」總數對齊 yaml（非舊 07/12/18 分槽）
"""
import logging
import asyncio
from datetime import datetime
from typing import Optional

from app.services.automation.scheduler import SchedulerService
from app.services.automation.topic_day_hkt import (
    category_counts,
    expected_topics_today,
    hkt_day_utc_bounds,
    is_daily_mode,
    today_hkt_str,
)
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
        self.monitoring = False
        logger.info("排程監控服務已停止")

    async def _count_topics_hkt_today(self) -> int:
        start_utc, end_utc = hkt_day_utc_bounds()
        items = await self.topic_repo.find_many(
            {"generated_at": {"$gte": start_utc, "$lte": end_utc}},
            skip=0,
            limit=200,
            sort=[("generated_at", -1)],
        )
        return len(items)

    async def _check_scheduler_health(self):
        try:
            if not self.scheduler_service.is_running:
                logger.warning("排程服務未運行，嘗試重新啟動...")
                self.scheduler_service.start()
                logger.info("排程服務已重新啟動")

            if is_daily_mode():
                expected = expected_topics_today()
                count = await self._count_topics_hkt_today()
                day = today_hkt_str()
                if count < expected:
                    logger.warning(
                        f"HKT 今日（{day}）主題不足：{count}/{expected}，"
                        f"建議檢查 ENABLE_SCHEDULED_TOPIC_COLLECTION 或手動觸發"
                    )
                else:
                    logger.debug(f"HKT 今日（{day}）主題 OK：{count}/{expected}")
            else:
                # interval 模式：保留輕量提示，不依 07/12/18 假分槽
                day = today_hkt_str()
                count = await self._count_topics_hkt_today()
                logger.debug(f"interval 模式 HKT 今日主題數：{count}（{day}）")

            self.last_check = datetime.utcnow()
        except Exception as e:
            logger.error(f"健康檢查失敗: {e}")

    async def ensure_today_topics(self):
        from app.utils.cost_controls import scheduled_topic_collection_enabled

        if not scheduled_topic_collection_enabled():
            logger.info(
                "跳過 ensure_today_topics（ENABLE_SCHEDULED_TOPIC_COLLECTION=false）"
            )
            return
        try:
            expected = expected_topics_today()
            count = await self._count_topics_hkt_today()
            if count >= expected:
                logger.info(f"今日主題已足（{count}/{expected}），略過補生成")
                return

            logger.info(f"今日主題不足（{count}/{expected}），自動觸發生成...")
            from app.models.topic import Category

            counts = category_counts()
            for category in [Category.FASHION, Category.FOOD, Category.TREND]:
                need = counts.get(category.value, 5)
                try:
                    await self.scheduler_service.trigger_manual_generation(
                        category=category,
                        count=need,
                    )
                    logger.info(f"已觸發生成 {category.value} 主題 ×{need}")
                except Exception as e:
                    logger.error(f"觸發生成 {category.value} 主題失敗: {e}")
        except Exception as e:
            logger.error(f"確保今日主題失敗: {e}")
