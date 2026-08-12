"""
Channel API 端點
Phase 3: 內容功能
會員自定義頻道管理
"""
from typing import Optional, List, Dict, Any, Literal
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from app.models.channel import (
    ChannelCreate, ChannelUpdate, ChannelResponse, ChannelListResponse,
    ChannelCategory, ChannelRegion,
)
from app.services.channel_service import channel_service, MAX_CHANNELS_PER_USER
from app.services.channel_collector import channel_collector
from app.services.channel_assist_service import channel_assist_service
from app.services.feed_url_probe_service import probe_feed_url
from app.services.feed_validate_rate_limit import (
    enforce_feed_validate_rate_limit,
    enforce_feed_search_rate_limit,
)
from app.services.feed_whitelist_search_service import search_whitelist_feeds
from app.middleware.jwt_auth import get_current_user
from app.schemas.topic import TopicResponse, TopicListResponse
from app.schemas.common import PaginationResponse
from app.services.repositories.topic_repository import TopicRepository
from app.services.repositories.content_repository import ContentRepository
from app.services.repositories.image_repository import ImageRepository
from app.api.v1.topics import _convert_to_response
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/channels", tags=["channels"])


@router.get("", response_model=ChannelListResponse)
async def get_my_channels(
    current_user: dict = Depends(get_current_user)
):
    """
    取得我的頻道列表
    
    - 返回用戶的所有活躍頻道
    - 最多 3 個頻道
    """
    channels = await channel_service.get_user_channels(current_user["id"])
    
    return ChannelListResponse(
        channels=[ChannelResponse(**ch) for ch in channels],
        total=len(channels),
        max_channels=MAX_CHANNELS_PER_USER
    )


