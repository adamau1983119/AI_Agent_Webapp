"""
建立「社會媒體趨勢」主題範例
示範如何建立 TREND 類別的主題並生成內容和圖片
"""
import asyncio
import json
from datetime import datetime
from app.database import connect_to_mongo, close_mongo_connection
from app.services.repositories.topic_repository import TopicRepository
from app.services.repositories.content_repository import ContentRepository
from app.services.repositories.image_repository import ImageRepository
from app.services.ai.qwen import QwenService
from app.services.ai.ollama import OllamaService
from app.services.images.image_service_manager import ImageServiceManager
from app.config import settings
from app.models.topic import Category, Status
from app.models.image import ImageSource
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_trend_topic():
    """建立社會媒體趨勢主題範例：2026年社交媒體內容創作趨勢"""
    topic_repo = TopicRepository()
    
    topic_data = {
        "id": "social_media_trends_2026",
        "title": "2026年社交媒體內容創作趨勢",
        "category": Category.TREND,  # 趨勢分類
        "status": Status.PENDING,
        "source": "Social Media Today",
        "sources": [
            {
                "name": "Social Media Today",
                "url": "https://www.socialmediatoday.com",
                "type": "trend_media",
                "keywords": ["social media", "trends", "2026", "content creation", "social media marketing", "trends", "digital marketing"],
                "verified": True,
                "verified_at": datetime.utcnow().isoformat(),
                "reliability": "high"
            },
            {
                "name": "Hootsuite Blog",
                "url": "https://blog.hootsuite.com",
                "type": "social_media_platform",
                "keywords": ["Hootsuite", "social media trends", "content strategy", "social media marketing"],
                "verified": True,
                "verified_at": datetime.utcnow().isoformat(),
                "reliability": "high"
            },
            {
                "name": "Sprout Social",
                "url": "https://sproutsocial.com/insights",
                "type": "social_media_platform",
                "keywords": ["Sprout Social", "social media trends", "content creation", "social media strategy"],
                "verified": True,
                "verified_at": datetime.utcnow().isoformat(),
                "reliability": "high"
            }
        ],
        "generated_at": datetime.utcnow(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    try:
        # 檢查是否已存在
        existing = await topic_repo.get_topic_by_id("social_media_trends_2026")
        if existing:
            logger.info("✅ 主題已存在，使用現有主題")
            return existing
        
        # 建立新主題
        topic = await topic_repo.create_topic(topic_data)
        logger.info(f"✅ 趨勢主題建立成功: {topic['id']}")
        return topic
    except Exception as e:
        logger.error(f"❌ 建立主題失敗: {e}")
        raise


async def generate_content_for_trend():
    """為趨勢主題生成內容"""
    content_repo = ContentRepository()
    topic_repo = TopicRepository()
    
    # 根據配置選擇 AI 服務
    if settings.AI_SERVICE in ["ollama", "ollama_cloud"]:
        ai_service = OllamaService()
        logger.info(f"使用 Ollama 服務（{'雲端' if settings.OLLAMA_API_KEY else '本地'}）")
    elif settings.AI_SERVICE == "qwen":
        ai_service = QwenService()
        logger.info("使用通義千問服務")
    else:
        if settings.OLLAMA_API_KEY:
            ai_service = OllamaService()
            logger.info("使用 Ollama 雲端服務（自動選擇）")
        else:
            ai_service = QwenService()
            logger.info("使用通義千問服務（自動選擇）")
    
    topic_id = "social_media_trends_2026"
    
    # 取得主題
    topic = await topic_repo.get_topic_by_id(topic_id)
    if not topic:
        raise ValueError(f"主題不存在: {topic_id}")
    
    # 提取關鍵字
    keywords = []
    for source in topic.get("sources", []):
        keywords.extend(source.get("keywords", []))
    keywords = list(set(keywords))  # 去重
    
    logger.info(f"📝 開始生成趨勢內容，關鍵字: {keywords}")
    
    try:
        # 生成短文（500字以內）和腳本（30秒以內）
        result = await ai_service.generate_both(
            topic_title=topic["title"],
            topic_category=topic["category"],
            keywords=keywords,
            article_length=500,
            script_duration=30
        )
        
        article = result.get("article", "")
        script = result.get("script", "")
        
        logger.info(f"✅ 內容生成成功")
        logger.info(f"📄 短文長度: {len(article)} 字")
        logger.info(f"🎬 腳本長度: {len(script)} 字")
        
        # 計算字數
        word_count = len(article) + len(script)
        
        # 儲存內容
        content_data = {
            "topic_id": topic_id,
            "article": article,
            "script": script,
            "word_count": word_count,
            "generated_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "versions": []
        }
        
        # 檢查是否已存在內容
        existing_content = await content_repo.get_content_by_topic_id(topic_id)
        if existing_content:
            # 更新現有內容
            await content_repo.update_content(
                existing_content["id"],
                content_data,
                create_version=True
            )
            logger.info("✅ 內容已更新")
        else:
            # 建立新內容
            await content_repo.create_content(content_data)
            logger.info("✅ 內容已建立")
        
        return {"article": article, "script": script}
    except Exception as e:
        logger.error(f"❌ 生成內容失敗: {e}")
        raise


async def search_images_for_trend():
    """為趨勢主題搜尋圖片"""
    image_repo = ImageRepository()
    image_manager = ImageServiceManager()
    
    topic_id = "social_media_trends_2026"
    
    # 趨勢相關關鍵字
    keywords = "social media trends content creation digital marketing 2026"
    
    logger.info(f"🖼️ 開始搜尋趨勢圖片，關鍵字: {keywords}")
    
    try:
        # 搜尋圖片
        images = await image_manager.search_images(
            keywords=keywords,
            page=1,
            limit=8  # 選擇 8 張圖片
        )
        
        if not images:
            logger.warning("⚠️ 未找到圖片")
            return []
        
        logger.info(f"✅ 找到 {len(images)} 張圖片")
        
        # 刪除現有圖片
        existing_images = await image_repo.get_images_by_topic_id(topic_id)
        for img in existing_images:
            await image_repo.delete_image(img["id"])
        
        # 儲存新圖片
        saved_images = []
        for idx, img in enumerate(images[:8]):  # 最多儲存 8 張
            image_data = {
                "topic_id": topic_id,
                "url": img.get("url", ""),
                "source": ImageSource(img.get("source", "Unsplash")),
                "photographer": img.get("photographer"),
                "photographer_url": img.get("photographer_url"),
                "license": img.get("license", "Unsplash License"),
                "keywords": img.get("keywords", []),
                "order": idx,
                "width": img.get("width"),
                "height": img.get("height"),
                "fetched_at": datetime.utcnow(),
                "api_response": True,  # 標記為 API 回應
                "fetched_at": datetime.utcnow()
            }
            
            image = await image_repo.create_image(image_data)
            saved_images.append(image)
            logger.info(f"✅ 圖片 {idx + 1}/8 已儲存: {img.get('url', '')[:50]}...")
        
        logger.info(f"✅ 共儲存 {len(saved_images)} 張圖片")
        return saved_images
    except Exception as e:
        logger.error(f"❌ 搜尋圖片失敗: {e}")
        raise


async def main():
    """主函數"""
    logger.info("=" * 60)
    logger.info("📱 開始建立社會媒體趨勢主題範例")
    logger.info("=" * 60)
    
    try:
        # 連接資料庫
        await connect_to_mongo()
        logger.info("✅ 資料庫連接成功")
        
        # 1. 建立主題
        logger.info("\n📋 步驟 1: 建立趨勢主題")
        topic = await create_trend_topic()
        
        # 2. 生成內容
        logger.info("\n📝 步驟 2: 生成內容")
        content = await generate_content_for_trend()
        
        # 3. 搜尋圖片
        logger.info("\n🖼️ 步驟 3: 搜尋圖片")
        images = await search_images_for_trend()
        
        # 4. 儲存結果
        result = {
            "topic": {
                "id": topic["id"],
                "title": topic["title"],
                "category": topic["category"],
                "status": topic["status"]
            },
            "content": {
                "article": content["article"],
                "script": content["script"],
                "word_count": len(content["article"]) + len(content["script"])
            },
            "images": [
                {
                    "url": img["url"],
                    "source": img["source"],
                    "order": img["order"]
                }
                for img in images
            ],
            "created_at": datetime.utcnow().isoformat()
        }
        
        # 儲存到檔案
        with open("trend_sample_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ 社會媒體趨勢主題建立完成！")
        logger.info("=" * 60)
        logger.info(f"📄 結果已儲存到: trend_sample_result.json")
        logger.info(f"🌐 可以在 Dashboard 查看: http://localhost:3000/topics/{topic['id']}")
        
    except Exception as e:
        logger.error(f"❌ 執行失敗: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())

