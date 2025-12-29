"""
測試生成「2026年 Dior 春夏show」實際 Sample
"""
import asyncio
import json
from datetime import datetime
from app.database import connect_to_mongo
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


async def create_dior_topic():
    """建立 Dior 主題"""
    topic_repo = TopicRepository()
    
    topic_data = {
        "id": "dior_2026_spring_summer",
        "title": "2026年 Dior 春夏show",
        "category": Category.FASHION,
        "status": Status.PENDING,
        "source": "Dior Official",
        "sources": [
            {
                "name": "Dior Official",
                "url": "https://www.dior.com",
                "type": "official",
                "keywords": ["Dior", "2026", "春夏", "時裝秀", "fashion show", "spring summer", "巴黎", "花園", "浪漫主義"],
                "verified": True,
                "verified_at": datetime.utcnow().isoformat(),
                "reliability": "very_high"
            },
            {
                "name": "Vogue Fashion Shows",
                "url": "https://www.vogue.com/fashion-shows/spring-2026-ready-to-wear/dior",
                "type": "fashion_media",
                "keywords": ["Dior", "2026", "spring", "fashion show", "Vogue"],
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
        existing = await topic_repo.get_topic_by_id("dior_2026_spring_summer")
        if existing:
            logger.info("✅ 主題已存在，使用現有主題")
            return existing
        
        # 建立新主題
        topic = await topic_repo.create_topic(topic_data)
        logger.info(f"✅ 主題建立成功: {topic['id']}")
        return topic
    except Exception as e:
        logger.error(f"❌ 建立主題失敗: {e}")
        raise


async def generate_content_for_dior():
    """為 Dior 主題生成內容"""
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
        # 預設使用 Ollama（如果有 API Key）或 Qwen
        if settings.OLLAMA_API_KEY:
            ai_service = OllamaService()
            logger.info("使用 Ollama 雲端服務（自動選擇）")
        else:
            ai_service = QwenService()
            logger.info("使用通義千問服務（自動選擇）")
    
    topic_id = "dior_2026_spring_summer"
    
    # 取得主題
    topic = await topic_repo.get_topic_by_id(topic_id)
    if not topic:
        raise ValueError(f"主題不存在: {topic_id}")
    
    # 提取關鍵字
    keywords = []
    for source in topic.get("sources", []):
        if "keywords" in source:
            keywords.extend(source["keywords"])
    
    logger.info(f"📝 開始生成內容...")
    logger.info(f"   主題: {topic['title']}")
    logger.info(f"   分類: {topic['category']}")
    logger.info(f"   關鍵字: {', '.join(keywords)}")
    
    # 生成短文和腳本
    try:
        result = await ai_service.generate_both(
            topic_title=topic["title"],
            topic_category=topic["category"],
            keywords=keywords,
            article_length=500,
            script_duration=30
        )
        
        article = result["article"]
        script = result["script"]
        
        logger.info(f"✅ 內容生成成功")
        logger.info(f"   短文長度: {len(article)} 字")
        logger.info(f"   腳本長度: {len(script)} 字")
        
        # 計算字數和時長
        word_count = len(article) + len(script)
        estimated_duration = word_count // 17
        
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
                "model_used": getattr(ai_service, 'model', 'qwen-turbo'),
                "prompt_version": "v1.0",
                "updated_at": now
            }
            
            updated = await content_repo.update_content(
                content_id,
                update_data,
                create_version=True
            )
            
            return updated
        else:
            # 建立新內容
            content_data = {
                "id": f"content_{topic_id}",
                "topic_id": topic_id,
                "article": article,
                "script": script,
                "word_count": word_count,
                "estimated_duration": estimated_duration,
                "model_used": getattr(ai_service, 'model', 'qwen-turbo'),
                "prompt_version": "v1.0",
                "version": 1,
                "generated_at": now,
                "updated_at": now
            }
            
            created = await content_repo.create_content(content_data)
            return created
            
    except Exception as e:
        logger.error(f"❌ 生成內容失敗: {e}")
        raise


async def search_images_for_dior():
    """為 Dior 主題搜尋圖片"""
    image_repo = ImageRepository()
    image_service = ImageServiceManager()
    
    topic_id = "dior_2026_spring_summer"
    
    # 搜尋關鍵字列表（按優先順序）
    search_keywords = [
        "Dior fashion show 2026",
        "fashion runway spring summer",
        "luxury fashion elegant",
        "fashion show paris",
        "haute couture",
        "fashion model runway"
    ]
    
    logger.info(f"🖼️  開始搜尋圖片...")
    
    all_images = []
    
    for keywords in search_keywords:
        try:
            logger.info(f"   搜尋關鍵字: {keywords}")
            images = await image_service.search_images(
                keywords=keywords,
                page=1,
                limit=10
            )
            
            logger.info(f"   ✅ 找到 {len(images)} 張圖片")
            all_images.extend(images)
            
            # 如果已經找到足夠的圖片，停止搜尋
            if len(all_images) >= 20:
                break
                
        except Exception as e:
            logger.warning(f"   ⚠️ 搜尋失敗: {e}，繼續下一個關鍵字...")
            continue
    
    # 去重（根據 URL）
    seen_urls = set()
    unique_images = []
    for img in all_images:
        url = img.get("url") or img.get("image_url")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_images.append(img)
    
    logger.info(f"✅ 總共找到 {len(unique_images)} 張不重複圖片")
    
    # 選擇前 8 張圖片（可以根據評分選擇，這裡簡化為前 8 張）
    selected_images = unique_images[:8]
    
    # 驗證圖片 URL 格式
    def validate_image_url(url: str) -> bool:
        """驗證圖片 URL 格式"""
        if not url:
            return False
        # 檢查是否為有效的 HTTP/HTTPS URL
        return url.startswith("http://") or url.startswith("https://")
    
    # 儲存圖片到資料庫
    saved_images = []
    for idx, img_data in enumerate(selected_images, start=1):
        try:
            image_url = img_data.get("url") or img_data.get("image_url")
            
            # 驗證 URL 格式
            if not validate_image_url(image_url):
                logger.warning(f"   ⚠️ 圖片 {idx} URL 格式無效，跳過: {image_url}")
                continue
            
            image_data = {
                "id": f"img_{topic_id}_{idx}",
                "topic_id": topic_id,
                "url": image_url,  # 真實的 API 回應 URL
                "thumbnail_url": img_data.get("thumbnail_url") or image_url,
                "source": img_data.get("source", ImageSource.UNSPLASH),
                "photographer": img_data.get("photographer") or img_data.get("author", "Unknown"),
                "photographer_url": img_data.get("photographer_url") or "",
                "description": img_data.get("description") or img_data.get("alt", ""),
                "width": img_data.get("width", 0),
                "height": img_data.get("height", 0),
                "license": img_data.get("license", "Unsplash License"),
                "order": idx,
                "created_at": datetime.utcnow(),
                "api_response": True,  # 標記為 API 回應
                "fetched_at": datetime.utcnow()
            }
            
            created = await image_repo.create_image(image_data)
            saved_images.append(created)
            logger.info(f"   ✅ 圖片 {idx} 已儲存")
            logger.info(f"      URL: {image_url[:80]}...")
            logger.info(f"      來源: {image_data.get('source')}")
            logger.info(f"      攝影師: {image_data.get('photographer')}")
            
        except Exception as e:
            logger.warning(f"   ⚠️ 儲存圖片 {idx} 失敗: {e}")
            continue
    
    return saved_images


async def main():
    """主函數"""
    logger.info("=" * 60)
    logger.info("開始生成「2026年 Dior 春夏show」實際 Sample")
    logger.info("=" * 60)
    
    # 預先檢查配置
    from app.config import settings
    
    # 檢查 AI 服務配置
    ai_service_configured = False
    if settings.AI_SERVICE in ["ollama", "ollama_cloud"]:
        if settings.OLLAMA_API_KEY:
            ai_service_configured = True
            logger.info(f"✅ 使用 Ollama 雲端 API（已設定 API Key）")
        else:
            logger.warning("⚠️ OLLAMA_API_KEY 未設定，將嘗試使用本地 Ollama")
            ai_service_configured = True  # 本地 Ollama 不需要 API Key
    elif settings.AI_SERVICE == "qwen":
        if settings.QWEN_API_KEY:
            ai_service_configured = True
            logger.info("✅ 使用通義千問 API（已設定 API Key）")
        else:
            logger.error("❌ 錯誤：QWEN_API_KEY 未設定")
            logger.error("   請在 .env 檔案中設定 QWEN_API_KEY")
            logger.error("   或切換到 Ollama 服務（設定 AI_SERVICE=ollama）")
            logger.error("   參考文件：Dior_Sample失敗原因分析與解決方案.md")
            return
    else:
        # 自動選擇：優先使用 Ollama（如果有 API Key），否則使用 Qwen
        if settings.OLLAMA_API_KEY:
            ai_service_configured = True
            logger.info("✅ 自動選擇：使用 Ollama 雲端 API")
        elif settings.QWEN_API_KEY:
            ai_service_configured = True
            logger.info("✅ 自動選擇：使用通義千問 API")
        else:
            logger.error("❌ 錯誤：未設定任何 AI 服務的 API Key")
            logger.error("   請在 .env 檔案中設定以下任一項：")
            logger.error("   - OLLAMA_API_KEY（推薦）")
            logger.error("   - QWEN_API_KEY")
            logger.error("   參考文件：Dior_Sample失敗原因分析與解決方案.md")
            return
    
    try:
        # 連接資料庫
        await connect_to_mongo()
        logger.info("✅ 資料庫連接成功")
        
        # 1. 建立主題
        logger.info("\n" + "=" * 60)
        logger.info("步驟 1: 建立主題")
        logger.info("=" * 60)
        topic = await create_dior_topic()
        
        # 2. 生成內容
        logger.info("\n" + "=" * 60)
        logger.info("步驟 2: 生成內容")
        logger.info("=" * 60)
        content = await generate_content_for_dior()
        
        # 3. 搜尋圖片
        logger.info("\n" + "=" * 60)
        logger.info("步驟 3: 搜尋圖片")
        logger.info("=" * 60)
        images = await search_images_for_dior()
        
        # 4. 輸出結果
        logger.info("\n" + "=" * 60)
        logger.info("生成結果摘要")
        logger.info("=" * 60)
        logger.info(f"✅ 主題 ID: {topic['id']}")
        logger.info(f"✅ 主題標題: {topic['title']}")
        logger.info(f"✅ 內容 ID: {content['id']}")
        logger.info(f"✅ 短文長度: {content['word_count']} 字")
        logger.info(f"✅ 圖片數量: {len(images)} 張")
        
        # 儲存結果到檔案
        result = {
            "topic": {
                "id": topic["id"],
                "title": topic["title"],
                "category": topic["category"],
                "status": topic["status"],
                "sources": topic.get("sources", [])
            },
            "content": {
                "id": content["id"],
                "article": content.get("article", ""),
                "script": content.get("script", ""),
                "word_count": content.get("word_count", 0),
                "estimated_duration": content.get("estimated_duration", 0),
                "model_used": content.get("model_used", "unknown")
            },
            "images": [
                {
                    "id": img["id"],
                    "url": img.get("url", ""),
                    "description": img.get("description", ""),
                    "source": img.get("source", ""),
                    "photographer": img.get("photographer", "")
                }
                for img in images
            ],
            "generated_at": datetime.utcnow().isoformat()
        }
        
        with open("dior_sample_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\n✅ 結果已儲存到: dior_sample_result.json")
        logger.info("\n" + "=" * 60)
        logger.info("生成完成！")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ 執行失敗: {e}")
        import traceback
        traceback.print_exc()
    finally:
        from app.database import close_mongo_connection
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())