@router.post("", response_model=ChannelResponse, status_code=status.HTTP_201_CREATED)
async def create_channel(
    channel_data: ChannelCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    建立新頻道
    
    - **name**: 頻道名稱（必須）
    - **category**: 類別（fashion/food/trend/finance/sports/tech/entertainment/other）
    - **region**: 地區（hong_kong/taiwan/japan/korea/china/usa/uk/global）
    - **custom_keywords**: 自定義關鍵字（當類別為 other 時必填）
    - **description**: 頻道描述（可選）
    - **selected_feeds**: 建立時於 Step 2 選取之 RSS 來源（最多 10 筆；留空則使用系統預設池）
    
    每位用戶最多可建立 3 個頻道
    """
    channel, error = await channel_service.create_channel(
        user_id=current_user["id"],
        channel_data=channel_data
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    logger.info(f"用戶 {current_user['email']} 建立頻道: {channel['name']}")
    
    return ChannelResponse(**channel)


@router.get("/categories")
async def get_categories():
    """
    取得可用的類別列表
    """
    categories = await channel_service.get_available_categories()
    return {"categories": categories}


@router.get("/regions")
async def get_regions():
    """
    取得可用的地區列表
    """
    regions = await channel_service.get_available_regions()
    return {"regions": regions}


@router.get("/defaults/rss-sources")
async def get_default_rss_sources_for_create(
    category: ChannelCategory = Query(..., description="頻道類別"),
    region: ChannelRegion = Query(..., description="頻道地區"),
    current_user: dict = Depends(get_current_user),
):
    """
    建立頻道 Step 2：取得該類別＋地區之系統預設 RSS 候選列表（與收集 Layer 1 相同）。
    """
    feeds = channel_service.list_default_primary_feeds(category, region)
    return {
        "sources": [
            {
                "name": s.get("name", "") or "",
                "url": s.get("url", "") or "",
                "role": (s.get("role") or "") or "",
            }
            for s in feeds
        ]
    }


class FeedValidateRequest(BaseModel):
    """使用者貼上之 RSS／Feed URL 驗證（SSRF 基本防護 + 粗判格式）"""
    url: str = Field(..., min_length=1, max_length=2048, description="欲驗證的 URL")


class FeedValidateResponse(BaseModel):
    valid: bool = Field(..., description="是否通過驗證")
    title: Optional[str] = Field(None, description="Feed 標題（若可解析）")
    suggested_name: Optional[str] = Field(None, description="建議顯示名稱")
    error_code: Optional[str] = Field(None, description="失敗時機器可讀代碼（供前端 i18n）")


class FeedSearchResultItem(BaseModel):
    name: str
    url: str
    role: str = ""
    category: str
    region: str


class FeedSearchResponse(BaseModel):
    query: str
    results: List[FeedSearchResultItem]


@router.get("/feeds/search", response_model=FeedSearchResponse)
async def search_channel_feeds_whitelist(
    request: Request,
    q: str = Query(..., min_length=1, max_length=120, description="關鍵字（空白分隔為 AND，比對 name/url/role/類別/地區）"),
    limit: int = Query(30, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
):
    """
    站內 RSS 白名單檢索（`DEFAULT_RSS_SOURCES`），不對外爬網。
    """
    await enforce_feed_search_rate_limit(request)
    rows = search_whitelist_feeds(q, limit=limit)
    return FeedSearchResponse(
        query=q.strip(),
        results=[FeedSearchResultItem(**r) for r in rows],
    )


@router.post("/feeds/validate", response_model=FeedValidateResponse)
async def validate_channel_feed_url(
    request: Request,
    body: FeedValidateRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    驗證自訂 Feed URL（建立頻道 Step 2 用）。

    - 僅允許 http(s)；阻擋內網／metadata 等常見 SSRF 目標
    - 下載本體並以 feedparser 粗判是否像 RSS／Atom
    """
    await enforce_feed_validate_rate_limit(request)
    result = await probe_feed_url(body.url)
    return FeedValidateResponse(
        valid=bool(result.get("valid")),
        title=result.get("title"),
        suggested_name=result.get("suggested_name"),
        error_code=result.get("error_code"),
    )


@router.get("/{channel_id}", response_model=ChannelResponse)
async def get_channel(
    channel_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    取得特定頻道詳情
    """
    channel = await channel_service.get_channel(current_user["id"], channel_id)
    
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="頻道不存在"
        )
    
    return ChannelResponse(**channel)


@router.put("/{channel_id}", response_model=ChannelResponse)
async def update_channel(
    channel_id: str,
    update_data: ChannelUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    更新頻道
    
    可更新的欄位：
    - **name**: 頻道名稱
    - **custom_keywords**: 自定義關鍵字
    - **description**: 頻道描述
    - **status**: 狀態（active/paused）
    """
    channel, error = await channel_service.update_channel(
        user_id=current_user["id"],
        channel_id=channel_id,
        update_data=update_data
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    logger.info(f"用戶 {current_user['email']} 更新頻道: {channel_id}")
    
    return ChannelResponse(**channel)


@router.delete("/{channel_id}")
async def delete_channel(
    channel_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    刪除頻道（軟刪除）
    """
    success, error = await channel_service.delete_channel(
        user_id=current_user["id"],
        channel_id=channel_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    logger.info(f"用戶 {current_user['email']} 刪除頻道: {channel_id}")
    
    return {"message": "頻道已刪除"}


@router.get("/{channel_id}/sources")
async def get_channel_sources(
    channel_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    取得頻道的 RSS 來源（含三層備用）
    
    - Layer 1: 主要來源（類別 + 地區）
    - Layer 2: 備用來源（相近類別）
    - Layer 3: AI 生成（當 RSS 全部失敗時自動觸發）
    """
    channel = await channel_service.get_channel(current_user["id"], channel_id)
    
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="頻道不存在"
        )
    
    sources = channel_service.get_rss_sources_for_channel(channel)
    
    # 分層顯示
    layer1 = [s for s in sources if s.get("layer") == 1]
    layer2 = [s for s in sources if s.get("layer") == 2]
    
    return {
        "channel_id": channel_id,
        "category": channel.get("category"),
        "region": channel.get("region"),
        "layers": {
            "layer_1": {
                "description": "主要來源",
                "sources": layer1,
                "count": len(layer1)
            },
            "layer_2": {
                "description": "備用來源（相近類別）",
                "sources": layer2,
                "count": len(layer2)
            },
            "layer_3": {
                "description": "AI 生成（當 RSS 全部失敗時自動觸發）",
                "sources": [],
                "count": 0,
                "note": "此層不需要預設來源，由 AI 即時生成"
            }
        },
        "total_sources": len(sources)
    }


_topic_repo = TopicRepository()
_content_repo = ContentRepository()
_image_repo = ImageRepository()


@router.get("/{channel_id}/topics", response_model=TopicListResponse)
async def list_channel_topics(
    channel_id: str,
    page: int = Query(1, ge=1, description="頁碼"),
    limit: int = Query(50, ge=1, le=100, description="每頁數量"),
    lang: Optional[str] = Query(None, description="Content Locale：ui_lang（zh-TW/en/ja）"),
    current_user: dict = Depends(get_current_user),
):
    """
    取得頻道底下已寫入資料庫的主題列表（依 channel_id 篩選，非僅 topic_count 數字）。
    """
    channel = await channel_service.get_channel(current_user["id"], channel_id)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="頻道不存在",
        )

    topics, total = await _topic_repo.list_by_channel_id(
        channel_id=channel_id,
        user_id=current_user["id"],
        page=page,
        limit=limit,
    )

    if lang:
        from app.api.v1.topics import normalize_language
        from app.services.content_locale.topic_locale_resolver import resolve_topics_list_locale

        ui_lang = normalize_language(lang)
        topics = await resolve_topics_list_locale(topics, ui_lang)

    topic_responses = []
    for topic in topics:
        topic_copy = dict(topic)
        try:
            topic_copy["image_count"] = await _image_repo.count_by_topic_id(topic_copy["id"])
        except Exception as e:
            logger.warning(f"取得主題 {topic_copy.get('id')} 圖片數失敗: {e}")
            topic_copy["image_count"] = 0
        try:
            content = await _content_repo.get_content_by_topic_id(topic_copy["id"])
            topic_copy["word_count"] = content.get("word_count", 0) if content else 0
        except Exception as e:
            logger.warning(f"取得主題 {topic_copy.get('id')} 字數失敗: {e}")
            topic_copy["word_count"] = 0
        try:
            topic_responses.append(_convert_to_response(topic_copy))
        except Exception as e:
            logger.warning(f"轉換頻道主題 {topic_copy.get('id')} 失敗: {e}")

    pagination = PaginationResponse.create(page, limit, total)
    return TopicListResponse(data=topic_responses, pagination=pagination)


@router.post("/{channel_id}/collect")
async def trigger_channel_collection(
    channel_id: str,
    language: str = Query("zh-TW", description="UI 語言（zh-TW/en/ja）"),
    current_user: dict = Depends(get_current_user)
):
    """
    手動觸發頻道內容收集
    
    - 全球多語 RSS → AI 翻譯為用戶語言（資訊差）
    - 三層備援：L1 頻道 RSS → L2 相近類別 → L3 僅 RSS 全失敗
    """
    channel = await channel_service.get_channel(current_user["id"], channel_id)
    
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="頻道不存在"
        )
    
    allowed = ("zh-TW", "en", "ja")
    target_language = language if language in allowed else "zh-TW"
    
    # 執行收集
    result = await channel_collector.collect_for_channel(
        channel_id,
        target_language
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "收集失敗")
        )
    
    logger.info(f"用戶 {current_user['email']} 觸發頻道收集: {channel_id}, 收集了 {result['topics_collected']} 個主題")
    
    msg_key = result.get("message", "ok")
    return {
        "message": "收集完成" if result["topics_collected"] > 0 else "無符合頻道設定與語言的主題",
        "message_code": msg_key,
        "channel_id": channel_id,
        "topics_collected": result["topics_collected"],
        "collection_log": result.get("collection_log", {}),
    }


