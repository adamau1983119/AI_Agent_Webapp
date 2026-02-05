"""
排程服務 v4.1
使用 APScheduler 執行定時任務
支援：
- 每 6 小時收集（Phase 1, v4.1 更新）
- 分層資料清理（Phase 1, v4.1 更新）
- 分級健康監控（Phase 1）
- 每週 RSS 驗證（v4.1 新增）
"""
import logging
from datetime import datetime, time, timedelta
from typing import Dict, Any, List, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from app.services.automation.topic_collector import TopicCollector
from app.services.automation.workflow import AutomationWorkflow
from app.services.repositories.topic_repository import TopicRepository
from app.models.topic import Category, Status
from app.config.topic_config import get_topic_config

logger = logging.getLogger(__name__)


class SchedulerService:
    """排程服務 v4.1 - 支援多種排程模式 + RSS 驗證"""
    
    def __init__(self):
        logger.info("開始初始化 SchedulerService v4.1...")
        try:
            logger.info("初始化 AsyncIOScheduler...")
            self.scheduler = AsyncIOScheduler()
            logger.info("初始化 TopicCollector...")
            self.topic_collector = TopicCollector()
            logger.info("初始化 AutomationWorkflow...")
            self.workflow = AutomationWorkflow()
            logger.info("初始化 TopicRepository...")
            self.topic_repo = TopicRepository()
            logger.info("設置運行狀態...")
            self.is_running = False
            logger.info("載入配置檔...")
            self.config = get_topic_config()  # 載入配置檔
            logger.info("SchedulerService v4.1 初始化完成")
        except Exception as e:
            import traceback
            logger.error(f"SchedulerService 初始化過程中發生錯誤: {e}")
            logger.error(f"錯誤類型: {type(e).__name__}")
            logger.error(f"完整錯誤堆疊:\n{traceback.format_exc()}")
            raise
    
    def start(self):
        """啟動排程服務"""
        if self.is_running:
            logger.warning("排程服務已經在運行")
            return
        
        # Phase 1: 根據配置決定收集模式
        collection_mode = self.config.get_collection_mode()
        logger.info(f"收集模式: {collection_mode}")
        
        if collection_mode == "interval":
            self._setup_interval_collection()
        else:
            self._setup_daily_collection()
        
        # Phase 1: 設定資料清理任務
        self._setup_data_cleanup()
        
        # v4.1: 設定 RSS 驗證任務（每週日 04:00 UTC）
        self._setup_rss_validation()
        
        self.scheduler.start()
        self.is_running = True
        logger.info("排程服務已啟動")
    
    def _setup_interval_collection(self):
        """設定間隔收集（每 6 小時，v4.1 更新）"""
        collection_hours = self.config.get_collection_hours()
        interval_hours = self.config.get_interval_hours()
        categories = [Category.FASHION, Category.FOOD, Category.TREND]
        
        logger.info(f"設定每 {interval_hours} 小時收集模式，收集時間點 (UTC): {collection_hours}")
        
        for hour in collection_hours:
            for category in categories:
                category_name = category.value
                job_id = f"{category_name}_topics_interval_{hour:02d}00"
                
                self.scheduler.add_job(
                    self._generate_topics_for_category,
                    CronTrigger(hour=hour, minute=0, timezone='UTC'),
                    id=job_id,
                    args=[category, f"{hour:02d}:00 UTC"],
                    replace_existing=True
                )
                
                logger.info(f"排程任務已設定: {job_id} - {category_name} 分類，{hour:02d}:00 UTC")
    
    def _setup_daily_collection(self):
        """設定每日收集（向後相容）"""
        hkt_time_str = self.config.get_daily_generation_time()
        utc_time = self.config.get_utc_time_for_schedule()
        
        logger.info(f"設定每日收集模式: {hkt_time_str} ({self.config.get_daily_generation_timezone()})")
        logger.info(f"轉換為 UTC 時間: {utc_time.hour:02d}:{utc_time.minute:02d}")
        
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
            
            logger.info(f"排程任務已設定: {job_id} - {category_name} 分類，{hkt_time_str} HKT")
    
    def _setup_data_cleanup(self):
        """設定資料清理任務（Phase 1: 分層保留）"""
        cleanup_config = self.config.get_data_cleanup_config()
        
        if not cleanup_config.get("enabled", True):
            logger.info("資料清理功能已停用")
            return
        
        cleanup_hour = cleanup_config.get("cleanup_hour", 3)
        cleanup_minute = cleanup_config.get("cleanup_minute", 0)
        
        self.scheduler.add_job(
            self._cleanup_old_data,
            CronTrigger(hour=cleanup_hour, minute=cleanup_minute, timezone='UTC'),
            id="data_cleanup_daily",
            replace_existing=True
        )
        
        logger.info(f"資料清理任務已設定: 每日 {cleanup_hour:02d}:{cleanup_minute:02d} UTC")
    
    def _setup_rss_validation(self):
        """設定 RSS 驗證任務（v4.1: 每週日 04:00 UTC）"""
        self.scheduler.add_job(
            self._validate_rss_sources,
            CronTrigger(day_of_week='sun', hour=4, minute=0, timezone='UTC'),
            id="rss_validation_weekly",
            replace_existing=True
        )
        
        logger.info("RSS 驗證任務已設定: 每週日 04:00 UTC")
    
    async def _validate_rss_sources(self):
        """
        執行 RSS 來源驗證（v4.1 新增）
        """
        logger.info("🔍 開始執行每週 RSS 驗證...")
        
        try:
            from app.services.rss_validator import RSSValidator
            from pathlib import Path
            
            validator = RSSValidator(timeout=15.0)
            report = await validator.validate_all_channel_sources()
            
            # 生成報告
            report_md = validator.generate_report_markdown(report)
            
            # 保存報告
            report_path = Path(__file__).parent.parent.parent / "RSS_驗證報告.md"
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report_md)
            
            # 記錄結果
            logger.info(f"✅ RSS 驗證完成: {report['valid_count']}/{report['total_sources']} 有效")
            logger.info(f"⚠️ 空: {report['empty_count']}, ❌ 錯誤: {report['error_count']}")
            logger.info(f"📄 報告已保存: {report_path}")
            
            # 如果錯誤率超過 20%，記錄警告
            error_rate = report['error_count'] / report['total_sources'] if report['total_sources'] > 0 else 0
            if error_rate > 0.2:
                logger.warning(f"⚠️ RSS 錯誤率過高: {error_rate:.1%}，請檢查來源配置")
            
        except Exception as e:
            logger.error(f"RSS 驗證任務失敗: {e}")
    
    async def _cleanup_old_data(self):
        """
        清理過期資料（Phase 1: 15 天）
        """
        logger.info("開始執行資料清理任務...")
        
        try:
            cleanup_config = self.config.get_data_cleanup_config()
            retention_days = cleanup_config.get("retention_days", 15)
            batch_size = cleanup_config.get("batch_size", 100)
            
            # 計算過期日期
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            logger.info(f"清理 {retention_days} 天前的資料（截止日期: {cutoff_date}）")
            
            # 批次刪除過期主題
            total_deleted = 0
            while True:
                deleted_count = await self.topic_repo.delete_topics_before_date(
                    cutoff_date=cutoff_date,
                    batch_size=batch_size
                )
                
                if deleted_count == 0:
                    break
                
                total_deleted += deleted_count
                logger.info(f"已刪除 {deleted_count} 個過期主題（累計: {total_deleted}）")
            
            logger.info(f"資料清理完成，共刪除 {total_deleted} 個過期主題")
            
        except Exception as e:
            logger.error(f"資料清理任務失敗: {e}")
    
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
                    
                    # Phase 5A：從 sources[].images 提取預覽圖片
                    preview_images = []
                    for source in topic_data.get("sources", []):
                        source_imgs = source.get("images", [])
                        preview_images.extend(source_imgs[:3])  # 每個來源最多取 3 張
                    topic_data["preview_images"] = preview_images[:5] if preview_images else []  # 最多 5 張
                    
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
        count: int = 10
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
                    
                    # Phase 5A：從 sources[].images 提取預覽圖片
                    preview_images = []
                    for source in topic_data.get("sources", []):
                        source_imgs = source.get("images", [])
                        preview_images.extend(source_imgs[:3])  # 每個來源最多取 3 張
                    topic_data["preview_images"] = preview_images[:5] if preview_images else []  # 最多 5 張
                    
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

