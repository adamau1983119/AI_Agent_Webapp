"""
靈感策劃偏好清理服務
根據 v5.0 靈感策劃技術設計報告 - 建議 3：上下文管理需設計「過期與清理」機制

功能：
1. 自動標記過時偏好（90 天未使用）
2. 自動清理過期偏好（180 天未使用）
3. 啟動時提醒機制
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from app.services.inspiration_preference_service import InspirationPreferenceRepository
import logging

logger = logging.getLogger(__name__)


# 清理配置
STALE_THRESHOLD_DAYS = 90  # 90 天未使用視為過時
EXPIRED_THRESHOLD_DAYS = 180  # 180 天未使用自動清理


class InspirationPreferenceCleanupService:
    """偏好清理服務"""
    
    def __init__(self):
        self.preference_repo = InspirationPreferenceRepository()
    
    async def check_and_mark_stale(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        檢查並標記過時偏好
        
        Args:
            user_id: 用戶 ID
            
        Returns:
            Optional[Dict]: 如果標記為過時，返回偏好數據；否則返回 None
        """
        preferences = await self.preference_repo.get_preferences(user_id)
        
        if not preferences:
            return None
        
        usage_stats = preferences.get("usage_stats", {})
        last_used = usage_stats.get("last_used_at")
        
        if not last_used:
            return None
        
        # 轉換為 datetime（如果是字串）
        if isinstance(last_used, str):
            try:
                last_used = datetime.fromisoformat(last_used.replace('Z', '+00:00'))
            except:
                logger.warning(f"無法解析 last_used_at: {last_used}")
                return None
        
        # 移除時區資訊（如果有的話）
        if hasattr(last_used, 'replace'):
            last_used = last_used.replace(tzinfo=None)
        
        days_since_use = (datetime.utcnow() - last_used).days
        
        if days_since_use >= STALE_THRESHOLD_DAYS:
            # 標記為過時
            update_data = {
                "status": "stale",
                "stale_since": datetime.utcnow()
            }
            
            await self.preference_repo.update_preferences(user_id, update_data)
            
            logger.info(
                f"偏好已標記為過時: user_id={user_id}, "
                f"days={days_since_use}, threshold={STALE_THRESHOLD_DAYS}"
            )
            
            # 返回更新後的偏好
            updated_prefs = await self.preference_repo.get_preferences(user_id)
            return updated_prefs
        
        return None
    
    async def auto_cleanup_expired(self, user_id: str) -> bool:
        """
        自動清理過期偏好
        
        Args:
            user_id: 用戶 ID
            
        Returns:
            bool: 是否執行了清理
        """
        preferences = await self.preference_repo.get_preferences(user_id)
        
        if not preferences:
            return False
        
        usage_stats = preferences.get("usage_stats", {})
        last_used = usage_stats.get("last_used_at")
        
        if not last_used:
            return False
        
        # 轉換為 datetime（如果是字串）
        if isinstance(last_used, str):
            try:
                last_used = datetime.fromisoformat(last_used.replace('Z', '+00:00'))
            except:
                logger.warning(f"無法解析 last_used_at: {last_used}")
                return False
        
        # 移除時區資訊（如果有的話）
        if hasattr(last_used, 'replace'):
            last_used = last_used.replace(tzinfo=None)
        
        days_since_use = (datetime.utcnow() - last_used).days
        
        if days_since_use >= EXPIRED_THRESHOLD_DAYS:
            # 重置為預設偏好（保留結構，清除具體值）
            default_prefs = await self.preference_repo.create_default_preferences(user_id)
            
            # 保留 user_id，但重置其他偏好
            update_data = {
                "preferences": default_prefs.get("preferences", {}),
                "usage_stats": {
                    "total_sessions": 0,
                    "most_used_format": "video_script",
                    "most_used_tone": "casual",
                    "last_used_at": datetime.utcnow(),
                    "last_updated": datetime.utcnow()
                },
                "status": "active",
                "confirmation_pending": [],
                "stale_since": None
            }
            
            await self.preference_repo.update_preferences(user_id, update_data)
            
            logger.info(
                f"偏好已自動清理: user_id={user_id}, "
                f"days={days_since_use}, threshold={EXPIRED_THRESHOLD_DAYS}"
            )
            
            return True
        
        return False
    
    async def get_stale_warning(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        取得過時偏好警告（用於啟動時提醒）
        
        Args:
            user_id: 用戶 ID
            
        Returns:
            Optional[Dict]: 如果有過時偏好，返回警告資訊；否則返回 None
        """
        preferences = await self.preference_repo.get_preferences(user_id)
        
        if not preferences:
            return None
        
        if preferences.get("status") != "stale":
            return None
        
        stale_since = preferences.get("stale_since")
        if not stale_since:
            return None
        
        # 轉換為 datetime（如果是字串）
        if isinstance(stale_since, str):
            try:
                stale_since = datetime.fromisoformat(stale_since.replace('Z', '+00:00'))
            except:
                logger.warning(f"無法解析 stale_since: {stale_since}")
                return None
        
        # 移除時區資訊（如果有的話）
        if hasattr(stale_since, 'replace'):
            stale_since = stale_since.replace(tzinfo=None)
        
        stale_days = (datetime.utcnow() - stale_since).days
        
        # 注意：返回的 message 和 suggestion 使用 i18n key，前端根據語言顯示
        # actions 使用 i18n key，前端根據語言顯示對應文字
        return {
            "message_key": "inspiration.preference.staleWarning",  # i18n key
            "message_params": {"days": stale_days},  # 參數
            "suggestion_key": "inspiration.preference.staleSuggestion",  # i18n key
            "actions": [
                {
                    "key": "inspiration.preference.updatePreference",
                    "action": "update_preference"
                },
                {
                    "key": "inspiration.preference.continueUsing",
                    "action": "continue_using"
                },
                {
                    "key": "inspiration.preference.scheduleReminder",
                    "action": "schedule_reminder"
                }
            ],
            "stale_days": stale_days
        }
    
    async def cleanup_all_users(self) -> Dict[str, Any]:
        """
        清理所有用戶的過時偏好（定期任務使用）
        
        Returns:
            Dict: 清理統計
        """
        stats = {
            "stale_marked": 0,
            "expired_cleaned": 0,
            "errors": 0
        }
        
        # 注意：此方法需要取得所有用戶列表
        # 實際實現時需要從 users collection 取得用戶列表
        # 目前為框架實現
        
        logger.info("開始執行偏好清理任務...")
        
        # 範例：假設有用戶列表
        # users = await get_all_users()
        # for user in users:
        #     try:
        #         stale_result = await self.check_and_mark_stale(user["id"])
        #         if stale_result:
        #             stats["stale_marked"] += 1
        #         
        #         cleaned = await self.auto_cleanup_expired(user["id"])
        #         if cleaned:
        #             stats["expired_cleaned"] += 1
        #     except Exception as e:
        #         logger.error(f"清理用戶 {user['id']} 偏好失敗: {e}")
        #         stats["errors"] += 1
        
        logger.info(f"偏好清理任務完成: {stats}")
        
        return stats


# 建立全域實例
inspiration_preference_cleanup_service = InspirationPreferenceCleanupService()

