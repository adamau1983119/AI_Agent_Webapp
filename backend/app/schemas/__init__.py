"""
Pydantic Schemas 模組
用於 API 請求和回應的資料驗證
"""
from app.schemas.topic import (
    TopicCreate,
    TopicUpdate,
    TopicResponse,
    TopicListResponse,
    TopicDetailResponse,
)
from app.schemas.content import (
    ContentCreate,
    ContentUpdate,
    ContentResponse,
    ContentVersionResponse,
    GenerateContentRequest,
)
from app.schemas.image import (
    ImageCreate,
    ImageUpdate,
    ImageResponse,
    ImageSearchResponse,
    ImageReorderRequest,
)
from app.schemas.user_preferences import (
    UserPreferencesResponse,
    UserPreferencesUpdate,
)
from app.schemas.common import (
    PaginationParams,
    PaginationResponse,
    ErrorResponse,
    SuccessResponse,
)

__all__ = [
    # Topic
    "TopicCreate",
    "TopicUpdate",
    "TopicResponse",
    "TopicListResponse",
    "TopicDetailResponse",
    # Content
    "ContentCreate",
    "ContentUpdate",
    "ContentResponse",
    "ContentVersionResponse",
    "GenerateContentRequest",
    # Image
    "ImageCreate",
    "ImageUpdate",
    "ImageResponse",
    "ImageSearchResponse",
    "ImageReorderRequest",
    # UserPreferences
    "UserPreferencesResponse",
    "UserPreferencesUpdate",
    # Common
    "PaginationParams",
    "PaginationResponse",
    "ErrorResponse",
    "SuccessResponse",
]
