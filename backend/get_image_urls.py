"""
快速獲取圖片搜尋結果的 URL
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.images.image_service_manager import ImageServiceManager
from app.models.image import ImageSource

async def get_image_urls():
    """獲取圖片 URL"""
    manager = ImageServiceManager()
    
    result = await manager.search_images(
        keywords="technology",
        source=ImageSource.GOOGLE_CUSTOM_SEARCH,
        page=1,
        limit=5,
        trace_id="url_test"
    )
    
    items = result.get('items', [])
    print(f"\n關鍵字: technology")
    print(f"返回結果: {len(items)} 張圖片\n")
    print("=" * 80)
    
    for i, img in enumerate(items, 1):
        print(f"\n圖片 {i}:")
        print(f"  來源: {img.get('source', 'unknown')}")
        print(f"  URL: {img.get('url', '')}")
        if img.get('title'):
            print(f"  標題: {img.get('title', '')[:80]}")
        if img.get('thumbnail_url') and img.get('thumbnail_url') != img.get('url'):
            print(f"  縮圖: {img.get('thumbnail_url')}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(get_image_urls())

