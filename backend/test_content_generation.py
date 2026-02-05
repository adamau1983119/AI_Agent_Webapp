"""
測試內容生成和圖片提取功能
驗證新的改進邏輯是否正常工作
"""
import asyncio
import sys
import io
import httpx
from app.services.automation.topic_collector import TopicCollector
from app.models.topic import Category
from app.utils.article_extractor import ArticleExtractor

# 設置 UTF-8 編碼輸出
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


async def test_content_generation():
    """測試內容生成和圖片提取功能"""
    print("=" * 80)
    print("🧪 測試內容生成和圖片提取功能")
    print("=" * 80)
    print()
    
    # 1. 測試從 RSS Feed 收集主題
    print("1️⃣ 測試從 RSS Feed 收集主題...")
    collector = TopicCollector()
    
    # 測試時尚類別
    print("\n📰 測試 FASHION 類別（收集 1 個主題）...")
    try:
        fashion_topics = await collector.collect_topics(
            category=Category.FASHION,
            count=1,
            use_fallback=False
        )
        
        if fashion_topics:
            topic = fashion_topics[0]
            print(f"✅ 成功收集主題: {topic.get('title', 'N/A')}")
            print(f"   來源: {topic.get('source', 'N/A')}")
            print(f"   摘要: {topic.get('description', 'N/A')}")
            
            # 檢查來源資訊
            sources = topic.get('sources', [])
            if sources:
                source = sources[0]
                print(f"\n📋 來源資訊:")
                print(f"   原文連結: {source.get('url', 'N/A')}")
                
                images = source.get('images', [])
                if images:
                    print(f"   原文圖片: {len(images)} 張")
                    for idx, img_url in enumerate(images[:3], 1):
                        print(f"      {idx}. {img_url[:80]}...")
                else:
                    print(f"   ⚠️  未提取到原文圖片")
                
                original_content = source.get('original_content')
                if original_content:
                    print(f"   原文內容: {len(original_content)} 字")
                    print(f"   前100字: {original_content[:100]}...")
                else:
                    print(f"   ⚠️  未提取到原文內容")
                
                language = source.get('language')
                if language:
                    print(f"   語言: {language}")
                
                style = source.get('style')
                if style:
                    print(f"   風格: {style}")
            else:
                print("   ⚠️  沒有來源資訊")
        else:
            print("❌ 未能收集到主題")
    except Exception as e:
        print(f"❌ 收集主題失敗: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("2️⃣ 測試文章提取器...")
    print("=" * 80)
    
    # 測試文章提取器
    test_url = "https://www.vogue.com/slideshow/the-best-street-style-photos-from-the-fall-2026-menswear-shows-in-milan"
    print(f"\n🔗 測試 URL: {test_url}")
    
    extractor = ArticleExtractor()
    try:
        article_info = await extractor.extract_article_info(test_url)
        
        if article_info.get("success"):
            print("✅ 文章提取成功！")
            print(f"   圖片數量: {len(article_info.get('images', []))}")
            print(f"   內容長度: {len(article_info.get('original_content', ''))} 字")
            print(f"   語言: {article_info.get('language', 'N/A')}")
            print(f"   風格: {article_info.get('style', 'N/A')}")
            
            images = article_info.get('images', [])
            if images:
                print(f"\n📸 提取的圖片（前3張）:")
                for idx, img_url in enumerate(images[:3], 1):
                    print(f"   {idx}. {img_url}")
        else:
            print(f"❌ 文章提取失敗: {article_info.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ 文章提取失敗: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("3️⃣ 測試後端 API（如果服務正在運行）...")
    print("=" * 80)
    
    # 測試後端 API
    api_base_url = "http://localhost:8000"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 測試健康檢查
            print("\n🔍 測試健康檢查端點...")
            response = await client.get(f"{api_base_url}/health")
            if response.status_code == 200:
                print("✅ 後端服務正在運行")
                health_data = response.json()
                print(f"   狀態: {health_data.get('status', 'N/A')}")
                print(f"   環境: {health_data.get('environment', 'N/A')}")
                db_status = health_data.get('database', {}).get('status', 'N/A')
                print(f"   資料庫: {db_status}")
            else:
                print(f"⚠️  後端服務回應異常: HTTP {response.status_code}")
            
            # 測試主題收集端點
            print("\n🔍 測試主題收集端點...")
            try:
                response = await client.post(
                    f"{api_base_url}/api/v1/topics/collect",
                    json={"category": "fashion", "count": 1},
                    headers={"X-API-Key": "test"} if True else {}
                )
                if response.status_code == 200:
                    print("✅ 主題收集端點正常")
                    data = response.json()
                    print(f"   收集到 {len(data.get('topics', []))} 個主題")
                else:
                    print(f"⚠️  主題收集端點回應: HTTP {response.status_code}")
                    print(f"   訊息: {response.text[:200]}")
            except Exception as e:
                print(f"⚠️  主題收集端點測試失敗: {e}")
            
    except httpx.ConnectError:
        print("⚠️  後端服務未運行（http://localhost:8000）")
        print("   請先啟動後端服務：")
        print("   cd backend")
        print("   .\\venv\\Scripts\\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"⚠️  API 測試失敗: {e}")
    
    print("\n" + "=" * 80)
    print("📋 測試總結")
    print("=" * 80)
    print("\n✅ 測試完成！")
    print("\n💡 下一步：")
    print("   1. 確保後端服務在 http://localhost:8000 運行")
    print("   2. 確保前端服務在 http://localhost:3000 運行（或檢查實際端口）")
    print("   3. 訪問前端頁面測試完整流程")
    print("   4. 檢查生成的內容是否包含原文連結和圖片")


if __name__ == "__main__":
    asyncio.run(test_content_generation())