# ============================================
# AI 頻道助手 API
# ============================================

class ConversationTurn(BaseModel):
    """單輪對話（供多輪上下文）"""
    role: Literal["user", "assistant"] = Field(..., description="user 或 assistant")
    content: str = Field(..., min_length=1, max_length=800, description="該輪文字內容")


class ChannelAssistRequest(BaseModel):
    """頻道助手請求"""
    user_input: str = Field(..., min_length=1, max_length=500, description="用戶自然語言輸入")
    language: Optional[str] = Field(default="zh-TW", description="用戶語言（zh-TW/en/ja）")
    conversation_history: List[ConversationTurn] = Field(
        default_factory=list,
        description="先前對話輪次（由舊到新）；不含本次 user_input",
    )
    exclude_urls: List[str] = Field(
        default_factory=list,
        max_length=50,
        description="排除之 RSS URL（已選／已推薦），推薦列表改由白名單後段補滿",
    )


class ChannelAssistResponse(BaseModel):
    """頻道助手回應"""
    category: Optional[str] = Field(None, description="解析出的類別")
    region: Optional[str] = Field(None, description="解析出的地區")
    keywords: List[str] = Field(default=[], description="提取的關鍵字")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="解析信心度")
    clarification_needed: bool = Field(False, description="是否需要澄清")
    clarification_question: Optional[str] = Field(None, description="澄清問題")
    recommended_sources: List[Dict[str, Any]] = Field(default=[], description="推薦的 RSS 來源")
    suggested_channel_name: Optional[str] = Field(None, description="#32 建議頻道名稱")
    suggested_channel_description: Optional[str] = Field(None, description="#33 建議頻道描述")


