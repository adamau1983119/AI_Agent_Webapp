"""
靈感策劃 API 端點
Phase 3: 內容功能
提供靈感搜尋和關鍵字提取
"""
from typing import Optional, List, Dict, Any
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
    # UI language query 為 SoT；不再覆寫為帳戶 profile 語言
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
    取得搜尋建議（自動完成）- 改進版：結合資料庫搜尋和預定義詞彙
    
    - **q**: 搜尋前綴
    
    返回基於輸入的智能搜尋建議
    """
    from app.services.repositories.topic_repository import TopicRepository
    
    suggestions: List[str] = []
    topic_repo = TopicRepository()
    
    try:
        # 1. 從資料庫中搜尋相關主題標題（智能建議）
        # 搜尋標題包含輸入關鍵字的主題
        topics, _ = await topic_repo.list_topics(
            search=q,
            page=1,
            limit=10,
            sort="generated_at",
            order="desc"
        )
        
        # 從主題標題中提取建議（提取包含輸入關鍵字的部分）
        for topic in topics:
            title = topic.get("title", "")
            if title and q.lower() in title.lower():
                # 提取標題中包含關鍵字的部分（最多30字）
                # 如果標題較短，直接使用整個標題
                if len(title) <= 30:
                    if title not in suggestions:
                        suggestions.append(title)
                else:
                    # 找到關鍵字在標題中的位置
                    q_lower = q.lower()
                    title_lower = title.lower()
                    idx = title_lower.find(q_lower)
                    if idx >= 0:
                        # 提取關鍵字前後各15字
                        start = max(0, idx - 15)
                        end = min(len(title), idx + len(q) + 15)
                        extracted = title[start:end].strip()
                        if extracted and len(extracted) >= len(q) and extracted not in suggestions:
                            suggestions.append(extracted)
        
        # 2. 如果資料庫建議不足，補充預定義的熱門搜尋詞
        if len(suggestions) < 5:
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
            
            # 篩選匹配的預定義詞彙
            for term in popular_terms:
                if q.lower() in term.lower() and term not in suggestions:
                    suggestions.append(term)
                    if len(suggestions) >= 5:
                        break
            
            # 如果仍然不足，添加最熱門的詞彙
            if len(suggestions) < 5:
                for term in popular_terms[:5]:
                    if term not in suggestions:
                        suggestions.append(term)
                        if len(suggestions) >= 5:
                            break
        
        # 限制建議數量為最多 5 個
        suggestions = suggestions[:5]
        
    except Exception as e:
        logger.warning(f"取得智能搜尋建議失敗，使用預定義詞彙: {e}")
        # 如果資料庫搜尋失敗，回退到預定義詞彙
        popular_terms = [
            "時尚穿搭",
            "美食探店",
            "科技新品",
            "旅遊攻略",
            "健身教學",
        ]
        suggestions = [
            term for term in popular_terms
            if q.lower() in term.lower()
        ][:5]
        if not suggestions:
            suggestions = popular_terms[:5]
    
    return {
        "query": q,
        "suggestions": suggestions
    }


# ============================================
# AI 助手 API 端點（v5.0 新增）
# ============================================

class AssistantStartRequest(BaseModel):
    """開始對話請求"""
    topic: str = Field(..., min_length=2, max_length=200, description="主題")
    language: str = Field("zh-TW", description="語言（zh-TW/en/ja）")


class QuestionOption(BaseModel):
    """問題選項"""
    question_id: str
    question: str
    type: str
    options: List[str] = []
    required: bool = True


class AssistantStartResponse(BaseModel):
    """開始對話回應"""
    session_id: str
    conversation_id: str
    questions: List[QuestionOption]
    preferences_applied: Optional[Dict[str, Any]] = None


@router.post("/assistant/start", response_model=AssistantStartResponse)
async def start_assistant_conversation(
    request: AssistantStartRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    開始智慧助手對話，AI 動態生成問題
    
    - **topic**: 主題（必填，2-200 字）
    - **language**: 語言（可選，預設 zh-TW）
    
    AI 會根據主題生成 1-5 個針對性問題，幫助用戶明確創作需求。
    """
    from app.services.inspiration_conversation_service import inspiration_conversation_service
    from app.services.inspiration_question_generator_service import inspiration_question_generator_service
    from app.services.inspiration_preference_service import inspiration_preference_service
    from app.services.inspiration_cost_monitor import inspiration_cost_monitor
    from app.config import settings
    
    try:
        user_id = current_user["id"]
        language = request.language or "zh-TW"
        
        # 0. 成本檢查（預估問題生成需要 300-500 tokens）
        estimated_tokens = 500
        cost_check = await inspiration_cost_monitor.check_cost(user_id, estimated_tokens)
        if not cost_check.get("allowed"):
            from app.utils.i18n import get_error_message, get_user_language
            language = get_user_language(user=current_user)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=cost_check.get("message", get_error_message("inspiration.cost_limit_exceeded", language))
            )
        
        # 1. 建立會話
        session = await inspiration_conversation_service.start_conversation(
            user_id=user_id,
            topic=request.topic,
            language=language
        )
        
        # 2. 取得用戶偏好
        preferences = await inspiration_preference_service.get_preferences(user_id)
        prefs = preferences.get("preferences", {})
        
        # 3. AI 生成問題
        questions_data = await inspiration_question_generator_service.generate_questions(
            topic=request.topic,
            language=language,
            user_preferences=preferences,
            max_questions=3
        )
        
        # 3.5. 記錄成本（估算 token 使用量）
        # 估算：prompt 約 200 tokens，response 約 300 tokens
        # 簡單估算：中文約 1.5 tokens/字，英文約 0.75 tokens/字
        prompt_text = request.topic + " " + language
        prompt_tokens = int(len(prompt_text) * 1.2)  # 保守估算
        
        response_text = " ".join([q.get("question", "") for q in questions_data])
        response_tokens = int(len(response_text) * 1.2)  # 保守估算
        
        # 取得當前 AI 服務名稱
        current_service = settings.AI_SERVICE or "deepseek"
        
        # 記錄成本
        await inspiration_cost_monitor.record_usage(
            user_id=user_id,
            service=current_service,
            input_tokens=prompt_tokens,
            output_tokens=response_tokens,
            operation="question_generation"
        )
        
        # 4. 轉換為回應格式
        questions = [
            QuestionOption(
                question_id=q.get("question_id", f"q{i+1}"),
                question=q.get("question", ""),
                type=q.get("type", "general"),
                options=q.get("options", []),
                required=q.get("required", True)
            )
            for i, q in enumerate(questions_data)
        ]
        
        # 5. 添加助手訊息到會話
        await inspiration_conversation_service.add_assistant_message(
            session_id=session["session_id"],
            content=f"我已經為「{request.topic}」準備了 {len(questions)} 個問題，幫助您明確創作需求。",
            message_type="question"
        )
        
        return AssistantStartResponse(
            session_id=session["session_id"],
            conversation_id=session["conversation_id"],
            questions=questions,
            preferences_applied={
                "format": prefs.get("default_format"),
                "tone": prefs.get("default_tone"),
                "language": language
            }
        )
        
    except Exception as e:
        logger.error(f"開始對話失敗: {e}")
        from app.utils.i18n import get_error_message, get_user_language
        from fastapi import Request
        language = get_user_language(user=current_user)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_error_message("inspiration.assistant.start_failed", language)
        )


