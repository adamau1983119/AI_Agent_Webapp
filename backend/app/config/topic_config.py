"""
主題生成配置檔讀取系統
從 YAML 配置檔讀取主題生成參數
"""
import os
import yaml
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import time
import pytz

logger = logging.getLogger(__name__)


class TopicGenerationConfig:
    """主題生成配置"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置
        
        Args:
            config_path: 配置檔路徑（可選，預設為 backend/config/topic_generation.yaml）
        """
        if config_path is None:
            # 預設路徑：從 app 目錄向上兩層到 backend/config
            base_dir = Path(__file__).parent.parent.parent
            config_path = base_dir / "config" / "topic_generation.yaml"
        
        self.config_path = Path(config_path)
        self._config: Optional[Dict[str, Any]] = None
        self._load_config()
    
    def _load_config(self):
        """載入配置檔"""
        try:
            if not self.config_path.exists():
                logger.warning(f"配置檔不存在: {self.config_path}，使用預設配置")
                self._config = self._get_default_config()
                return
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}
            
            # 驗證配置
            self._validate_config()
            
            logger.info(f"配置檔載入成功: {self.config_path}")
            
        except Exception as e:
            logger.error(f"載入配置檔失敗: {e}，使用預設配置")
            self._config = self._get_default_config()
    
    def _validate_config(self):
        """驗證配置檔結構"""
        if not isinstance(self._config, dict):
            raise ValueError("配置檔必須是字典格式")
        
        # 驗證 daily_generation
        if "daily_generation" not in self._config:
            logger.warning("配置檔缺少 daily_generation，使用預設值")
            self._config["daily_generation"] = self._get_default_config()["daily_generation"]
        
        # 驗證 categories
        daily_gen = self._config["daily_generation"]
        if "categories" not in daily_gen:
            logger.warning("配置檔缺少 categories，使用預設值")
            daily_gen["categories"] = self._get_default_config()["daily_generation"]["categories"]
    
    def _get_default_config(self) -> Dict[str, Any]:
        """取得預設配置"""
        return {
            "daily_generation": {
                "time": "07:00",
                "timezone": "Asia/Hong_Kong",
                "categories": {
                    "fashion": {
                        "count": 10,
                        "preview_images": 1,
                        "generate_content": False
                    },
                    "food": {
                        "count": 10,
                        "preview_images": 1,
                        "generate_content": False
                    },
                    "trend": {
                        "count": 10,
                        "preview_images": 1,
                        "generate_content": False
                    }
                }
            },
            "image_search": {
                "preview": {
                    "count": 1,
                    "keywords_enhancement": [
                        "editorial fashion",
                        "luxury",
                        "high-end",
                        "professional photography"
                    ],
                    "quality": {
                        "min_resolution": "1920x1080",
                        "min_saturation": 0.6
                    }
                },
                "full": {
                    "count": 8,
                    "use_content_keywords": True
                }
            },
            "daily_limit": {
                "enabled": True,
                "unique_key": "date_category"
            }
        }
    
    def get_daily_generation_time(self) -> str:
        """取得每日生成時間（格式：HH:MM）"""
        return self._config.get("daily_generation", {}).get("time", "07:00")
    
    def get_daily_generation_timezone(self) -> str:
        """取得每日生成時區"""
        return self._config.get("daily_generation", {}).get("timezone", "Asia/Hong_Kong")
    
    def get_category_config(self, category: str) -> Dict[str, Any]:
        """
        取得分類配置
        
        Args:
            category: 分類名稱（fashion, food, trend）
            
        Returns:
            分類配置字典
        """
        categories = self._config.get("daily_generation", {}).get("categories", {})
        return categories.get(category, {
            "count": 10,
            "preview_images": 1,
            "generate_content": False
        })
    
    def get_category_count(self, category: str) -> int:
        """取得分類的生成數量"""
        config = self.get_category_config(category)
        return config.get("count", 10)
    
    def get_preview_images_count(self, category: str) -> int:
        """取得預覽圖片數量"""
        config = self.get_category_config(category)
        return config.get("preview_images", 1)
    
    def should_generate_content(self, category: str) -> bool:
        """檢查是否應該生成內容"""
        config = self.get_category_config(category)
        return config.get("generate_content", False)
    
    def get_image_search_config(self, mode: str = "preview") -> Dict[str, Any]:
        """
        取得圖片搜尋配置
        
        Args:
            mode: 搜尋模式（preview 或 full）
            
        Returns:
            圖片搜尋配置字典
        """
        image_search = self._config.get("image_search", {})
        return image_search.get(mode, {
            "count": 1 if mode == "preview" else 8,
            "keywords_enhancement": [] if mode == "full" else [
                "editorial fashion",
                "luxury",
                "high-end",
                "professional photography"
            ]
        })
    
    def get_preview_keywords_enhancement(self) -> List[str]:
        """取得 Preview 模式的關鍵字增強列表"""
        preview_config = self.get_image_search_config("preview")
        return preview_config.get("keywords_enhancement", [])
    
    def is_daily_limit_enabled(self) -> bool:
        """檢查是否啟用每日限制"""
        daily_limit = self._config.get("daily_limit", {})
        return daily_limit.get("enabled", True)
    
    def get_daily_limit_unique_key(self) -> str:
        """取得每日限制的唯一鍵類型"""
        daily_limit = self._config.get("daily_limit", {})
        return daily_limit.get("unique_key", "date_category")
    
    def get_utc_time_for_schedule(self) -> time:
        """
        取得 UTC 時間（用於排程）
        
        Returns:
            UTC 時間的 time 對象
        """
        hkt_time_str = self.get_daily_generation_time()
        timezone_str = self.get_daily_generation_timezone()
        
        # 解析時間字串（格式：HH:MM）
        hour, minute = map(int, hkt_time_str.split(":"))
        
        # 建立時區對象
        tz = pytz.timezone(timezone_str)
        
        # 建立今天的時間（使用當前日期）
        from datetime import datetime, date
        today = date.today()
        hkt_datetime = tz.localize(datetime.combine(today, time(hour, minute)))
        
        # 轉換為 UTC
        utc_datetime = hkt_datetime.astimezone(pytz.UTC)
        
        return utc_datetime.time()
    
    # ============================================
    # Phase 1: 新增方法 - 收集排程設定
    # ============================================
    
    def get_collection_mode(self) -> str:
        """
        取得收集模式
        
        Returns:
            "interval" 或 "daily"
        """
        return self._config.get("collection_schedule", {}).get("mode", "daily")
    
    def get_collection_hours(self) -> List[int]:
        """
        取得收集時間點（每 4 小時模式）
        
        Returns:
            收集時間點列表（UTC 小時）
        """
        return self._config.get("collection_schedule", {}).get(
            "collection_hours", [0, 4, 8, 12, 16, 20]
        )
    
    def get_interval_hours(self) -> int:
        """取得收集間隔（小時）"""
        return self._config.get("collection_schedule", {}).get("interval_hours", 4)
    
    # ============================================
    # Phase 1: 新增方法 - 資料清理設定
    # ============================================
    
    def get_data_cleanup_config(self) -> Dict[str, Any]:
        """
        取得資料清理配置
        
        Returns:
            資料清理配置字典
        """
        default = {
            "enabled": True,
            "retention_days": 15,
            "cleanup_hour": 3,
            "cleanup_minute": 0,
            "batch_size": 100
        }
        return self._config.get("data_cleanup", default)
    
    def get_retention_days(self) -> int:
        """取得資料保留天數"""
        return self.get_data_cleanup_config().get("retention_days", 15)
    
    # ============================================
    # Phase 1: 新增方法 - 分級健康監控設定
    # ============================================
    
    def get_health_monitoring_config(self) -> Dict[str, Any]:
        """取得健康監控配置"""
        return self._config.get("health_monitoring", {})
    
    def get_health_level_config(self, level: int) -> Dict[str, Any]:
        """
        取得特定等級的健康監控配置
        
        Args:
            level: 健康等級（1-4）
            
        Returns:
            該等級的配置字典
        """
        config = self.get_health_monitoring_config()
        return config.get(f"level_{level}", {})
    
    # ============================================
    # Phase 1: 新增方法 - RSS 來源名單管理
    # ============================================
    
    def get_rss_source_lists_config(self) -> Dict[str, Any]:
        """取得 RSS 來源名單配置"""
        return self._config.get("rss_source_lists", {})
    
    def get_whitelist_config(self) -> Dict[str, Any]:
        """取得白名單配置"""
        return self.get_rss_source_lists_config().get("whitelist", {"enabled": True})
    
    def get_blacklist_config(self) -> Dict[str, Any]:
        """取得黑名單配置"""
        return self.get_rss_source_lists_config().get("blacklist", {"enabled": True, "sources": []})
    
    def get_greylist_config(self) -> Dict[str, Any]:
        """取得灰名單配置"""
        return self.get_rss_source_lists_config().get("greylist", {"enabled": True})
    
    # ============================================
    # Phase 1: 新增方法 - 多樣性門檻
    # ============================================
    
    def get_diversity_threshold(self, category: str) -> Dict[str, Any]:
        """
        取得特定分類的多樣性門檻
        
        Args:
            category: 分類名稱
            
        Returns:
            多樣性門檻配置
        """
        thresholds = self._config.get("diversity_thresholds", {})
        default = {"min_score": 0.6, "min_sources": 3}
        return thresholds.get(category.lower(), default)
    
    def reload(self):
        """重新載入配置檔"""
        self._load_config()


# 全域配置實例（單例模式）
_config_instance: Optional[TopicGenerationConfig] = None


def get_topic_config() -> TopicGenerationConfig:
    """
    取得配置實例（單例模式）
    
    Returns:
        TopicGenerationConfig 實例
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = TopicGenerationConfig()
    return _config_instance

