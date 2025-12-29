"""
測試圖片搜尋功能
"""
import asyncio
from app.services.images.image_service import ImageService
from app.models.image import ImageSource
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_image_search():
    """測試圖片搜尋功能"""
    try:
        image_service = ImageService()
        
        # 檢查是否有可用的 API Key
        has_unsplash = bool(settings.UNSPLASH_ACCESS_KEY)
        has_pexels = bool(settings.PEXELS_API_KEY)
        has_pixabay = bool(settings.PIXABAY_API_KEY)
        
        logger.info("API Key 狀態:")
        logger.info(f"  Unsplash: {'✅' if has_unsplash else '❌'}")
        logger.info(f"  Pexels: {'✅' if has_pexels else '❌'}")
        logger.info(f"  Pixabay: {'✅' if has_pixabay else '❌'}")
        
        if not (has_unsplash or has_pexels or has_pixabay):
            logger.error("❌ 沒有可用的圖片服務 API Key！")
            logger.info("請在 .env 檔案中至少設定一個圖片服務的 API Key")
            return
        
        # 測試搜尋
        keywords = "fashion"
        logger.info(f"\n開始搜尋圖片: {keywords}")
        
        try:
            images = await image_service.search_images(
                keywords=keywords,
                page=1,
                limit=5,
                use_fallback=True
            )
            
            logger.info(f"✅ 搜尋成功！找到 {len(images)} 張圖片")
            
            # 顯示前 3 張圖片資訊
            for i, img in enumerate(images[:3], 1):
                logger.info(f"\n圖片 {i}:")
                logger.info(f"  ID: {img.get('id', 'N/A')}")
                logger.info(f"  來源: {img.get('source', 'N/A')}")
                logger.info(f"  攝影師: {img.get('photographer', 'N/A')}")
                logger.info(f"  URL: {img.get('url', 'N/A')[:80]}...")
                logger.info(f"  尺寸: {img.get('width', 'N/A')}x{img.get('height', 'N/A')}")
            
            logger.info("\n✅ 圖片搜尋測試完成！")
            
        except ValueError as e:
            logger.error(f"❌ 搜尋失敗: {e}")
        except Exception as e:
            logger.error(f"❌ 搜尋時發生錯誤: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
    except Exception as e:
        logger.error(f"❌ 測試失敗: {e}")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(test_image_search())
