"""
Feed 健康狀態 Repository
使用 MongoDB 記錄 RSS Feed 的健康狀態（成功/失敗事件）
支援自動暫停機制：連續 3 次失敗在 1 小時內 → 暫停該來源
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.services.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class FeedHealthRepository(BaseRepository):
    """Feed 健康狀態 Repository"""
    
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        super().__init__("feed_health", db)
        self._indexes_created = False
    
    async def ensure_indexes(self):
        """確保索引存在（首次使用時調用）"""
        if self._indexes_created:
            return
        
        try:
            collection = await self._get_collection()
            
            # 創建索引
            await collection.create_index("feed_url")
            await collection.create_index("timestamp")
            await collection.create_index("status")
            await collection.create_index([("feed_url", 1), ("timestamp", -1)])
            
            # TTL 索引：30 天後自動刪除舊記錄
            await collection.create_index(
                "timestamp",
                expireAfterSeconds=30 * 24 * 60 * 60,  # 30 days
                name="ttl_30_days"
            )
            
            self._indexes_created = True
            logger.info("Feed health 索引創建完成")
        except Exception as e:
            logger.warning(f"創建索引時發生錯誤（可能已存在）: {e}")
            self._indexes_created = True
    
    async def record_failure(self, feed_url: str, error: str, source_name: str = "") -> None:
        """
        記錄一次失敗事件
        
        Args:
            feed_url: Feed URL
            error: 錯誤訊息
            source_name: 來源名稱（可選）
        """
        await self.ensure_indexes()
        
        document = {
            "feed_url": feed_url,
            "source_name": source_name,
            "status": "failure",
            "error": error,
            "timestamp": datetime.utcnow(),
        }
        
        await self.create(document)
        logger.debug(f"記錄 Feed 失敗: {feed_url} - {error}")
        
        # 檢查是否需要暫停
        if await self._should_auto_pause(feed_url):
            logger.warning(f"⚠️ Feed 連續失敗 3 次，自動暫停 1 小時: {feed_url}")
    
    async def record_success(self, feed_url: str, source_name: str = "") -> None:
        """
        記錄一次成功事件
        
        Args:
            feed_url: Feed URL
            source_name: 來源名稱（可選）
        """
        await self.ensure_indexes()
        
        document = {
            "feed_url": feed_url,
            "source_name": source_name,
            "status": "success",
            "timestamp": datetime.utcnow(),
        }
        
        await self.create(document)
        logger.debug(f"記錄 Feed 成功: {feed_url}")
    
    async def is_paused(self, feed_url: str) -> bool:
        """
        檢查 Feed 是否應該暫停（過去 1 小時內連續失敗 3+ 次）
        
        Args:
            feed_url: Feed URL
            
        Returns:
            True 如果應該暫停，False 如果可以繼續使用
        """
        await self.ensure_indexes()
        
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        collection = await self._get_collection()
        
        # 計算過去 1 小時的失敗次數
        failure_count = await collection.count_documents({
            "feed_url": feed_url,
            "status": "failure",
            "timestamp": {"$gte": one_hour_ago}
        })
        
        # 檢查最近一次成功是否在這些失敗之後
        last_success = await collection.find_one(
            {
                "feed_url": feed_url,
                "status": "success",
                "timestamp": {"$gte": one_hour_ago}
            },
            sort=[("timestamp", -1)]
        )
        
        if last_success:
            # 如果有成功記錄，計算成功之後的失敗次數
            failures_after_success = await collection.count_documents({
                "feed_url": feed_url,
                "status": "failure",
                "timestamp": {"$gt": last_success["timestamp"]}
            })
            return failures_after_success >= 3
        
        return failure_count >= 3
    
    async def _should_auto_pause(self, feed_url: str) -> bool:
        """檢查是否達到自動暫停條件"""
        return await self.is_paused(feed_url)
    
    async def get_health_report(self, feed_url: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        獲取 Feed 的健康報告（最近 N 筆記錄）
        
        Args:
            feed_url: Feed URL
            limit: 返回記錄數量
            
        Returns:
            健康記錄列表
        """
        await self.ensure_indexes()
        
        collection = await self._get_collection()
        cursor = collection.find(
            {"feed_url": feed_url}
        ).sort("timestamp", -1).limit(limit)
        
        records = await cursor.to_list(length=limit)
        
        # 轉換 ObjectId 為字串
        for record in records:
            if "_id" in record:
                record["_id"] = str(record["_id"])
        
        return records
    
    async def get_reliability_score(self, feed_url: str, days: int = 7) -> float:
        """
        計算 Feed 在過去 N 天的可靠度分數
        
        Args:
            feed_url: Feed URL
            days: 統計天數
            
        Returns:
            可靠度分數 (0.0 - 1.0)
        """
        await self.ensure_indexes()
        
        since = datetime.utcnow() - timedelta(days=days)
        collection = await self._get_collection()
        
        # 計算總記錄數
        total = await collection.count_documents({
            "feed_url": feed_url,
            "timestamp": {"$gte": since}
        })
        
        if total == 0:
            return 1.0  # 無記錄視為健康（新來源）
        
        # 計算成功次數
        successes = await collection.count_documents({
            "feed_url": feed_url,
            "status": "success",
            "timestamp": {"$gte": since}
        })
        
        return round(successes / total, 4)
    
    async def get_all_feed_health(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        獲取所有 Feed 的健康狀態摘要
        
        Args:
            category: 分類過濾（可選）
            
        Returns:
            各 Feed 的健康狀態列表
        """
        await self.ensure_indexes()
        
        collection = await self._get_collection()
        
        # 聚合查詢：按 feed_url 分組，計算統計數據
        pipeline = [
            {
                "$match": {
                    "timestamp": {"$gte": datetime.utcnow() - timedelta(days=7)}
                }
            },
            {
                "$group": {
                    "_id": "$feed_url",
                    "source_name": {"$first": "$source_name"},
                    "total_requests": {"$sum": 1},
                    "success_count": {
                        "$sum": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}
                    },
                    "failure_count": {
                        "$sum": {"$cond": [{"$eq": ["$status", "failure"]}, 1, 0]}
                    },
                    "last_status": {"$last": "$status"},
                    "last_timestamp": {"$max": "$timestamp"},
                    "last_error": {
                        "$last": {
                            "$cond": [{"$eq": ["$status", "failure"]}, "$error", None]
                        }
                    }
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "feed_url": "$_id",
                    "source_name": 1,
                    "total_requests": 1,
                    "success_count": 1,
                    "failure_count": 1,
                    "reliability_score": {
                        "$cond": [
                            {"$gt": ["$total_requests", 0]},
                            {"$divide": ["$success_count", "$total_requests"]},
                            1.0
                        ]
                    },
                    "last_status": 1,
                    "last_timestamp": 1,
                    "last_error": 1
                }
            },
            {
                "$sort": {"reliability_score": 1}  # 最不可靠的排在前面
            }
        ]
        
        cursor = collection.aggregate(pipeline)
        results = await cursor.to_list(length=None)
        
        # 添加 is_paused 狀態
        for result in results:
            result["is_paused"] = await self.is_paused(result["feed_url"])
            
            # 計算健康狀態
            score = result.get("reliability_score", 1.0)
            if result["is_paused"]:
                result["health_status"] = "paused"
            elif score >= 0.9:
                result["health_status"] = "healthy"
            elif score >= 0.7:
                result["health_status"] = "degraded"
            else:
                result["health_status"] = "unhealthy"
        
        return results
    
    async def get_stats_summary(self) -> Dict[str, Any]:
        """
        獲取整體統計摘要
        
        Returns:
            統計摘要
        """
        await self.ensure_indexes()
        
        collection = await self._get_collection()
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        one_day_ago = datetime.utcnow() - timedelta(days=1)
        
        # 過去 1 小時統計
        hour_total = await collection.count_documents({
            "timestamp": {"$gte": one_hour_ago}
        })
        hour_failures = await collection.count_documents({
            "status": "failure",
            "timestamp": {"$gte": one_hour_ago}
        })
        
        # 過去 24 小時統計
        day_total = await collection.count_documents({
            "timestamp": {"$gte": one_day_ago}
        })
        day_failures = await collection.count_documents({
            "status": "failure",
            "timestamp": {"$gte": one_day_ago}
        })
        
        # 獲取暫停的 Feed 數量
        all_health = await self.get_all_feed_health()
        paused_count = sum(1 for h in all_health if h.get("is_paused"))
        
        return {
            "last_hour": {
                "total_requests": hour_total,
                "failures": hour_failures,
                "success_rate": round((hour_total - hour_failures) / hour_total, 4) if hour_total > 0 else 1.0
            },
            "last_24_hours": {
                "total_requests": day_total,
                "failures": day_failures,
                "success_rate": round((day_total - day_failures) / day_total, 4) if day_total > 0 else 1.0
            },
            "feeds": {
                "total_tracked": len(all_health),
                "healthy": sum(1 for h in all_health if h.get("health_status") == "healthy"),
                "degraded": sum(1 for h in all_health if h.get("health_status") == "degraded"),
                "unhealthy": sum(1 for h in all_health if h.get("health_status") == "unhealthy"),
                "paused": paused_count
            },
            "generated_at": datetime.utcnow()
        }

