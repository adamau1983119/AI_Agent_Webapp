"""
Channel 服務
Phase 3: 內容功能
包含三層備用機制（確保頻道永不空白）
"""
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from app.services.repositories.channel_repository import ChannelRepository, MAX_CHANNELS_PER_USER
from app.models.channel import (
    ChannelCreate, ChannelUpdate, ChannelResponse,
    ChannelCategory, ChannelRegion, ChannelStatus, ChannelCollectionStatus,
    DEFAULT_RSS_SOURCES, CATEGORY_FALLBACK_MAP, REGION_LANGUAGE_MAP
)
from app.utils.i18n import get_error_message
import logging

logger = logging.getLogger(__name__)


class ChannelService:
    """Channel 服務"""
    
    def __init__(self):
        self.channel_repo = ChannelRepository()
    
    async def create_channel(
        self,
        user_id: str,
        channel_data: ChannelCreate,
        language: str = "zh-TW"
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        建立頻道
        
        Args:
            user_id: 用戶 ID
            channel_data: 頻道資料
            language: 用戶語言（zh-TW/en/ja）
            
        Returns:
            (頻道資料, 錯誤訊息)
        """
        # 檢查用戶頻道數量
        current_count = await self.channel_repo.count_user_channels(user_id)
        if current_count >= MAX_CHANNELS_PER_USER:
            return None, get_error_message("channel.max_reached_detail", language, max=MAX_CHANNELS_PER_USER)
        
        # 驗證自定義關鍵字
        if channel_data.category == ChannelCategory.OTHER:
            if not channel_data.custom_keywords or len(channel_data.custom_keywords) == 0:
                return None, get_error_message("channel.custom_keywords_required", language)
        
        # 建立頻道
        channel = await self.channel_repo.create_channel(
            user_id=user_id,
            channel_data=channel_data.model_dump()
        )
        
        if not channel:
            return None, get_error_message("channel.create_failed", language)
        
        logger.info(f"用戶 {user_id} 建立頻道: {channel['id']} ({channel_data.category.value})")
        
        return channel, None
    
    async def get_user_channels(
        self,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """取得用戶的所有頻道"""
        return await self.channel_repo.get_user_channels(user_id)
    
    async def get_channel(
        self,
        user_id: str,
        channel_id: str
    ) -> Optional[Dict[str, Any]]:
        """取得用戶的特定頻道"""
        return await self.channel_repo.get_user_channel(user_id, channel_id)
    
    async def update_channel(
        self,
        user_id: str,
        channel_id: str,
        update_data: ChannelUpdate,
        language: str = "zh-TW"
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        更新頻道
        
        Args:
            user_id: 用戶 ID
            channel_id: 頻道 ID
            update_data: 更新資料
            language: 用戶語言（zh-TW/en/ja）
            
        Returns:
            (更新後的頻道, 錯誤訊息)
        """
        # 確認頻道存在且屬於用戶
        channel = await self.channel_repo.get_user_channel(user_id, channel_id)
        if not channel:
            return None, get_error_message("channel.not_found", language)
        
        # 過濾空值
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
        
        if not update_dict:
            return channel, None
        
        # 更新頻道
        updated = await self.channel_repo.update_channel(channel_id, update_dict)
        
        if not updated:
            return None, get_error_message("channel.update_failed", language)
        
        logger.info(f"用戶 {user_id} 更新頻道: {channel_id}")
        
        return updated, None
    
    async def delete_channel(
        self,
        user_id: str,
        channel_id: str,
        language: str = "zh-TW"
    ) -> Tuple[bool, Optional[str]]:
        """
        刪除頻道
        
        Args:
            user_id: 用戶 ID
            channel_id: 頻道 ID
            language: 用戶語言（zh-TW/en/ja）
            
        Returns:
            (是否成功, 錯誤訊息)
        """
        success = await self.channel_repo.delete_channel(channel_id, user_id)
        
        if not success:
            return False, get_error_message("channel.delete_failed", language)
        
        logger.info(f"用戶 {user_id} 刪除頻道: {channel_id}")
        
        return True, None
    
    def list_default_primary_feeds(
        self,
        category: ChannelCategory,
        region: ChannelRegion,
    ) -> List[Dict[str, Any]]:
        """建立頻道 Step 2：回傳該類別＋地區之預設 RSS 候選（與 Layer 1 相同列表）"""
        return [dict(s) for s in self._get_primary_sources(category, region)]
    
    def get_rss_sources_for_channel(
        self,
        channel: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        取得頻道的 RSS 來源（三層備用機制）
        
        Layer 1: 主要來源（類別 + 地區，或使用者 **selected_feeds**）
        Layer 2: 備用來源（相近類別，僅在 Layer 1 不足時由收集器啟用）
        Layer 3: AI 生成（僅在 RSS 全數失敗時，由收集器觸發）
        
        若頻道存有 **selected_feeds**，Layer 1 僅用使用者選取；Layer 2 仍可提供相近類別備援。
        
        Args:
            channel: 頻道資料
            
        Returns:
            RSS 來源列表（含層級標記）
        """
        category = ChannelCategory(channel.get("category", ChannelCategory.TREND.value))
        region = ChannelRegion(channel.get("region", ChannelRegion.GLOBAL.value))
        
        sources = []
        raw_selected = channel.get("selected_feeds") or []

        if raw_selected:
            for feed in raw_selected[:10]:
                if not isinstance(feed, dict):
                    continue
                url = (feed.get("url") or "").strip()
                if not url.startswith(("http://", "https://")):
                    continue
                name = (feed.get("name") or "").strip() or "RSS"
                role = (feed.get("role") or "").strip() or "selected"
                sources.append({
                    "name": name,
                    "url": url,
                    "role": role,
                    "layer": 1,
                    "category": category.value,
                    "region": region.value,
                })
            if sources:
                fallback_categories = CATEGORY_FALLBACK_MAP.get(category, [])
                for fallback_cat in fallback_categories:
                    fallback_sources = self._get_primary_sources(fallback_cat, region)
                    for source in fallback_sources[:2]:
                        s = dict(source)
                        s["layer"] = 2
                        s["category"] = fallback_cat.value
                        s["region"] = region.value
                        sources.append(s)
                return sources
            # selected_feeds 鍵存在但無有效 URL：改走下方預設邏輯
        
        # Layer 1: 主要來源（類別 + 地區預設池）
        primary_sources = self._get_primary_sources(category, region)
        for source in primary_sources:
            s = dict(source)
            s["layer"] = 1
            s["category"] = category.value
            s["region"] = region.value
            sources.append(s)
        
        # Layer 2: 備用來源（相近類別）
        fallback_categories = CATEGORY_FALLBACK_MAP.get(category, [])
        for fallback_cat in fallback_categories:
            fallback_sources = self._get_primary_sources(fallback_cat, region)
            for source in fallback_sources[:2]:
                s = dict(source)
                s["layer"] = 2
                s["category"] = fallback_cat.value
                s["region"] = region.value
                sources.append(s)
        
        return sources
    
    def _get_primary_sources(
        self,
        category: ChannelCategory,
        region: ChannelRegion
    ) -> List[Dict[str, Any]]:
        """取得主要 RSS 來源"""
        # 檢查該類別是否有預設來源
        if category not in DEFAULT_RSS_SOURCES:
            # 使用 TREND 作為預設
            category = ChannelCategory.TREND
        
        category_sources = DEFAULT_RSS_SOURCES.get(category, {})
        region_sources = category_sources.get(region, [])
        
        if not region_sources:
            # 使用 GLOBAL 作為預設
            region_sources = category_sources.get(ChannelRegion.GLOBAL, [])
        
        return [source.copy() for source in region_sources]
    
    def get_target_language(
        self,
        channel: Dict[str, Any],
        user_language: str = "zh-TW"
    ) -> str:
        """
        取得頻道的目標語言
        
        邏輯：
        - 使用用戶的語言偏好
        - 如果用戶語言與地區不符，仍使用用戶語言
        
        Args:
            channel: 頻道資料
            user_language: 用戶語言偏好
            
        Returns:
            目標語言代碼
        """
        return user_language
    
    async def get_available_categories(self) -> List[Dict[str, str]]:
        """取得可用的類別列表"""
        return [
            {"value": cat.value, "label": self._get_category_label(cat)}
            for cat in ChannelCategory
        ]
    
    async def get_available_regions(self) -> List[Dict[str, str]]:
        """取得可用的地區列表"""
        return [
            {"value": region.value, "label": self._get_region_label(region)}
            for region in ChannelRegion
        ]
    
    def _get_category_label(self, category: ChannelCategory) -> str:
        """取得類別標籤"""
        labels = {
            ChannelCategory.FASHION: "時尚",
            ChannelCategory.FOOD: "美食",
            ChannelCategory.TREND: "趨勢",
            ChannelCategory.FINANCE: "財經",
            ChannelCategory.SPORTS: "運動",
            ChannelCategory.TECH: "科技",
            ChannelCategory.ENTERTAINMENT: "娛樂",
            ChannelCategory.OTHER: "其他（自定義）",
        }
        return labels.get(category, category.value)
    
    def _get_region_label(self, region: ChannelRegion) -> str:
        """取得地區標籤"""
        labels = {
            ChannelRegion.HONG_KONG: "香港",
            ChannelRegion.TAIWAN: "台灣",
            ChannelRegion.JAPAN: "日本",
            ChannelRegion.KOREA: "韓國",
            ChannelRegion.CHINA: "中國大陸",
            ChannelRegion.USA: "美國",
            ChannelRegion.UK: "英國",
            ChannelRegion.GLOBAL: "全球",
        }
        return labels.get(region, region.value)


# 建立全域實例
channel_service = ChannelService()

