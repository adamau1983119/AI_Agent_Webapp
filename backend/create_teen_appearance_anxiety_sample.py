"""
建立「13-16青少年的容貌焦慮」主題範例
使用真實 API 生成內容和搜尋圖片
"""
import asyncio
import json
import hashlib
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


async def create_teen_appearance_anxiety_topic():
    """建立青少年容貌焦慮主題"""
    topic_repo = TopicRepository()
    
    topic_data = {
        "id": "teen_appearance_anxiety_2026",
        "title": "13-16青少年的容貌焦慮",
        "category": Category.TREND,
        "status": Status.PENDING,
        "source": "Social Media Today",
        "sources": [
            {
                "name": "Social Media Today",
                "url": "https://www.socialmediatoday.com",
                "type": "trend_media",
                "keywords": ["teenager", "appearance anxiety", "body image", "social media", "mental health", "青少年", "容貌焦慮", "身體形象", "社交媒體", "心理健康", "13-16歲", "adolescent"],
                "verified": True,
                "verified_at": datetime.utcnow().isoformat(),
                "reliability": "high"
            },
            {
                "name": "Psychology Today",
                "url": "https://www.psychologytoday.com",
                "type": "psychology_media",
                "keywords": ["appearance anxiety", "body image", "teenagers", "social media impact", "mental health", "容貌焦慮", "身體形象", "青少年", "社交媒體影響"],
                "verified": True,
                "verified_at": datetime.utcnow().isoformat(),
                "reliability": "high"
            },
            {
                "name": "Common Sense Media",
                "url": "https://www.commonsensemedia.org",
                "type": "education_platform",
                "keywords": ["teen social media", "body image", "self-esteem", "adolescent mental health", "青少年社交媒體", "身體形象", "自尊", "青少年心理健康"],
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
        existing = await topic_repo.get_topic_by_id("teen_appearance_anxiety_2026")
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


async def generate_content_for_teen_anxiety():
    """為青少年容貌焦慮主題生成內容"""
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
    
    topic_id = "teen_appearance_anxiety_2026"
    
    # 取得主題
    topic = await topic_repo.get_topic_by_id(topic_id)
    if not topic:
        raise ValueError(f"主題不存在: {topic_id}")
    
    # 提取關鍵字
    keywords = []
    for source in topic.get("sources", []):
        keywords.extend(source.get("keywords", []))
    keywords = list(set(keywords))  # 去重
    
    logger.info(f"📝 開始生成青少年容貌焦慮內容，關鍵字: {keywords}")
    
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
        
        # 生成唯一 ID
        content_id = f"content_{topic_id}_{hashlib.md5((article[:50] + script[:50]).encode()).hexdigest()[:12]}"
        
        # 儲存內容
        content_data = {
            "id": content_id,
            "topic_id": topic_id,
            "article": article,
            "script": script,
            "word_count": word_count,
            "model_used": settings.AI_SERVICE,
            "generated_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "versions": []
        }
        
        # 檢查是否已存在內容
        existing_content = await content_repo.get_content_by_topic_id(topic_id)
        if existing_content:
            # 更新現有內容
            content_id = existing_content.get("id") or existing_content.get("_id")
            if content_id:
                await content_repo.update_content(
                    content_id,
                    content_data,
                    create_version=True
                )
                logger.info("✅ 內容已更新")
            else:
                # 如果沒有 ID，建立新內容
                await content_repo.create_content(content_data)
                logger.info("✅ 內容已建立（新）")
        else:
            # 建立新內容
            await content_repo.create_content(content_data)
            logger.info("✅ 內容已建立")
        
        return {"article": article, "script": script}
    except Exception as e:
        logger.error(f"❌ 生成內容失敗: {e}")
        raise


async def search_images_for_teen_anxiety():
    """為青少年容貌焦慮主題搜尋圖片"""
    image_repo = ImageRepository()
    image_manager = ImageServiceManager()
    
    topic_id = "teen_appearance_anxiety_2026"
    
    # 青少年心理健康相關關鍵字
    keywords = "teenager mental health social media body image self-esteem adolescent 青少年 心理健康 社交媒體 身體形象"
    
    logger.info(f"🖼️ 開始搜尋青少年心理健康圖片，關鍵字: {keywords}")
    
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
            image_id = img.get("id") or img.get("_id")
            if image_id:
                await image_repo.delete_image(image_id)
        
        # 儲存新圖片
        saved_images = []
        for idx, img in enumerate(images[:8]):  # 最多儲存 8 張
            # 生成唯一 ID
            image_id = f"img_{hashlib.md5(img.get('url', '').encode()).hexdigest()[:12]}"
            
            image_data = {
                "id": image_id,
                "topic_id": topic_id,
                "url": img.get("url", ""),
                "source": ImageSource(img.get("source", "Unsplash")),
                "photographer": img.get("photographer", ""),
                "photographer_url": img.get("photographer_url", ""),
                "license": img.get("license", "Unsplash License"),
                "keywords": img.get("keywords", []),
                "order": idx,
                "width": img.get("width"),
                "height": img.get("height"),
                "fetched_at": datetime.utcnow(),
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
    logger.info("📱 開始建立「13-16青少年的容貌焦慮」主題")
    logger.info("=" * 60)
    
    try:
        # 連接資料庫
        await connect_to_mongo()
        logger.info("✅ 資料庫連接成功")
        
        # 1. 建立主題
        logger.info("\n📋 步驟 1: 建立趨勢主題")
        topic = await create_teen_appearance_anxiety_topic()
        
        # 2. 生成內容
        logger.info("\n📝 步驟 2: 生成內容（使用真實 AI API）")
        content = await generate_content_for_teen_anxiety()
        
        # 3. 搜尋圖片
        logger.info("\n🖼️ 步驟 3: 搜尋圖片（使用真實圖片 API）")
        images = await search_images_for_teen_anxiety()
        
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
        with open("teen_anxiety_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ 青少年容貌焦慮主題建立完成！")
        logger.info("=" * 60)
        logger.info(f"📄 結果已儲存到: teen_anxiety_result.json")
        logger.info(f"🌐 可以在 Dashboard 查看: http://localhost:5173/topics/{topic['id']}")
        
    except Exception as e:
        logger.error(f"❌ 執行失敗: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())