class WizardQuickOptionItem(BaseModel):
    """精靈可點選：類別或地區（label_key 對應前端 i18n）"""
    kind: Literal["category", "region"] = Field(..., description="category 或 region")
    value: str = Field(..., description="列舉值，如 fashion、hong_kong")
    label_key: str = Field(..., description="翻譯鍵，如 channels.category.fashion")


class WizardFeedOptionItem(BaseModel):
    """精靈 RSS 候選（白名單檢索 MVP）"""
    kind: Literal["feed"] = Field(default="feed", description="固定 feed")
    name: str = Field(..., description="來源顯示名稱")
    url: str = Field(..., description="Feed URL")
    role: str = Field(default="", description="角色／類型標籤")


class ChannelAssistWizardOptionsRequest(BaseModel):
    """精靈步驟結構化選項請求（檢索 MVP：站內白名單）"""
    step: Literal[1, 2, 3] = Field(..., description="建立頻道精靈步驟 1～3")
    category: Optional[ChannelCategory] = Field(None, description="Step 2 建議帶入")
    region: Optional[ChannelRegion] = Field(None, description="Step 2 建議帶入")
    exclude_urls: List[str] = Field(
        default_factory=list,
        max_length=50,
        description="排除之 URL（已選等），最多 50 筆",
    )
    language: Optional[str] = Field(default="zh-TW", description="介面語言（Step 3 範本用）")
    custom_keywords: List[str] = Field(
        default_factory=list,
        max_length=5,
        description="Step 3 範本用關鍵字（每則最多 30 字）",
    )


class ChannelAssistWizardOptionsResponse(BaseModel):
    """精靈步驟結構化選項回應"""
    step: int = Field(..., ge=1, le=3)
    retrieval_mvp: Literal["whitelist_default_rss"] = Field(
        default="whitelist_default_rss",
        description="本版僅使用預設 RSS 白名單，與 GET .../defaults/rss-sources 同源",
    )
    quick_options: List[WizardQuickOptionItem] = Field(default_factory=list)
    feed_options: List[WizardFeedOptionItem] = Field(default_factory=list)
    suggested_channel_name: Optional[str] = Field(None, description="Step 3 建議名稱（範本或後續擴充）")
    suggested_channel_description: Optional[str] = Field(None, description="Step 3 建議描述")


