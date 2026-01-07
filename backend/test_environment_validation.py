"""
測試環境變數驗證和 API 端點
"""
import asyncio
import sys
import logging

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_environment_variables():
    """測試環境變數讀取"""
    logger.info("=== 測試環境變數讀取 ===")
    
    from app.config import settings
    
    logger.info(f"AI_SERVICE: {settings.AI_SERVICE}")
    logger.info(f"DEEPSEEK_API_KEY 存在: {bool(settings.DEEPSEEK_API_KEY)}")
    logger.info(f"GOOGLE_API_KEY 存在: {bool(settings.GOOGLE_API_KEY)}")
    logger.info(f"GOOGLE_SEARCH_ENGINE_ID 存在: {bool(settings.GOOGLE_SEARCH_ENGINE_ID)}")
    logger.info(f"UNSPLASH_ACCESS_KEY 存在: {bool(settings.UNSPLASH_ACCESS_KEY)}")
    logger.info(f"PEXELS_API_KEY 存在: {bool(settings.PEXELS_API_KEY)}")
    logger.info(f"PIXABAY_API_KEY 存在: {bool(settings.PIXABAY_API_KEY)}")
    
    return True


def test_ai_service_factory():
    """測試 AIServiceFactory"""
    logger.info("=== 測試 AIServiceFactory ===")
    
    from app.services.ai.ai_service_factory import AIServiceFactory
    from app.config import settings
    
    try:
        service = AIServiceFactory.get_service(settings.AI_SERVICE)
        logger.info(f"✅ 成功載入 AI 服務: {settings.AI_SERVICE} ({type(service).__name__})")
        return True
    except Exception as e:
        logger.error(f"❌ 載入 AI 服務失敗: {e}")
        return False


async def test_validate_images_endpoint():
    """測試圖片驗證端點邏輯"""
    logger.info("=== 測試圖片驗證端點邏輯 ===")
    
    from app.config import settings
    
    # 模擬端點邏輯
    available_services = [
        svc for svc in [
            "duckduckgo",  # 總是可用
            "unsplash" if settings.UNSPLASH_ACCESS_KEY else None,
            "pexels" if settings.PEXELS_API_KEY else None,
            "pixabay" if settings.PIXABAY_API_KEY else None,
            "google_custom_search" if (settings.GOOGLE_API_KEY and settings.GOOGLE_SEARCH_ENGINE_ID) else None
        ] if svc
    ]
    
    result = {
        "unsplash": bool(settings.UNSPLASH_ACCESS_KEY),
        "pexels": bool(settings.PEXELS_API_KEY),
        "pixabay": bool(settings.PIXABAY_API_KEY),
        "google_api_key": bool(settings.GOOGLE_API_KEY),
        "google_search_engine_id": bool(settings.GOOGLE_SEARCH_ENGINE_ID),
        "duckduckgo": True,
        "available_services": available_services
    }
    
    logger.info(f"圖片服務狀態: {result}")
    logger.info(f"可用服務: {available_services}")
    
    return result


async def main():
    """主測試函數"""
    logger.info("開始測試環境變數驗證和 API 端點...")
    
    # 測試環境變數讀取
    await test_environment_variables()
    
    # 測試 AIServiceFactory
    ai_factory_ok = test_ai_service_factory()
    
    # 測試圖片驗證端點邏輯
    images_result = await test_validate_images_endpoint()
    
    logger.info("=== 測試完成 ===")
    logger.info(f"AIServiceFactory 測試: {'✅ 通過' if ai_factory_ok else '❌ 失敗'}")
    logger.info(f"圖片服務可用數量: {len(images_result['available_services'])}")
    
    return ai_factory_ok and len(images_result['available_services']) > 0


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except Exception as e:
        logger.error(f"測試失敗: {e}", exc_info=True)
        sys.exit(1)

