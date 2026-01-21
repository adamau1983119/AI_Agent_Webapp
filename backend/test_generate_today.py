"""
測試生成今日主題功能
"""
import asyncio
import sys
import io
import httpx
import json
from datetime import datetime

# 設置 UTF-8 編碼輸出
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


async def test_generate_today():
    """測試生成今日主題功能"""
    api_base_url = "http://localhost:8000"
    
    print("=" * 80)
    print("🧪 測試生成今日主題功能")
    print("=" * 80)
    print()
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # 1. 檢查健康狀態
        print("1️⃣ 檢查後端健康狀態...")
        try:
            response = await client.get(f"{api_base_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ 後端服務正常")
                print(f"   狀態: {health_data.get('status')}")
                print(f"   資料庫: {health_data.get('database', {}).get('status')}")
            else:
                print(f"❌ 後端服務異常: HTTP {response.status_code}")
                return
        except Exception as e:
            print(f"❌ 無法連接到後端服務: {e}")
            print("   請確保後端服務運行在 http://localhost:8000")
            return
        
        print()
        
        # 2. 檢查現有主題
        print("2️⃣ 檢查現有主題...")
        try:
            response = await client.get(f"{api_base_url}/api/v1/topics?limit=5&page=1")
            if response.status_code == 200:
                topics_data = response.json()
                topics = topics_data.get('data', [])
                print(f"✅ 找到 {len(topics)} 個主題")
                
                if topics:
                    print("\n   最近的主題:")
                    for idx, topic in enumerate(topics[:3], 1):
                        print(f"   {idx}. {topic.get('title', 'N/A')[:50]}...")
                        print(f"      分類: {topic.get('category', 'N/A')}")
                        print(f"      狀態: {topic.get('status', 'N/A')}")
                        
                        # 檢查來源資訊
                        sources = topic.get('sources', [])
                        if sources:
                            source = sources[0]
                            print(f"      原文連結: {source.get('url', 'N/A')[:60]}...")
                            images = source.get('images', [])
                            if images:
                                print(f"      原文圖片: {len(images)} 張")
                            else:
                                print(f"      原文圖片: 無")
                        print()
            else:
                print(f"⚠️  獲取主題失敗: HTTP {response.status_code}")
        except Exception as e:
            print(f"⚠️  檢查主題失敗: {e}")
        
        print()
        
        # 3. 生成今日主題
        print("3️⃣ 生成今日主題...")
        print("   這可能需要 1-2 分鐘，請稍候...")
        try:
            response = await client.post(
                f"{api_base_url}/api/v1/schedules/generate-today",
                json={"force": False},
                timeout=120.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 生成任務已提交")
                print(f"   訊息: {result.get('message', 'N/A')}")
                print(f"   分類: {', '.join(result.get('categories', []))}")
                print(f"   預期數量: {result.get('expected_count', 0)}")
                print(f"   現有數量: {result.get('existing_count', 0)}")
                
                print("\n   等待 10 秒後檢查生成的主題...")
                await asyncio.sleep(10)
                
                # 4. 檢查生成的主題
                print("\n4️⃣ 檢查生成的主題...")
                response = await client.get(f"{api_base_url}/api/v1/topics?limit=30&page=1")
                if response.status_code == 200:
                    topics_data = response.json()
                    topics = topics_data.get('data', [])
                    
                    # 過濾今日主題
                    today = datetime.utcnow().date().isoformat()
                    today_topics = []
                    for topic in topics:
                        generated_at = topic.get('generated_at')
                        if generated_at:
                            if isinstance(generated_at, str):
                                topic_date = generated_at.split('T')[0]
                            else:
                                topic_date = str(generated_at).split('T')[0]
                            if topic_date == today:
                                today_topics.append(topic)
                    
                    print(f"✅ 找到 {len(today_topics)} 個今日主題")
                    
                    if today_topics:
                        print("\n   今日主題詳情:")
                        for idx, topic in enumerate(today_topics[:5], 1):
                            print(f"\n   {idx}. {topic.get('title', 'N/A')}")
                            print(f"      分類: {topic.get('category', 'N/A')}")
                            print(f"      摘要: {topic.get('description', 'N/A')[:50]}...")
                            
                            # 檢查來源資訊
                            sources = topic.get('sources', [])
                            if sources:
                                source = sources[0]
                                print(f"      原文連結: {source.get('url', 'N/A')[:60]}...")
                                
                                images = source.get('images', [])
                                if images:
                                    print(f"      ✅ 原文圖片: {len(images)} 張")
                                    for img_idx, img_url in enumerate(images[:2], 1):
                                        print(f"         {img_idx}. {img_url[:70]}...")
                                else:
                                    print(f"      ⚠️  原文圖片: 無")
                                
                                original_content = source.get('original_content')
                                if original_content:
                                    print(f"      ✅ 原文內容: {len(original_content)} 字")
                                else:
                                    print(f"      ⚠️  原文內容: 無")
                                
                                language = source.get('language')
                                if language:
                                    print(f"      語言: {language}")
                                
                                style = source.get('style')
                                if style:
                                    print(f"      風格: {style}")
                    else:
                        print("   ⚠️  沒有找到今日主題")
                        print("   提示: 主題可能還在生成中，請稍後再試")
            else:
                print(f"❌ 生成失敗: HTTP {response.status_code}")
                print(f"   回應: {response.text[:200]}")
        except httpx.TimeoutException:
            print("⚠️  請求超時（這可能是正常的，生成需要時間）")
            print("   請在前端界面查看生成進度")
        except Exception as e:
            print(f"❌ 生成失敗: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("📋 測試總結")
    print("=" * 80)
    print("\n✅ 測試完成！")
    print("\n💡 下一步：")
    print("   1. 在前端 Dashboard 點擊「生成中...」按鈕")
    print("   2. 等待主題生成完成（通常需要 1-2 分鐘）")
    print("   3. 檢查生成的主題是否包含原文連結和圖片")
    print("   4. 選擇一個主題生成內容")
    print("   5. 檢查生成的內容是否正確引用原文")


if __name__ == "__main__":
    asyncio.run(test_generate_today())

