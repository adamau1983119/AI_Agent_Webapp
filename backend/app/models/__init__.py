"""
資料模型模組
包含所有 MongoDB 文檔模型
"""
from app.models.topic import Topic, Category, Status, SourceInfo, SourceStyle
from app.models.content import Content
from app.models.image import Image, ImageSource, ImageType
from app.models.user_preferences import UserPreferences
from app.models.audit_log import AuditLog

# Phase 6: 新增 Article 和 Photo 模型
from app.models.article import (
    Article,
    ArticleCategory,
    ArticleStatus,
    ArticleImages,
    ArticleSourceInfo,
    ImagePreview,
    ImageMatched,
    generate_article_id,
)
from app.models.photo import (
    Photo,
    PhotoSource,
    PhotoType,
    generate_photo_id,
    create_photo_from_url,
)

__all__ = [
    # 原有模型
    "Topic",
    "Category",
    "Status",
    "SourceInfo",
    "SourceStyle",
    "Content",
    "Image",
    "ImageSource",
    "ImageType",
    "UserPreferences",
    "AuditLog",
    # Phase 6: 新增模型
    "Article",
    "ArticleCategory",
    "ArticleStatus",
    "ArticleImages",
    "ArticleSourceInfo",
    "ImagePreview",
    "ImageMatched",
    "generate_article_id",
    "Photo",
    "PhotoSource",
    "PhotoType",
    "generate_photo_id",
    "create_photo_from_url",
]
