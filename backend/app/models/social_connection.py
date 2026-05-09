"""
SocialConnection 社交平台連接模型
Phase 5: 分發與整合
用於管理用戶的社交平台帳號連接
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class SocialPlatform(str, Enum):
    """社交平台"""
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    THREADS = "threads"
    TIKTOK = "tiktok"
    TWITTER = "twitter"  # 暫緩


class ConnectionStatus(str, Enum):
    """連接狀態"""
    CONNECTED = "connected"         # 已連接
    DISCONNECTED = "disconnected"   # 已斷開
    EXPIRED = "expired"             # Token 過期
    ERROR = "error"                 # 錯誤


class PublishStatus(str, Enum):
    """發布狀態"""
    PENDING = "pending"             # 等待中
    PUBLISHING = "publishing"       # 發布中
    PUBLISHED = "published"         # 已發布
    FAILED = "failed"               # 失敗
    RETRY = "retry"                 # 重試中


# ============================================
# SocialConnection Schema
# ============================================

class SocialConnectionBase(BaseModel):
    """社交連接基礎"""
    platform: SocialPlatform
    platform_user_id: str = Field(..., description="平台用戶 ID")
    platform_username: str = Field(..., description="平台用戶名")
    platform_name: Optional[str] = Field(None, description="平台顯示名稱")
    profile_image_url: Optional[str] = Field(None, description="頭像 URL")


class SocialConnectionCreate(SocialConnectionBase):
    """建立社交連接"""
    access_token: str
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    scopes: List[str] = []


class SocialConnectionResponse(SocialConnectionBase):
    """社交連接回應"""
    id: str
    user_id: str
    status: ConnectionStatus
    token_expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    # 不包含敏感的 token 資訊

    model_config = ConfigDict(from_attributes=True)


class SocialConnectionListResponse(BaseModel):
    """社交連接列表回應"""
    connections: List[SocialConnectionResponse]
    total: int


# ============================================
# Publish 發布相關 Schema
# ============================================

class PublishRequest(BaseModel):
    """發布請求"""
    content_id: str = Field(..., description="內容 ID")
    content: str = Field(..., description="要發布的內容")
    platforms: List[SocialPlatform] = Field(..., description="目標平台列表")
    hashtags: List[str] = Field(default=[], description="Hashtags")
    image_urls: List[str] = Field(default=[], description="圖片 URL 列表")
    scheduled_at: Optional[datetime] = Field(None, description="排程發布時間")


class PublishResult(BaseModel):
    """發布結果"""
    platform: SocialPlatform
    status: PublishStatus
    post_id: Optional[str] = None
    post_url: Optional[str] = None
    error_message: Optional[str] = None
    published_at: Optional[datetime] = None


class PublishResponse(BaseModel):
    """發布回應"""
    publish_id: str
    content_id: str
    total_platforms: int
    successful: int
    failed: int
    results: List[PublishResult]
    created_at: datetime


class PublishHistoryItem(BaseModel):
    """發布歷史項目"""
    id: str
    content_id: str
    content_preview: str
    platforms: List[SocialPlatform]
    status: PublishStatus
    results: List[PublishResult]
    created_at: datetime
    published_at: Optional[datetime]


class PublishHistoryResponse(BaseModel):
    """發布歷史回應"""
    items: List[PublishHistoryItem]
    total: int
    page: int
    limit: int


# ============================================
# 平台配置
# ============================================

PLATFORM_CONFIGS: Dict[SocialPlatform, Dict[str, Any]] = {
    SocialPlatform.INSTAGRAM: {
        "name": "Instagram",
        "icon": "📸",
        "max_caption_length": 2200,
        "max_hashtags": 30,
        "image_required": True,
        "supported_media": ["image", "carousel", "reels"],
        "rate_limit": {
            "posts_per_day": 25,
            "posts_per_hour": 10
        }
    },
    SocialPlatform.FACEBOOK: {
        "name": "Facebook",
        "icon": "👤",
        "max_caption_length": 63206,
        "max_hashtags": 30,
        "image_required": False,
        "supported_media": ["text", "image", "video", "link"],
        "rate_limit": {
            "posts_per_day": 50,
            "posts_per_hour": 25
        }
    },
    SocialPlatform.THREADS: {
        "name": "Threads",
        "icon": "🧵",
        "max_caption_length": 500,
        "max_hashtags": 10,
        "image_required": False,
        "supported_media": ["text", "image"],
        "rate_limit": {
            "posts_per_day": 50,
            "posts_per_hour": 25
        }
    },
    SocialPlatform.TIKTOK: {
        "name": "TikTok",
        "icon": "🎵",
        "max_caption_length": 2200,
        "max_hashtags": 30,
        "image_required": False,  # 影片為主
        "supported_media": ["video"],
        "rate_limit": {
            "posts_per_day": 10,
            "posts_per_hour": 5
        }
    },
    SocialPlatform.TWITTER: {
        "name": "Twitter/X",
        "icon": "🐦",
        "max_caption_length": 280,
        "max_hashtags": 5,
        "image_required": False,
        "supported_media": ["text", "image", "video"],
        "rate_limit": {
            "posts_per_day": 100,
            "posts_per_hour": 50
        },
        "note": "暫緩（API 成本 $100/月）"
    },
}


# ============================================
# OAuth 配置
# ============================================

META_OAUTH_SCOPES = [
    "instagram_basic",
    "instagram_content_publish",
    "instagram_manage_comments",
    "pages_show_list",
    "pages_read_engagement",
    "pages_manage_posts",
    "threads_basic",
    "threads_content_publish",
    "threads_manage_replies",
]

TIKTOK_OAUTH_SCOPES = [
    "user.info.basic",
    "video.list",
    "video.publish",
]


def get_platform_config(platform: SocialPlatform) -> Dict[str, Any]:
    """取得平台配置"""
    return PLATFORM_CONFIGS.get(platform, {})


def optimize_content_for_platform(
    content: str,
    hashtags: List[str],
    platform: SocialPlatform
) -> Dict[str, Any]:
    """
    針對平台優化內容
    
    返回優化後的內容和 hashtags
    """
    config = get_platform_config(platform)
    max_length = config.get("max_caption_length", 2000)
    max_hashtags = config.get("max_hashtags", 10)
    
    # 截斷內容
    optimized_content = content
    if len(content) > max_length:
        optimized_content = content[:max_length - 3] + "..."
    
    # 限制 hashtags
    optimized_hashtags = hashtags[:max_hashtags]
    
    # 組合 hashtags
    hashtag_str = " ".join([f"#{tag}" for tag in optimized_hashtags])
    
    # 如果加上 hashtags 後超過長度，需要進一步截斷
    full_content = f"{optimized_content}\n\n{hashtag_str}" if hashtag_str else optimized_content
    if len(full_content) > max_length:
        available_length = max_length - len(hashtag_str) - 4  # 4 for "\n\n" and "..."
        optimized_content = content[:available_length] + "..."
        full_content = f"{optimized_content}\n\n{hashtag_str}" if hashtag_str else optimized_content
    
    return {
        "content": optimized_content,
        "full_content": full_content,
        "hashtags": optimized_hashtags,
        "hashtag_string": hashtag_str,
        "character_count": len(full_content),
        "platform": platform.value
    }

