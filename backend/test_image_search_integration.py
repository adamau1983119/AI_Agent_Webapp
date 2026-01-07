"""
圖片搜尋功能整合測試
測試完整的數據流：API 端點 → ImageServiceManager → Google Custom Search → 響應
"""
import asyncio
import sys
import os

# 添加項目根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.images.image_service_manager import ImageServiceManager
from app.models.image import ImageSource
import logging

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_image_search():
    """測試圖片搜尋功能"""
    print("=" * 80)
    print("圖片搜尋功能整合測試")
    print("=" * 80)
    
    manager = ImageServiceManager()
    test_keywords = "technology"
    trace_id = "test_001"
    
    print(f"\n測試 1: 搜尋關鍵字 '{test_keywords}'（所有來源）")
    print("-" * 80)
    
    try:
        result = await manager.search_images(
            keywords=test_keywords,
            source=None,  # 自動選擇
            page=1,
            limit=5,
            trace_id=trace_id
        )
        
        print(f"[OK] 搜尋成功")
        print(f"   使用的來源: {result.get('source', 'None')}")
        print(f"   返回圖片數: {len(result.get('items', []))}")
        print(f"   嘗試記錄數: {len(result.get('attempts', []))}")
        
        # 顯示 attempts
        if result.get('attempts'):
            print("\n   嘗試記錄:")
            for attempt in result.get('attempts', []):
                status_icon = {
                    'success': '[OK]',
                    'no_results': '[WARN]',
                    'error': '[ERROR]',
                    'unavailable': '[SKIP]',
                    'exception': '[EXCEPTION]'
                }.get(attempt.get('status'), '[?]')
                
                print(f"     {status_icon} {attempt.get('source', 'unknown')}: {attempt.get('status', 'unknown')}")
                if attempt.get('count') is not None:
                    print(f"       數量: {attempt.get('count')}")
                if attempt.get('message'):
                    print(f"       訊息: {attempt.get('message')}")
        
        # 顯示所有圖片
        items = result.get('items', [])
        if items:
            print(f"\n   返回的 {len(items)} 張圖片:")
            for i, img in enumerate(items, 1):
                url = img.get('url', '')
                source = img.get('source', 'unknown')
                title = img.get('title', '')[:50] if img.get('title') else '無標題'
                print(f"\n     {i}. {source}")
                print(f"        URL: {url}")
                print(f"        標題: {title}")
                if img.get('thumbnail_url') and img.get('thumbnail_url') != url:
                    print(f"        縮圖: {img.get('thumbnail_url')}")
        else:
            print("\n   [WARN] 沒有返回圖片")
            
    except Exception as e:
        print(f"[ERROR] 搜尋失敗: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("測試 2: 指定 Google Custom Search 來源")
    print("-" * 80)
    
    try:
        result = await manager.search_images(
            keywords=test_keywords,
            source=ImageSource.GOOGLE_CUSTOM_SEARCH,
            page=1,
            limit=5,
            trace_id="test_002"
        )
        
        print(f"[OK] 搜尋成功")
        print(f"   使用的來源: {result.get('source', 'None')}")
        print(f"   返回圖片數: {len(result.get('items', []))}")
        
        items = result.get('items', [])
        if items:
            print(f"\n   返回的 {len(items)} 張圖片:")
            for i, img in enumerate(items, 1):
                url = img.get('url', '')
                source = img.get('source', 'unknown')
                title = img.get('title', '')[:50] if img.get('title') else '無標題'
                print(f"\n     {i}. {source}")
                print(f"        URL: {url}")
                print(f"        標題: {title}")
                if img.get('thumbnail_url') and img.get('thumbnail_url') != url:
                    print(f"        縮圖: {img.get('thumbnail_url')}")
        else:
            print("\n   [WARN] 沒有返回圖片")
            if result.get('attempts'):
                print("\n   嘗試記錄:")
                for attempt in result.get('attempts', []):
                    print(f"     {attempt.get('source', 'unknown')}: {attempt.get('status', 'unknown')} - {attempt.get('message', '')}")
                    
    except Exception as e:
        print(f"[ERROR] 搜尋失敗: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("測試完成")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_image_search())

