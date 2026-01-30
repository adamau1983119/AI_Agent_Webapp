"""
靈感策劃 API 端點
Phase 3: 內容功能
提供靈感搜尋和關鍵字提取
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from app.services.inspiration_service import inspiration_service
from app.middleware.jwt_auth import get_current_user, get_current_user_optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/inspiration", tags=["inspiration"])


class InspirationItem(BaseModel):
    """靈感項目"""
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    source: str = "unknown"
    image_url: Optional[str] = None
    published_date: Optional[str] = None


class InspirationSearchResponse(BaseModel):
    """靈感搜尋回應"""
    query: str
    results: List[InspirationItem]
    total: int


class KeywordExtractionRequest(BaseModel):
    """關鍵字提取請求"""
    text: str = Field(..., min_length=10, max_length=2000, description="要提取關鍵字的文本")


class KeywordExtractionResponse(BaseModel):
    """關鍵字提取回應"""
    keywords: List[str]
    count: int


class TrendingTopicsResponse(BaseModel):
    """熱門主題回應"""
    category: str
    region: str
    topics: List[InspirationItem]
    total: int


@router.get("/search", response_model=InspirationSearchResponse)
async def search_inspiration(
    q: str = Query(..., min_length=2, max_length=100, description="搜尋關鍵字"),
    language: str = Query("zh-TW", description="語言（zh-TW/en/ja）"),
    limit: int = Query(5, ge=1, le=10, description="返回數量"),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    搜尋靈感
    
    - **q**: 搜尋關鍵字（必填）
    - **language**: 語言偏好
    - **limit**: 返回數量（1-10）
    
    來源：
    1. Google Custom Search（優先）
    2. AI 生成（當搜尋結果不足時）
    """
    # 如果用戶已登入，使用用戶的語言偏好
    if current_user:
        language = current_user.get("language", language)
    
    results = await inspiration_service.search_inspiration(
        query=q,
        language=language,
        limit=limit
    )
    
    return InspirationSearchResponse(
        query=q,
        results=[InspirationItem(**r) for r in results],
        total=len(results)
    )


@router.post("/extract-keywords", response_model=KeywordExtractionResponse)
async def extract_keywords(
    request: KeywordExtractionRequest,
    language: str = Query("zh-TW", description="語言"),
    limit: int = Query(5, ge=1, le=10, description="返回數量"),
    current_user: dict = Depends(get_current_user)
):
    """
    從文本提取關鍵字
    
    - **text**: 要提取關鍵字的文本（10-2000 字）
    - **language**: 語言
    - **limit**: 返回數量（1-10）
    
    使用 AI 智能提取，適用於：
    - 從長文中提取關鍵主題
    - 為內容搜尋提供關鍵字建議
    """
    keywords = await inspiration_service.extract_keywords(
        text=request.text,
        language=language,
        limit=limit
    )
    
    return KeywordExtractionResponse(
        keywords=keywords,
        count=len(keywords)
    )


@router.get("/trending", response_model=TrendingTopicsResponse)
async def get_trending_topics(
    category: str = Query("general", description="類別"),
    region: str = Query("global", description="地區"),
    language: str = Query("zh-TW", description="語言"),
    limit: int = Query(10, ge=1, le=20, description="返回數量"),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    取得熱門趨勢主題
    
    - **category**: 類別（fashion/food/tech/finance/sports/entertainment/general）
    - **region**: 地區
    - **language**: 語言
    - **limit**: 返回數量
    
    適用於：
    - 探索當前熱門話題
    - 尋找創作靈感
    """
    # 如果用戶已登入，使用用戶的語言偏好
    if current_user:
        language = current_user.get("language", language)
    
    topics = await inspiration_service.get_trending_topics(
        category=category,
        region=region,
        language=language,
        limit=limit
    )
    
    return TrendingTopicsResponse(
        category=category,
        region=region,
        topics=[InspirationItem(**t) for t in topics],
        total=len(topics)
    )


@router.get("/suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=1, max_length=50, description="搜尋前綴"),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    取得搜尋建議（自動完成）
    
    - **q**: 搜尋前綴
    
    返回基於輸入的搜尋建議
    """
    # 預定義的熱門搜尋詞
    popular_terms = [
        "時尚穿搭",
        "美食探店",
        "科技新品",
        "旅遊攻略",
        "健身教學",
        "美妝教程",
        "投資理財",
        "職場技巧",
        "生活小技巧",
        "電影推薦",
        "音樂推薦",
        "寵物日常",
    ]
    
    # 篩選匹配的建議
    suggestions = [
        term for term in popular_terms
        if q.lower() in term.lower()
    ][:5]
    
    # 如果沒有匹配，返回熱門搜尋
    if not suggestions:
        suggestions = popular_terms[:5]
    
    return {
        "query": q,
        "suggestions": suggestions
    }