class AssistantGenerateRequest(BaseModel):
    """生成內容請求"""
    session_id: str = Field(..., description="會話 ID")
    answers: Dict[str, Any] = Field(..., description="用戶回答")


class AssistantGenerateResponse(BaseModel):
    """生成內容回應"""
    state: str
    content: str
    verification_status: Optional[Dict[str, Any]] = None
    modules_included: List[str] = []
    sources: List[Dict[str, Any]] = []


@router.post("/assistant/generate", response_model=AssistantGenerateResponse)
async def generate_assistant_content(
    request: AssistantGenerateRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    生成內容（包含搜尋、驗證、生成）
    
    - **session_id**: 會話 ID（必填）
    - **answers**: 用戶回答（必填）
    
    流程：
    1. 多來源搜尋
    2. AI 驗證來源
    3. 生成內容
    """
    from app.services.inspiration_conversation_service import inspiration_conversation_service
    from app.services.inspiration_service import inspiration_service
    from app.services.inspiration_source_verification_service import inspiration_source_verification_service
    from app.services.inspiration_content_generator_service import inspiration_content_generator_service
    
    try:
        user_id = current_user["id"]
        
        # 1. 取得會話
        session = await inspiration_conversation_service.conversation_repo.get_session(request.session_id)
        if not session or session.get("user_id") != user_id:
            from app.utils.i18n import get_error_message, get_user_language
            language = get_user_language(user=current_user)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=get_error_message("inspiration.session.not_found", language)
            )
        
        topic = session.get("topic", "")
        language = session.get("preferences", {}).get("language", "zh-TW")
        
        # 2. 添加用戶回答到會話
        for key, value in request.answers.items():
            await inspiration_conversation_service.add_user_message(
                session_id=request.session_id,
                content=f"{key}: {value}"
            )
        
        # 3. 多來源搜尋
        search_results = await inspiration_service.search_inspiration(
            query=topic,
            language=language,
            limit=5
        )
        
        # 4. AI 驗證來源
        verification_status = None
        if search_results:
            # 提取資訊（使用第一個搜尋結果的標題和描述）
            information = f"{search_results[0].get('title', '')} {search_results[0].get('description', '')}"
            
            # 轉換為驗證服務格式
            sources_for_verification = [
                {
                    "url": r.get("url", ""),
                    "type": r.get("source", "other"),
                    "content": r.get("description", "")
                }
                for r in search_results
            ]
            
            verification_status = await inspiration_source_verification_service.verify_sources(
                information=information,
                sources=sources_for_verification,
                language=language
            )
        
        # 5. 確定格式類型
        format_type = request.answers.get("format", "video_script")
        if format_type not in ["video_script", "article", "post", "outline"]:
            format_type = "video_script"
        
        # 6. 提取模組要求
        modules = []
        if "address" in request.answers.get("modules", []):
            modules.append("address")
        if "history" in request.answers.get("modules", []):
            modules.append("history")
        
        # 6.5. 成本檢查（預估內容生成需要 2000-3000 tokens）
        estimated_tokens = 3000
        cost_check = await inspiration_cost_monitor.check_cost(user_id, estimated_tokens)
        if not cost_check.get("allowed"):
            from app.utils.i18n import get_error_message, get_user_language
            language = get_user_language(user=current_user)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=cost_check.get("message", get_error_message("inspiration.cost_limit_exceeded", language))
            )
        
        # 7. 生成內容
        content_result = await inspiration_content_generator_service.generate_content(
            topic=topic,
            user_id=user_id,
            format_type=format_type,
            language=language,
            search_results=search_results,
            verification_status=verification_status,
            user_answers=request.answers,
            modules=modules if modules else None
        )
        
        # 7.5. 記錄成本（估算 token 使用量）
        # 估算：prompt 約 1500 tokens，response 約 1500 tokens
        # 簡單估算：中文約 1.5 tokens/字，英文約 0.75 tokens/字
        prompt_text = topic + " " + str(request.answers)
        prompt_tokens = int(len(prompt_text) * 1.2)  # 保守估算
        
        response_text = content_result["content"]
        response_tokens = int(len(response_text) * 1.2)  # 保守估算
        
        # 取得當前 AI 服務名稱
        from app.config import settings
        current_service = settings.AI_SERVICE or "deepseek"
        
        # 記錄成本
        cost_record = await inspiration_cost_monitor.record_usage(
            user_id=user_id,
            service=current_service,
            input_tokens=prompt_tokens,
            output_tokens=response_tokens,
            operation="content_generation"
        )
        
        # 如果有警告，記錄到日誌
        if cost_record.get("warnings"):
            for warning in cost_record["warnings"]:
                logger.warning(f"成本警告（用戶 {user_id}）: {warning.get('message')}")
        
        # 8. 添加生成的內容到會話
        await inspiration_conversation_service.add_assistant_message(
            session_id=request.session_id,
            content=content_result["content"][:200] + "...",
            message_type="content"
        )
        
        # 9. 完成會話
        await inspiration_conversation_service.complete_conversation(request.session_id)
        
        return AssistantGenerateResponse(
            state="completed",
            content=content_result["content"],
            verification_status=verification_status,
            modules_included=content_result.get("modules_included", []),
            sources=content_result.get("sources", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成內容失敗: {e}")
        from app.utils.i18n import get_error_message, get_user_language
        language = get_user_language(user=current_user)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_error_message("inspiration.assistant.generate_failed", language)
        )


@router.get("/preferences")
async def get_inspiration_preferences(
    current_user: dict = Depends(get_current_user)
):
    """
    取得用戶偏好
    """
    from app.services.inspiration_preference_service import inspiration_preference_service
    
    try:
        preferences = await inspiration_preference_service.get_preferences(current_user["id"])
        return preferences
    except Exception as e:
        logger.error(f"取得偏好失敗: {e}")
        from app.utils.i18n import get_error_message, get_user_language
        language = get_user_language(user=current_user)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_error_message("inspiration.preferences.get_failed", language)
        )


@router.put("/preferences")
async def update_inspiration_preferences(
    preferences: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """
    更新用戶偏好
    """
    from app.services.inspiration_preference_service import inspiration_preference_service
    
    try:
        updated = await inspiration_preference_service.preference_repo.update_preferences(
            user_id=current_user["id"],
            update_data={"preferences": preferences}
        )
        return updated
    except Exception as e:
        logger.error(f"更新偏好失敗: {e}")
        from app.utils.i18n import get_error_message, get_user_language
        language = get_user_language(user=current_user)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_error_message("inspiration.preferences.update_failed", language)
        )


@router.get("/cost/summary")
async def get_cost_summary(
    current_user: dict = Depends(get_current_user)
):
    """
    取得成本摘要
    
    返回每日/每月使用量、警告狀態
    """
    from app.services.inspiration_cost_monitor import inspiration_cost_monitor
    
    try:
        summary = await inspiration_cost_monitor.get_cost_summary(current_user["id"])
        return summary
    except Exception as e:
        logger.error(f"取得成本摘要失敗: {e}")
        from app.utils.i18n import get_error_message, get_user_language
        language = get_user_language(user=current_user)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_error_message("inspiration.cost.get_failed", language)
        )


@router.get("/cost/statistics")
async def get_cost_statistics(
    days: int = Query(30, ge=1, le=365, description="統計天數"),
    current_user: dict = Depends(get_current_user)
):
    """
    取得成本統計資訊
    
    - **days**: 統計天數（1-365，預設 30）
    """
    from app.services.inspiration_cost_monitor import inspiration_cost_monitor
    
    try:
        statistics = await inspiration_cost_monitor.get_user_statistics(
            current_user["id"],
            days=days
        )
        return statistics
    except Exception as e:
        logger.error(f"取得成本統計失敗: {e}")
        from app.utils.i18n import get_error_message, get_user_language
        language = get_user_language(user=current_user)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_error_message("inspiration.cost.get_failed", language)
        )


@router.get("/cost/service-info")
async def get_service_cost_info(
    service: str = Query(..., description="AI 服務名稱"),
    current_user: dict = Depends(get_current_user)
):
    """
    取得服務成本資訊
    
    - **service**: AI 服務名稱（deepseek/openai/gemini/qwen/ollama）
    """
    from app.services.inspiration_cost_monitor import inspiration_cost_monitor
    
    try:
        info = inspiration_cost_monitor.get_service_cost_info(service)
        return info
    except Exception as e:
        logger.error(f"取得服務成本資訊失敗: {e}")
        from app.utils.i18n import get_error_message, get_user_language
        language = get_user_language(user=current_user)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_error_message("inspiration.cost.get_failed", language)
        )


@router.get("/cost/compare-services")
async def compare_services_cost(
    input_tokens: int = Query(1000, ge=1, description="輸入 Token 數量"),
    output_tokens: int = Query(1000, ge=1, description="輸出 Token 數量"),
    current_user: dict = Depends(get_current_user)
):
    """
    比較不同服務的成本
    
    - **input_tokens**: 輸入 Token 數量（預設 1000）
    - **output_tokens**: 輸出 Token 數量（預設 1000）
    """
    from app.services.inspiration_cost_monitor import inspiration_cost_monitor
    
    try:
        comparison = inspiration_cost_monitor.compare_services_cost(
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )
        return comparison
    except Exception as e:
        logger.error(f"比較服務成本失敗: {e}")
        from app.utils.i18n import get_error_message, get_user_language
        language = get_user_language(user=current_user)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_error_message("inspiration.cost.get_failed", language)
        )

