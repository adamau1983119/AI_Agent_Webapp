"""
測試 DuckDuckGo 圖片搜尋功能
"""
import asyncio
import sys
import os

# 添加專案路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.images.image_service_manager import ImageServiceManager
import logging

# 設定輸出編碼
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_search():
    """測試圖片搜尋"""
    try:
        mgr = ImageServiceManager()
        
        # 測試搜尋 "dior 2026春夏"
        keywords = "dior 2026春夏"
        logger.info(f"搜尋關鍵字: {keywords}")
        
        images = await mgr.search_images(keywords, limit=5)
        
        logger.info(f"找到 {len(images)} 張圖片")
        
        # 顯示前 3 張圖片
        for i, img in enumerate(images[:3], 1):
            logger.info(f"\n圖片 {i}:")
            logger.info(f"  ID: {img.get('id', 'N/A')}")
            logger.info(f"  URL: {img.get('url', 'N/A')[:80]}...")
            logger.info(f"  標題: {img.get('title', 'N/A')[:50]}...")
            logger.info(f"  來源: {img.get('source', 'N/A')}")
            logger.info(f"  尺寸: {img.get('width', 0)}x{img.get('height', 0)}")
        
        logger.info("\n✅ 測試成功！")
        
    except Exception as e:
        logger.error(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_search())

