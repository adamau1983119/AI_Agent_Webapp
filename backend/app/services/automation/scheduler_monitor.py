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
    category_deficits,
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
        self._is_ensuring: bool = False
        self._last_ensure_time: Optional[datetime] = None

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
        """只計目前世代（soft cutover）；舊卡不擋補生成。"""
        from app.utils.topic_pipeline import list_topics_generation_filter

        start_utc, end_utc = hkt_day_utc_bounds()
        clauses = [{"generated_at": {"$gte": start_utc, "$lte": end_utc}}]
        gen_f = list_topics_generation_filter(include_legacy=False)
        if gen_f:
            clauses.append(gen_f)
        filt = clauses[0] if len(clauses) == 1 else {"$and": clauses}
        return await self.topic_repo.count(filt)

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
                        f"檢查自動補產卡條件..."
                    )
                    from app.utils.cost_controls import scheduled_topic_collection_enabled

                    if scheduled_topic_collection_enabled():
                        now = datetime.utcnow()
                        cooldown_passed = (
                            self._last_ensure_time is None
                            or (now - self._last_ensure_time).total_seconds() >= 900
                        )
                        if not self._is_ensuring and cooldown_passed:
                            logger.info("自動觸發 ensure_today_topics 補生成今日主題卡")
                            asyncio.create_task(self.ensure_today_topics())
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

        if self._is_ensuring:
            logger.info("已有 ensure_today_topics 正在執行中，略過")
            return

        self._is_ensuring = True
        self._last_ensure_time = datetime.utcnow()
        try:
            expected = expected_topics_today()
            current_by_cat = await self.topic_repo.count_hkt_today_by_category()
            count = sum(current_by_cat.values())
            deficits = category_deficits(current_by_cat)
            if count >= expected and all(v == 0 for v in deficits.values()):
                logger.info(f"今日主題已足（{count}/{expected}），略過補生成")
                return

            logger.info(
                f"今日主題不足（{count}/{expected}），依分類缺口補生成: {deficits}"
            )
            from app.models.topic import Category

            for category in [Category.FASHION, Category.FOOD, Category.TREND]:
                need = deficits.get(category.value, 0)
                if need <= 0:
                    logger.info(f"{category.value} 已達配額，略過補生成")
                    continue
                try:
                    topics = await self.scheduler_service.trigger_manual_generation(
                        category=category,
                        count=need,
                        respect_quota=True,
                    )
                    logger.info(
                        f"已補生成 {category.value} 主題 ×{len(topics)}（目標缺口 {need}）"
                    )
                except Exception as e:
                    logger.error(f"觸發生成 {category.value} 主題失敗: {e}")
        except Exception as e:
            logger.error(f"確保今日主題失敗: {e}")
        finally:
            self._is_ensuring = False
