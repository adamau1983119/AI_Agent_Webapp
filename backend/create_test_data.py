"""
建立測試資料腳本
"""
import asyncio
from datetime import datetime
from app.database import connect_to_mongo, close_mongo_connection
from app.services.repositories.topic_repository import TopicRepository
from app.models.topic import Category, Status
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_test_data():
    """建立測試資料"""
    await connect_to_mongo()
    
    try:
        topic_repo = TopicRepository()
        
        # 測試主題列表
        test_topics = [
            {
                "id": "topic_001",
                "title": "2025 春夏時尚趨勢",
                "category": Category.FASHION.value,
                "status": Status.PENDING.value,
                "source": "Vogue",
                "sources": [
                    {
                        "type": "rss",
                        "url": "https://example.com/rss",
                        "keywords": ["時尚", "春夏", "趨勢"]
                    }
                ],
                "generated_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "created_at": datetime.utcnow()
            },
            {
                "id": "topic_002",
                "title": "台北必吃美食推薦",
                "category": Category.FOOD.value,
                "status": Status.PENDING.value,
                "source": "CNN",
                "sources": [
                    {
                        "type": "youtube",
                        "url": "https://youtube.com/watch?v=example",
                        "keywords": ["美食", "台北", "推薦"]
                    }
                ],
                "generated_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "created_at": datetime.utcnow()
            }
        ]
        
        # 建立測試主題
        for topic_data in test_topics:
            existing = await topic_repo.get_topic_by_id(topic_data["id"])
            if existing:
                logger.info(f"主題 {topic_data['id']} 已存在，跳過")
            else:
                await topic_repo.create_topic(topic_data)
                logger.info(f"✅ 已建立主題: {topic_data['title']}")
        
        logger.info("\n✅ 測試資料建立完成！")
        
    except Exception as e:
        logger.error(f"❌ 建立測試資料失敗: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(create_test_data())