@router.post("/assist", response_model=ChannelAssistResponse)
async def assist_channel_creation(
    request: ChannelAssistRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    AI 頻道助手
    
    使用 AI 解析用戶的自然語言輸入，協助建立頻道。
    
    - **user_input**: 用戶的自然語言描述（例如：「我想看日本的潮流穿搭」）
    - **language**: 用戶語言（zh-TW/en/ja）
    
    返回：
    - 解析出的類別、地區、關鍵字
    - 推薦的 RSS 來源列表
    - 如果需要澄清，會提供澄清問題
    """
    try:
        # 解析用戶意圖
        history_payload = [turn.model_dump() for turn in request.conversation_history][-24:]

        parsed = await channel_assist_service.parse_user_intent(
            user_input=request.user_input,
            language=request.language,
            conversation_history=history_payload,
        )
        
        # 如果解析成功且有類別和地區，推薦來源
        recommended_sources = []
        if parsed["category"] and parsed["region"] and parsed["confidence"] >= 0.7:
            recommended_sources = channel_assist_service.recommend_sources(
                category=parsed["category"],
                region=parsed["region"],
                exclude_urls=list(request.exclude_urls or [])[:50],
            )
        
        logger.info(f"用戶 {current_user['email']} 使用 AI 助手: {request.user_input} -> {parsed['category']}/{parsed['region']}")
        
        return ChannelAssistResponse(
            category=parsed["category"],
            region=parsed["region"],
            keywords=parsed["keywords"],
            confidence=parsed["confidence"],
            clarification_needed=parsed["clarification_needed"],
            clarification_question=parsed["clarification_question"],
            recommended_sources=recommended_sources,
            suggested_channel_name=parsed.get("suggested_channel_name"),
            suggested_channel_description=parsed.get("suggested_channel_description"),
        )
        
    except Exception as e:
        logger.error(f"AI 助手錯誤: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"處理請求時發生錯誤: {str(e)}"
        )


@router.post("/assist/wizard-options", response_model=ChannelAssistWizardOptionsResponse)
async def assist_channel_wizard_options(
    request: ChannelAssistWizardOptionsRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    建立頻道精靈：回傳當前步驟之 **結構化** 可點選選項（檢索 MVP＝站內白名單）。

    - Step 1：全部類別
    - Step 2：全部地區；若帶 category＋region 則另附 feed_options（已扣 exclude_urls）
    - Step 3：建議頻道名稱／描述範本（#32/#33 後備）；亦可搭配 assist 之 AI 欄位

    詳見 `docs/channel_create_ai_guided_spec.md`。
    """
    exclude = list(request.exclude_urls or [])[:50]
    kws = [str(x).strip()[:30] for x in (request.custom_keywords or []) if str(x).strip()][:5]
    payload = channel_assist_service.get_wizard_options(
        step=request.step,
        category=request.category.value if request.category else None,
        region=request.region.value if request.region else None,
        exclude_urls=exclude,
        language=request.language or "zh-TW",
        custom_keywords=kws,
    )
    quick = [WizardQuickOptionItem(**item) for item in payload.get("quick_options") or []]
    feeds = [WizardFeedOptionItem(**item) for item in payload.get("feed_options") or []]
    logger.info(
        "用戶 %s 取得精靈選項 step=%s quick=%s feeds=%s",
        current_user.get("email"),
        request.step,
        len(quick),
        len(feeds),
    )
    return ChannelAssistWizardOptionsResponse(
        step=payload["step"],
        retrieval_mvp=payload.get("retrieval_mvp", "whitelist_default_rss"),
        quick_options=quick,
        feed_options=feeds,
        suggested_channel_name=payload.get("suggested_channel_name"),
        suggested_channel_description=payload.get("suggested_channel_description"),
    )

