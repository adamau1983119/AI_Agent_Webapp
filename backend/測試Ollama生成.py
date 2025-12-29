"""
測試 Ollama 本地 AI 生成功能
"""
import asyncio
from app.database import connect_to_mongo, close_mongo_connection
from app.services.repositories.topic_repository import TopicRepository
from app.services.repositories.content_repository import ContentRepository
from app.services.ai.ollama import OllamaService
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_ollama_generation():
    """測試 Ollama 生成功能"""
    await connect_to_mongo()
    
    try:
        # 檢查 Ollama 配置
        if settings.OLLAMA_API_KEY:
            logger.info("使用 Ollama 雲端 API")
            logger.info(f"Ollama Cloud URL: {settings.OLLAMA_CLOUD_BASE_URL}")
            logger.info(f"Ollama Model: {settings.OLLAMA_MODEL}")
            logger.info(f"API Key: {settings.OLLAMA_API_KEY[:20]}...")
        else:
            logger.info("使用 Ollama 本地部署")
            logger.info(f"Ollama URL: {settings.OLLAMA_BASE_URL}")
            logger.info(f"Ollama Model: {settings.OLLAMA_MODEL}")
        
        topic_repo = TopicRepository()
        content_repo = ContentRepository()
        
        # 初始化 Ollama 服務
        try:
            ai_service = OllamaService()
            if ai_service.use_cloud:
                logger.info("✅ Ollama 雲端服務初始化成功")
            else:
                logger.info("✅ Ollama 本地服務初始化成功")
        except Exception as e:
            logger.error(f"❌ Ollama 服務初始化失敗: {e}")
            if settings.OLLAMA_API_KEY:
                logger.info("請檢查：")
                logger.info("1. API Key 是否正確")
                logger.info("2. OLLAMA_CLOUD_BASE_URL 是否正確")
                logger.info("3. 網路連接是否正常")
            else:
                logger.info("請確保 Ollama 正在運行：")
                logger.info("1. 安裝 Ollama: https://ollama.ai/download")
                logger.info(f"2. 下載模型: ollama pull {settings.OLLAMA_MODEL}")
                logger.info("3. 啟動服務: ollama serve（通常會自動啟動）")
            return
        
        # 取得測試主題
        topic_id = "topic_001"
        topic = await topic_repo.get_topic_by_id(topic_id)
        
        if not topic:
            logger.error(f"❌ 主題 {topic_id} 不存在，請先執行 建立測試資料.py")
            return
        
        logger.info(f"✅ 找到主題: {topic['title']}")
        
        # 取得關鍵字
        keywords = []
        for source in topic.get("sources", []):
            if "keywords" in source:
                keywords.extend(source["keywords"])
        
        logger.info(f"關鍵字: {', '.join(keywords)}")
        
        # 測試生成短文
        logger.info("\n開始生成短文（這可能需要一些時間）...")
        try:
            article = await ai_service.generate_article(
                topic_title=topic["title"],
                topic_category=topic["category"],
                keywords=keywords,
                length=500
            )
            logger.info("✅ 短文生成成功！")
            logger.info(f"長度: {len(article)} 字")
            logger.info(f"內容預覽: {article[:200]}...")
        except Exception as e:
            logger.error(f"❌ 短文生成失敗: {e}")
            import traceback
            logger.error(traceback.format_exc())
            logger.info("\n請檢查：")
            logger.info("1. Ollama 是否正在運行")
            logger.info(f"2. 模型 {settings.OLLAMA_MODEL} 是否已下載")
            logger.info("3. 是否有足夠的 RAM（建議 8GB+）")
            return
        
        # 測試生成腳本
        logger.info("\n開始生成腳本（這可能需要一些時間）...")
        try:
            script = await ai_service.generate_script(
                topic_title=topic["title"],
                topic_category=topic["category"],
                keywords=keywords,
                duration=30
            )
            logger.info("✅ 腳本生成成功！")
            logger.info(f"長度: {len(script)} 字")
            logger.info(f"內容預覽: {script[:200]}...")
        except Exception as e:
            logger.error(f"❌ 腳本生成失敗: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return
        
        # 儲存到資料庫
        logger.info("\n儲存內容到資料庫...")
        from datetime import datetime
        
        content_data = {
            "id": f"content_{topic_id}",
            "topic_id": topic_id,
            "article": article,
            "script": script,
            "word_count": len(article) + len(script),
            "estimated_duration": (len(article) + len(script)) // 17,
            "model_used": ai_service.model,
            "prompt_version": "v1.0",
            "version": 1,
            "generated_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        existing = await content_repo.get_content_by_topic_id(topic_id)
        if existing:
            await content_repo.update_content(existing["id"], content_data, create_version=True)
            logger.info("✅ 內容已更新")
        else:
            await content_repo.create_content(content_data)
            logger.info("✅ 內容已建立")
        
        logger.info("\n✅ Ollama 生成測試完成！")
        
    except Exception as e:
        logger.error(f"❌ 測試失敗: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(test_ollama_generation())
