"""
配置載入器
從 YAML 文件載入配置，支援熱重載
"""
import logging
import os
from typing import Dict, Any, Optional
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

# 配置檔案目錄
CONFIG_DIR = Path(__file__).parent.parent.parent / "config"


class ConfigLoader:
    """配置載入器"""
    
    _instance: Optional["ConfigLoader"] = None
    _configs: Dict[str, Any] = {}
    _last_modified: Dict[str, float] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._configs = {}
            self._last_modified = {}
    
    def load_config(self, filename: str, force_reload: bool = False) -> Dict[str, Any]:
        """
        載入配置文件
        
        Args:
            filename: 配置文件名（不含路徑）
            force_reload: 是否強制重新載入
            
        Returns:
            配置字典
        """
        filepath = CONFIG_DIR / filename
        
        if not filepath.exists():
            logger.warning(f"配置文件不存在: {filepath}")
            return {}
        
        # 檢查是否需要重新載入
        current_mtime = filepath.stat().st_mtime
        if not force_reload and filename in self._configs:
            if self._last_modified.get(filename) == current_mtime:
                return self._configs[filename]
        
        # 載入配置
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
            
            self._configs[filename] = config
            self._last_modified[filename] = current_mtime
            
            logger.info(f"已載入配置文件: {filename}")
            return config
        except Exception as e:
            logger.error(f"載入配置文件失敗 {filename}: {e}")
            return self._configs.get(filename, {})
    
    def get_topic_generation_config(self) -> Dict[str, Any]:
        """獲取主題生成配置"""
        return self.load_config("topic_generation.yaml")
    
    def get_scoring_config(self) -> Dict[str, Any]:
        """獲取評分配置"""
        config = self.get_topic_generation_config()
        return config.get("scoring", {})
    
    def get_image_search_config(self) -> Dict[str, Any]:
        """獲取圖片搜尋配置"""
        config = self.get_topic_generation_config()
        return config.get("image_search", {})
    
    def get_role_distribution(self, category: str) -> Dict[str, int]:
        """
        獲取分類的角色分配比例
        
        Args:
            category: 分類名稱 (fashion, food, trend)
            
        Returns:
            角色分配字典 {role_name: count}
        """
        config = self.get_topic_generation_config()
        categories = config.get("daily_generation", {}).get("categories", {})
        category_config = categories.get(category.lower(), {})
        return category_config.get("role_distribution", {})
    
    def get_category_count(self, category: str) -> int:
        """
        獲取分類的主題生成數量
        
        Args:
            category: 分類名稱
            
        Returns:
            主題數量
        """
        config = self.get_topic_generation_config()
        categories = config.get("daily_generation", {}).get("categories", {})
        category_config = categories.get(category.lower(), {})
        return category_config.get("count", 10)
    
    def get_health_monitoring_config(self) -> Dict[str, Any]:
        """獲取健康監控配置"""
        config = self.get_topic_generation_config()
        return config.get("health_monitoring", {})
    
    def is_health_monitoring_enabled(self) -> bool:
        """檢查健康監控是否啟用"""
        config = self.get_health_monitoring_config()
        return config.get("enabled", False)
    
    def get_failure_threshold(self) -> int:
        """獲取失敗次數閾值"""
        config = self.get_health_monitoring_config()
        return config.get("failure_threshold", 3)
    
    def get_pause_duration(self) -> int:
        """獲取暫停時長（秒）"""
        config = self.get_health_monitoring_config()
        return config.get("pause_duration", 3600)
    
    def get_diversity_min_score(self) -> float:
        """獲取多樣性最低分數"""
        config = self.get_scoring_config()
        diversity = config.get("diversity", {})
        return diversity.get("min_score", 0.6)
    
    def get_smart_matching_config(self) -> Dict[str, Any]:
        """獲取智能匹配配置"""
        config = self.get_image_search_config()
        return config.get("smart_matching", {})
    
    def get_smart_matching_weights(self) -> Dict[str, float]:
        """獲取智能匹配權重"""
        config = self.get_smart_matching_config()
        return config.get("weights", {
            "keyword": 0.40,
            "trust": 0.25,
            "quality": 0.15,
            "diversity": 0.20
        })
    
    def reload_all(self) -> None:
        """重新載入所有配置"""
        for filename in list(self._configs.keys()):
            self.load_config(filename, force_reload=True)
        logger.info("已重新載入所有配置")


# 創建全域實例
config_loader = ConfigLoader()


def get_config_loader() -> ConfigLoader:
    """獲取配置載入器實例"""
    return config_loader

