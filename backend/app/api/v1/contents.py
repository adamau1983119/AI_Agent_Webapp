"""
Contents API 端點
"""
from fastapi import APIRouter, HTTPException, Path
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


def _convert_to_response(content_doc: dict) -> ContentResponse:
    """將 MongoDB 文檔轉換為 ContentResponse"""
    from datetime import datetime
    
    content_doc.pop("_id", None)
    
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
async def get_content(topic_id: str = Path(..., description="主題 ID")):
    """
    取得主題內容
    """
    try:
        content = await content_repo.get_content_by_topic_id(topic_id)
        if not content:
            raise HTTPException(
                status_code=404,
                detail=f"內容不存在: topic_id={topic_id}"
            )
        
        return _convert_to_response(content)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"取得內容失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{topic_id}/generate", response_model=ContentResponse)
async def generate_content(
    topic_id: str = Path(..., description="主題 ID"),
    request: GenerateContentRequest = ...
):
    """
    生成內容（同步生成）
    
    注意：這是簡化版本，實際應該使用 Celery 異步任務
    """
    try:
        # 檢查主題是否存在
        topic = await topic_repo.get_topic_by_id(topic_id)
        if not topic:
            raise HTTPException(
                status_code=404,
                detail=f"主題不存在: {topic_id}"
            )
        
        # 調用 AI 服務生成內容（根據配置選擇服務）
        from app.config import settings
        from datetime import datetime
        
        # 根據配置選擇 AI 服務
        if settings.AI_SERVICE in ["ollama", "ollama_cloud"]:
            from app.services.ai.ollama import OllamaService
            ai_service = OllamaService()
        elif settings.AI_SERVICE == "gemini":
            from app.services.ai.gemini import GeminiService
            ai_service = GeminiService()
        elif settings.AI_SERVICE == "openai":
            from app.services.ai.openai import OpenAIService
            ai_service = OpenAIService()
        else:  # 預設使用通義千問
            from app.services.ai.qwen import QwenService
            ai_service = QwenService()
        
        # 取得關鍵字（從主題的 sources 中提取）
        keywords = []
        for source in topic.get("sources", []):
            if "keywords" in source:
                keywords.extend(source["keywords"])
        
        # 生成內容
        if request.type == "article":
            article = await ai_service.generate_article(
                topic_title=topic["title"],
                topic_category=topic["category"],
                keywords=keywords,
                length=request.article_length
            )
            script = None
        elif request.type == "script":
            script = await ai_service.generate_script(
                topic_title=topic["title"],
                topic_category=topic["category"],
                keywords=keywords,
                duration=request.script_duration
            )
            article = None
        else:  # both
            result = await ai_service.generate_both(
                topic_title=topic["title"],
                topic_category=topic["category"],
                keywords=keywords,
                article_length=request.article_length,
                script_duration=request.script_duration
            )
            article = result["article"]
            script = result["script"]
        
        # 計算字數和時長
        word_count = len(article or "") + len(script or "")
        estimated_duration = word_count // 17  # 假設每 17 字 = 1 秒
        
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
                "model_used": getattr(ai_service, 'model', getattr(ai_service, 'model_name', 'unknown')),
                "prompt_version": "v1.0"
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
                "model_used": getattr(ai_service, 'model', getattr(ai_service, 'model_name', 'unknown')),
                "prompt_version": "v1.0",
                "version": 1,
                "generated_at": now,
                "updated_at": now
            }
            
            created = await content_repo.create_content(content_data)
            return _convert_to_response(created)
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成內容失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{topic_id}", response_model=ContentResponse)
async def update_content(
    topic_id: str = Path(..., description="主題 ID"),
    update_data: ContentUpdate = ...
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
            raise HTTPException(
                status_code=404,
                detail=f"內容不存在: topic_id={topic_id}"
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
    topic_id: str = Path(..., description="主題 ID"),
    request: GenerateContentRequest = ...
):
    """
    重新生成內容（同步生成）
    
    注意：這是簡化版本，實際應該使用 Celery 異步任務
    """
    try:
        # 檢查主題是否存在
        topic = await topic_repo.get_topic_by_id(topic_id)
        if not topic:
            raise HTTPException(
                status_code=404,
                detail=f"主題不存在: {topic_id}"
            )
        
        # 調用生成內容端點（邏輯相同）
        return await generate_content(topic_id, request)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"重新生成內容失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))
