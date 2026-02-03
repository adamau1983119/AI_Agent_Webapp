"""
內容生成 API 端點
Phase 4: AI 個人化
提供個人化內容生成功能
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from app.models.style_profile import OutputFormat
from app.services.style_learning_service import style_learning_service
from app.services.ai.ai_service_factory import AIServiceFactory
from app.middleware.jwt_auth import get_current_user, get_current_user_optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/generate", tags=["generate"])


class GenerateRequest(BaseModel):
    """生成請求"""
    topic_id: str = Field(..., description="主題 ID")
    title: str = Field(..., description="主題標題")
    summary: Optional[str] = Field(None, description="主題摘要")
    category: Optional[str] = Field(None, description="主題類別")
    output_format: OutputFormat = Field(default=OutputFormat.SOCIAL_POST, description="輸出格式")
    language: str = Field(default="zh-TW", description="輸出語言")


class GenerateResponse(BaseModel):
    """生成回應"""
    content_id: str
    topic_id: str
    content: str
    output_format: str
    word_count: int
    hashtags: list
    generation_time_ms: int


@router.post("", response_model=GenerateResponse)
async def generate_content(
    request: GenerateRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    生成個人化內容
    
    根據用戶的風格檔案生成個人化內容：
    - **topic_id**: 主題 ID
    - **title**: 主題標題
    - **summary**: 主題摘要
    - **output_format**: 輸出格式（full_article/social_post/caption/script）
    - **language**: 輸出語言
    
    系統會根據用戶的風格偏好自動調整：
    - 語氣（正式/輕鬆）
    - 長度
    - 表情符號使用
    - 主題取向
    """
    import time
    import secrets
    
    start_time = time.time()
    
    # 建構個人化 Prompt
    topic_data = {
        "title": request.title,
        "summary": request.summary or "",
        "category": request.category or ""
    }
    
    prompt = await style_learning_service.build_generation_prompt(
        user_id=current_user["id"],
        topic=topic_data,
        output_format=request.output_format,
        target_language=request.language
    )
    
    # 呼叫 AI 服務生成內容
    try:
        ai_service = AIServiceFactory.get_service()
        generated_content = await ai_service.generate(prompt)
        
        if not generated_content:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="內容生成失敗"
            )
    except Exception as e:
        logger.error(f"AI 生成失敗: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成失敗: {str(e)}"
        )
    
    # 提取 Hashtags
    hashtags = extract_hashtags(generated_content)
    
    # 計算字數
    word_count = len(generated_content.replace(" ", "").replace("\n", ""))
    
    # 生成內容 ID
    content_id = f"content_{secrets.token_urlsafe(12)}"
    
    generation_time = int((time.time() - start_time) * 1000)
    
    logger.info(f"用戶 {current_user['email']} 生成內容: {content_id}, 格式: {request.output_format.value}")
    
    return GenerateResponse(
        content_id=content_id,
        topic_id=request.topic_id,
        content=generated_content,
        output_format=request.output_format.value,
        word_count=word_count,
        hashtags=hashtags,
        generation_time_ms=generation_time
    )


@router.post("/preview")
async def preview_generation(
    request: GenerateRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    預覽生成 Prompt
    
    返回將用於生成的 Prompt，不實際生成內容
    適用於調試和理解系統如何根據風格檔案生成內容
    """
    topic_data = {
        "title": request.title,
        "summary": request.summary or "",
        "category": request.category or ""
    }
    
    prompt = await style_learning_service.build_generation_prompt(
        user_id=current_user["id"],
        topic=topic_data,
        output_format=request.output_format,
        target_language=request.language
    )
    
    # 取得用戶風格檔案
    profile = await style_learning_service.get_profile(current_user["id"])
    
    return {
        "prompt": prompt,
        "output_format": request.output_format.value,
        "language": request.language,
        "style_profile_summary": {
            "preset_style": profile.get("preset_style") if profile else None,
            "learning_stage": profile.get("learning_stage") if profile else None,
            "confidence_score": profile.get("confidence_score") if profile else None,
        }
    }


@router.get("/quick")
async def quick_generate(
    title: str = Query(..., description="主題標題"),
    format: OutputFormat = Query(OutputFormat.CAPTION, description="輸出格式"),
    language: str = Query("zh-TW", description="語言"),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    快速生成（簡化版）
    
    適用於快速測試，只需提供標題
    """
    import time
    import secrets
    
    start_time = time.time()
    
    # 如果用戶已登入，使用個人化 Prompt
    if current_user:
        prompt = await style_learning_service.build_generation_prompt(
            user_id=current_user["id"],
            topic={"title": title, "summary": "", "category": ""},
            output_format=format,
            target_language=language
        )
    else:
        # 訪客使用預設 Prompt
        prompt = build_guest_prompt(title, format, language)
    
    # 呼叫 AI 服務
    try:
        ai_service = AIServiceFactory.get_service()
        generated_content = await ai_service.generate(prompt)
        
        if not generated_content:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="內容生成失敗"
            )
    except Exception as e:
        logger.error(f"AI 生成失敗: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成失敗: {str(e)}"
        )
    
    hashtags = extract_hashtags(generated_content)
    word_count = len(generated_content.replace(" ", "").replace("\n", ""))
    content_id = f"content_{secrets.token_urlsafe(12)}"
    generation_time = int((time.time() - start_time) * 1000)
    
    return {
        "content_id": content_id,
        "content": generated_content,
        "output_format": format.value,
        "word_count": word_count,
        "hashtags": hashtags,
        "generation_time_ms": generation_time,
        "personalized": current_user is not None
    }


def extract_hashtags(content: str) -> list:
    """從內容中提取 Hashtags"""
    import re
    hashtags = re.findall(r'#(\w+)', content)
    return list(set(hashtags))


def build_guest_prompt(title: str, format: OutputFormat, language: str) -> str:
    """為訪客建構預設 Prompt"""
    from app.models.style_profile import OUTPUT_FORMAT_CONFIGS
    
    format_config = OUTPUT_FORMAT_CONFIGS.get(format, OUTPUT_FORMAT_CONFIGS[OutputFormat.SOCIAL_POST])
    
    lang_labels = {
        "zh-TW": "繁體中文",
        "en": "English",
        "ja": "日本語",
    }
    
    return f"""作為專業內容創作者，請根據以下主題生成{format_config['name']}。

主題：{title}

要求：
- 格式：{format_config['name']}
- 字數：{format_config['min_length']}-{format_config['max_length']} 字
- 語言：{lang_labels.get(language, '繁體中文')}
- Hashtag 數量：{format_config['hashtag_count']} 個
- 使用輕鬆活潑的語氣
- 適當使用表情符號

請直接輸出內容，不要添加任何解釋。"""

