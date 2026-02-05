"""
資料庫操作服務（Repository Pattern）
提供 CRUD 操作和查詢功能
"""
from app.services.repositories.topic_repository import TopicRepository
from app.services.repositories.content_repository import ContentRepository
from app.services.repositories.image_repository import ImageRepository
from app.services.repositories.user_preferences_repository import UserPreferencesRepository
from app.services.repositories.audit_log_repository import AuditLogRepository

# Phase 6: 新增 Article 和 Photo Repository
from app.services.repositories.article_repository import ArticleRepository
from app.services.repositories.photo_repository import PhotoRepository

__all__ = [
    # 原有 Repository
    "TopicRepository",
    "ContentRepository",
    "ImageRepository",
    "UserPreferencesRepository",
    "AuditLogRepository",
    # Phase 6: 新增 Repository
    "ArticleRepository",
    "PhotoRepository",
]
