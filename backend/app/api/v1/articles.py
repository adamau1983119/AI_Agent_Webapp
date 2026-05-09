"""
Articles API (Phase 6.7)
文章 API 端點
"""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from datetime import datetime
from app.services.repositories.article_repository import ArticleRepository
from app.services.image_matching_service import ImageMatchingService
from app.models.article import ArticleCategory, ArticleStatus
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/articles", tags=["Articles"])


# ============================================
# Response Models
# ============================================

class ImagePreviewResponse(BaseModel):
    photo_id: str
    url: str
    thumbnail_url: Optional[str] = None
    caption: Optional[str] = None


class ImageMatchedResponse(BaseModel):
    photo_id: str
    url: str
    thumbnail_url: Optional[str] = None
    keywords: List[str] = []
    score: float = 0.0
    source: str = "unknown"
    is_original: bool = False


class ArticleImagesResponse(BaseModel):
    preview: List[ImagePreviewResponse] = []
    matched: List[ImageMatchedResponse] = []


class ArticleResponse(BaseModel):
    article_id: str
    title: str
    original_title: Optional[str] = None
    description: Optional[str] = None
    link: str
    category: str
    status: str
    source: str
    hashtags: List[str] = []
    images: ArticleImagesResponse
    score: float = 0.0
    collected_at: Optional[datetime] = None


class ArticleListResponse(BaseModel):
    articles: List[ArticleResponse]
    total: int
    page: int
    limit: int


class MatchedImagesResponse(BaseModel):
    article_id: str
    matched_images: List[ImageMatchedResponse]
    total: int


class RefreshImagesResponse(BaseModel):
    article_id: str
    success: bool
    matched_count: int
    message: str


# ============================================
# Dependencies
# ============================================

def get_article_repo():
    return ArticleRepository()


def get_matching_service():
    return ImageMatchingService()


# ============================================
# Endpoints
# ============================================

@router.get("", response_model=ArticleListResponse)
async def list_articles(
    category: Optional[str] = Query(None, description="分類篩選"),
    status: Optional[str] = Query(None, description="狀態篩選"),
    search: Optional[str] = Query(None, description="搜尋關鍵字"),
    page: int = Query(1, ge=1, description="頁碼"),
    limit: int = Query(10, ge=1, le=100, description="每頁數量"),
    sort: str = Query("collected_at", description="排序欄位"),
    order: str = Query("desc", description="排序順序"),
    repo: ArticleRepository = Depends(get_article_repo)
):
    """
    獲取文章列表
    
    - **category**: 分類篩選（fashion/food/trend）
    - **status**: 狀態篩選（pending/confirmed/published/deleted）
    - **search**: 搜尋標題、來源、hashtags
    - **page**: 頁碼
    - **limit**: 每頁數量
    """
    try:
        # 轉換分類
        category_enum = None
        if category:
            try:
                category_enum = ArticleCategory(category)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
        
        # 轉換狀態
        status_enum = None
        if status:
            try:
                status_enum = ArticleStatus(status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
        
        articles, total = await repo.list_articles(
            category=category_enum,
            status=status_enum,
            search=search,
            page=page,
            limit=limit,
            sort=sort,
            order=order
        )
        
        # 轉換為 response 格式
        article_responses = []
        for article in articles:
            images = article.get("images", {})
            article_responses.append(ArticleResponse(
                article_id=article.get("article_id", ""),
                title=article.get("title", ""),
                original_title=article.get("original_title"),
                description=article.get("description"),
                link=article.get("link", ""),
                category=article.get("category", ""),
                status=article.get("status", "pending"),
                source=article.get("source", ""),
                hashtags=article.get("hashtags", []),
                images=ArticleImagesResponse(
                    preview=[ImagePreviewResponse(**img) for img in images.get("preview", [])],
                    matched=[ImageMatchedResponse(**img) for img in images.get("matched", [])]
                ),
                score=article.get("score", 0.0),
                collected_at=article.get("collected_at")
            ))
        
        return ArticleListResponse(
            articles=article_responses,
            total=total,
            page=page,
            limit=limit
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list articles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: str,
    repo: ArticleRepository = Depends(get_article_repo)
):
    """
    獲取單篇文章
    
    - **article_id**: 文章 ID
    """
    try:
        article = await repo.get_by_id(article_id)
        
        if not article:
            raise HTTPException(status_code=404, detail=f"Article not found: {article_id}")
        
        images = article.get("images", {})
        return ArticleResponse(
            article_id=article.get("article_id", ""),
            title=article.get("title", ""),
            original_title=article.get("original_title"),
            description=article.get("description"),
            link=article.get("link", ""),
            category=article.get("category", ""),
            status=article.get("status", "pending"),
            source=article.get("source", ""),
            hashtags=article.get("hashtags", []),
            images=ArticleImagesResponse(
                preview=[ImagePreviewResponse(**img) for img in images.get("preview", [])],
                matched=[ImageMatchedResponse(**img) for img in images.get("matched", [])]
            ),
            score=article.get("score", 0.0),
            collected_at=article.get("collected_at")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get article {article_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{article_id}/matched-images", response_model=MatchedImagesResponse)
async def get_matched_images(
    article_id: str,
    limit: int = Query(10, ge=1, le=50, description="圖片數量"),
    include_original: bool = Query(True, description="是否包含原文照片"),
    service: ImageMatchingService = Depends(get_matching_service)
):
    """
    獲取文章的匹配圖片
    
    使用 MongoDB 聚合查詢，根據文章的 hashtags 和原文照片關鍵字匹配相關圖片。
    
    - **article_id**: 文章 ID
    - **limit**: 圖片數量限制
    - **include_original**: 是否包含原文照片
    """
    try:
        matched = await service.get_matched_images(
            article_id=article_id,
            limit=limit,
            include_original=include_original
        )
        
        return MatchedImagesResponse(
            article_id=article_id,
            matched_images=[ImageMatchedResponse(**img) for img in matched],
            total=len(matched)
        )
        
    except Exception as e:
        logger.error(f"Failed to get matched images for {article_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{article_id}/refresh-images", response_model=RefreshImagesResponse)
async def refresh_images(
    article_id: str,
    force: bool = Query(False, description="是否強制刷新"),
    limit: int = Query(10, ge=1, le=50, description="圖片數量"),
    service: ImageMatchingService = Depends(get_matching_service)
):
    """
    重新匹配文章的圖片
    
    重新執行圖片匹配流程，更新文章的 matched 圖片列表。
    
    - **article_id**: 文章 ID
    - **force**: 是否強制刷新（即使已有匹配圖片）
    - **limit**: 圖片數量限制
    """
    try:
        if force:
            result = await service.update_matched_images(article_id, limit=limit)
        else:
            result = await service.refresh_article_images(article_id, force=False)
        
        if result:
            matched_count = len(result.get("images", {}).get("matched", []))
            return RefreshImagesResponse(
                article_id=article_id,
                success=True,
                matched_count=matched_count,
                message=f"Successfully matched {matched_count} images"
            )
        else:
            return RefreshImagesResponse(
                article_id=article_id,
                success=False,
                matched_count=0,
                message="No images matched or article not found"
            )
        
    except Exception as e:
        logger.error(f"Failed to refresh images for {article_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_articles_stats(
    category: Optional[str] = Query(None, description="分類篩選"),
    repo: ArticleRepository = Depends(get_article_repo)
):
    """
    獲取文章統計
    
    - **category**: 分類篩選
    """
    try:
        category_enum = None
        if category:
            try:
                category_enum = ArticleCategory(category)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
        
        stats = await repo.get_articles_stats(category=category_enum)
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get articles stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

