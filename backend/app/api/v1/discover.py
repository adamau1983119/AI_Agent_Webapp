"""
主題發掘 API 端點
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Body
from app.models.topic import Category
from app.services.automation.enhanced_topic_collector import EnhancedTopicCollector
from app.services.automation.data_validator import DataValidator
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/discover", tags=["discover"])

# Service 實例
topic_collector = EnhancedTopicCollector()
data_validator = DataValidator()


@router.post("/topics/auto")
async def auto_discover_topics(
    category: Category = Body(..., description="主題分類"),
    region: str = Body(default="global", description="地區"),
    count: int = Body(default=3, ge=1, le=10, description="生成數量"),
    time_slot: str = Body(default="morning", description="時間段")
):
    """
    自動發掘當日排行榜前3位關鍵字（排程觸發）
    """
    try:
        # 使用增強版主題收集器（3-2-1備援機制）
        topics = await topic_collector.collect_topics_with_redundancy(
            category=category,
            count=count,
            region=region
        )
        
        # 為每個主題驗證一致性
        validated_topics = []
        for topic in topics:
            # 驗證一致性
            validation = await data_validator.validate_topic_consistency(
                keyword=topic.get("keyword", topic.get("title", "")),
                category=category,
                sources=topic.get("sources", [])
            )
            
            if validation.get("valid"):
                topic["validation"] = validation
                validated_topics.append(topic)
            else:
                logger.warning(f"主題 {topic.get('title')} 驗證失敗: {validation.get('reason')}")
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "category": category.value,
            "time_slot": time_slot,
            "region": region,
            "topics": validated_topics
        }
    except Exception as e:
        logger.error(f"自動發掘主題失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/topics/manual")
async def manual_discover_topics(
    category: Category = Body(..., description="主題分類"),
    region: str = Body(default="global", description="地區"),
    count: int = Body(default=3, ge=1, le=10, description="生成數量")
):
    """
    手動觸發主題發掘
    """
    try:
        topics = await topic_collector.collect_topics_with_redundancy(
            category=category,
            count=count,
            region=region
        )
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "category": category.value,
            "region": region,
            "topics": topics
        }
    except Exception as e:
        logger.error(f"手動發掘主題失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/topics/rankings")
async def get_rankings(
    category: Category = Query(..., description="主題分類"),
    region: str = Query(default="global", description="地區"),
    date: Optional[str] = Query(None, description="日期（YYYY-MM-DD）")
):
    """
    查詢排行榜關鍵字
    """
    try:
        # 簡化版：返回模擬排行榜數據
        # 實際應該從 Google Trends API 或其他來源獲取
        
        rankings = [
            {
                "rank": 1,
                "keyword": "Dior 2026 春夏秀" if category == Category.FASHION else "元朗最好食燒賣top 3" if category == Category.FOOD else "13-16歲青少年的容貌焦慮",
                "search_volume": 50000,
                "trend": "up",
                "source": "Vogue Trending" if category == Category.FASHION else "Google Trends" if category == Category.FOOD else "學術資料庫"
            },
            {
                "rank": 2,
                "keyword": "Gucci 新系列" if category == Category.FASHION else "香港美食推薦" if category == Category.FOOD else "社會趨勢分析",
                "search_volume": 35000,
                "trend": "stable",
                "source": "WWD" if category == Category.FASHION else "OpenRice" if category == Category.FOOD else "新聞網站"
            },
            {
                "rank": 3,
                "keyword": "巴黎時裝週" if category == Category.FASHION else "街頭小吃" if category == Category.FOOD else "科技創新",
                "search_volume": 28000,
                "trend": "down",
                "source": "Fashion Week" if category == Category.FASHION else "大眾點評" if category == Category.FOOD else "社交媒體"
            }
        ]
        
        return {
            "date": date or datetime.utcnow().strftime("%Y-%m-%d"),
            "category": category.value,
            "region": region,
            "rankings": rankings
        }
    except Exception as e:
        logger.error(f"查詢排行榜失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

