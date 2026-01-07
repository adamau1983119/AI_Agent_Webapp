"""
添加測試圖片到指定主題
用於測試圖片顯示功能
"""
import asyncio
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.repositories.image_repository import ImageRepository
from app.models.image import ImageSource

# 測試圖片 URL（關鍵字：technology）
TEST_IMAGES = [
    {
        "url": "https://globalfocusmagazine.com/wp-content/uploads/2020/02/Engaging_with_technology-scaled.jpg",
        "title": "Engaging with technology",
        "source": ImageSource.GOOGLE_CUSTOM_SEARCH.value,
        "photographer": "globalfocusmagazine.com",
        "license": "Unknown",
        "keywords": ["technology"],
    },
    {
        "url": "https://miro.medium.com/v2/resize:fit:1400/1*6-dNFz13P5prRz_kYaInXg.jpeg",
        "title": "Is Technology Ruining Your Experience At Work?",
        "source": ImageSource.GOOGLE_CUSTOM_SEARCH.value,
        "photographer": "Medium",
        "license": "Unknown",
        "keywords": ["technology"],
    },
    {
        "url": "https://bernardmarr.com/wp-content/uploads/2022/04/The-10-Biggest-Technology-Trends-That-Will-Transform-The-Next-Decade.jpg",
        "title": "The 10 Biggest Technology Trends That Will Transform The Next Decade",
        "source": ImageSource.GOOGLE_CUSTOM_SEARCH.value,
        "photographer": "Bernard Marr",
        "license": "Unknown",
        "keywords": ["technology"],
    },
    {
        "url": "https://cdn.britannica.com/84/203584-050-57D326E5/speed-internet-technology-background.jpg",
        "title": "History of Technology Timeline",
        "source": ImageSource.GOOGLE_CUSTOM_SEARCH.value,
        "photographer": "Britannica",
        "license": "Unknown",
        "keywords": ["technology"],
    },
    {
        "url": "https://thrivabilitymatters.org/2024/wp-content/uploads/2023/10/view-bioengineering-advance-with-robotic-hands-1024x768.jpg",
        "title": "Why Technology Is A Necessity",
        "source": ImageSource.GOOGLE_CUSTOM_SEARCH.value,
        "photographer": "THRIVE Project",
        "license": "Unknown",
        "keywords": ["technology"],
    },
]


async def add_test_images(topic_id: str):
    """添加測試圖片到指定主題"""
    print("=" * 80)
    print("添加測試圖片到主題")
    print("=" * 80)
    print(f"\n主題 ID: {topic_id}")
    print(f"圖片數量: {len(TEST_IMAGES)} 張\n")
    
    image_repo = ImageRepository()
    
    # 檢查現有圖片數量
    existing_images = await image_repo.get_images_by_topic_id(topic_id)
    max_order = max([img.get("order", 0) for img in existing_images]) if existing_images else -1
    
    print(f"現有圖片數量: {len(existing_images)}")
    print(f"當前最大 order: {max_order}\n")
    
    added_count = 0
    failed_count = 0
    
    for idx, img_data in enumerate(TEST_IMAGES, 1):
        try:
            image_data = {
                "id": f"test_img_{topic_id}_{idx}_{int(datetime.utcnow().timestamp())}",
                "topic_id": topic_id,
                "url": img_data["url"],
                "source": img_data["source"],
                "photographer": img_data.get("photographer", ""),
                "photographer_url": "",
                "license": img_data.get("license", "Unknown"),
                "keywords": img_data.get("keywords", []),
                "order": max_order + idx,
                "fetched_at": datetime.utcnow(),
            }
            
            created = await image_repo.create_image(image_data)
            added_count += 1
            print(f"[OK] 圖片 {idx} 已添加")
            print(f"     URL: {img_data['url'][:70]}...")
            print(f"     標題: {img_data.get('title', '無標題')[:50]}")
            
        except Exception as e:
            failed_count += 1
            print(f"[ERROR] 圖片 {idx} 添加失敗: {e}")
            print(f"     URL: {img_data['url'][:70]}...")
    
    print("\n" + "=" * 80)
    print(f"添加完成: 成功 {added_count} 張，失敗 {failed_count} 張")
    print("=" * 80)
    
    # 驗證添加結果
    final_images = await image_repo.get_images_by_topic_id(topic_id)
    print(f"\n主題現在共有 {len(final_images)} 張圖片")
    
    return added_count, failed_count


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法: python add_test_images.py <topic_id>")
        print("\n範例:")
        print("  python add_test_images.py topic_trend_20260107062510_2")
        sys.exit(1)
    
    topic_id = sys.argv[1]
    asyncio.run(add_test_images(topic_id))

