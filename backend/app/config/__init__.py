"""
配置模組
包含應用設定和主題生成配置
"""
# 從 config_module.py 導入 Settings 並創建實例
from app.config_module import Settings

# 創建 settings 實例（單例模式）
settings = Settings()

# 也導出 topic_config
from app.config.topic_config import get_topic_config, TopicGenerationConfig

__all__ = ['settings', 'get_topic_config', 'TopicGenerationConfig']

