"""
Contents API 端點
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Request

from app.config import settings
from app.middleware.jwt_auth import get_current_user_optional
from app.schemas.content import (
    ContentCreate,
    ContentUpdate,
    ContentResponse,
    ContentVersionsResponse,
    ContentVersionResponse,
    GenerateContentRequest,
)
from app.services.repositories.content_repository import ContentRepository
from app.services.repositories.topic_repository import TopicRepository
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/contents", tags=["contents"])

# Repository 實例
content_repo = ContentRepository()
topic_repo = TopicRepository()


def _pro_model() -> str:
    return getattr(settings, "DEEPSEEK_MODEL_PRO", "deepseek-v4-pro")


def _require_summary_flash(topic: dict, language: str = "zh-TW") -> str:
    """v7 Phase 3：generate 必須有 DB summary_flash（不以 body 為 SoT）。"""
    sf = (topic.get("summary_flash") or "").strip()
    if not sf:
        from app.utils.i18n import get_error_message
        raise HTTPException(
            status_code=400,
            detail=get_error_message("content.summary_flash_required", language),
        )
    return sf


def _style_hint_from_context(ctx: dict) -> str:
    compressed = (ctx.get("compressed_dna") or "").strip()
    if compressed:
        return compressed
    return (ctx.get("legacy_style_hint") or "").strip()


def _generation_meta_from_context(ctx: dict) -> dict:
    meta = {"dna_status": ctx.get("dna_status", "pending")}
    version_id = ctx.get("dna_version_id")
    if version_id:
        meta["dna_version_id"] = version_id
    return meta


async def _resolve_generate_style(user_id: Optional[str]) -> tuple[str, dict]:
    if not user_id:
        from app.services.content_style_service import _empty_context

        ctx = _empty_context("contents_generate")
        return "", _generation_meta_from_context(ctx)
    from app.services.content_style_service import content_style_service

    ctx = await content_style_service.resolve_for_route(user_id, "contents_generate")
    return _style_hint_from_context(ctx), _generation_meta_from_context(ctx)


def _convert_to_response(content_doc: dict) -> ContentResponse:
    """將 MongoDB 文檔轉換為 ContentResponse"""
    from datetime import datetime
    
    # 保存 _id（如果需要）
    mongo_id = content_doc.pop("_id", None)
    content_doc.pop("_id", None)  # 確保移除
    
    # 確保 id 欄位存在（如果沒有，使用 topic_id 或從 _id 生成）
    if "id" not in content_doc:
        if "topic_id" in content_doc:
            # 通常內容的 id 和 topic_id 相同（一個主題只有一個內容）
            content_doc["id"] = content_doc["topic_id"]
        elif mongo_id:
            # 如果沒有 topic_id，使用 MongoDB 的 _id
            content_doc["id"] = str(mongo_id)
        else:
            raise ValueError("Content document must have either 'id' or 'topic_id' field")
    
    # 確保所有必需欄位都存在
    if "word_count" not in content_doc:
        # 計算字數
        article = content_doc.get("article", "") or ""
        script = content_doc.get("script", "") or ""
        content_doc["word_count"] = len(article) + len(script)
    
    if "estimated_duration" not in content_doc:
        # 估算時長（每 150 字約 1 分鐘）
        word_count = content_doc.get("word_count", 0)
        content_doc["estimated_duration"] = max(10, int(word_count / 150 * 60))
    
    if "version" not in content_doc:
        content_doc["version"] = 1
    
    if "model_used" not in content_doc:
        content_doc["model_used"] = "unknown"
    
    if "prompt_version" not in content_doc:
        content_doc["prompt_version"] = "v1.0"
    
    if "generated_at" not in content_doc:
        content_doc["generated_at"] = datetime.utcnow()
    
    if "updated_at" not in content_doc:
        content_doc["updated_at"] = content_doc.get("generated_at", datetime.utcnow())
    
    return ContentResponse(**content_doc)


@router.get("/{topic_id}", response_model=ContentResponse)
async def get_content(
    http_request: Request,
    topic_id: str = Path(..., description="主題 ID"),
):
    """
    取得主題內容
    """
    try:
        content = await content_repo.get_content_by_topic_id(topic_id)
        if not content:
            from app.utils.i18n import get_error_message, get_user_language
            language = get_user_language(request=http_request)
            raise HTTPException(
                status_code=404,
                detail=get_error_message("content.not_found", language)
            )
        
        return _convert_to_response(content)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"取得內容失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{topic_id}/generate", response_model=ContentResponse)
async def generate_content(
    http_request: Request,
    topic_id: str = Path(..., description="主題 ID"),
    body: GenerateContentRequest = ...,
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    """
    生成內容（同步生成）
    
    注意：這是簡化版本，實際應該使用 Celery 異步任務
    """
    try:
        # 檢查主題是否存在
        from app.utils.i18n import get_user_language

        language = get_user_language(user=current_user, request=http_request)
        topic = await topic_repo.get_topic_by_id(topic_id)
        if not topic:
            from app.utils.i18n import get_error_message
            raise HTTPException(
                status_code=404,
                detail=get_error_message("content.topic_not_found", language)
            )

        from app.services.ai.ai_service_factory import AIServiceFactory
        from datetime import datetime

        ai_service = AIServiceFactory.get_service(settings.AI_SERVICE)
        logger.info("generate %s AI=%s", topic_id, settings.AI_SERVICE)

        keywords = []
        source_urls = []
        for source in topic.get("sources", []):
            if "keywords" in source:
                keywords.extend(source["keywords"])
            if "url" in source:
                source_urls.append(source["url"])

        summary_flash = _require_summary_flash(topic, language)
        uid = None
        if current_user:
            uid = current_user.get("id") or current_user.get("user_id")
        style_hint, generation_meta = await _resolve_generate_style(uid)
        pro_model = _pro_model()
        pro_max_tokens = int(getattr(settings, "DEEPSEEK_PRO_MAX_TOKENS", 4096))
        target_lang = body.language or topic.get("display_language", "zh-TW")
        from app.prompts.article_prompt import build_article_prompt

        if body.type == "article":
            prompt = build_article_prompt(
                topic_title=topic["title"],
                topic_category=topic["category"],
                keywords=keywords,
                target_length=body.article_length,
                summary_flash=summary_flash,
                source_urls=source_urls,
                target_language=target_lang,
                style_hint=style_hint,
            )
            article = await ai_service._call_api(
                prompt, model=pro_model, max_tokens=pro_max_tokens
            )
            script = None
        elif body.type == "script":
            script = await ai_service.generate_script(
                topic_title=topic["title"],
                topic_category=topic["category"],
                keywords=keywords,
                duration=body.script_duration,
            )
            article = None
        else:
            article_prompt = build_article_prompt(
                topic_title=topic["title"],
                topic_category=topic["category"],
                keywords=keywords,
                target_length=body.article_length,
                summary_flash=summary_flash,
                source_urls=source_urls,
                target_language=target_lang,
                style_hint=style_hint,
            )
            article = await ai_service._call_api(
                article_prompt, model=pro_model, max_tokens=pro_max_tokens
            )
            script = await ai_service.generate_script(
                topic_title=topic["title"],
                topic_category=topic["category"],
                keywords=keywords,
                duration=body.script_duration,
            )
        
        # 計算字數和時長
        word_count = len(article or "") + len(script or "")
        estimated_duration = word_count // 17  # 假設每 17 字 = 1 秒
        
        # 提取來源圖片
        source_images = []
        for source in topic.get("sources", []):
            if "images" in source and source["images"]:
                source_images.extend(source["images"])
        
        # 檢查是否已存在內容
        existing_content = await content_repo.get_content_by_topic_id(topic_id)
        
        now = datetime.utcnow()
        
        if existing_content:
            # 更新現有內容
            content_id = existing_content["id"]
            update_data = {
                "article": article,
                "script": script,
                "word_count": word_count,
                "estimated_duration": estimated_duration,
                "model_used": pro_model if body.type in ("article", "both") else getattr(ai_service, "model", "unknown"),
                "prompt_version": "v3.1-content-style-dna",
                "source_urls": source_urls,
                "source_images": source_images,
                "generation_meta": generation_meta,
            }
            
            updated = await content_repo.update_content(
                content_id,
                update_data,
                create_version=True
            )
            
            return _convert_to_response(updated)
        else:
            # 建立新內容
            content_data = {
                "id": f"content_{topic_id}",
                "topic_id": topic_id,
                "article": article,
                "script": script,
                "word_count": word_count,
                "estimated_duration": estimated_duration,
                "model_used": pro_model if body.type in ("article", "both") else getattr(ai_service, "model", "unknown"),
                "prompt_version": "v3.1-content-style-dna",
                "source_urls": source_urls,
                "source_images": source_images,
                "generation_meta": generation_meta,
                "version": 1,
                "generated_at": now,
                "updated_at": now
            }
            
            created = await content_repo.create_content(content_data)
            return _convert_to_response(created)
            
    except ValueError as e:
        error_msg = str(e)
        logger.error(f"生成內容失敗 (ValueError): {error_msg}")
        
        # 如果是 API Key 未設定的錯誤，提供更詳細的錯誤訊息和建議
        if "API Key 未設定" in error_msg or "未設定" in error_msg:
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=400,
                content={
                    "detail": error_msg,
                    "message": error_msg,
                    "suggestion": f"請在後端環境變數中設置 {settings.AI_SERVICE.upper()}_API_KEY。\n"
                                 f"1. 如果使用 DeepSeek，請設置 DEEPSEEK_API_KEY\n"
                                 f"2. 訪問 https://platform.deepseek.com/api_keys 獲取 API Key\n"
                                 f"3. 在 Railway/Docker 環境變數中添加 DEEPSEEK_API_KEY=sk-你的API Key"
                }
            )
        
        raise HTTPException(status_code=400, detail=error_msg)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成內容失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{topic_id}", response_model=ContentResponse)
async def update_content(
    http_request: Request,
    topic_id: str = Path(..., description="主題 ID"),
    update_data: ContentUpdate = ...,
):
    """
    更新內容
    """
    try:
        # 準備更新資料
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # 更新字數統計（如果內容有變更）
        if "article" in update_dict or "script" in update_dict:
            content = await content_repo.get_content_by_topic_id(topic_id)
            if content:
                article = update_dict.get("article", content.get("article", ""))
                script = update_dict.get("script", content.get("script", ""))
                word_count = len(article) + len(script)
                update_dict["word_count"] = word_count
                
                # 估算時長（假設每 17 字 = 1 秒）
                update_dict["estimated_duration"] = word_count // 17
        
        # 更新內容
        updated = await content_repo.update_content_by_topic_id(
            topic_id,
            update_dict,
            create_version=True
        )
        
        if not updated:
            from app.utils.i18n import get_error_message, get_user_language
            language = get_user_language(request=http_request)
            raise HTTPException(
                status_code=404,
                detail=get_error_message("content.not_found", language)
            )
        
        return _convert_to_response(updated)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新內容失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{topic_id}/versions", response_model=ContentVersionsResponse)
async def get_content_versions(topic_id: str = Path(..., description="主題 ID")):
    """
    取得內容版本歷史
    """
    try:
        versions = await content_repo.get_content_versions(topic_id)
        
        version_responses = []
        for version in versions:
            version_responses.append(ContentVersionResponse(**version))
        
        return ContentVersionsResponse(data=version_responses)
    except Exception as e:
        logger.error(f"取得版本歷史失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{topic_id}/regenerate", response_model=ContentResponse)
async def regenerate_content(
    http_request: Request,
    topic_id: str = Path(..., description="主題 ID"),
    body: GenerateContentRequest = ...,
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    """
    重新生成內容（同步生成）
    
    注意：這是簡化版本，實際應該使用 Celery 異步任務
    """
    try:
        # 檢查主題是否存在
        topic = await topic_repo.get_topic_by_id(topic_id)
        if not topic:
            from app.utils.i18n import get_error_message, get_user_language
            language = get_user_language(request=http_request)
            raise HTTPException(
                status_code=404,
                detail=get_error_message("content.topic_not_found", language)
            )
        
        # 調用生成內容端點（邏輯相同）
        return await generate_content(http_request, topic_id, body, current_user)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"重新生成內容失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))
