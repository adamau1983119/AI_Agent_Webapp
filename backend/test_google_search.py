"""
測試 Google Custom Search API 圖片搜尋功能
"""
import asyncio
import sys
import os

# 添加專案路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.images.image_service_manager import ImageServiceManager
from app.models.image import ImageSource
from app.config import settings
import logging

# 設定輸出編碼
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_google_search():
    """測試 Google Custom Search 圖片搜尋"""
    try:
        # 檢查設定
        has_api_key = bool(settings.GOOGLE_API_KEY)
        has_search_engine_id = bool(settings.GOOGLE_SEARCH_ENGINE_ID)
        
        logger.info("Google Custom Search API 設定狀態:")
        logger.info(f"  API Key: {'✅ 已設定' if has_api_key else '❌ 未設定'}")
        logger.info(f"  Search Engine ID: {'✅ 已設定' if has_search_engine_id else '❌ 未設定'}")
        
        if not has_api_key or not has_search_engine_id:
            logger.error("❌ Google Custom Search API 未完整設定！")
            logger.info("請執行 .\設定Google_Custom_Search_API.ps1 進行設定")
            return
        
        mgr = ImageServiceManager()
        
        # 測試搜尋 "dior 2026春夏"
        keywords = "dior 2026春夏"
        logger.info(f"\n搜尋關鍵字: {keywords}")
        logger.info("嘗試使用 Google Custom Search...")
        
        # 直接指定使用 Google Custom Search
        images = await mgr.search_images(
            keywords=keywords,
            source=ImageSource.GOOGLE_CUSTOM_SEARCH,
            limit=5
        )
        
        logger.info(f"✅ 找到 {len(images)} 張圖片")
        
        # 顯示前 3 張圖片
        for i, img in enumerate(images[:3], 1):
            logger.info(f"\n圖片 {i}:")
            logger.info(f"  ID: {img.get('id', 'N/A')}")
            logger.info(f"  URL: {img.get('url', 'N/A')[:80]}...")
            logger.info(f"  標題: {img.get('title', 'N/A')[:50]}...")
            logger.info(f"  來源: {img.get('source', 'N/A')}")
            logger.info(f"  尺寸: {img.get('width', 0)}x{img.get('height', 0)}")
        
        logger.info("\n✅ Google Custom Search 測試成功！")
        
    except ValueError as e:
        logger.error(f"❌ 設定錯誤: {e}")
        logger.info("請確認 API Key 和 Search Engine ID 是否正確設定")
    except Exception as e:
        logger.error(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_google_search())

