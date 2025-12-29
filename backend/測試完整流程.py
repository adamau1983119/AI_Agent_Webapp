"""
測試完整 API 流程
包括建立主題、生成內容、搜尋圖片
"""
import asyncio
import httpx
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:8000/api/v1"


async def test_full_flow():
    """測試完整流程"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        logger.info("=" * 60)
        logger.info("開始測試完整 API 流程")
        logger.info("=" * 60)
        
        # 1. 檢查健康狀態
        logger.info("\n1. 檢查 API 健康狀態...")
        try:
            response = await client.get(f"{API_BASE_URL}/health")
            if response.status_code == 200:
                logger.info(f"✅ API 正常運行: {response.json()}")
            else:
                logger.error(f"❌ API 健康檢查失敗: {response.status_code}")
                return
        except Exception as e:
            logger.error(f"❌ 無法連接到 API: {e}")
            logger.info("請確保後端服務正在運行（執行 'python -m uvicorn app.main:app --reload'）")
            return
        
        # 2. 取得主題列表
        logger.info("\n2. 取得主題列表...")
        try:
            response = await client.get(f"{API_BASE_URL}/topics?page=1&limit=10")
            if response.status_code == 200:
                data = response.json()
                topics = data.get("data", [])
                logger.info(f"✅ 取得 {len(topics)} 個主題")
                if topics:
                    logger.info(f"   範例: {topics[0].get('title', 'N/A')}")
            else:
                logger.error(f"❌ 取得主題列表失敗: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ 錯誤: {e}")
        
        # 3. 取得主題詳情
        logger.info("\n3. 取得主題詳情...")
        try:
            response = await client.get(f"{API_BASE_URL}/topics/topic_001")
            if response.status_code == 200:
                topic = response.json()
                logger.info(f"✅ 取得主題詳情: {topic.get('title', 'N/A')}")
            elif response.status_code == 404:
                logger.warning("⚠️  主題 topic_001 不存在，請先執行 建立測試資料.py")
            else:
                logger.error(f"❌ 取得主題詳情失敗: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ 錯誤: {e}")
        
        # 4. 測試生成內容（需要 API Key）
        logger.info("\n4. 測試生成內容...")
        try:
            response = await client.post(
                f"{API_BASE_URL}/contents/topic_001/generate",
                json={
                    "type": "both",
                    "article_length": 500,
                    "script_duration": 30
                },
                timeout=120.0  # AI 生成可能需要較長時間
            )
            if response.status_code == 200:
                content = response.json()
                logger.info("✅ 內容生成成功！")
                logger.info(f"   字數: {content.get('word_count', 0)}")
                logger.info(f"   時長: {content.get('estimated_duration', 0)} 秒")
            elif response.status_code == 400:
                logger.warning("⚠️  生成內容失敗（可能是 API Key 未設定）")
            else:
                logger.error(f"❌ 生成內容失敗: {response.status_code} - {response.text}")
        except httpx.TimeoutException:
            logger.warning("⚠️  請求超時（AI 生成可能需要更長時間）")
        except Exception as e:
            logger.error(f"❌ 錯誤: {e}")
        
        # 5. 測試搜尋圖片（需要 API Key）
        logger.info("\n5. 測試搜尋圖片...")
        try:
            response = await client.get(
                f"{API_BASE_URL}/images/search?keywords=fashion&page=1&limit=5",
                timeout=30.0
            )
            if response.status_code == 200:
                data = response.json()
                images = data.get("data", [])
                logger.info(f"✅ 搜尋成功！找到 {len(images)} 張圖片")
                if images:
                    logger.info(f"   範例: {images[0].get('url', 'N/A')[:80]}...")
            elif response.status_code == 400:
                logger.warning("⚠️  搜尋圖片失敗（可能是 API Key 未設定）")
            else:
                logger.error(f"❌ 搜尋圖片失敗: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"❌ 錯誤: {e}")
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ 測試完成！")
        logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_full_flow())
