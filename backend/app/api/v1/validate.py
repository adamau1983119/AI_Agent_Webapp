"""
資料驗證 API 端點
"""
from typing import List
from fastapi import APIRouter, HTTPException, Body
from app.services.automation.data_validator import DataValidator
from app.models.topic import Category
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/validate", tags=["validate"])

# Service 實例
data_validator = DataValidator()


@router.post("/sources")
async def validate_sources(
    topic_id: str = Body(..., description="主題 ID"),
    sources: List[dict] = Body(..., description="來源列表")
):
    """
    驗證並抓取來源資料
    """
    try:
        validated_sources = []
        failed_sources = []
        
        for source in sources:
            validation_result = await data_validator.validate_and_fetch_source(
                source_url=source.get("url", ""),
                source_name=source.get("name", "")
            )
            
            if validation_result.get("valid"):
                validated_sources.append(validation_result)
            else:
                failed_sources.append({
                    "source": source,
                    "reason": validation_result.get("reason", "驗證失敗")
                })
        
        return {
            "topic_id": topic_id,
            "validated_sources": validated_sources,
            "validation_summary": {
                "total_sources": len(sources),
                "verified_sources": len(validated_sources),
                "failed_sources": len(failed_sources)
            },
            "failed_sources": failed_sources
        }
    except Exception as e:
        logger.error(f"驗證來源失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/topic-consistency")
async def validate_topic_consistency(
    keyword: str = Body(..., description="關鍵字"),
    category: Category = Body(..., description="主題分類"),
    sources: List[dict] = Body(..., description="來源列表")
):
    """
    驗證主題的跨來源一致性
    """
    try:
        validation = await data_validator.validate_topic_consistency(
            keyword=keyword,
            category=category,
            sources=sources
        )
        
        return {
            "valid": validation.get("valid", False),
            "confidence": validation.get("consistency_score", 0.0),
            "consistency_score": validation.get("consistency_score", 0.0),
            "sources_verified": len(sources),
            "is_factual": validation.get("is_factual", False),
            "warnings": [validation.get("warning")] if validation.get("warning") else []
        }
    except Exception as e:
        logger.error(f"驗證一致性失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/source-health/{source_url:path}")
async def check_source_health(source_url: str):
    """
    檢查來源健康度
    """
    try:
        health = await data_validator.check_source_health(source_url)
        return health
    except Exception as e:
        logger.error(f"檢查來源健康度失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

