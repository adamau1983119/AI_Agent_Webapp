"""
PublishQueue Repository
Phase 5: 分發與整合
提供發布佇列的 CRUD 操作
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.services.repositories.base_repository import BaseRepository
from app.models.social_connection import SocialPlatform, PublishStatus
import logging
import secrets

logger = logging.getLogger(__name__)

# 重試配置
RETRY_INTERVALS = [5, 15, 30]  # 分鐘
MAX_RETRIES = 3


class PublishQueueRepository(BaseRepository):
    """PublishQueue Repository"""
    
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        super().__init__("publish_queue", db=db)
        self._indexes_created = False
    
    async def ensure_indexes(self):
        """確保索引存在"""
        if self._indexes_created:
            return
        
        try:
            collection = await self._get_collection()
            
            await collection.create_index("user_id")
            await collection.create_index("content_id")
            await collection.create_index("status")
            await collection.create_index("scheduled_at")
            await collection.create_index("created_at")
            await collection.create_index([("status", 1), ("scheduled_at", 1)])
            
            self._indexes_created = True
            logger.info("PublishQueue 索引創建完成")
        except Exception as e:
            logger.warning(f"創建索引時發生錯誤（可能已存在）: {e}")
            self._indexes_created = True
    
    async def create_publish_job(
        self,
        user_id: str,
        publish_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """建立發布任務"""
        await self.ensure_indexes()
        
        now = datetime.utcnow()
        publish_id = f"pub_{secrets.token_urlsafe(12)}"
        
        # 初始化各平台結果
        platforms = publish_data.get("platforms", [])
        platform_results = {}
        for platform in platforms:
            platform_value = platform.value if isinstance(platform, SocialPlatform) else platform
            platform_results[platform_value] = {
                "status": PublishStatus.PENDING.value,
                "post_id": None,
                "post_url": None,
                "error_message": None,
                "published_at": None,
                "retry_count": 0,
                "next_retry_at": None,
            }
        
        document = {
            "id": publish_id,
            "user_id": user_id,
            "content_id": publish_data.get("content_id"),
            "content": publish_data.get("content"),
            "content_preview": publish_data.get("content", "")[:100],
            "platforms": [p.value if isinstance(p, SocialPlatform) else p for p in platforms],
            "platform_results": platform_results,
            "hashtags": publish_data.get("hashtags", []),
            "image_urls": publish_data.get("image_urls", []),
            "status": PublishStatus.PENDING.value,
            "scheduled_at": publish_data.get("scheduled_at") or now,
            "published_at": None,
            "created_at": now,
            "updated_at": now,
        }
        
        return await self.create(document)
    
    async def get_publish_job(self, publish_id: str) -> Optional[Dict[str, Any]]:
        """取得發布任務"""
        return await self.find_by_id(publish_id, id_field="id")
    
    async def get_user_publish_history(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """取得用戶的發布歷史"""
        await self.ensure_indexes()
        return await self.find_many(
            {"user_id": user_id},
            sort=[("created_at", -1)],
            skip=skip,
            limit=limit
        )
    
    async def get_pending_jobs(
        self,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """取得待處理的發布任務"""
        await self.ensure_indexes()
        now = datetime.utcnow()
        
        return await self.find_many(
            {
                "status": {"$in": [PublishStatus.PENDING.value, PublishStatus.RETRY.value]},
                "scheduled_at": {"$lte": now}
            },
            sort=[("scheduled_at", 1)],
            limit=limit
        )
    
    async def get_retry_jobs(self) -> List[Dict[str, Any]]:
        """取得需要重試的任務"""
        await self.ensure_indexes()
        now = datetime.utcnow()
        
        # 查找有需要重試的平台的任務
        collection = await self._get_collection()
        
        # 使用聚合查詢找出有 retry 狀態平台且重試時間已到的任務
        pipeline = [
            {"$match": {"status": PublishStatus.RETRY.value}},
            {"$addFields": {
                "retry_platforms": {
                    "$filter": {
                        "input": {"$objectToArray": "$platform_results"},
                        "cond": {
                            "$and": [
                                {"$eq": ["$$this.v.status", PublishStatus.RETRY.value]},
                                {"$lte": ["$$this.v.next_retry_at", now]}
                            ]
                        }
                    }
                }
            }},
            {"$match": {"retry_platforms": {"$ne": []}}},
            {"$limit": 10}
        ]
        
        jobs = []
        async for doc in collection.aggregate(pipeline):
            jobs.append(doc)
        
        return jobs
    
    async def update_platform_result(
        self,
        publish_id: str,
        platform: SocialPlatform,
        result_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """更新特定平台的發布結果"""
        platform_value = platform.value if isinstance(platform, SocialPlatform) else platform
        
        update_data = {
            f"platform_results.{platform_value}": result_data,
            "updated_at": datetime.utcnow()
        }
        
        return await self.update_by_id(publish_id, {"$set": update_data}, id_field="id")
    
    async def mark_platform_success(
        self,
        publish_id: str,
        platform: SocialPlatform,
        post_id: str,
        post_url: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """標記平台發布成功"""
        platform_value = platform.value if isinstance(platform, SocialPlatform) else platform
        
        result = await self.update_platform_result(publish_id, platform, {
            "status": PublishStatus.PUBLISHED.value,
            "post_id": post_id,
            "post_url": post_url,
            "published_at": datetime.utcnow(),
            "error_message": None
        })
        
        # 檢查是否所有平台都已完成
        await self._check_and_update_overall_status(publish_id)
        
        return result
    
    async def mark_platform_failed(
        self,
        publish_id: str,
        platform: SocialPlatform,
        error_message: str,
        should_retry: bool = True
    ) -> Optional[Dict[str, Any]]:
        """標記平台發布失敗"""
        platform_value = platform.value if isinstance(platform, SocialPlatform) else platform
        
        # 取得當前任務
        job = await self.get_publish_job(publish_id)
        if not job:
            return None
        
        current_result = job.get("platform_results", {}).get(platform_value, {})
        retry_count = current_result.get("retry_count", 0)
        
        if should_retry and retry_count < MAX_RETRIES:
            # 設定重試
            retry_interval = RETRY_INTERVALS[min(retry_count, len(RETRY_INTERVALS) - 1)]
            next_retry = datetime.utcnow() + timedelta(minutes=retry_interval)
            
            result = await self.update_platform_result(publish_id, platform, {
                "status": PublishStatus.RETRY.value,
                "error_message": error_message,
                "retry_count": retry_count + 1,
                "next_retry_at": next_retry
            })
            
            # 更新整體狀態為 RETRY
            await self.update_by_id(publish_id, {"$set": {
                "status": PublishStatus.RETRY.value,
                "updated_at": datetime.utcnow()
            }}, id_field="id")
        else:
            # 最終失敗
            result = await self.update_platform_result(publish_id, platform, {
                "status": PublishStatus.FAILED.value,
                "error_message": error_message,
                "retry_count": retry_count
            })
            
            # 檢查整體狀態
            await self._check_and_update_overall_status(publish_id)
        
        return result
    
    async def _check_and_update_overall_status(self, publish_id: str):
        """檢查並更新整體發布狀態"""
        job = await self.get_publish_job(publish_id)
        if not job:
            return
        
        platform_results = job.get("platform_results", {})
        
        all_published = True
        any_failed = False
        any_pending = False
        any_retry = False
        
        for result in platform_results.values():
            status = result.get("status")
            if status == PublishStatus.PUBLISHED.value:
                continue
            elif status == PublishStatus.FAILED.value:
                any_failed = True
                all_published = False
            elif status == PublishStatus.RETRY.value:
                any_retry = True
                all_published = False
            else:
                any_pending = True
                all_published = False
        
        if all_published:
            overall_status = PublishStatus.PUBLISHED.value
            published_at = datetime.utcnow()
        elif any_retry:
            overall_status = PublishStatus.RETRY.value
            published_at = None
        elif any_pending:
            overall_status = PublishStatus.PUBLISHING.value
            published_at = None
        else:
            overall_status = PublishStatus.FAILED.value
            published_at = None
        
        await self.update_by_id(publish_id, {"$set": {
            "status": overall_status,
            "published_at": published_at,
            "updated_at": datetime.utcnow()
        }}, id_field="id")
    
    async def count_user_publishes(
        self,
        user_id: str,
        status: Optional[PublishStatus] = None
    ) -> int:
        """計算用戶的發布數量"""
        filter_query = {"user_id": user_id}
        if status:
            filter_query["status"] = status.value
        return await self.count(filter_query)

